import { useFocusEffect, useRouter } from 'expo-router';
import { useCallback, useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, Text, View } from 'react-native';
import { Plus, ScanLine, Wallet, ChevronRight, TrendingDown, Scale } from 'lucide-react-native';
import { Card, PersonBadge, SectionTitle } from '@/components/ui';
import { colors, radius, shadows, spacing } from '@/lib/theme';
import { formatCOP, formatDate, monthLabel } from '@/lib/format';
import { fetchAccounts, fetchExpenses, computeBalance, describeBalance, computeShare } from '@/lib/finance';
import { PEOPLE, PERSON_LIST } from '@/lib/people';
import type { Account, Expense } from '@/lib/types';
import { Header } from '@/components/Header';

export default function HomeScreen() {
  const router = useRouter();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [balance, setBalance] = useState(0);
  const [loading, setLoading] = useState(true);

  useFocusEffect(
    useCallback(() => {
      let active = true;
      (async () => {
        setLoading(true);
        try {
          const [accs, exps, bal] = await Promise.all([fetchAccounts(), fetchExpenses(50), computeBalance()]);
          if (!active) return;
          setAccounts(accs);
          setExpenses(exps);
          setBalance(bal);
        } catch (e) {
          console.error('Home load error', e);
        } finally {
          if (active) setLoading(false);
        }
      })();
      return () => {
        active = false;
      };
    }, []),
  );

  const balanceInfo = describeBalance(balance);
  const totalDebit = accounts
    .filter((a) => a.type === 'debit' || a.type === 'savings')
    .reduce((sum, a) => sum + a.balance, 0);

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <ScrollView contentContainerStyle={{ paddingHorizontal: spacing.md, paddingTop: spacing.lg, paddingBottom: spacing.xl + 40 }} showsVerticalScrollIndicator={false}>
        <Header title="Finanzas" subtitle={`Hola Ana y Daniel · ${monthLabel(new Date())}`} />

        {/* Balance card */}
        <View
          style={{
            borderRadius: radius.lg,
            padding: spacing.lg,
            marginBottom: spacing.lg,
            backgroundColor: balance === 0 ? colors.emeraldDeep : colors.emerald,
            ...shadows.elevated,
          }}
        >
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.xs }}>
            <Scale color="#fff" size={18} strokeWidth={2} />
            <Text style={{ fontFamily: 'Inter-Medium', fontSize: 14, color: '#d1fae5' }}>Balance entre ustedes</Text>
          </View>
          <Text style={{ fontFamily: 'Inter-Bold', fontSize: 22, color: '#fff', marginBottom: spacing.xs }}>
            {balanceInfo.label}
          </Text>
          {balance !== 0 && (
            <Text style={{ fontFamily: 'Inter-Bold', fontSize: 34, color: '#fff' }}>
              {formatCOP(balanceInfo.amount)}
            </Text>
          )}
          {balance !== 0 && (
            <Text style={{ fontFamily: 'Inter-Regular', fontSize: 13, color: '#a7f3d0', marginTop: spacing.xs }}>
              {balanceInfo.owesFrom} → {balanceInfo.owesTo}
            </Text>
          )}
        </View>

        {/* Quick actions */}
        <View style={{ flexDirection: 'row', gap: spacing.sm, marginBottom: spacing.lg }}>
          <QuickAction icon={<Plus color="#fff" size={22} strokeWidth={2} />} label="Nuevo gasto" onPress={() => router.push('/gastos?nuevo=1')} bg={colors.emerald} />
          <QuickAction icon={<ScanLine color="#fff" size={22} strokeWidth={2} />} label="Escanear" onPress={() => router.push('/escanear')} bg={colors.daniel} />
          <QuickAction icon={<Wallet color="#fff" size={22} strokeWidth={2} />} label="Cuentas" onPress={() => router.push('/cuentas')} bg={colors.ana} />
        </View>

        {/* Loading state */}
        {loading ? (
          <View style={{ paddingVertical: spacing.xl, alignItems: 'center' }}>
            <ActivityIndicator size="large" color={colors.emerald} />
          </View>
        ) : (
          <>
            {/* Account summary */}
            <View style={{ marginBottom: spacing.lg }}>
              <SectionTitle title="Resumen de cuentas" action={<Pressable onPress={() => router.push('/cuentas')}><Text style={{ fontFamily: 'Inter-Medium', fontSize: 14, color: colors.emerald }}>Ver todas</Text></Pressable>} />
              <View style={{ gap: spacing.sm }}>
                {accounts.map((a) => (
                  <AccountRow key={a.id} account={a} onPress={() => router.push(`/cuentas?id=${a.id}`)} />
                ))}
              </View>
            </View>

            {/* Recent expenses */}
            <View>
              <SectionTitle title="Gastos recientes" action={<Pressable onPress={() => router.push('/gastos')}><Text style={{ fontFamily: 'Inter-Medium', fontSize: 14, color: colors.emerald }}>Ver todos ({expenses.length})</Text></Pressable>} />
              {expenses.length === 0 ? (
                <Card style={{ alignItems: 'center', paddingVertical: spacing.lg }}>
                  <Text style={{ fontFamily: 'Inter-Regular', fontSize: 15, color: colors.textSecondary }}>Aún no hay gastos registrados</Text>
                </Card>
              ) : (
                <View style={{ gap: spacing.sm }}>
                  {expenses.slice(0, 8).map((e) => (
                    <ExpenseRow key={e.id} expense={e} />
                  ))}
                </View>
              )}
            </View>
          </>
        )}
      </ScrollView>
    </View>
  );
}

