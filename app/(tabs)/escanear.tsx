import { useState } from 'react';
import { ActivityIndicator, Image, Modal, Pressable, ScrollView, Switch, Text, TextInput, View } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { AlertCircle, Camera, Check, Image as ImageIcon, ScanLine, X } from 'lucide-react-native';
import { Button, Card, Chip } from '@/components/ui';
import { Header } from '@/components/Header';
import { colors, radius, shadows, spacing } from '@/lib/theme';
import { formatCOP, formatDate, parseCOP, toInputDate } from '@/lib/format';
import { fetchAccounts, saveScannedReceipt, scanReceiptImage } from '@/lib/finance';
import { DANIEL_ID, ANA_ID, PERSON_LIST } from '@/lib/people';
import type { Account, Assignment } from '@/lib/types';

type Phase = 'input' | 'scanning' | 'review' | 'saving' | 'done' | 'error';
type ConceptDraft = { name: string; amount: number; assigned_to: Assignment };

export default function EscanearScreen() {
  const [phase, setPhase] = useState<Phase>('input');
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [draftId, setDraftId] = useState<number | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [savedMsg, setSavedMsg] = useState<string | null>(null);
  const [paidBy, setPaidBy] = useState(DANIEL_ID);
  const [accountId, setAccountId] = useState<string | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [surcharge, setSurcharge] = useState(false);
  const [store, setStore] = useState('');
  const [date, setDate] = useState(toInputDate(new Date()));
  const [concepts, setConcepts] = useState<ConceptDraft[]>([]);
  const [showAccountPicker, setShowAccountPicker] = useState(false);

  const conceptsTotal = concepts.reduce((sum, concept) => sum + concept.amount, 0);
  const surchargeAmount = surcharge ? Math.round(conceptsTotal * 0.03) : 0;
  const grandTotal = conceptsTotal + surchargeAmount;
  const availableAccounts = accounts.filter((account) => account.person_id === paidBy);
  const selectedAccount = accounts.find((account) => account.id === accountId);

  function reset() {
    setPhase('input');
    setImageUri(null);
    setDraftId(null);
    setErrorMsg(null);
    setSavedMsg(null);
    setPaidBy(DANIEL_ID);
    setAccountId(null);
    setSurcharge(false);
    setStore('');
    setDate(toInputDate(new Date()));
    setConcepts([]);
  }

  async function pickImage(source: 'camera' | 'gallery') {
    setErrorMsg(null);
    const permission =
      source === 'camera'
        ? await ImagePicker.requestCameraPermissionsAsync()
        : await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      setErrorMsg(source === 'camera' ? 'Activa el permiso de camara.' : 'Activa el permiso de galeria.');
      setPhase('error');
      return;
    }

    const result =
      source === 'camera'
        ? await ImagePicker.launchCameraAsync({ quality: 0.85 })
        : await ImagePicker.launchImageLibraryAsync({ quality: 0.85, mediaTypes: ImagePicker.MediaTypeOptions.Images });

    if (!result.canceled && result.assets[0]?.uri) {
      const uri = result.assets[0].uri;
      setImageUri(uri);
      await runScan(uri);
    }
  }

  async function runScan(uri: string) {
    setPhase('scanning');
    try {
      const accountsData = await fetchAccounts();
      setAccounts(accountsData);
      const defaultAccount = accountsData.find((account) => account.person_id === DANIEL_ID && account.is_default);
      setAccountId(defaultAccount?.id ?? null);

      const scanned = await scanReceiptImage(uri);
      if (scanned.concepts.length === 0) {
        throw new Error('No se detectaron conceptos en la factura. Intenta con una foto mas clara.');
      }
      setDraftId(scanned.draftId);
      setStore(scanned.store ?? 'Factura escaneada');
      setDate(toInputDate(new Date()));
      setConcepts(scanned.concepts);
      setPhase('review');
    } catch (error: any) {
      setErrorMsg(error?.message ?? 'No se pudo escanear la factura.');
      setPhase('error');
    }
  }

  function onPaidByChange(personId: string) {
    setPaidBy(personId);
    const nextAccount = accounts.find((account) => account.person_id === personId && account.is_default) ?? accounts.find((account) => account.person_id === personId);
    setAccountId(nextAccount?.id ?? null);
  }

  function updateConcept(index: number, field: keyof ConceptDraft, value: string | number | Assignment) {
    setConcepts(concepts.map((concept, i) => (i === index ? { ...concept, [field]: value } : concept)));
  }

  async function handleSave() {
    setPhase('saving');
    try {
      if (!draftId) throw new Error('Falta el borrador de la factura. Escanea de nuevo.');
      await saveScannedReceipt({
        draftId,
        title: store.trim() || 'Factura escaneada',
        date,
        paidBy: paidBy === ANA_ID ? 'ana' : 'daniel',
        accountId,
        addSurcharge: surcharge,
        surchargePercent: 3,
        items: concepts.map((concept) => ({
          description: concept.name,
          amount: concept.amount,
          assignedTo: concept.assigned_to === 'half' ? 'equal' : concept.assigned_to,
        })),
      });
      setSavedMsg(`Factura registrada por ${formatCOP(grandTotal)}`);
      setPhase('done');
    } catch (error: any) {
      setErrorMsg(error?.message ?? 'No se pudo guardar la factura.');
      setPhase('error');
    }
  }

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <ScrollView contentContainerStyle={{ paddingHorizontal: spacing.md, paddingTop: spacing.lg, paddingBottom: spacing.xl + 40 }} showsVerticalScrollIndicator={false}>
        <Header title="Escanear factura" subtitle="Toma una foto o sube una imagen" />

        {phase === 'input' && (
          <View style={{ gap: spacing.md }}>
            <Card style={{ alignItems: 'center', paddingVertical: spacing.xl }}>
              <View style={{ width: 80, height: 80, borderRadius: 40, backgroundColor: colors.emeraldLight, alignItems: 'center', justifyContent: 'center', marginBottom: spacing.md }}>
                <ScanLine color={colors.emerald} size={36} strokeWidth={2} />
              </View>
              <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 17, color: colors.text, textAlign: 'center' }}>Escanea tu factura con IA</Text>
              <Text style={{ fontFamily: 'Inter-Regular', fontSize: 14, color: colors.textSecondary, marginTop: spacing.xs, textAlign: 'center' }}>
                Extraemos tienda y conceptos. Luego decides que paga Ana, Daniel o mitad.
              </Text>
            </Card>
            <ActionButton icon={<Camera color="#fff" size={22} strokeWidth={2} />} label="Tomar foto" onPress={() => pickImage('camera')} bg={colors.daniel} />
            <ActionButton icon={<ImageIcon color="#fff" size={22} strokeWidth={2} />} label="Subir de galeria" onPress={() => pickImage('gallery')} bg={colors.emerald} />
          </View>
        )}

        {phase === 'scanning' && (
          <StatusCard imageUri={imageUri} title="Analizando factura..." subtitle="La IA esta leyendo los conceptos y el total" />
        )}

        {phase === 'review' && imageUri && (
          <View style={{ gap: spacing.md }}>
            <View style={{ flexDirection: 'row', gap: spacing.sm }}>
              <Image source={{ uri: imageUri }} style={{ width: 90, height: 120, borderRadius: radius.md, resizeMode: 'cover' }} />
              <View style={{ flex: 1, justifyContent: 'center' }}>
                <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 16, color: colors.text }}>Revisa los conceptos</Text>
                <Text style={{ fontFamily: 'Inter-Regular', fontSize: 13, color: colors.textSecondary, marginTop: spacing.xs }}>
                  Edita montos y asigna cada producto antes de guardar.
                </Text>
              </View>
            </View>

            <Card>
              <Label text="Tienda" />
              <TextInput value={store} onChangeText={setStore} placeholder="Factura escaneada" placeholderTextColor={colors.textMuted} style={inputStyle} />
              <View style={{ height: spacing.md }} />
              <Label text="Fecha" />
              <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 16, color: colors.text }}>{formatDate(date)}</Text>
            </Card>

            <Card>
              <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 15, color: colors.text, marginBottom: spacing.md }}>Conceptos ({concepts.length})</Text>
              <View style={{ gap: spacing.sm }}>
                {concepts.map((concept, index) => (
                  <View key={`${concept.name}-${index}`} style={{ borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, padding: spacing.sm }}>
                    <View style={{ flexDirection: 'row', gap: spacing.sm, alignItems: 'center' }}>
                      <TextInput value={concept.name} onChangeText={(value) => updateConcept(index, 'name', value)} style={[inputStyle, { flex: 1 }]} />
                      <TextInput value={formatCOP(concept.amount)} onChangeText={(value) => updateConcept(index, 'amount', parseCOP(value))} keyboardType="numeric" style={[inputStyle, { width: 120, fontFamily: 'Inter-SemiBold' }]} />
                    </View>
                    <View style={{ flexDirection: 'row', gap: 6, marginTop: spacing.sm }}>
                      <Chip label="Ana" selected={concept.assigned_to === 'ana'} onPress={() => updateConcept(index, 'assigned_to', 'ana')} color={colors.ana} lightColor={colors.anaLight} />
                      <Chip label="Daniel" selected={concept.assigned_to === 'daniel'} onPress={() => updateConcept(index, 'assigned_to', 'daniel')} color={colors.daniel} lightColor={colors.danielLight} />
                      <Chip label="Mitad" selected={concept.assigned_to === 'half'} onPress={() => updateConcept(index, 'assigned_to', 'half')} />
                    </View>
                  </View>
                ))}
              </View>
            </Card>

            <Card>
              <SummaryRow label="Subtotal conceptos" value={formatCOP(conceptsTotal)} />
              {surcharge && <SummaryRow label="Recargo datafono 3%" value={formatCOP(surchargeAmount)} color={colors.warning} />}
              <View style={{ height: 1, backgroundColor: colors.border, marginVertical: spacing.sm }} />
              <SummaryRow label="Total" value={formatCOP(grandTotal)} strong color={colors.emerald} />
            </Card>

            <Card>
              <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
                <View style={{ flex: 1 }}>
                  <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 15, color: colors.text }}>Recargo datafono 3%</Text>
                  <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: colors.textSecondary }}>Activarlo solo si el local lo cobro</Text>
                </View>
                <Switch value={surcharge} onValueChange={setSurcharge} trackColor={{ false: colors.border, true: colors.emerald }} />
              </View>
            </Card>

            <Card>
              <Label text="Pagado por" />
              <View style={{ flexDirection: 'row', gap: spacing.sm }}>
                {PERSON_LIST.map((person) => (
                  <Pressable key={person.id} onPress={() => onPaidByChange(person.id)} style={{ flex: 1, alignItems: 'center', paddingVertical: spacing.sm + 2, borderRadius: radius.md, borderWidth: 1.5, borderColor: paidBy === person.id ? person.color : colors.border, backgroundColor: paidBy === person.id ? person.color + '14' : '#fff' }}>
                    <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 14, color: paidBy === person.id ? person.color : colors.textSecondary }}>{person.name}</Text>
                  </Pressable>
                ))}
              </View>
            </Card>

            <Card>
              <Label text="Cuenta usada" />
              <Pressable onPress={() => setShowAccountPicker(true)} style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
                <View>
                  <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 15, color: colors.text }}>{selectedAccount ? selectedAccount.name : 'Sin cuenta'}</Text>
                  {selectedAccount && <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: colors.textSecondary }}>{selectedAccount.bank}</Text>}
                </View>
                <Text style={{ fontFamily: 'Inter-Medium', fontSize: 14, color: colors.emerald }}>Cambiar</Text>
              </Pressable>
            </Card>

            <View style={{ flexDirection: 'row', gap: spacing.sm }}>
              <Button label="Reescanear" onPress={() => runScan(imageUri)} variant="secondary" />
              <Button label="Guardar factura" onPress={handleSave} fullWidth icon={<Check color="#fff" size={20} strokeWidth={2} />} />
            </View>
          </View>
        )}

        {phase === 'saving' && <StatusCard title="Guardando factura..." />}

        {phase === 'done' && (
          <Card style={{ alignItems: 'center', paddingVertical: spacing.xl + 8 }}>
            <Check color={colors.emerald} size={42} strokeWidth={2.5} />
            <Text style={{ fontFamily: 'Inter-Bold', fontSize: 20, color: colors.text, marginTop: spacing.md }}>Listo</Text>
            <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 18, color: colors.emerald, marginTop: spacing.sm }}>{savedMsg}</Text>
            <View style={{ marginTop: spacing.lg, width: '100%' }}>
              <Button label="Escanear otra factura" onPress={reset} fullWidth />
            </View>
          </Card>
        )}

        {phase === 'error' && (
          <Card style={{ alignItems: 'center', paddingVertical: spacing.xl }}>
            <AlertCircle color={colors.error} size={38} strokeWidth={2} />
            <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 16, color: colors.text, marginTop: spacing.md }}>No se pudo procesar</Text>
            <Text style={{ fontFamily: 'Inter-Regular', fontSize: 14, color: colors.textSecondary, marginTop: spacing.xs, textAlign: 'center' }}>{errorMsg}</Text>
            <View style={{ marginTop: spacing.lg, width: '100%' }}>
              <Button label="Empezar de nuevo" onPress={reset} variant="secondary" fullWidth />
            </View>
          </Card>
        )}
      </ScrollView>

      <Modal visible={showAccountPicker} transparent animationType="slide" onRequestClose={() => setShowAccountPicker(false)}>
        <View style={{ flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.4)' }}>
          <View style={{ backgroundColor: colors.card, borderTopLeftRadius: radius.xl, borderTopRightRadius: radius.xl, padding: spacing.lg, paddingBottom: spacing.xl }}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.md }}>
              <Text style={{ fontFamily: 'Inter-Bold', fontSize: 18, color: colors.text }}>Selecciona cuenta</Text>
              <Pressable onPress={() => setShowAccountPicker(false)}><X color={colors.textSecondary} size={22} strokeWidth={2} /></Pressable>
            </View>
            <View style={{ gap: spacing.sm }}>
              {availableAccounts.map((account) => (
                <Pressable key={account.id} onPress={() => { setAccountId(account.id); setShowAccountPicker(false); }} style={{ paddingVertical: spacing.sm + 2, paddingHorizontal: spacing.md, borderRadius: radius.md, backgroundColor: accountId === account.id ? colors.emeraldLight : colors.bg }}>
                  <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 15, color: colors.text }}>{account.name}</Text>
                  <Text style={{ fontFamily: 'Inter-Regular', fontSize: 12, color: colors.textSecondary }}>{account.bank}</Text>
                </Pressable>
              ))}
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

