export function formatCOP(amount: number): string {
  const rounded = Math.round(amount);
  const abs = Math.abs(rounded);
  const parts: string[] = [];
  const str = abs.toString();
  for (let i = str.length; i > 0; i -= 3) {
    parts.unshift(str.slice(Math.max(0, i - 3), i));
  }
  const grouped = parts.join('.');
  return `${rounded < 0 ? '-' : ''}$${grouped}`;
}

export function parseCOP(input: string): number {
  const cleaned = input.replace(/[^0-9]/g, '');
  return cleaned ? parseInt(cleaned, 10) : 0;
}

export function formatDate(iso: string): string {
  const d = new Date(iso + (iso.length <= 10 ? 'T00:00:00' : ''));
  return d.toLocaleDateString('es-CO', { day: 'numeric', month: 'short', year: 'numeric' });
}

export function formatShortDate(iso: string): string {
  const d = new Date(iso + (iso.length <= 10 ? 'T00:00:00' : ''));
  return d.toLocaleDateString('es-CO', { day: '2-digit', month: '2-digit' });
}

export function toInputDate(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

export function monthLabel(date: Date): string {
  return date.toLocaleDateString('es-CO', { month: 'long', year: 'numeric' });
}
