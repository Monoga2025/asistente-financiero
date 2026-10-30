export type AccountType = 'debit' | 'savings' | 'credit';
export type SplitType = 'half' | 'all_daniel' | 'all_ana' | 'by_items';
export type Assignment = 'ana' | 'daniel' | 'half';
export type ExpenseSource = 'manual' | 'scan';

export interface Person {
  id: string;
  name: string;
  emoji: string;
  color: string;
}

export interface Account {
  id: string;
  person_id: string;
  name: string;
  bank: string;
  type: AccountType;
  balance: number;
  is_default: boolean;
  credit_limit: number | null;
  credit_used: number | null;
  cutoff_day: number | null;
  due_day: number | null;
  created_at: string;
}

export interface ExpenseItem {
  id: string;
  expense_id: string;
  name: string;
  amount: number;
  assigned_to: Assignment;
}

export interface Expense {
  id: string;
  title: string;
  expense_date: string;
  total_amount: number;
  paid_by_person_id: string;
  account_id: string | null;
  split_type: SplitType;
  surcharge_applied: boolean;
  surcharge_amount: number;
  already_paid: boolean;
  note: string | null;
  image_url: string | null;
  source: ExpenseSource;
  created_at: string;
  expense_items?: ExpenseItem[];
  share_daniel?: number;
  share_ana?: number;
}

export interface AccountTransaction {
  id: string;
  account_id: string;
  expense_id: string | null;
  settlement_id: string | null;
  amount: number;
  type: 'expense' | 'payment' | 'settlement' | 'adjustment';
  description: string | null;
  created_at: string;
}

export interface Settlement {
  id: string;
  from_person_id: string;
  to_person_id: string;
  amount: number;
  account_id: string | null;
  settlement_date: string;
  note: string | null;
  created_at: string;
}

export interface ReceiptConcept {
  name: string;
  amount: number;
  assigned_to: Assignment;
}

export interface ScanResult {
  store: string | null;
  date: string | null;
  concepts: ReceiptConcept[];
  total: number;
}
