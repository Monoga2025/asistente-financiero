import { useFocusEffect, useLocalSearchParams } from 'expo-router';
import { useCallback, useState } from 'react';
import { ActivityIndicator, Modal, Pressable, ScrollView, Text, TextInput, View } from 'react-native';
import { ChevronRight, CreditCard, Landmark, ArrowDownLeft, ArrowUpRight, Plus, Pencil, X } from 'lucide-react-native';
import { Button, Card, Chip, PersonBadge } from '@/components/ui';
import { Header } from '@/components/Header';
import { colors, radius, spacing } from '@/lib/theme';
import { formatCOP, formatShortDate, parseCOP } from '@/lib/format';
import {
  createAccount,
  fetchAccounts,
  fetchAccountTransactions,
  recordAccountMovement,
  updateAccount,
} from '@/lib/finance';
import { PERSON_LIST, DANIEL_ID } from '@/lib/people';
import type { Account, AccountTransaction } from '@/lib/types';

export default function CuentasScreen() {
  const params = useLocalSearchParams<{ id?: string }>();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);
  const [transactions, setTransactions] = useState<AccountTransaction[]>([]);
  const [loadingTx, setLoadingTx] = useState(false);
  const [showNewModal, setShowNewModal] = useState(false);

  const loadAccounts = useCallback(async () => {
    setLoading(true);
    try {
      const accs = await fetchAccounts();
      setAccounts(accs);
      if (params.id) {
        const found = accs.find((a) => a.id === params.id);
        if (found) openDetail(found);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [params.id]);

  useFocusEffect(
    useCallback(() => {
      loadAccounts();
    }, [loadAccounts]),
  );

  async function openDetail(account: Account) {
    setSelectedAccount(account);
    setLoadingTx(true);
    try {
      const txs = await fetchAccountTransactions(account.id, 100);
      setTransactions(txs);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingTx(false);
    }
  }

  async function refreshSelectedAccount(accountId: string) {
    const [accs, txs] = await Promise.all([fetchAccounts(), fetchAccountTransactions(accountId, 100)]);
    setAccounts(accs);
    const updated = accs.find((a) => a.id === accountId) ?? null;
    setSelectedAccount(updated);
    setTransactions(txs);
  }

  if (loading) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.bg, alignItems: 'center', justifyContent: 'center' }}>
        <ActivityIndicator size="large" color={colors.emerald} />
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <ScrollView contentContainerStyle={{ paddingHorizontal: spacing.md, paddingTop: spacing.lg, paddingBottom: spacing.xl + 40 }} showsVerticalScrollIndicator={false}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <View style={{ flex: 1 }}>
            <Header title="Cuentas" subtitle="Tus cuentas bancarias y tarjetas" />
          </View>
          <Pressable
            onPress={() => setShowNewModal(true)}
            style={{
              flexDirection: 'row',
              alignItems: 'center',
              gap: 4,
              backgroundColor: colors.emerald,
              paddingHorizontal: spacing.md,
              paddingVertical: spacing.sm,
              borderRadius: radius.full,
              marginTop: 4,
            }}
          >
            <Plus color="#fff" size={16} strokeWidth={2.5} />
            <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 13, color: '#fff' }}>Nueva cuenta</Text>
          </Pressable>
        </View>

        {PERSON_LIST.map((person) => {
          const personAccounts = accounts.filter((a) => a.person_id === person.id);
          return (
            <View key={person.id} style={{ marginBottom: spacing.lg }}>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.sm }}>
                <PersonBadge name={person.name} emoji={person.emoji} color={person.color} size="sm" />
                <View style={{ flex: 1, height: 1, backgroundColor: colors.border }} />
              </View>
              <View style={{ gap: spacing.sm }}>
                {personAccounts.map((a) => (
                  <AccountCard key={a.id} account={a} onPress={() => openDetail(a)} />
                ))}
              </View>
            </View>
          );
        })}
      </ScrollView>

      {/* Account detail modal */}
      <Modal visible={!!selectedAccount} transparent animationType="slide" onRequestClose={() => setSelectedAccount(null)}>
        <View style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.4)' }}>
          <View style={{ flex: 1, marginTop: 60, backgroundColor: colors.bg, borderTopLeftRadius: radius.xl, borderTopRightRadius: radius.xl, overflow: 'hidden' }}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: spacing.lg, borderBottomWidth: 1, borderBottomColor: colors.border }}>
              <Text style={{ fontFamily: 'Inter-Bold', fontSize: 18, color: colors.text }}>{selectedAccount?.name}</Text>
              <Pressable onPress={() => setSelectedAccount(null)}><X color={colors.textSecondary} size={22} strokeWidth={2} /></Pressable>
            </View>
            <ScrollView contentContainerStyle={{ padding: spacing.md, paddingBottom: spacing.xl + 40 }} showsVerticalScrollIndicator={false}>
              {selectedAccount && (
                <AccountDetail
                  account={selectedAccount}
                  transactions={transactions}
                  loadingTx={loadingTx}
                  onChanged={() => refreshSelectedAccount(selectedAccount.id)}
                />
              )}
            </ScrollView>
          </View>
        </View>
      </Modal>

      {/* Create account modal */}
      <NewAccountModal
        visible={showNewModal}
        onClose={() => setShowNewModal(false)}
        onCreated={async () => {
          setShowNewModal(false);
          await loadAccounts();
        }}
      />
    </View>
  );
}

