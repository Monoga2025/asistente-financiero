import { useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { ActivityIndicator, Modal, Pressable, ScrollView, Text, TextInput, View } from 'react-native';
import { BarChart3, ChevronLeft, ChevronRight, Plus, Sparkles, Target, Trash2, X } from 'lucide-react-native';
import { Button, Card, Chip } from '@/components/ui';
import { Header } from '@/components/Header';
import { colors, radius, shadows, spacing } from '@/lib/theme';
import { formatCOP, parseCOP } from '@/lib/format';
import {
  createGoal,
  deleteGoal,
  fetchGoalProjection,
  fetchGoals,
  fetchMonthClose,
  updateGoal,
} from '@/lib/finance';
import type { Goal, GoalProjection, MonthCloseSummary } from '@/lib/types';

const MONTHS = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
];

export default function MetasScreen() {
  const today = new Date();
  const [tab, setTab] = useState<'goals' | 'month'>('goals');
  const [goals, setGoals] = useState<Goal[]>([]);
  const [summary, setSummary] = useState<MonthCloseSummary | null>(null);
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);
  const [loading, setLoading] = useState(true);

  const [showNewGoal, setShowNewGoal] = useState(false);
  const [selectedGoal, setSelectedGoal] = useState<Goal | null>(null);
  const [abonoAmount, setAbonoAmount] = useState('');
  const [monthlySim, setMonthlySim] = useState('300000');
  const [projection, setProjection] = useState<GoalProjection | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [goalsData, monthData] = await Promise.all([
        fetchGoals(),
        fetchMonthClose(year, month),
      ]);
      setGoals(goalsData);
      setSummary(monthData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [year, month]);

  useFocusEffect(
    useCallback(() => {
      loadData();
    }, [loadData]),
  );

  function changeMonth(delta: number) {
    let nextMonth = month + delta;
    let nextYear = year;
    if (nextMonth < 1) {
      nextMonth = 12;
      nextYear -= 1;
    } else if (nextMonth > 12) {
      nextMonth = 1;
      nextYear += 1;
    }
    setYear(nextYear);
    setMonth(nextMonth);
  }

  async function openGoalDetail(goal: Goal) {
    setSelectedGoal(goal);
    setAbonoAmount('');
    try {
      const proj = await fetchGoalProjection(goal.id, parseCOP(monthlySim) || 300000);
      setProjection(proj);
    } catch {
      setProjection(null);
    }
  }

  async function handleAbonar() {
    if (!selectedGoal) return;
    const add = parseCOP(abonoAmount);
    if (add <= 0) return;
    const updated = await updateGoal(selectedGoal.id, {
      current_saved: selectedGoal.current_saved + add,
    });
    setSelectedGoal(updated);
    setAbonoAmount('');
    const proj = await fetchGoalProjection(updated.id, parseCOP(monthlySim) || 300000);
    setProjection(proj);
    await loadData();
  }

  async function handleSimulate(val: string) {
    setMonthlySim(val);
    if (!selectedGoal) return;
    const amt = parseCOP(val);
    if (amt > 0) {
      const proj = await fetchGoalProjection(selectedGoal.id, amt);
      setProjection(proj);
    }
  }

  async function handleDeleteGoal(id: number) {
    await deleteGoal(id);
    setSelectedGoal(null);
    await loadData();
  }

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <ScrollView
        contentContainerStyle={{ paddingHorizontal: spacing.md, paddingTop: spacing.lg, paddingBottom: spacing.xl + 40 }}
        showsVerticalScrollIndicator={false}
      >
        <Header title="Metas y Cierre" subtitle="Ahorro en pareja y análisis mensual" />

        {/* Segmented control */}
        <View style={{ flexDirection: 'row', backgroundColor: '#e2e8f0', borderRadius: radius.md, padding: 4, marginBottom: spacing.lg }}>
          <Pressable
            onPress={() => setTab('goals')}
            style={{
              flex: 1,
              flexDirection: 'row',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 6,
              paddingVertical: spacing.sm + 2,
              borderRadius: radius.sm,
              backgroundColor: tab === 'goals' ? '#fff' : 'transparent',
            }}
          >
            <Target color={tab === 'goals' ? colors.emerald : colors.textSecondary} size={16} strokeWidth={2} />
            <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 13, color: tab === 'goals' ? colors.text : colors.textSecondary }}>
              Metas de Ahorro
            </Text>
          </Pressable>
          <Pressable
            onPress={() => setTab('month')}
            style={{
              flex: 1,
              flexDirection: 'row',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 6,
              paddingVertical: spacing.sm + 2,
              borderRadius: radius.sm,
              backgroundColor: tab === 'month' ? '#fff' : 'transparent',
            }}
          >
            <BarChart3 color={tab === 'month' ? colors.emerald : colors.textSecondary} size={16} strokeWidth={2} />
            <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 13, color: tab === 'month' ? colors.text : colors.textSecondary }}>
              Cierre de Mes
            </Text>
          </Pressable>
        </View>

        {loading ? (
          <View style={{ paddingVertical: spacing.xl, alignItems: 'center' }}>
            <ActivityIndicator size="large" color={colors.emerald} />
          </View>
        ) : tab === 'goals' ? (
          <View style={{ gap: spacing.md }}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
              <Text style={{ fontFamily: 'Inter-Bold', fontSize: 18, color: colors.text }}>Bolsillos y Metas</Text>
              <Pressable
                onPress={() => setShowNewGoal(true)}
                style={{
                  flexDirection: 'row',
                  alignItems: 'center',
                  gap: 4,
                  backgroundColor: colors.emerald,
                  paddingHorizontal: spacing.md,
                  paddingVertical: spacing.xs + 3,
                  borderRadius: radius.full,
                }}
              >
                <Plus color="#fff" size={15} strokeWidth={2.5} />
                <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 12, color: '#fff' }}>Nueva meta</Text>
              </Pressable>
            </View>

            {goals.length === 0 ? (
              <Card style={{ alignItems: 'center', paddingVertical: spacing.xl }}>
                <Target color={colors.emerald} size={40} strokeWidth={1.8} />
                <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 16, color: colors.text, marginTop: spacing.md }}>
                  Aún no tienen metas creadas
                </Text>
                <Text style={{ fontFamily: 'Inter-Regular', fontSize: 13, color: colors.textSecondary, marginTop: 4, textAlign: 'center' }}>
                  Crea una meta para un viaje, fondo de emergencia o compra del hogar y calcula en cuántos meses la logran.
                </Text>
                <View style={{ marginTop: spacing.md }}>
                  <Button label="Crear primera meta" onPress={() => setShowNewGoal(true)} />
                </View>
              </Card>
            ) : (
              goals.map((g) => {
                const pct = Math.min(100, Math.round((g.current_saved / g.target_amount) * 100));
                const missing = Math.max(0, g.target_amount - g.current_saved);
                return (
                  <Card key={g.id} onPress={() => openGoalDetail(g)}>
                    <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <View style={{ flex: 1 }}>
                        <Text style={{ fontFamily: 'Inter-Bold', fontSize: 16, color: colors.text }}>{g.name}</Text>
                        {g.deadline && (
                          <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: colors.textSecondary, marginTop: 2 }}>
                            Fecha meta: {g.deadline}
                          </Text>
                        )}
                      </View>
                      <View style={{ paddingHorizontal: 10, paddingVertical: 3, borderRadius: radius.full, backgroundColor: pct >= 100 ? colors.emeraldLight : colors.danielLight }}>
                        <Text style={{ fontFamily: 'Inter-Bold', fontSize: 12, color: pct >= 100 ? colors.emeraldDeep : colors.daniel }}>
                          {pct}%
                        </Text>
                      </View>
                    </View>

                    <View style={{ height: 10, backgroundColor: '#e2e8f0', borderRadius: 5, marginVertical: spacing.sm, overflow: 'hidden' }}>
                      <View style={{ width: `${pct}%`, height: '100%', backgroundColor: colors.emerald, borderRadius: 5 }} />
                    </View>

                    <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                      <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 13, color: colors.emeraldDeep }}>
                        Ahorrado: {formatCOP(g.current_saved)}
                      </Text>
                      <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.textSecondary }}>
                        Meta: {formatCOP(g.target_amount)}
                      </Text>
                    </View>
                    {missing > 0 && (
                      <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: colors.textMuted, marginTop: 4 }}>
                        Faltan {formatCOP(missing)} · Toca para abonar o simular proyección
                      </Text>
                    )}
                  </Card>
                );
              })
            )}
          </View>
        ) : (
          <View style={{ gap: spacing.md }}>
            {/* Month selector */}
            <Card style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingVertical: spacing.sm + 2 }}>
              <Pressable onPress={() => changeMonth(-1)} style={{ padding: spacing.xs }}>
                <ChevronLeft color={colors.text} size={22} strokeWidth={2} />
              </Pressable>
              <Text style={{ fontFamily: 'Inter-Bold', fontSize: 17, color: colors.text }}>
                {MONTHS[month - 1]} {year}
              </Text>
              <Pressable onPress={() => changeMonth(1)} style={{ padding: spacing.xs }}>
                <ChevronRight color={colors.text} size={22} strokeWidth={2} />
              </Pressable>
            </Card>

            {summary && (
              <>
                <View
                  style={{
                    borderRadius: radius.lg,
                    padding: spacing.lg,
                    backgroundColor: colors.emeraldDeep,
                    ...shadows.elevated,
                  }}
                >
                  <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: '#a7f3d0' }}>
                    Total gastado en {MONTHS[month - 1]} ({summary.count} gastos)
                  </Text>
                  <Text style={{ fontFamily: 'Inter-Bold', fontSize: 34, color: '#fff', marginVertical: 4 }}>
                    {formatCOP(summary.total)}
                  </Text>
                  <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: spacing.xs }}>
                    <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: '#d1fae5' }}>
                      Promedio diario: {formatCOP(summary.daily_average)}
                    </Text>
                    {summary.change_pct !== null && (
                      <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 12, color: summary.change_pct > 0 ? '#fde68a' : '#a7f3d0' }}>
                        {summary.change_pct > 0 ? `+${summary.change_pct}%` : `${summary.change_pct}%`} vs mes anterior
                      </Text>
                    )}
                  </View>
                </View>

                {/* Split by person */}
                <Card>
                  <Text style={{ fontFamily: 'Inter-Bold', fontSize: 16, color: colors.text, marginBottom: spacing.sm }}>
                    Cuánto asumió cada uno este mes
                  </Text>
                  <View style={{ flexDirection: 'row', gap: spacing.sm }}>
                    <View style={{ flex: 1, padding: spacing.md, borderRadius: radius.md, backgroundColor: colors.danielLight }}>
                      <Text style={{ fontFamily: 'Inter-Medium', fontSize: 12, color: colors.daniel }}>Daniel</Text>
                      <Text style={{ fontFamily: 'Inter-Bold', fontSize: 18, color: colors.daniel, marginTop: 2 }}>
                        {formatCOP(summary.by_person.daniel ?? 0)}
                      </Text>
                    </View>
                    <View style={{ flex: 1, padding: spacing.md, borderRadius: radius.md, backgroundColor: colors.anaLight }}>
                      <Text style={{ fontFamily: 'Inter-Medium', fontSize: 12, color: colors.ana }}>Silvia</Text>
                      <Text style={{ fontFamily: 'Inter-Bold', fontSize: 18, color: colors.ana, marginTop: 2 }}>
                        {formatCOP(summary.by_person.ana ?? 0)}
                      </Text>
                    </View>
                  </View>
                </Card>

                {/* Breakdown by category */}
                <Card>
                  <Text style={{ fontFamily: 'Inter-Bold', fontSize: 16, color: colors.text, marginBottom: spacing.sm }}>
                    Gastos por categoría (IA + Reglas)
                  </Text>
                  {Object.keys(summary.by_category).length === 0 ? (
                    <Text style={{ fontFamily: 'Inter-Regular', fontSize: 14, color: colors.textSecondary }}>
                      No hay gastos registrados en este mes.
                    </Text>
                  ) : (
                    <View style={{ gap: spacing.sm }}>
                      {Object.entries(summary.by_category).map(([cat, amt]) => {
                        const pct = summary.total > 0 ? Math.round((amt / summary.total) * 100) : 0;
                        return (
                          <View key={cat}>
                            <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 }}>
                              <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 14, color: colors.text }}>{cat}</Text>
                              <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 14, color: colors.text }}>
                                {formatCOP(amt)} ({pct}%)
                              </Text>
                            </View>
                            <View style={{ height: 8, backgroundColor: '#e2e8f0', borderRadius: 4, overflow: 'hidden' }}>
                              <View style={{ width: `${pct}%`, height: '100%', backgroundColor: colors.emerald, borderRadius: 4 }} />
                            </View>
                          </View>
                        );
                      })}
                    </View>
                  )}
                </Card>
              </>
            )}
          </View>
        )}
      </ScrollView>

      {/* Goal Detail & Projection Modal */}
      <Modal visible={!!selectedGoal} transparent animationType="slide" onRequestClose={() => setSelectedGoal(null)}>
        <View style={{ flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.4)' }}>
          <View style={{ backgroundColor: colors.card, borderTopLeftRadius: radius.xl, borderTopRightRadius: radius.xl, padding: spacing.lg, paddingBottom: spacing.xl, gap: spacing.sm }}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
              <Text style={{ fontFamily: 'Inter-Bold', fontSize: 18, color: colors.text }}>{selectedGoal?.name}</Text>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.md }}>
                {selectedGoal && (
                  <Pressable onPress={() => handleDeleteGoal(selectedGoal.id)}>
                    <Trash2 color={colors.error} size={20} strokeWidth={2} />
                  </Pressable>
                )}
                <Pressable onPress={() => setSelectedGoal(null)}>
                  <X color={colors.textSecondary} size={22} strokeWidth={2} />
                </Pressable>
              </View>
            </View>

            {selectedGoal && (
              <>
                <Text style={{ fontFamily: 'Inter-Regular', fontSize: 14, color: colors.textSecondary }}>
                  Ahorrado: <Text style={{ fontFamily: 'Inter-Bold', color: colors.emerald }}>{formatCOP(selectedGoal.current_saved)}</Text> de {formatCOP(selectedGoal.target_amount)}
                </Text>

                <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.textSecondary, marginTop: spacing.xs }}>
                  Sumar abono a esta meta
                </Text>
                <View style={{ flexDirection: 'row', gap: spacing.sm }}>
                  <TextInput
                    value={abonoAmount ? formatCOP(parseCOP(abonoAmount)) : ''}
                    onChangeText={(t) => setAbonoAmount(String(parseCOP(t)))}
                    placeholder="$0"
                    placeholderTextColor={colors.textMuted}
                    keyboardType="numeric"
                    style={[inputStyle, { flex: 1 }]}
                  />
                  <Button label="Abonar" onPress={handleAbonar} />
                </View>

                <View style={{ marginTop: spacing.sm, paddingTop: spacing.sm, borderTopWidth: 1, borderTopColor: colors.border, gap: spacing.xs }}>
                  <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
                    <Sparkles color={colors.emerald} size={16} strokeWidth={2} />
                    <Text style={{ fontFamily: 'Inter-Bold', fontSize: 14, color: colors.text }}>Simulador de proyección mensual</Text>
                  </View>
                  <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: colors.textSecondary }}>
                    ¿Cuánto pueden ahorrar juntos cada mes para esta meta?
                  </Text>
                  <TextInput
                    value={monthlySim ? formatCOP(parseCOP(monthlySim)) : ''}
                    onChangeText={(t) => handleSimulate(String(parseCOP(t)))}
                    placeholder="$300.000"
                    keyboardType="numeric"
                    style={inputStyle}
                  />
                  {projection && (
                    <View style={{ backgroundColor: colors.emeraldLight, padding: spacing.md, borderRadius: radius.md, marginTop: 4 }}>
                      {projection.reached ? (
                        <Text style={{ fontFamily: 'Inter-Bold', fontSize: 14, color: colors.emeraldDeep }}>
                          🎉 ¡Meta completada al 100%!
                        </Text>
                      ) : (
                        <>
                          <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 14, color: colors.emeraldDeep }}>
                            Ahorrando {formatCOP(parseCOP(monthlySim))} al mes ({formatCOP(Math.round(parseCOP(monthlySim) / 2))} cada uno):
                          </Text>
                          <Text style={{ fontFamily: 'Inter-Bold', fontSize: 16, color: colors.text, marginTop: 4 }}>
                            La alcanzan en {projection.estimated_months ?? '?'} mes(es)
                          </Text>
                          {projection.needed_monthly !== null && (
                            <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: colors.textSecondary, marginTop: 2 }}>
                              Para cumplir antes de la fecha límite necesitan ahorrar {formatCOP(projection.needed_monthly)}/mes.
                            </Text>
                          )}
                        </>
                      )}
                    </View>
                  )}
                </View>
              </>
            )}
          </View>
        </View>
      </Modal>

      {/* New Goal Modal */}
      <NewGoalModal
        visible={showNewGoal}
        onClose={() => setShowNewGoal(false)}
        onCreated={async () => {
          setShowNewGoal(false);
          await loadData();
        }}
      />
    </View>
  );
}

