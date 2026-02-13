import { supabase } from './supabase';
import type { QuoteItem } from '../types';
import type {
  SavedQuote,
  SavedQuoteWithItems,
  SaveQuoteFormData,
} from '../types/quote';

export async function saveQuote(
  formData: SaveQuoteFormData,
  items: QuoteItem[],
  isContractor: boolean
): Promise<SavedQuote> {
  const subtotal = items.reduce((sum, item) => sum + item.result.quote_price, 0);
  const discountAmount = 0;
  const grandTotal = subtotal - discountAmount;

  const { data: quote, error: quoteError } = await supabase
    .from('quotes')
    .insert({
      po_number: formData.po_number || null,
      customer_first_name: formData.customer_first_name,
      customer_last_name: formData.customer_last_name,
      customer_phone: formData.customer_phone || null,
      customer_email: formData.customer_email || null,
      customer_notes: formData.customer_notes || null,
      status: 'draft',
      is_contractor: isContractor,
      subtotal,
      discount_amount: discountAmount,
      grand_total: grandTotal,
    })
    .select()
    .single();

  if (quoteError) throw quoteError;

  const lineItems = items.map((item, index) => ({
    quote_id: quote.id,
    sort_order: index,
    description: item.description,
    form_data: item.formData,
    result: item.result,
    line_total: item.result.quote_price,
    width_input: item.widthInput,
    height_input: item.heightInput,
    diameter_input: item.diameterInput,
  }));

  const { error: itemsError } = await supabase
    .from('quote_line_items')
    .insert(lineItems);

  if (itemsError) throw itemsError;

  return quote as SavedQuote;
}

export async function getQuotes(): Promise<SavedQuote[]> {
  const { data, error } = await supabase
    .from('quotes')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) throw error;
  return data as SavedQuote[];
}

export async function getQuoteWithItems(id: string): Promise<SavedQuoteWithItems> {
  const { data: quote, error: quoteError } = await supabase
    .from('quotes')
    .select('*')
    .eq('id', id)
    .single();

  if (quoteError) throw quoteError;

  const { data: lineItems, error: itemsError } = await supabase
    .from('quote_line_items')
    .select('*')
    .eq('quote_id', id)
    .order('sort_order');

  if (itemsError) throw itemsError;

  return {
    ...(quote as SavedQuote),
    line_items: lineItems,
  } as SavedQuoteWithItems;
}

export async function updateQuoteStatus(
  id: string,
  status: SavedQuote['status']
): Promise<void> {
  const { error } = await supabase
    .from('quotes')
    .update({ status })
    .eq('id', id);

  if (error) throw error;
}

export async function deleteQuote(id: string): Promise<void> {
  const { error } = await supabase
    .from('quotes')
    .delete()
    .eq('id', id);

  if (error) throw error;
}
