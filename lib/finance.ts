import { DANIEL_ID, ANA_ID } from './people';
import type { Account, AccountTransaction, Assignment, Expense, ExpenseItem, Settlement, SplitType } from './types';

const API_BASE = process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const APP_TOKEN = process.env.EXPO_PUBLIC_APP_TOKEN;
let bootstrapCache: { data: ApiBootstrap; time: number } | null = null;
const BOOTSTRAP_TTL_MS = 15_000;

export interface BalanceInfo {
  amount: number;
  label: string;
  owesFrom: string | null;
  owesTo: string | null;
}

export function describeBalance(amount: number): BalanceInfo {
  if (amount === 0) return { amount: 0, label: 'Van a mano', owesFrom: null, owesTo: null };
  if (amount > 0) {
    return { amount, label: 'Ana le debe a Daniel', owesFrom: 'Ana', owesTo: 'Daniel' };
  }
  return { amount: Math.abs(amount), label: 'Daniel le debe a Ana', owesFrom: 'Daniel', owesTo: 'Ana' };
}

export function computeShare(
  total: number,
  splitType: SplitType,
  items: ExpenseItem[] | undefined,
  paidByPersonId: string,
): { danielShare: number; anaShare: number } {
  if (items?.length && splitType === 'by_items') {
    let daniel = 0;
    let ana = 0;
    for (const item of items) {
      if (item.assigned_to === 'daniel') daniel += item.amount;
      else if (item.assigned_to === 'ana') ana += item.amount;
      else {
        const half = Math.floor(item.amount / 2);
        ana += half;
        daniel += item.amount - half;
      }
    }
    const remainder = total - daniel - ana;
    if (remainder > 0) {
      const half = Math.floor(remainder / 2);
      ana += half;
      daniel += remainder - half;
    }
    return { danielShare: daniel, anaShare: ana };
  }
  if (splitType === 'all_daniel') return { danielShare: total, anaShare: 0 };
  if (splitType === 'all_ana') return { danielShare: 0, anaShare: total };
  const anaShare = Math.floor(total / 2);
  return { danielShare: total - anaShare, anaShare };
}

export function balanceDeltaForExpense(paidByPersonId: string, danielShare: number, anaShare: number): number {
  if (paidByPersonId === DANIEL_ID) return anaShare;
  if (paidByPersonId === ANA_ID) return -danielShare;
  return 0;
}

export async function fetchAccounts(): Promise<Account[]> {
  const data = await getBootstrap();
  return data.accounts.map(mapAccount);
}

export async function fetchExpenses(limit = 50): Promise<Expense[]> {
  const data = await getBootstrap();
  return data.expenses.slice(0, limit).map(mapExpense);
}

export async function fetchSettlements(limit = 50): Promise<Settlement[]> {
  const data = await getBootstrap();
  return data.settlements.slice(0, limit).map(mapSettlement);
}

export async function computeBalance(): Promise<number> {
  const data = await getBootstrap();
  return data.balance.net;
}

export interface SaveExpenseInput {
  title: string;
  expenseDate: string;
  totalAmount: number;
  paidByPersonId: string;
  accountId: string | null;
  splitType: SplitType;
  surchargeApplied: boolean;
  surchargeAmount: number;
  alreadyPaid: boolean;
  note: string | null;
  imageUrl: string | null;
  source: 'manual' | 'scan';
  items?: { name: string; amount: number; assigned_to: Assignment }[];
}

export async function saveExpense(input: SaveExpenseInput): Promise<Expense> {
  const data = await apiPost<{ expenseId: number }>('/expenses', input);
  invalidateBootstrap();
  const expenses = await fetchExpenses(200);
  const saved = expenses.find((expense) => expense.id === String(data.expenseId));
  if (!saved) throw new Error('El gasto se guardo, pero no se pudo recargar.');
  return saved;
}

