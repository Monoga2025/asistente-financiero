import { useLocalSearchParams, useRouter } from 'expo-router';
import { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Modal,
  Pressable,
  ScrollView,
  Switch,
  Text,
  TextInput,
  View,
} from 'react-native';
import { Calendar, Check, ChevronDown, Image as ImageIcon, Plus, Trash2, X } from 'lucide-react-native';
import { Button, Card, Chip, PersonBadge } from '@/components/ui';
import { Header } from '@/components/Header';
import { colors, radius, shadows, spacing } from '@/lib/theme';
import { formatCOP, formatDate, parseCOP, toInputDate } from '@/lib/format';
import { balanceDeltaForExpense, computeShare, fetchAccounts, fetchExpenses, saveExpense } from '@/lib/finance';
import { PEOPLE, PERSON_LIST, DANIEL_ID, ANA_ID } from '@/lib/people';
import type { Account, Assignment, Expense, SplitType } from '@/lib/types';
import type { SaveExpenseInput } from '@/lib/finance';

interface ItemDraft {
  id: string;
  name: string;
  amount: string;
  assigned_to: Assignment;
}

export default function GastosScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ nuevo?: string }>();

  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loadingAccounts, setLoadingAccounts] = useState(true);

  const [title, setTitle] = useState('');
  const [date, setDate] = useState(toInputDate(new Date()));
  const [amount, setAmount] = useState('');
  const [paidBy, setPaidBy] = useState(DANIEL_ID);
  const [accountId, setAccountId] = useState<string | null>(null);
  const [splitType, setSplitType] = useState<SplitType>('half');
  const [surcharge, setSurcharge] = useState(false);
  const [alreadyPaid, setAlreadyPaid] = useState(false);
  const [note, setNote] = useState('');
  const [items, setItems] = useState<ItemDraft[]>([]);

  const [showAccountPicker, setShowAccountPicker] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const accs = await fetchAccounts();
        setAccounts(accs);
        const def = accs.find((a) => a.person_id === paidBy && a.is_default) ?? accs.find((a) => a.person_id === paidBy);
        setAccountId(def?.id ?? null);
      } catch (e) {
        console.error(e);
      } finally {
        setLoadingAccounts(false);
      }
    })();
  }, []);

  useEffect(() => {
    if (params.nuevo === '1') {
      setShowForm(true);
    }
  }, [params.nuevo]);

  const numericAmount = parseCOP(amount);
  const surchargeAmount = surcharge ? Math.round(numericAmount * 0.03) : 0;
  const totalWithSurcharge = numericAmount + surchargeAmount;

  const availableAccounts = accounts.filter((a) => a.person_id === paidBy);
  const selectedAccount = accounts.find((a) => a.id === accountId);

  function resetForm() {
    setTitle('');
    setDate(toInputDate(new Date()));
    setAmount('');
    setPaidBy(DANIEL_ID);
    setSplitType('half');
    setSurcharge(false);
    setAlreadyPaid(false);
    setNote('');
    setItems([]);
    setError(null);
  }

  function onPaidByChange(personId: string) {
    setPaidBy(personId);
    const def = accounts.find((a) => a.person_id === personId && a.is_default) ?? accounts.find((a) => a.person_id === personId);
    setAccountId(def?.id ?? null);
  }

  function addItem() {
    setItems([...items, { id: `item_${Date.now()}`, name: '', amount: '', assigned_to: 'half' }]);
  }

  function updateItem(id: string, field: keyof ItemDraft, value: string | Assignment) {
    setItems(items.map((it) => (it.id === id ? { ...it, [field]: value } : it)));
  }

  function removeItem(id: string) {
    setItems(items.filter((it) => it.id !== id));
  }

  const itemsSum = items.reduce((sum, it) => sum + parseCOP(it.amount), 0);
  const itemsMatch = itemsSum === numericAmount;

  async function handleSave() {
    setError(null);
    if (!title.trim()) return setError('Escribe un título para el gasto');
    if (numericAmount <= 0) return setError('El monto debe ser mayor que cero');
    if (splitType === 'by_items') {
      if (items.length === 0) return setError('Agrega al menos un concepto');
      if (!items.every((it) => it.name.trim() && parseCOP(it.amount) > 0)) return setError('Completa todos los conceptos');
      if (!itemsMatch) return setError(`La suma de conceptos (${formatCOP(itemsSum)}) no coincide con el monto (${formatCOP(numericAmount)})`);
    }

    setSaving(true);
    try {
      const input: SaveExpenseInput = {
        title: title.trim(),
        expenseDate: date,
        totalAmount: totalWithSurcharge,
        paidByPersonId: paidBy,
        accountId,
        splitType,
        surchargeApplied: surcharge,
        surchargeAmount,
        alreadyPaid,
        note: note.trim() || null,
        imageUrl: null,
        source: 'manual',
        items:
          splitType === 'by_items'
            ? items.map((it) => ({ name: it.name.trim(), amount: parseCOP(it.amount), assigned_to: it.assigned_to }))
            : undefined,
      };
      await saveExpense(input);
      resetForm();
      setShowForm(false);
      router.setParams({});
    } catch (e: any) {
      setError(e?.message ?? 'No se pudo guardar el gasto');
    } finally {
      setSaving(false);
    }
  }

  if (loadingAccounts) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.bg, alignItems: 'center', justifyContent: 'center' }}>
        <ActivityIndicator size="large" color={colors.emerald} />
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <ScrollView contentContainerStyle={{ paddingHorizontal: spacing.md, paddingTop: spacing.lg, paddingBottom: spacing.xl + 40 }} showsVerticalScrollIndicator={false}>
        <Header title="Gastos" subtitle="Registra y revisa tus gastos compartidos" />

        {!showForm ? (
          <ExpenseList />
        ) : (
          <View style={{ gap: spacing.md }}>
            {/* Title */}
            <Card>
              <Label text="Título" />
              <TextInput
                value={title}
                onChangeText={setTitle}
                placeholder="Ej. Mercados Éxito"
                placeholderTextColor={colors.textMuted}
                style={inputStyle}
              />
            </Card>

            {/* Date */}
            <Card>
              <Label text="Fecha" />
              <Pressable onPress={() => setShowDatePicker(true)} style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
                <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 16, color: colors.text }}>{formatDate(date)}</Text>
                <Calendar color={colors.textSecondary} size={20} strokeWidth={2} />
              </Pressable>
            </Card>

            {/* Amount */}
            <Card>
              <Label text="Monto" />
              <TextInput
                value={amount ? formatCOP(numericAmount) : ''}
                onChangeText={(t) => setAmount(t)}
                onFocus={() => setAmount(String(numericAmount))}
                onBlur={() => setAmount(numericAmount ? String(numericAmount) : '')}
                placeholder="$0"
                placeholderTextColor={colors.textMuted}
                keyboardType="numeric"
                style={[inputStyle, { fontFamily: 'Inter-Bold', fontSize: 24 }]}
              />
              {surcharge && (
                <View style={{ marginTop: spacing.sm, paddingTop: spacing.sm, borderTopWidth: 1, borderTopColor: colors.border }}>
                  <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                    <Text style={{ fontFamily: 'Inter-Regular', fontSize: 13, color: colors.textSecondary }}>Subtotal</Text>
                    <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.text }}>{formatCOP(numericAmount)}</Text>
                  </View>
                  <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                    <Text style={{ fontFamily: 'Inter-Regular', fontSize: 13, color: colors.textSecondary }}>Recargo datáfono 3%</Text>
                    <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.warning }}>{formatCOP(surchargeAmount)}</Text>
                  </View>
                  <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: spacing.xs }}>
                    <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 14, color: colors.text }}>Total</Text>
                    <Text style={{ fontFamily: 'Inter-Bold', fontSize: 14, color: colors.text }}>{formatCOP(totalWithSurcharge)}</Text>
                  </View>
                </View>
              )}
            </Card>

            {/* Paid by */}
            <Card>
              <Label text="Pagado por" />
              <View style={{ flexDirection: 'row', gap: spacing.sm }}>
                {PERSON_LIST.map((p) => (
                  <Pressable
                    key={p.id}
                    onPress={() => onPaidByChange(p.id)}
                    style={{
                      flex: 1,
                      flexDirection: 'row',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: spacing.xs,
                      paddingVertical: spacing.sm + 2,
                      borderRadius: radius.md,
                      borderWidth: 1.5,
                      borderColor: paidBy === p.id ? p.color : colors.border,
                      backgroundColor: paidBy === p.id ? p.color + '14' : '#fff',
                    }}
                  >
                    <Text style={{ fontSize: 16 }}>{p.emoji}</Text>
                    <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 14, color: paidBy === p.id ? p.color : colors.textSecondary }}>{p.name}</Text>
                  </Pressable>
                ))}
              </View>
            </Card>

            {/* Account */}
            <Card>
              <Label text="Cuenta usada" />
              <Pressable onPress={() => setShowAccountPicker(true)} style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
                <View>
                  <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 15, color: colors.text }}>
                    {selectedAccount ? selectedAccount.name : 'Sin cuenta'}
                  </Text>
                  {selectedAccount && (
                    <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: colors.textSecondary }}>
                      {selectedAccount.bank} · {selectedAccount.type === 'credit' ? 'Tarjeta de crédito' : 'Débito/Ahorro'}
                    </Text>
                  )}
                </View>
                <ChevronDown color={colors.textSecondary} size={20} strokeWidth={2} />
              </Pressable>
            </Card>

            {/* Split */}
            <Card>
              <Label text="División" />
              <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm }}>
                <Chip label="Mitad y mitad" selected={splitType === 'half'} onPress={() => setSplitType('half')} />
                <Chip label="Todo Daniel" selected={splitType === 'all_daniel'} onPress={() => setSplitType('all_daniel')} color={colors.daniel} lightColor={colors.danielLight} />
                <Chip label="Todo Ana" selected={splitType === 'all_ana'} onPress={() => setSplitType('all_ana')} color={colors.ana} lightColor={colors.anaLight} />
                <Chip label="Por conceptos" selected={splitType === 'by_items'} onPress={() => setSplitType('by_items')} />
              </View>

              {splitType === 'by_items' && (
                <View style={{ marginTop: spacing.md, gap: spacing.sm }}>
                  {items.map((it) => (
                    <View key={it.id} style={{ borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, padding: spacing.sm }}>
                      <View style={{ flexDirection: 'row', gap: spacing.sm, alignItems: 'center' }}>
                        <TextInput
                          value={it.name}
                          onChangeText={(v) => updateItem(it.id, 'name', v)}
                          placeholder="Concepto"
                          placeholderTextColor={colors.textMuted}
                          style={[inputStyle, { flex: 1 }]}
                        />
                        <TextInput
                          value={it.amount ? formatCOP(parseCOP(it.amount)) : ''}
                          onChangeText={(v) => updateItem(it.id, 'amount', String(parseCOP(v)))}
                          placeholder="$0"
                          placeholderTextColor={colors.textMuted}
                          keyboardType="numeric"
                          style={[inputStyle, { width: 110, fontFamily: 'Inter-SemiBold' }]}
                        />
                        <Pressable onPress={() => removeItem(it.id)}>
                          <Trash2 color={colors.error} size={18} strokeWidth={2} />
                        </Pressable>
                      </View>
                      <View style={{ flexDirection: 'row', gap: 6, marginTop: spacing.sm }}>
                        <Chip label="Ana" selected={it.assigned_to === 'ana'} onPress={() => updateItem(it.id, 'assigned_to', 'ana')} color={colors.ana} lightColor={colors.anaLight} />
                        <Chip label="Daniel" selected={it.assigned_to === 'daniel'} onPress={() => updateItem(it.id, 'assigned_to', 'daniel')} color={colors.daniel} lightColor={colors.danielLight} />
                        <Chip label="Mitad" selected={it.assigned_to === 'half'} onPress={() => updateItem(it.id, 'assigned_to', 'half')} />
                      </View>
                    </View>
                  ))}
                  <Pressable
                    onPress={addItem}
                    style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: spacing.xs, paddingVertical: spacing.sm, borderWidth: 1.5, borderStyle: 'dashed', borderColor: colors.emerald, borderRadius: radius.md }}
                  >
                    <Plus color={colors.emerald} size={18} strokeWidth={2} />
                    <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 14, color: colors.emerald }}>Agregar concepto</Text>
                  </Pressable>
                  {items.length > 0 && (
                    <Text style={{ fontFamily: 'Inter-Medium', fontSize: 12, color: itemsMatch ? colors.emerald : colors.warning, textAlign: 'center' }}>
                      Suma: {formatCOP(itemsSum)} / {formatCOP(numericAmount)} {itemsMatch ? '✓' : '— no coincide'}
                    </Text>
                  )}
                </View>
              )}
            </Card>

            {/* Surcharge toggle */}
            <Card>
              <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
                <View style={{ flex: 1 }}>
                  <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 15, color: colors.text }}>Recargo datáfono 3%</Text>
                  <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: colors.textSecondary }}>Si el local cobra 3% por tarjeta</Text>
                </View>
                <Switch value={surcharge} onValueChange={setSurcharge} trackColor={{ false: colors.border, true: colors.emerald }} />
              </View>
            </Card>

            {/* Already paid toggle */}
            <Card>
              <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
                <View style={{ flex: 1 }}>
                  <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 15, color: colors.text }}>Ya fue pagado antes</Text>
                  <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: colors.textSecondary }}>Registra la deuda sin tocar el saldo de la cuenta</Text>
                </View>
                <Switch value={alreadyPaid} onValueChange={setAlreadyPaid} trackColor={{ false: colors.border, true: colors.emerald }} />
              </View>
            </Card>

            {/* Note */}
            <Card>
              <Label text="Nota (opcional)" />
              <TextInput
                value={note}
                onChangeText={setNote}
                placeholder="Ej. Compra del mes..."
                placeholderTextColor={colors.textMuted}
                multiline
                style={[inputStyle, { minHeight: 60, textAlignVertical: 'top' }]}
              />
            </Card>

            {error && (
              <View style={{ backgroundColor: colors.errorLight, borderRadius: radius.md, padding: spacing.md }}>
                <Text style={{ fontFamily: 'Inter-Medium', fontSize: 14, color: colors.error }}>{error}</Text>
              </View>
            )}

            <View style={{ flexDirection: 'row', gap: spacing.sm }}>
              <Button label="Cancelar" onPress={() => { resetForm(); setShowForm(false); }} variant="secondary" fullWidth />
              <Button label={saving ? 'Guardando...' : 'Guardar gasto'} onPress={handleSave} fullWidth disabled={saving} />
            </View>
          </View>
        )}
      </ScrollView>

      {/* Floating new button when not in form mode */}
      {!showForm && (
        <Pressable
          onPress={() => setShowForm(true)}
          style={{
            position: 'absolute',
            bottom: spacing.xl + 16,
            right: spacing.md,
            width: 58,
            height: 58,
            borderRadius: 29,
            backgroundColor: colors.emerald,
            alignItems: 'center',
            justifyContent: 'center',
            ...shadows.elevated,
          }}
        >
          <Plus color="#fff" size={28} strokeWidth={2.5} />
        </Pressable>
      )}

      {/* Account picker modal */}
      <Modal visible={showAccountPicker} transparent animationType="slide" onRequestClose={() => setShowAccountPicker(false)}>
        <View style={{ flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.4)' }}>
          <View style={{ backgroundColor: colors.card, borderTopLeftRadius: radius.xl, borderTopRightRadius: radius.xl, padding: spacing.lg, paddingBottom: spacing.xl }}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.md }}>
              <Text style={{ fontFamily: 'Inter-Bold', fontSize: 18, color: colors.text }}>Selecciona cuenta</Text>
              <Pressable onPress={() => setShowAccountPicker(false)}><X color={colors.textSecondary} size={22} strokeWidth={2} /></Pressable>
            </View>
            <View style={{ gap: spacing.sm }}>
              <Pressable onPress={() => { setAccountId(null); setShowAccountPicker(false); }} style={{ paddingVertical: spacing.sm + 2, borderRadius: radius.md, backgroundColor: !accountId ? colors.emeraldLight : colors.bg }}>
                <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 15, color: !accountId ? colors.emeraldDeep : colors.textSecondary, textAlign: 'center' }}>Sin cuenta</Text>
              </Pressable>
              {availableAccounts.map((a) => (
                <Pressable
                  key={a.id}
                  onPress={() => { setAccountId(a.id); setShowAccountPicker(false); }}
                  style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingVertical: spacing.sm + 2, paddingHorizontal: spacing.md, borderRadius: radius.md, backgroundColor: accountId === a.id ? colors.emeraldLight : colors.bg }}
                >
                  <View>
                    <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 15, color: colors.text }}>{a.name}</Text>
                    <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: colors.textSecondary }}>{a.bank} · {a.type === 'credit' ? 'Crédito' : 'Débito'}</Text>
                  </View>
                  {accountId === a.id && <Check color={colors.emerald} size={20} strokeWidth={2} />}
                </Pressable>
              ))}
              {availableAccounts.length === 0 && (
                <Text style={{ fontFamily: 'Inter-Regular', fontSize: 14, color: colors.textSecondary, textAlign: 'center', paddingVertical: spacing.md }}>
                  No hay cuentas para esta persona
                </Text>
              )}
            </View>
          </View>
        </View>
      </Modal>

      {/* Date picker modal (simple scrollable) */}
      <Modal visible={showDatePicker} transparent animationType="slide" onRequestClose={() => setShowDatePicker(false)}>
        <View style={{ flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.4)' }}>
          <View style={{ backgroundColor: colors.card, borderTopLeftRadius: radius.xl, borderTopRightRadius: radius.xl, padding: spacing.lg, paddingBottom: spacing.xl }}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.md }}>
              <Text style={{ fontFamily: 'Inter-Bold', fontSize: 18, color: colors.text }}>Fecha del gasto</Text>
              <Pressable onPress={() => setShowDatePicker(false)}><X color={colors.textSecondary} size={22} strokeWidth={2} /></Pressable>
            </View>
            <DatePickerGrid value={date} onChange={setDate} onDone={() => setShowDatePicker(false)} />
          </View>
        </View>
      </Modal>
    </View>
  );
}