function AccountCard({ account, onPress }: { account: Account; onPress: () => void }) {
  const isCredit = account.type === 'credit';
  const available = isCredit ? (account.credit_limit ?? 0) - (account.credit_used ?? 0) : account.balance;
  const typeConfig: Record<string, { icon: React.ReactNode; bg: string; fg: string; label: string }> = {
    debit: { icon: <Landmark color={colors.debit} size={20} strokeWidth={2} />, bg: colors.debitLight, fg: colors.debit, label: 'Débito' },
    savings: { icon: <Landmark color={colors.debit} size={20} strokeWidth={2} />, bg: colors.debitLight, fg: colors.debit, label: 'Ahorro' },
    credit: { icon: <CreditCard color={colors.credit} size={20} strokeWidth={2} />, bg: colors.creditLight, fg: colors.credit, label: 'Crédito' },
  };
  const tc = typeConfig[account.type];

  return (
    <Pressable onPress={onPress} style={({ pressed }) => [{ opacity: pressed ? 0.8 : 1 }]}>
      <Card style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.sm }}>
        <View style={{ width: 44, height: 44, borderRadius: radius.sm, backgroundColor: tc.bg, alignItems: 'center', justifyContent: 'center' }}>
          {tc.icon}
        </View>
        <View style={{ flex: 1 }}>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
            <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 15, color: colors.text }}>{account.name}</Text>
            {account.is_default && (
              <View style={{ paddingHorizontal: spacing.xs + 2, paddingVertical: 2, borderRadius: radius.full, backgroundColor: colors.emeraldLight }}>
                <Text style={{ fontFamily: 'Inter-Medium', fontSize: 9, color: colors.emeraldDeep }}>Principal</Text>
              </View>
            )}
          </View>
          <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: colors.textSecondary }}>{account.bank} · {tc.label}</Text>
          {isCredit ? (
            <Text style={{ fontFamily: 'Inter-Bold', fontSize: 16, color: colors.text, marginTop: 4 }}>{formatCOP(available)}</Text>
          ) : (
            <Text style={{ fontFamily: 'Inter-Bold', fontSize: 16, color: account.balance < 0 ? colors.error : colors.text, marginTop: 4 }}>{formatCOP(account.balance)}</Text>
          )}
        </View>
        <ChevronRight color={colors.textMuted} size={20} strokeWidth={2} />
      </Card>
    </Pressable>
  );
}