export async function uploadReceiptImage(): Promise<string> {
  throw new Error('La imagen se guarda desde el backend al escanear la factura.');
}

export async function saveSettlement(input: {
  fromPersonId: string;
  toPersonId: string;
  amount: number;
  accountId: string | null;
  date: string;
  note: string | null;
}): Promise<Settlement> {
  const data = await apiPost<{ settlementId: number }>('/settlements', input);
  invalidateBootstrap();
  const settlements = await fetchSettlements(200);
  const saved = settlements.find((settlement) => settlement.id === String(data.settlementId));
  if (!saved) throw new Error('El pago se guardo, pero no se pudo recargar.');
  return saved;
}

export async function fetchAccountTransactions(accountId: string, limit = 50): Promise<AccountTransaction[]> {
  const data = await apiGet<{ transactions: ApiTransaction[] }>(`/api/mobile/accounts/${accountId}/transactions`);
  return data.transactions.slice(0, limit).map((tx) => ({
    id: String(tx.id),
    account_id: String(tx.accountId),
    expense_id: tx.relatedExpenseId ? String(tx.relatedExpenseId) : null,
    settlement_id: null,
    amount: tx.amount,
    type: tx.type === 'expense' ? 'expense' : tx.type === 'payment' ? 'payment' : 'adjustment',
    description: tx.description,
    created_at: tx.date || tx.createdAt,
  }));
}

export async function scanReceiptImage(uri: string): Promise<{
  draftId: number;
  imageUrl: string | null;
  store: string | null;
  concepts: { name: string; amount: number; assigned_to: Assignment }[];
  aiNote: string | null;
}> {
  const form = new FormData();
  form.append('image', { uri, name: 'recibo.jpg', type: 'image/jpeg' } as any);
  const res = await fetch(`${API_BASE}/receipts/scan`, { method: 'POST', headers: authHeaders(), body: form });
  const json = await res.json();
  if (!res.ok || !json.ok) throw new Error(json.error || 'No se pudo escanear la factura.');
  return {
    draftId: json.draftId,
    imageUrl: json.draft?.imageUrl ?? null,
    store: json.draft?.merchantGuess ?? null,
    concepts: (json.draft?.items ?? []).map((item: any) => ({
      name: String(item.description || item.name || '').trim(),
      amount: Math.round(Number(item.amount) || 0),
      assigned_to: 'half' as Assignment,
    })).filter((item: { name: string; amount: number }) => item.name && item.amount > 0),
    aiNote: json.draft?.aiNote ?? null,
  };
}

export async function saveScannedReceipt(input: {
  draftId: number;
  title: string;
  date: string;
  paidBy: string;
  accountId: string | null;
  addSurcharge: boolean;
  surchargePercent: number;
  items: { description: string; amount: number; assignedTo: 'ana' | 'daniel' | 'equal' }[];
}) {
  const result = await apiPost<{ expenseId: number; totalAmount: number }>('/receipts/confirm', input);
  invalidateBootstrap();
  return result;
}

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { headers: authHeaders() });
  const json = await res.json();
  if (!res.ok || json.ok === false) throw new Error(json.error || json.detail || `Error ${res.status}`);
  return json as T;
}

async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(body),
  });
  const json = await res.json();
  if (!res.ok || json.ok === false) throw new Error(json.error || json.detail || `Error ${res.status}`);
  return json as T;
}

async function getBootstrap(): Promise<ApiBootstrap> {
  const now = Date.now();
  if (bootstrapCache && now - bootstrapCache.time < BOOTSTRAP_TTL_MS) return bootstrapCache.data;
  const data = await apiGet<ApiBootstrap>('/mobile/bootstrap');
  bootstrapCache = { data, time: now };
  return data;
}

function invalidateBootstrap() {
  bootstrapCache = null;
}

function authHeaders(): Record<string, string> {
  return APP_TOKEN ? { 'X-App-Token': APP_TOKEN } : {};
}