function QuickAction({ icon, label, onPress, bg }: { icon: React.ReactNode; label: string; onPress: () => void; bg: string }) {
  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [
        {
          flex: 1,
          backgroundColor: bg,
          borderRadius: radius.md,
          paddingVertical: spacing.md,
          paddingHorizontal: spacing.sm,
          alignItems: 'center',
          gap: spacing.xs,
          opacity: pressed ? 0.85 : 1,
          ...shadows.card,
        },
      ]}
    >
      {icon}
      <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 12, color: '#fff', textAlign: 'center' }}>{label}</Text>
    </Pressable>
  );
}

function AccountRow({ account, onPress }: { account: Account; onPress: () => void }) {
  const person = PEOPLE[account.person_id];
  const isCredit = account.type === 'credit';
  const available = isCredit ? (account.credit_limit ?? 0) - (account.credit_used ?? 0) : account.balance;
  const typeColors: Record<string, { bg: string; fg: string }> = {
    debit: { bg: colors.debitLight, fg: colors.debit },
    savings: { bg: colors.debitLight, fg: colors.debit },
    credit: { bg: colors.creditLight, fg: colors.credit },
  };
  const tc = typeColors[account.type];

  return (
    <Pressable onPress={onPress} style={({ pressed }) => [{ opacity: pressed ? 0.7 : 1 }]}>
      <Card style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.sm, flex: 1 }}>
          <View style={{ width: 42, height: 42, borderRadius: radius.sm, backgroundColor: tc.bg, alignItems: 'center', justifyContent: 'center' }}>
            <Wallet color={tc.fg} size={20} strokeWidth={2} />
          </View>
          <View style={{ flex: 1 }}>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.xs }}>
              <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 15, color: colors.text }}>{account.name}</Text>
              {account.is_default && (
                <View style={{ paddingHorizontal: spacing.xs + 2, paddingVertical: 2, borderRadius: radius.full, backgroundColor: colors.emeraldLight }}>
                  <Text style={{ fontFamily: 'Inter-Medium', fontSize: 9, color: colors.emeraldDeep }}>Principal</Text>
                </View>
              )}
            </View>
            <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: colors.textSecondary }}>{person?.name} · {account.bank}</Text>
          </View>
        </View>
        <View style={{ alignItems: 'flex-end' }}>
          <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 15, color: isCredit && available < 0 ? colors.error : colors.text }}>
            {isCredit ? formatCOP(available) : formatCOP(account.balance)}
          </Text>
          <Text style={{ fontFamily: 'Inter-Regular', fontSize: 11, color: colors.textMuted }}>{isCredit ? 'Disponible' : 'Saldo'}</Text>
        </View>
      </Card>
    </Pressable>
  );
}

function ExpenseRow({ expense }: { expense: Expense }) {
  const person = PEOPLE[expense.paid_by_person_id];
  const { danielShare, anaShare } = computeShare(expense.total_amount, expense.split_type, expense.expense_items, expense.paid_by_person_id);
  return (
    <Card>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <View style={{ flex: 1 }}>
          <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 15, color: colors.text }} numberOfLines={1}>{expense.title}</Text>
          <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: colors.textSecondary, marginTop: 2 }}>{formatDate(expense.expense_date)}</Text>
        </View>
        <Text style={{ fontFamily: 'Inter-Bold', fontSize: 16, color: colors.text }}>{formatCOP(expense.total_amount)}</Text>
      </View>
      <View style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginTop: spacing.sm }}>
        <PersonBadge name={person?.name ?? ''} emoji={person?.emoji ?? ''} color={person?.color ?? colors.emerald} size="sm" />
        <View style={{ flex: 1, flexDirection: 'row', flexWrap: 'wrap', gap: 6 }}>
          <ShareChip label={`D ${formatCOP(danielShare)}`} color={colors.daniel} />
          <ShareChip label={`S ${formatCOP(anaShare)}`} color={colors.ana} />
          {expense.surcharge_applied && <ShareChip label="+3% datáfono" color={colors.warning} />}
        </View>
      </View>
    </Card>
  );
}

function ShareChip({ label, color }: { label: string; color: string }) {
  return (
    <View style={{ paddingHorizontal: spacing.xs + 2, paddingVertical: 3, borderRadius: radius.full, backgroundColor: color + '1a' }}>
      <Text style={{ fontFamily: 'Inter-Medium', fontSize: 11, color }}>{label}</Text>
    </View>
  );
}