function NewGoalModal({ visible, onClose, onCreated }: { visible: boolean; onClose: () => void; onCreated: () => Promise<void> }) {
  const [name, setName] = useState('');
  const [target, setTarget] = useState('');
  const [saved, setSaved] = useState('');
  const [deadline, setDeadline] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSave() {
    if (!name.trim()) return setError('Escribe el nombre de la meta');
    const targetAmt = parseCOP(target);
    if (targetAmt <= 0) return setError('La meta debe ser mayor a cero');
    setSaving(true);
    setError(null);
    try {
      await createGoal({
        name: name.trim(),
        target_amount: targetAmt,
        current_saved: parseCOP(saved),
        deadline: deadline.trim() || null,
        frequency: 'mensual',
      });
      setName('');
      setTarget('');
      setSaved('');
      setDeadline('');
      await onCreated();
    } catch (e: any) {
      setError(e?.message ?? 'No se pudo crear la meta');
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onClose}>
      <View style={{ flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.4)' }}>
        <View style={{ backgroundColor: colors.card, borderTopLeftRadius: radius.xl, borderTopRightRadius: radius.xl, padding: spacing.lg, paddingBottom: spacing.xl, gap: spacing.sm }}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text style={{ fontFamily: 'Inter-Bold', fontSize: 18, color: colors.text }}>Nueva meta en pareja</Text>
            <Pressable onPress={onClose}><X color={colors.textSecondary} size={22} strokeWidth={2} /></Pressable>
          </View>

          <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.textSecondary }}>Nombre del objetivo</Text>
          <TextInput value={name} onChangeText={setName} placeholder="Ej. Viaje a San Andrés / Fondo Hogar" placeholderTextColor={colors.textMuted} style={inputStyle} />

          <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.textSecondary }}>Monto objetivo</Text>
          <TextInput
            value={target ? formatCOP(parseCOP(target)) : ''}
            onChangeText={(t) => setTarget(String(parseCOP(t)))}
            placeholder="$2.000.000"
            placeholderTextColor={colors.textMuted}
            keyboardType="numeric"
            style={inputStyle}
          />

          <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.textSecondary }}>Ahorrado hasta hoy (opcional)</Text>
          <TextInput
            value={saved ? formatCOP(parseCOP(saved)) : ''}
            onChangeText={(t) => setSaved(String(parseCOP(t)))}
            placeholder="$0"
            placeholderTextColor={colors.textMuted}
            keyboardType="numeric"
            style={inputStyle}
          />

          <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.textSecondary }}>Fecha límite opcional (AAAA-MM-DD)</Text>
          <TextInput value={deadline} onChangeText={setDeadline} placeholder="Ej. 2026-12-15" placeholderTextColor={colors.textMuted} style={inputStyle} />

          {error && <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.error }}>{error}</Text>}

          <Button label={saving ? 'Guardando...' : 'Crear meta'} onPress={handleSave} fullWidth disabled={saving} />
        </View>
      </View>
    </Modal>
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