function AccountDetail({
  account,
  transactions,
  loadingTx,
  onChanged,
}: {
  account: Account;
  transactions: AccountTransaction[];
  loadingTx: boolean;
  onChanged: () => Promise<void>;
}) {
  const isCredit = account.type === 'credit';
  const available = isCredit ? (account.credit_limit ?? 0) - (account.credit_used ?? 0) : account.balance;

  const [mode, setMode] = useState<'none' | 'income' | 'edit'>('none');
  const [amountInput, setAmountInput] = useState('');
  const [limitInput, setLimitInput] = useState('');
  const [descInput, setDescInput] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function openEditMode() {
    setError(null);
    setAmountInput(String(isCredit ? account.credit_used ?? 0 : account.balance));
    setLimitInput(String(account.credit_limit ?? 0));
    setDescInput('Ajuste de saldo inicial');
    setMode('edit');
  }

  function openIncomeMode() {
    setError(null);
    setAmountInput('');
    setDescInput(isCredit ? 'Abono a tarjeta de crédito' : 'Ingreso / Salario');
    setMode('income');
  }

  async function handleSaveAction() {
    setError(null);
    setSaving(true);
    try {
      if (mode === 'income') {
        const amt = parseCOP(amountInput);
        if (amt <= 0) throw new Error('Ingresa un monto mayor a cero.');
        await recordAccountMovement(account.id, {
          type: isCredit ? 'payment' : 'income',
          amount: amt,
          description: descInput.trim() || (isCredit ? 'Abono tarjeta' : 'Ingreso'),
        });
      } else if (mode === 'edit') {
        const newBal = parseCOP(amountInput);
        const newLimit = isCredit ? parseCOP(limitInput) : undefined;
        await updateAccount(account.id, {
          balance: newBal,
          creditLimit: newLimit,
          description: descInput.trim() || 'Ajuste de saldo',
        });
      }
      setMode('none');
      await onChanged();
    } catch (e: any) {
      setError(e?.message ?? 'No se pudo actualizar la cuenta.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <View style={{ gap: spacing.md }}>
      {/* Main balance */}
      <Card style={{ alignItems: 'center', paddingVertical: spacing.lg }}>
        <Text style={{ fontFamily: 'Inter-Medium', fontSize: 14, color: colors.textSecondary, marginBottom: spacing.xs }}>
          {isCredit ? 'Cupo disponible' : 'Saldo disponible'}
        </Text>
        <Text style={{ fontFamily: 'Inter-Bold', fontSize: 32, color: !isCredit && account.balance < 0 ? colors.error : colors.text }}>
          {formatCOP(available)}
        </Text>

        <View style={{ flexDirection: 'row', gap: spacing.sm, marginTop: spacing.md }}>
          <Pressable
            onPress={openIncomeMode}
            style={{
              flexDirection: 'row',
              alignItems: 'center',
              gap: 6,
              paddingHorizontal: spacing.md,
              paddingVertical: spacing.sm,
              borderRadius: radius.full,
              backgroundColor: colors.emerald,
            }}
          >
            <Plus color="#fff" size={16} strokeWidth={2.5} />
            <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 13, color: '#fff' }}>
              {isCredit ? 'Abonar a tarjeta' : 'Registrar ingreso'}
            </Text>
          </Pressable>

          <Pressable
            onPress={openEditMode}
            style={{
              flexDirection: 'row',
              alignItems: 'center',
              gap: 6,
              paddingHorizontal: spacing.md,
              paddingVertical: spacing.sm,
              borderRadius: radius.full,
              backgroundColor: colors.emeraldLight,
            }}
          >
            <Pencil color={colors.emeraldDeep} size={14} strokeWidth={2} />
            <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 13, color: colors.emeraldDeep }}>
              Ajustar saldo
            </Text>
          </Pressable>
        </View>
      </Card>

      {/* Action form (income or edit balance) */}
      {mode !== 'none' && (
        <Card style={{ gap: spacing.sm, borderWidth: 1.5, borderColor: colors.emerald }}>
          <Text style={{ fontFamily: 'Inter-Bold', fontSize: 16, color: colors.text }}>
            {mode === 'income'
              ? isCredit
                ? 'Abonar a tarjeta de crédito'
                : 'Registrar ingreso en la cuenta'
              : isCredit
              ? 'Ajustar cupo total y cupo usado'
              : 'Ajustar saldo actual de la cuenta'}
          </Text>

          <Text style={{ fontFamily: 'Inter-Medium', fontSize: 12, color: colors.textSecondary }}>
            {mode === 'income' ? 'Monto a sumar' : isCredit ? 'Cupo usado actual' : 'Nuevo saldo exacto'}
          </Text>
          <TextInput
            value={amountInput !== '' ? formatCOP(parseCOP(amountInput)) : ''}
            onChangeText={(t) => setAmountInput(String(parseCOP(t)))}
            placeholder="$0"
            placeholderTextColor={colors.textMuted}
            keyboardType="numeric"
            style={inputStyle}
          />

          {mode === 'edit' && isCredit && (
            <>
              <Text style={{ fontFamily: 'Inter-Medium', fontSize: 12, color: colors.textSecondary }}>Cupo total de la tarjeta</Text>
              <TextInput
                value={limitInput !== '' ? formatCOP(parseCOP(limitInput)) : ''}
                onChangeText={(t) => setLimitInput(String(parseCOP(t)))}
                placeholder="$0"
                placeholderTextColor={colors.textMuted}
                keyboardType="numeric"
                style={inputStyle}
              />
            </>
          )}

          <Text style={{ fontFamily: 'Inter-Medium', fontSize: 12, color: colors.textSecondary }}>Descripción</Text>
          <TextInput
            value={descInput}
            onChangeText={setDescInput}
            placeholder="Ej. Quincena / Saldo inicial"
            placeholderTextColor={colors.textMuted}
            style={inputStyle}
          />

          {error && <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.error }}>{error}</Text>}

          <View style={{ flexDirection: 'row', gap: spacing.sm, marginTop: spacing.xs }}>
            <Button label="Cancelar" onPress={() => setMode('none')} variant="secondary" fullWidth />
            <Button label={saving ? 'Guardando...' : 'Guardar'} onPress={handleSaveAction} fullWidth disabled={saving} />
          </View>
        </Card>
      )}

      {/* Credit card details */}
      {isCredit && (
        <Card>
          <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 15, color: colors.text, marginBottom: spacing.md }}>Detalle tarjeta de crédito</Text>
          <DetailRow label="Banco / App" value={account.bank} />
          <DetailRow label="Cupo total" value={formatCOP(account.credit_limit ?? 0)} />
          <DetailRow label="Cupo usado" value={formatCOP(account.credit_used ?? 0)} />
          <DetailRow label="Cupo disponible" value={formatCOP(available)} />
          <DetailRow label="Día de corte" value={`${account.cutoff_day}`} />
          <DetailRow label="Día límite de pago" value={`${account.due_day}`} />
          <View style={{ marginTop: spacing.md, paddingTop: spacing.md, borderTopWidth: 1, borderTopColor: colors.border }}>
            <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.textSecondary, marginBottom: spacing.xs }}>Próximo pago estimado</Text>
            <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 15, color: colors.text }}>
              Pago total a una cuota: {formatCOP(account.credit_used ?? 0)}
            </Text>
            <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: colors.textSecondary, marginTop: 4 }}>
              Nu cobra 0% de interés a una cuota. Paga antes del día {account.due_day} del próximo mes.
            </Text>
          </View>
        </Card>
      )}

      {/* Transactions */}
      <View>
        <Text style={{ fontFamily: 'Inter-Bold', fontSize: 18, color: colors.text, marginBottom: spacing.sm }}>Movimientos</Text>
        {loadingTx ? (
          <ActivityIndicator size="large" color={colors.emerald} />
        ) : transactions.length === 0 ? (
          <Card style={{ alignItems: 'center', paddingVertical: spacing.lg }}>
            <Text style={{ fontFamily: 'Inter-Regular', fontSize: 14, color: colors.textSecondary }}>Sin movimientos aún</Text>
          </Card>
        ) : (
          <View style={{ gap: spacing.sm }}>
            {transactions.map((tx) => (
              <Card key={tx.id}>
                <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
                  <View style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.sm, flex: 1 }}>
                    <View style={{ width: 36, height: 36, borderRadius: 18, backgroundColor: tx.amount < 0 ? colors.errorLight : colors.emeraldLight, alignItems: 'center', justifyContent: 'center' }}>
                      {tx.amount < 0 ? <ArrowUpRight color={colors.error} size={18} strokeWidth={2} /> : <ArrowDownLeft color={colors.emerald} size={18} strokeWidth={2} />}
                    </View>
                    <View style={{ flex: 1 }}>
                      <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 14, color: colors.text }} numberOfLines={1}>{tx.description ?? tx.type}</Text>
                      <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: colors.textSecondary }}>{formatShortDate(tx.created_at)}</Text>
                    </View>
                  </View>
                  <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 15, color: tx.amount < 0 ? colors.error : colors.emerald }}>
                    {tx.amount < 0 ? '-' : '+'}{formatCOP(Math.abs(tx.amount))}
                  </Text>
                </View>
              </Card>
            ))}
          </View>
        )}
      </View>
    </View>
  );
}