function ActionButton({ icon, label, onPress, bg }: { icon: React.ReactNode; label: string; onPress: () => void; bg: string }) {
  return (
    <Pressable onPress={onPress} style={({ pressed }) => [{ flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: spacing.sm, paddingVertical: spacing.md + 2, borderRadius: radius.md, backgroundColor: bg, opacity: pressed ? 0.88 : 1, ...shadows.card }]}>
      {icon}
      <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 16, color: '#fff' }}>{label}</Text>
    </Pressable>
  );
}

function StatusCard({ imageUri, title, subtitle }: { imageUri?: string | null; title: string; subtitle?: string }) {
  return (
    <Card style={{ alignItems: 'center', paddingVertical: spacing.xl + 8 }}>
      {imageUri && <Image source={{ uri: imageUri }} style={{ width: 160, height: 200, borderRadius: radius.md, marginBottom: spacing.md, resizeMode: 'cover' }} />}
      <ActivityIndicator size="large" color={colors.emerald} />
      <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 16, color: colors.text, marginTop: spacing.md }}>{title}</Text>
      {subtitle && <Text style={{ fontFamily: 'Inter-Regular', fontSize: 13, color: colors.textSecondary, marginTop: spacing.xs, textAlign: 'center' }}>{subtitle}</Text>}
    </Card>
  );
}

function Label({ text }: { text: string }) {
  return <Text style={{ fontFamily: 'Inter-Medium', fontSize: 13, color: colors.textSecondary, marginBottom: spacing.sm }}>{text}</Text>;
}

function SummaryRow({ label, value, color = colors.text, strong }: { label: string; value: string; color?: string; strong?: boolean }) {
  return (
    <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: spacing.xs }}>
      <Text style={{ fontFamily: strong ? 'Inter-Bold' : 'Inter-Regular', fontSize: strong ? 17 : 14, color: colors.textSecondary }}>{label}</Text>
      <Text style={{ fontFamily: strong ? 'Inter-Bold' : 'Inter-SemiBold', fontSize: strong ? 17 : 14, color }}>{value}</Text>
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
