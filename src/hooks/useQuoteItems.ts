import { useState, useMemo } from 'react';
import type { QuoteItem } from '../types';
import type { QuoteParams, QuoteResult } from '../services/calculator';

export function useQuoteItems() {
  const [items, setItems] = useState<QuoteItem[]>([]);

  const addItem = (
    formData: QuoteParams,
    result: QuoteResult,
    widthInput: string,
    heightInput: string,
    diameterInput: string
  ) => {
    let description = '';
    if (formData.is_circular && formData.diameter) {
      description = `${diameterInput}" Ø ${formData.thickness} ${formData.glass_type}`;
    } else {
      description = `${widthInput}" × ${heightInput}" ${formData.thickness} ${formData.glass_type}`;
    }

    if ((formData.quantity ?? 1) > 1) {
      description += ` (×${formData.quantity})`;
    }

    const newItem: QuoteItem = {
      id: Date.now().toString(),
      description,
      formData: { ...formData },
      result: { ...result },
      widthInput,
      heightInput,
      diameterInput,
    };

    setItems((prev) => [...prev, newItem]);
    return newItem.id;
  };

  const removeItem = (id: string) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
  };

  const clearItems = () => {
    setItems([]);
  };

  const grandTotal = useMemo(() => {
    return items.reduce((sum, item) => sum + item.result.quote_price, 0);
  }, [items]);

  return {
    items,
    addItem,
    removeItem,
    clearItems,
    grandTotal,
  };
}
