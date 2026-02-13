import type { QuoteParams, QuoteResult } from '../services/calculator';

export interface SavedQuote {
  id: string;
  quote_number: number;
  po_number: string | null;
  customer_first_name: string;
  customer_last_name: string;
  customer_phone: string | null;
  customer_email: string | null;
  customer_notes: string | null;
  status: 'draft' | 'sent' | 'accepted' | 'declined';
  is_contractor: boolean;
  subtotal: number;
  discount_amount: number;
  grand_total: number;
  created_at: string;
  updated_at: string;
  expires_at: string | null;
}

export interface SavedQuoteLineItem {
  id: string;
  quote_id: string;
  sort_order: number;
  description: string;
  form_data: QuoteParams;
  result: QuoteResult;
  line_total: number;
  width_input: string;
  height_input: string;
  diameter_input: string;
  created_at: string;
}

export interface SavedQuoteWithItems extends SavedQuote {
  line_items: SavedQuoteLineItem[];
}

export interface SaveQuoteFormData {
  po_number: string;
  customer_first_name: string;
  customer_last_name: string;
  customer_phone: string;
  customer_email: string;
  customer_notes: string;
}