function NewAccountModal({
  visible,
  onClose,
  onCreated,
}: {
  visible: boolean;
  onClose: () => void;
  onCreated: () => Promise<void>;
}) {
  const [personId, setPersonId] = useState(DANIEL_ID);
  const [name, setName] = useState('');
  const [bank, setBank] = useState<'Nequi' | 'Nu'>('Nequi');
  const [kind, setKind] = useState<'debit' | 'credit'>('debit');
  const [balance, setBalance] = useState('');
  const [creditLimit, setCreditLimit] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleCreate() {
    if (!name.trim()) return setError('Escribe el nombre de la cuenta');
    setSaving(true);
    setError(null);
    try {
      await createAccount({
        personId,
        name: name.trim(),
        bank,
        kind,
        balance: parseCOP(balance),
        creditLimit: kind === 'credit' ? parseCOP(creditLimit) : null,
      });
      setName('');
      setBalance('');
      setCreditLimit('');
      await onCreated();
    } catch (e: any) {
      setError(e?.message ?? 'No se pudo crear la cuenta.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onClose}>
      <View style={{ flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.4)' }}>
        <View style={{ backgroundColor: colors.card, borderTopLeftRadius: radius.xl, borderTopRightRadius: radius.xl, padding: spacing.lg, paddingBottom: spacing.xl, gap: spacing.sm }}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text style={{ fontFamily: 'Inter-Bold', fontSize: 18, color: colors.text }}>Nueva cuenta</Text>
            <Pressable onPress={onClose}><X color={colors.textSecondary} size={22} strokeWidth={2} /></Pressable>
          </View>

          <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.textSecondary }}>Titular</Text>
          <View style={{ flexDirection: 'row', gap: spacing.sm }}>
            {PERSON_LIST.map((p) => (
              <Chip key={p.id} label={p.name} selected={personId === p.id} onPress={() => setPersonId(p.id)} color={p.color} />
            ))}
          </View>

          <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.textSecondary }}>Nombre de la cuenta</Text>
          <TextInput value={name} onChangeText={setName} placeholder="Ej. Bancolombia / Nequi / Nu" placeholderTextColor={colors.textMuted} style={inputStyle} />

          <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.textSecondary }}>Tipo</Text>
          <View style={{ flexDirection: 'row', gap: spacing.sm }}>
            <Chip label="Débito / Ahorros" selected={kind === 'debit'} onPress={() => setKind('debit')} />
            <Chip label="Tarjeta de crédito" selected={kind === 'credit'} onPress={() => { setKind('credit'); setBank('Nu'); }} />
          </View>

          <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.textSecondary }}>
            {kind === 'credit' ? 'Cupo usado actual' : 'Saldo inicial'}
          </Text>
          <TextInput
            value={balance ? formatCOP(parseCOP(balance)) : ''}
            onChangeText={(t) => setBalance(String(parseCOP(t)))}
            placeholder="$0"
            placeholderTextColor={colors.textMuted}
            keyboardType="numeric"
            style={inputStyle}
          />

          {kind === 'credit' && (
            <>
              <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.textSecondary }}>Cupo total de la tarjeta</Text>
              <TextInput
                value={creditLimit ? formatCOP(parseCOP(creditLimit)) : ''}
                onChangeText={(t) => setCreditLimit(String(parseCOP(t)))}
                placeholder="$1.000.000"
                placeholderTextColor={colors.textMuted}
                keyboardType="numeric"
                style={inputStyle}
              />
            </>
          )}

          {error && <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.error }}>{error}</Text>}

          <Button label={saving ? 'Creando...' : 'Crear cuenta'} onPress={handleCreate} fullWidth disabled={saving} />
        </View>
      </View>
    </Modal>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={{ flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 6 }}>
      <Text style={{ fontFamily: 'Inter-Regular', fontSize: 14, color: colors.textSecondary }}>{label}</Text>
      <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 14, color: colors.text }}>{value}</Text>
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
