import { useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { ActivityIndicator, Modal, Pressable, ScrollView, Switch, Text, TextInput, View } from 'react-native';
import { ArrowRight, Check, Scale, X, HandCoins } from 'lucide-react-native';
import { Button, Card, Chip, PersonBadge } from '@/components/ui';
import { Header } from '@/components/Header';
import { colors, radius, shadows, spacing } from '@/lib/theme';
import { formatCOP, formatDate, toInputDate } from '@/lib/format';
import { computeBalance, describeBalance, fetchAccounts, fetchExpenses, fetchSettlements, saveSettlement, computeShare, balanceDeltaForExpense } from '@/lib/finance';
import { PEOPLE, PERSON_LIST, DANIEL_ID, ANA_ID } from '@/lib/people';
import type { Account, Expense, Settlement } from '@/lib/types';

export default function BalanceScreen() {
  const [balance, setBalance] = useState(0);
  const [loading, setLoading] = useState(true);
  const [settlements, setSettlements] = useState<Settlement[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [showSettleModal, setShowSettleModal] = useState(false);

  useFocusEffect(
    useCallback(() => {
      let active = true;
      (async () => {
        setLoading(true);
        try {
          const [bal, sets, exps, accs] = await Promise.all([computeBalance(), fetchSettlements(50), fetchExpenses(200), fetchAccounts()]);
          if (!active) return;
          setBalance(bal);
          setSettlements(sets);
          setExpenses(exps);
          setAccounts(accs);
        } catch (e) {
          console.error(e);
        } finally {
          if (active) setLoading(false);
        }
      })();
      return () => { active = false; };
    }, []),
  );

  const balanceInfo = describeBalance(balance);

  // Build per-expense contribution history
  const history = expenses.map((e) => {
    const { danielShare, anaShare } = computeShare(e.total_amount, e.split_type, e.expense_items, e.paid_by_person_id);
    const delta = balanceDeltaForExpense(e.paid_by_person_id, danielShare, anaShare);
    return {
      id: e.id,
      title: e.title,
      date: e.expense_date,
      total: e.total_amount,
      paidBy: e.paid_by_person_id,
      delta,
      danielShare,
      anaShare,
    };
  });

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <ScrollView contentContainerStyle={{ paddingHorizontal: spacing.md, paddingTop: spacing.lg, paddingBottom: spacing.xl + 40 }} showsVerticalScrollIndicator={false}>
        <Header title="Balance" subtitle="Deudas entre Ana y Daniel" />

        {loading ? (
          <ActivityIndicator size="large" color={colors.emerald} />
        ) : (
          <>
            {/* Main balance card */}
            <View
              style={{
                borderRadius: radius.lg,
                padding: spacing.lg,
                marginBottom: spacing.lg,
                backgroundColor: balance === 0 ? colors.emeraldDeep : colors.emerald,
                ...shadows.elevated,
              }}
            >
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.sm }}>
                <Scale color="#fff" size={20} strokeWidth={2} />
                <Text style={{ fontFamily: 'Inter-Medium', fontSize: 15, color: '#d1fae5' }}>Estado actual</Text>
              </View>
              <Text style={{ fontFamily: 'Inter-Bold', fontSize: 26, color: '#fff', marginBottom: spacing.xs }}>
                {balanceInfo.label}
              </Text>
              {balance !== 0 && (
                <>
                  <Text style={{ fontFamily: 'Inter-Bold', fontSize: 38, color: '#fff' }}>{formatCOP(balanceInfo.amount)}</Text>
                  <View style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginTop: spacing.sm }}>
                    <PersonBadge name={balanceInfo.owesFrom ?? ''} emoji={PEOPLE[balanceInfo.owesFrom === 'Ana' ? ANA_ID : DANIEL_ID]?.emoji ?? ''} color={PEOPLE[balanceInfo.owesFrom === 'Ana' ? ANA_ID : DANIEL_ID]?.color ?? colors.emerald} size="sm" />
                    <ArrowRight color="#fff" size={18} strokeWidth={2} />
                    <PersonBadge name={balanceInfo.owesTo ?? ''} emoji={PEOPLE[balanceInfo.owesTo === 'Ana' ? ANA_ID : DANIEL_ID]?.emoji ?? ''} color={PEOPLE[balanceInfo.owesTo === 'Ana' ? ANA_ID : DANIEL_ID]?.color ?? colors.emerald} size="sm" />
                  </View>
                </>
              )}
              {balance !== 0 && (
                <Pressable
                  onPress={() => setShowSettleModal(true)}
                  style={({ pressed }) => [{ marginTop: spacing.lg, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: spacing.sm, paddingVertical: spacing.sm + 2, borderRadius: radius.md, backgroundColor: 'rgba(255,255,255,0.2)', opacity: pressed ? 0.85 : 1 }]}
                >
                  <HandCoins color="#fff" size={18} strokeWidth={2} />
                  <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 15, color: '#fff' }}>Registrar pago</Text>
                </Pressable>
              )}
            </View>

            {/* History */}
            <View style={{ marginBottom: spacing.lg }}>
              <Text style={{ fontFamily: 'Inter-Bold', fontSize: 18, color: colors.text, marginBottom: spacing.sm }}>Historial de gastos</Text>
              <View style={{ gap: spacing.sm }}>
                {history.length === 0 ? (
                  <Card style={{ alignItems: 'center', paddingVertical: spacing.lg }}>
                    <Text style={{ fontFamily: 'Inter-Regular', fontSize: 14, color: colors.textSecondary }}>Aún no hay gastos</Text>
                  </Card>
                ) : (
                  history.slice(0, 20).map((h) => {
                    const payer = PEOPLE[h.paidBy];
                    return (
                      <Card key={h.id}>
                        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <View style={{ flex: 1 }}>
                            <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 14, color: colors.text }} numberOfLines={1}>{h.title}</Text>
                            <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: colors.textSecondary, marginTop: 2 }}>{formatDate(h.date)} · Pagó {payer?.name}</Text>
                          </View>
                          <Text style={{ fontFamily: 'Inter-Bold', fontSize: 15, color: colors.text }}>{formatCOP(h.total)}</Text>
                        </View>
                        <View style={{ flexDirection: 'row', gap: 6, marginTop: spacing.sm }}>
                          <View style={{ paddingHorizontal: spacing.xs + 2, paddingVertical: 3, borderRadius: radius.full, backgroundColor: colors.daniel + '1a' }}>
                            <Text style={{ fontFamily: 'Inter-Medium', fontSize: 11, color: colors.daniel }}>Daniel {formatCOP(h.danielShare)}</Text>
                          </View>
                          <View style={{ paddingHorizontal: spacing.xs + 2, paddingVertical: 3, borderRadius: radius.full, backgroundColor: colors.ana + '1a' }}>
                            <Text style={{ fontFamily: 'Inter-Medium', fontSize: 11, color: colors.ana }}>Ana {formatCOP(h.anaShare)}</Text>
                          </View>
                          {h.delta !== 0 && (
                            <View style={{ paddingHorizontal: spacing.xs + 2, paddingVertical: 3, borderRadius: radius.full, backgroundColor: h.delta > 0 ? colors.emeraldLight : colors.warningLight }}>
                              <Text style={{ fontFamily: 'Inter-Medium', fontSize: 11, color: h.delta > 0 ? colors.emeraldDeep : colors.warning }}>
                                {h.delta > 0 ? 'A→D' : 'D→A'} {formatCOP(Math.abs(h.delta))}
                              </Text>
                            </View>
                          )}
                        </View>
                      </Card>
                    );
                  })
                )}
              </View>
            </View>

            {/* Settlements */}
            {settlements.length > 0 && (
              <View>
                <Text style={{ fontFamily: 'Inter-Bold', fontSize: 18, color: colors.text, marginBottom: spacing.sm }}>Pagos realizados</Text>
                <View style={{ gap: spacing.sm }}>
                  {settlements.map((s) => {
                    const from = PEOPLE[s.from_person_id];
                    const to = PEOPLE[s.to_person_id];
                    return (
                      <Card key={s.id}>
                        <View style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.sm }}>
                          <View style={{ width: 36, height: 36, borderRadius: 18, backgroundColor: colors.emeraldLight, alignItems: 'center', justifyContent: 'center' }}>
                            <Check color={colors.emerald} size={18} strokeWidth={2.5} />
                          </View>
                          <View style={{ flex: 1 }}>
                            <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 14, color: colors.text }}>
                              {from?.name} → {to?.name}
                            </Text>
                            <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: colors.textSecondary }}>{formatDate(s.settlement_date)}</Text>
                          </View>
                          <Text style={{ fontFamily: 'Inter-Bold', fontSize: 15, color: colors.emerald }}>{formatCOP(s.amount)}</Text>
                        </View>
                      </Card>
                    );
                  })}
                </View>
              </View>
            )}
          </>
        )}
      </ScrollView>

      {/* Settle modal */}
      <SettleModal
        visible={showSettleModal}
        onClose={() => setShowSettleModal(false)}
        balanceInfo={balanceInfo}
        accounts={accounts}
        onDone={() => {
          setShowSettleModal(false);
          setLoading(true);
          computeBalance().then(setBalance).finally(() => setLoading(false));
          fetchSettlements(50).then(setSettlements);
        }}
      />
    </View>
  );
}