const inputStyle = {
  fontFamily: 'Inter-SemiBold',
  fontSize: 16,
  color: colors.text,
  paddingVertical: spacing.sm,
  paddingHorizontal: spacing.sm,
  backgroundColor: colors.bg,
  borderRadius: radius.sm,
} as const;

function Label({ text }: { text: string }) {
  return <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.textSecondary, marginBottom: spacing.sm }}>{text}</Text>;
}

function DatePickerGrid({ value, onChange, onDone }: { value: string; onChange: (v: string) => void; onDone: () => void }) {
  const [y, m, d] = value.split('-').map(Number);
  const today = new Date();
  const year = y ?? today.getFullYear();
  const month = m ?? today.getMonth() + 1;
  const day = d ?? today.getDate();

  const months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
  const daysInMonth = new Date(year, month, 0).getDate();

  return (
    <View style={{ gap: spacing.md }}>
      <View style={{ flexDirection: 'row', gap: spacing.sm }}>
        <PickerColumn
          label="Día"
          values={Array.from({ length: daysInMonth }, (_, i) => String(i + 1).padStart(2, '0'))}
          selected={String(day).padStart(2, '0')}
          onSelect={(v) => onChange(toInputDate(new Date(year, month - 1, parseInt(v, 10))))}
        />
        <PickerColumn
          label="Mes"
          values={months}
          selected={months[month - 1]}
          onSelect={(_, idx) => onChange(toInputDate(new Date(year, idx, day)))}
        />
        <PickerColumn
          label="Año"
          values={Array.from({ length: 5 }, (_, i) => String(today.getFullYear() - i))}
          selected={String(year)}
          onSelect={(v) => onChange(toInputDate(new Date(parseInt(v, 10), month - 1, day)))}
        />
      </View>
      <Button label="Listo" onPress={onDone} fullWidth />
    </View>
  );
}

