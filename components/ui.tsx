import { Pressable, Text, View, type ViewStyle } from 'react-native';
import { colors, radius, shadows, spacing } from '@/lib/theme';

interface ChipProps {
  label: string;
  selected: boolean;
  onPress: () => void;
  color?: string;
  lightColor?: string;
}

export function Chip({ label, selected, onPress, color = colors.emerald, lightColor = colors.emeraldLight }: ChipProps) {
  return (
    <Pressable
      onPress={onPress}
      style={{
        paddingVertical: spacing.sm + 2,
        paddingHorizontal: spacing.md,
        borderRadius: radius.full,
        borderWidth: 1.5,
        borderColor: selected ? color : colors.border,
        backgroundColor: selected ? color : '#fff',
        alignItems: 'center',
      }}
    >
      <Text
        style={{
          fontFamily: 'Inter-SemiBold',
          fontSize: 13,
          color: selected ? '#fff' : colors.textSecondary,
        }}
      >
        {label}
      </Text>
    </Pressable>
  );
}

interface CardProps {
  children: React.ReactNode;
  style?: ViewStyle;
  onPress?: () => void;
}

export function Card({ children, style, onPress }: CardProps) {
  if (onPress) {
    return (
      <Pressable
        onPress={onPress}
        style={[{ backgroundColor: colors.card, borderRadius: radius.lg, padding: spacing.md, ...shadows.card }, style]}
      >
        {children}
      </Pressable>
    );
  }
  return (
    <View style={[{ backgroundColor: colors.card, borderRadius: radius.lg, padding: spacing.md, ...shadows.card }, style]}>
      {children}
    </View>
  );
}

interface ButtonProps {
  label: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  fullWidth?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
}

export function Button({
  label,
  onPress,
  variant = 'primary',
  fullWidth,
  disabled,
  icon,
}: ButtonProps) {
  const bg =
    variant === 'primary'
      ? colors.emerald
      : variant === 'danger'
      ? colors.error
      : variant === 'ghost'
      ? 'transparent'
      : '#fff';
  const fg = variant === 'secondary' ? colors.text : variant === 'ghost' ? colors.emerald : '#fff';
  const border = variant === 'secondary' ? colors.border : 'transparent';

  return (
    <Pressable
      onPress={onPress}
      disabled={disabled}
      style={({ pressed }) => [
        {
          flexDirection: 'row',
          alignItems: 'center',
          justifyContent: 'center',
          gap: spacing.sm,
          paddingVertical: spacing.md,
          paddingHorizontal: spacing.lg,
          borderRadius: radius.md,
          backgroundColor: disabled ? colors.textMuted : bg,
          borderWidth: 1.5,
          borderColor: disabled ? colors.textMuted : border,
          opacity: pressed ? 0.85 : 1,
        },
        fullWidth && { flex: 1 },
      ]}
    >
      {icon}
      <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: 16, color: fg }}>{label}</Text>
    </Pressable>
  );
}

export function PersonBadge({ name, emoji, color, size = 'md' }: { name: string; emoji: string; color: string; size?: 'sm' | 'md' }) {
  const dim = size === 'sm' ? 26 : 34;
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', gap: spacing.xs }}>
      <View
        style={{
          width: dim,
          height: dim,
          borderRadius: dim / 2,
          backgroundColor: color + '22',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Text style={{ fontSize: size === 'sm' ? 14 : 17 }}>{emoji}</Text>
      </View>
      <Text style={{ fontFamily: 'Inter-SemiBold', fontSize: size === 'sm' ? 12 : 14, color: colors.text }}>
        {name}
      </Text>
    </View>
  );
}

export function SectionTitle({ title, action }: { title: string; action?: React.ReactNode }) {
  return (
    <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.sm }}>
      <Text style={{ fontFamily: 'Inter-Bold', fontSize: 18, color: colors.text }}>{title}</Text>
      {action}
    </View>
  );
}

export function ScreenContainer({ children }: { children: React.ReactNode }) {
  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <View style={{ flex: 1, paddingHorizontal: spacing.md }}>{children}</View>
    </View>
  );
}
