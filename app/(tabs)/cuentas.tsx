import { useFocusEffect, useLocalSearchParams, useRouter } from 'expo-router';
import { useCallback, useState } from 'react';
import { ActivityIndicator, Modal, Pressable, ScrollView, Text, View } from 'react-native';
import { ChevronRight, Wallet, CreditCard, Landmark, ArrowDownLeft, ArrowUpRight, X } from 'lucide-react-native';
import { Card, PersonBadge } from '@/components/ui';
import { Header } from '@/components/Header';
import { colors, radius, shadows, spacing } from '@/lib/theme';
import { formatCOP, formatDate, formatShortDate } from '@/lib/format';
import { fetchAccounts, fetchAccountTransactions } from '@/lib/finance';
import { PEOPLE, PERSON_LIST, DANIEL_ID, ANA_ID } from '@/lib/people';
import type { Account, AccountTransaction } from '@/lib/types';

export default function CuentasScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ id?: string }>();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);
  const [transactions, setTransactions] = useState<AccountTransaction[]>([]);
  const [loadingTx, setLoadingTx] = useState(false);

  useFocusEffect(
    useCallback(() => {
      let active = true;
      (async () => {
        setLoading(true);
        try {
          const accs = await fetchAccounts();
          if (!active) return;
          setAccounts(accs);
          if (params.id) {
            const found = accs.find((a) => a.id === params.id);
            if (found) openDetail(found);
          }
        } catch (e) {
          console.error(e);
        } finally {
          if (active) setLoading(false);
        }
      })();
      return () => { active = false; };
    }, [params.id]),
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
        <Header title="Cuentas" subtitle="Tus cuentas bancarias y tarjetas" />

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
              {selectedAccount && <AccountDetail account={selectedAccount} transactions={transactions} loadingTx={loadingTx} />}
            </ScrollView>
          </View>
        </View>
      </Modal>
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

function AccountDetail({ account, transactions, loadingTx }: { account: Account; transactions: AccountTransaction[]; loadingTx: boolean }) {
  const isCredit = account.type === 'credit';
  const available = isCredit ? (account.credit_limit ?? 0) - (account.credit_used ?? 0) : account.balance;

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
      </Card>

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

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={{ flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 6 }}>
      <Text style={{ fontFamily: 'Inter-Regular', fontSize: 14, color: colors.textSecondary }}>{label}</Text>
      <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 14, color: colors.text }}>{value}</Text>
    </View>
  );
}
