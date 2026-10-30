import { Text, View } from 'react-native';
import { colors, spacing } from '@/lib/theme';

export function Header({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <View style={{ marginBottom: spacing.lg }}>
      <Text style={{ fontFamily: 'Inter-Bold', fontSize: 28, color: colors.text }}>{title}</Text>
      {subtitle && <Text style={{ fontFamily: 'Inter-Regular', fontSize: 14, color: colors.textSecondary, marginTop: 2 }}>{subtitle}</Text>}
    </View>
  );
}