function mapAccount(account: ApiAccount): Account {
  const kind = account.kind === 'credit' ? 'credit' : 'debit';
  return {
    id: String(account.id),
    person_id: account.personSlug === 'ana' ? ANA_ID : DANIEL_ID,
    name: `${account.personName} ${account.name}`,
    bank: account.type?.startsWith('nu') ? 'Nu' : 'Nequi',
    type: kind,
    balance: account.balance,
    is_default: account.isDefault ?? account.name === 'Nequi',
    credit_limit: account.creditLimit,
    credit_used: kind === 'credit' ? account.balance : null,
    cutoff_day: account.cutoffDay,
    due_day: account.dueDay,
    created_at: '',
  };
}

function mapExpense(expense: ApiExpense): Expense {
  const splitType = mapSplitType(expense.splitType);
  return {
    id: String(expense.id),
    title: expense.title,
    expense_date: expense.date,
    total_amount: expense.totalAmount,
    paid_by_person_id: String(expense.paidByPersonId ?? (expense.paidBy === 'ana' ? ANA_ID : DANIEL_ID)),
    account_id: expense.accountId ? String(expense.accountId) : null,
    split_type: splitType,
    surcharge_applied: (expense.surchargeAmount ?? 0) > 0,
    surcharge_amount: expense.surchargeAmount ?? 0,
    already_paid: false,
    note: null,
    image_url: expense.receiptImageUrl ?? null,
    source: expense.source === 'receipt' ? 'scan' : 'manual',
    created_at: String(expense.createdAt ?? ''),
    expense_items: expense.items?.map((item) => ({
      id: String(item.id),
      expense_id: String(item.expenseId),
      name: item.description,
      amount: item.amount,
      assigned_to: item.assignedTo === 'equal' ? 'half' : (item.assignedTo as Assignment),
    })),
    share_daniel: expense.shareDaniel,
    share_ana: expense.shareAna,
  } as Expense & { share_daniel?: number; share_ana?: number };
}

function mapSettlement(settlement: ApiSettlement): Settlement {
  return {
    id: String(settlement.id),
    from_person_id: String(settlement.fromPersonId),
    to_person_id: String(settlement.toPersonId),
    amount: settlement.amount,
    account_id: null,
    settlement_date: settlement.date,
    note: settlement.note,
    created_at: String(settlement.createdAt ?? ''),
  };
}

function mapSplitType(value: string): SplitType {
  if (value === 'full_daniel') return 'all_daniel';
  if (value === 'full_ana') return 'all_ana';
  if (value === 'items') return 'by_items';
  return 'half';
}

type ApiAccount = {
  id: number;
  name: string;
  type: string;
  kind: string;
  balance: number;
  isDefault?: boolean;
  creditLimit: number | null;
  cutoffDay: number | null;
  dueDay: number | null;
  personSlug: 'ana' | 'daniel';
  personName: string;
};

type ApiBootstrap = {
  ok: boolean;
  balance: { net: number };
  accounts: ApiAccount[];
  expenses: ApiExpense[];
  settlements: ApiSettlement[];
};

type ApiExpense = {
  id: number;
  title: string;
  date: string;
  totalAmount: number;
  paidByPersonId?: number;
  paidBy?: 'ana' | 'daniel';
  accountId: number | null;
  splitType: string;
  shareAna: number;
  shareDaniel: number;
  surchargeAmount: number;
  receiptImageUrl: string | null;
  source: string;
  createdAt?: string;
  items?: { id: number; expenseId: number; description: string; amount: number; assignedTo: string }[];
};

type ApiSettlement = {
  id: number;
  fromPersonId: number;
  toPersonId: number;
  amount: number;
  date: string;
  note: string | null;
  createdAt?: string;
};

type ApiTransaction = {
  id: number;
  accountId: number;
  amount: number;
  type: string;
  description: string | null;
  date: string;
  relatedExpenseId: number | null;
  createdAt: string;
};