function PickerColumn({ label, values, selected, onSelect }: { label: string; values: string[]; selected: string; onSelect: (v: string, idx: number) => void }) {
  return (
    <View style={{ flex: 1 }}>
      <Text style={{ fontFamily: 'Inter-Medium', fontSize: 12, color: colors.textMuted, textAlign: 'center', marginBottom: spacing.xs }}>{label}</Text>
      <ScrollView style={{ maxHeight: 200 }} showsVerticalScrollIndicator={false}>
        {values.map((v, idx) => (
          <Pressable
            key={v}
            onPress={() => onSelect(v, idx)}
            style={{ paddingVertical: spacing.sm, borderRadius: radius.sm, backgroundColor: selected === v ? colors.emeraldLight : 'transparent', alignItems: 'center' }}
          >
            <Text style={{ fontFamily: selected === v ? 'Inter-SemiBold' : 'Inter-Regular', fontSize: 14, color: selected === v ? colors.emeraldDeep : colors.text }}>{v}</Text>
          </Pressable>
        ))}
      </ScrollView>
    </View>
  );
}

function ExpenseList() {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'daniel' | 'ana'>('all');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchExpenses(200);
      setExpenses(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffectSafe(load);

  const filtered = expenses.filter((e) => {
    if (filter === 'all') return true;
    if (filter === 'daniel') return e.paid_by_person_id === DANIEL_ID;
    return e.paid_by_person_id === ANA_ID;
  });

  if (loading) {
    return (
      <View style={{ paddingVertical: spacing.xl, alignItems: 'center' }}>
        <ActivityIndicator size="large" color={colors.emerald} />
      </View>
    );
  }

  if (expenses.length === 0) {
    return (
      <Card style={{ alignItems: 'center', paddingVertical: spacing.xl }}>
        <ImageIcon color={colors.textMuted} size={40} strokeWidth={1.5} />
        <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 16, color: colors.text, marginTop: spacing.md }}>No hay gastos aún</Text>
        <Text style={{ fontFamily: 'Inter-Regular', fontSize: 14, color: colors.textSecondary, marginTop: spacing.xs, textAlign: 'center' }}>
          Toca el botón + para registrar tu primer gasto
        </Text>
      </Card>
    );
  }

  return (
    <View style={{ gap: spacing.sm }}>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.xs }}>
        <Text style={{ fontFamily: 'Inter-Bold', fontSize: 18, color: colors.text }}>Todos los gastos</Text>
        <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.textSecondary }}>{filtered.length} de {expenses.length}</Text>
      </View>
      <View style={{ flexDirection: 'row', gap: spacing.sm, marginBottom: spacing.sm }}>
        <Chip label="Todos" selected={filter === 'all'} onPress={() => setFilter('all')} />
        <Chip label="Daniel" selected={filter === 'daniel'} onPress={() => setFilter('daniel')} color={colors.daniel} lightColor={colors.danielLight} />
        <Chip label="Ana" selected={filter === 'ana'} onPress={() => setFilter('ana')} color={colors.ana} lightColor={colors.anaLight} />
      </View>
      {filtered.map((e) => {
        const person = PEOPLE[e.paid_by_person_id];
        return (
          <Card key={e.id}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <View style={{ flex: 1 }}>
                <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 15, color: colors.text }} numberOfLines={1}>{e.title}</Text>
                <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: colors.textSecondary, marginTop: 2 }}>{formatDate(e.expense_date)}</Text>
              </View>
              <Text style={{ fontFamily: 'Inter-Bold', fontSize: 16, color: colors.text }}>{formatCOP(e.total_amount)}</Text>
            </View>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginTop: spacing.sm }}>
              <PersonBadge name={person?.name ?? ''} emoji={person?.emoji ?? ''} color={person?.color ?? colors.emerald} size="sm" />
              {e.source === 'scan' && (
                <View style={{ paddingHorizontal: spacing.xs + 2, paddingVertical: 2, borderRadius: radius.full, backgroundColor: colors.danielLight }}>
                  <Text style={{ fontFamily: 'Inter-Medium', fontSize: 10, color: colors.daniel }}>Factura</Text>
                </View>
              )}
              {e.surcharge_applied && (
                <View style={{ paddingHorizontal: spacing.xs + 2, paddingVertical: 2, borderRadius: radius.full, backgroundColor: colors.warningLight }}>
                  <Text style={{ fontFamily: 'Inter-Medium', fontSize: 10, color: colors.warning }}>+3%</Text>
                </View>
              )}
              {e.already_paid && (
                <View style={{ paddingHorizontal: spacing.xs + 2, paddingVertical: 2, borderRadius: radius.full, backgroundColor: colors.textMuted + '22' }}>
                  <Text style={{ fontFamily: 'Inter-Medium', fontSize: 10, color: colors.textSecondary }}>Histórico</Text>
                </View>
              )}
            </View>
            <ExpenseDetails expense={e} />
          </Card>
        );
      })}
    </View>
  );
}