function SettleModal({ visible, onClose, balanceInfo, accounts, onDone }: { visible: boolean; onClose: () => void; balanceInfo: ReturnType<typeof describeBalance>; accounts: Account[]; onDone: () => void }) {
  const fromId = balanceInfo.owesFrom === 'Ana' ? ANA_ID : balanceInfo.owesFrom === 'Daniel' ? DANIEL_ID : null;
  const toId = balanceInfo.owesTo === 'Ana' ? ANA_ID : balanceInfo.owesTo === 'Daniel' ? DANIEL_ID : null;
  const [amount, setAmount] = useState('');
  const [accountId, setAccountId] = useState<string | null>(null);
  const [note, setNote] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const payerAccounts = accounts.filter((a) => a.person_id === fromId);

  async function handleSave() {
    if (!fromId || !toId) return;
    const amt = parseInt(amount.replace(/[^0-9]/g, '') || '0', 10);
    if (amt <= 0) return setError('Ingresa un monto válido');
    setSaving(true);
    setError(null);
    try {
      await saveSettlement({
        fromPersonId: fromId,
        toPersonId: toId,
        amount: amt,
        accountId,
        date: toInputDate(new Date()),
        note: note.trim() || null,
      });
      setAmount('');
      setNote('');
      setAccountId(null);
      onDone();
    } catch (e: any) {
      setError(e?.message ?? 'No se pudo guardar el pago');
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onClose}>
      <View style={{ flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.4)' }}>
        <View style={{ backgroundColor: colors.card, borderTopLeftRadius: radius.xl, borderTopRightRadius: radius.xl, padding: spacing.lg, paddingBottom: spacing.xl }}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.md }}>
            <Text style={{ fontFamily: 'Inter-Bold', fontSize: 18, color: colors.text }}>Registrar pago</Text>
            <Pressable onPress={onClose}><X color={colors.textSecondary} size={22} strokeWidth={2} /></Pressable>
          </View>

          <View style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.md }}>
            <PersonBadge name={balanceInfo.owesFrom ?? ''} emoji={fromId === ANA_ID ? '👩' : '🧑'} color={fromId === ANA_ID ? colors.ana : colors.daniel} size="sm" />
            <ArrowRight color={colors.textMuted} size={18} strokeWidth={2} />
            <PersonBadge name={balanceInfo.owesTo ?? ''} emoji={toId === ANA_ID ? '👩' : '🧑'} color={toId === ANA_ID ? colors.ana : colors.daniel} size="sm" />
          </View>

          <Text style={{ fontFamily: 'Inter-Regular', fontSize: 13, color: colors.textSecondary, marginBottom: spacing.sm }}>
            Deuda actual: {formatCOP(balanceInfo.amount)}
          </Text>

          <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.textSecondary, marginBottom: spacing.xs }}>Monto a pagar</Text>
          <TextInput
            value={amount ? formatCOP(parseInt(amount.replace(/[^0-9]/g, '') || '0', 10)) : ''}
            onChangeText={(t) => setAmount(String(parseInt(t.replace(/[^0-9]/g, '') || '0', 10)))}
            placeholder="$0"
            placeholderTextColor={colors.textMuted}
            keyboardType="numeric"
            style={{
              fontFamily: 'Inter-Bold',
              fontSize: 22,
              color: colors.text,
              paddingVertical: spacing.sm,
              paddingHorizontal: spacing.md,
              backgroundColor: colors.bg,
              borderRadius: radius.md,
              marginBottom: spacing.md,
            }}
          />

          <Pressable
            onPress={() => setAmount(String(balanceInfo.amount))}
            style={{ alignSelf: 'flex-start', marginBottom: spacing.md, paddingHorizontal: spacing.sm + 4, paddingVertical: spacing.xs + 2, borderRadius: radius.full, backgroundColor: colors.emeraldLight }}
          >
            <Text style={{ fontFamily: 'Inter-Medium', fontSize: 12, color: colors.emeraldDeep }}>Pagar todo: {formatCOP(balanceInfo.amount)}</Text>
          </Pressable>

          {payerAccounts.length > 0 && (
            <>
              <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.textSecondary, marginBottom: spacing.sm }}>Cuenta (opcional)</Text>
              <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm, marginBottom: spacing.md }}>
                <Chip label="Sin cuenta" selected={!accountId} onPress={() => setAccountId(null)} />
                {payerAccounts.map((a) => (
                  <Chip key={a.id} label={a.name} selected={accountId === a.id} onPress={() => setAccountId(a.id)} />
                ))}
              </View>
            </>
          )}

          <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.textSecondary, marginBottom: spacing.xs }}>Nota (opcional)</Text>
          <TextInput
            value={note}
            onChangeText={setNote}
            placeholder="Ej. Transferencia Nequi"
            placeholderTextColor={colors.textMuted}
            style={{
              fontFamily: 'Inter-Regular',
              fontSize: 15,
              color: colors.text,
              paddingVertical: spacing.sm,
              paddingHorizontal: spacing.md,
              backgroundColor: colors.bg,
              borderRadius: radius.md,
              marginBottom: spacing.md,
            }}
          />

          {error && (
            <View style={{ backgroundColor: colors.errorLight, borderRadius: radius.md, padding: spacing.md, marginBottom: spacing.md }}>
              <Text style={{ fontFamily: 'Inter-Medium', fontSize: 14, color: colors.error }}>{error}</Text>
            </View>
          )}

          <Button label={saving ? 'Guardando...' : 'Confirmar pago'} onPress={handleSave} fullWidth disabled={saving} />
        </View>
      </View>
    </Modal>
  );
}