function ExpenseDetails({ expense }: { expense: Expense }) {
  const computed = computeShare(expense.total_amount, expense.split_type, expense.expense_items, expense.paid_by_person_id);
  const danielShare = expense.share_daniel ?? computed.danielShare;
  const anaShare = expense.share_ana ?? computed.anaShare;
  const delta = balanceDeltaForExpense(expense.paid_by_person_id, danielShare, anaShare);

  return (
    <View style={{ marginTop: spacing.sm, paddingTop: spacing.sm, borderTopWidth: 1, borderTopColor: colors.border, gap: spacing.sm }}>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 6 }}>
        <View style={{ paddingHorizontal: spacing.xs + 2, paddingVertical: 3, borderRadius: radius.full, backgroundColor: colors.daniel + '1a' }}>
          <Text style={{ fontFamily: 'Inter-Medium', fontSize: 11, color: colors.daniel }}>Daniel {formatCOP(danielShare)}</Text>
        </View>
        <View style={{ paddingHorizontal: spacing.xs + 2, paddingVertical: 3, borderRadius: radius.full, backgroundColor: colors.ana + '1a' }}>
          <Text style={{ fontFamily: 'Inter-Medium', fontSize: 11, color: colors.ana }}>Ana {formatCOP(anaShare)}</Text>
        </View>
        {delta !== 0 && (
          <View style={{ paddingHorizontal: spacing.xs + 2, paddingVertical: 3, borderRadius: radius.full, backgroundColor: delta > 0 ? colors.emeraldLight : colors.warningLight }}>
            <Text style={{ fontFamily: 'Inter-Medium', fontSize: 11, color: delta > 0 ? colors.emeraldDeep : colors.warning }}>
              {delta > 0 ? 'Ana debe' : 'Daniel debe'} {formatCOP(Math.abs(delta))}
            </Text>
          </View>
        )}
      </View>

      {!!expense.expense_items?.length && (
        <View style={{ gap: 6 }}>
          <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 12, color: colors.textSecondary }}>
            Conceptos ({expense.expense_items.length})
          </Text>
          {expense.expense_items.map((item) => (
            <View key={item.id} style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: spacing.sm }}>
              <View style={{ flex: 1 }}>
                <Text style={{ fontFamily: 'Inter-Regular', fontSize: 13, color: colors.text }}>{item.name}</Text>
                <Text style={{ fontFamily: 'Inter-Regular', fontSize: 11, color: colors.textSecondary }}>{assignmentLabel(item.assigned_to)}</Text>
              </View>
              <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 13, color: colors.text }}>{formatCOP(item.amount)}</Text>
            </View>
          ))}
        </View>
      )}
    </View>
  );
}

function assignmentLabel(value: Assignment) {
  if (value === 'daniel') return 'Daniel';
  if (value === 'ana') return 'Ana';
  return 'Mitad y mitad';
}

import { useFocusEffect } from 'expo-router';

function useFocusEffectSafe(fn: () => void) {
  useFocusEffect(
    useCallback(() => {
      fn();
    }, [fn]),
  );
}
