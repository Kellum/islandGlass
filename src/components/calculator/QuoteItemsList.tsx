import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Trash2 } from 'lucide-react';
import { AnimatedPrice } from './AnimatedPrice';
import { QuoteItemCard } from './QuoteItemCard';
import { QuoteActions } from './QuoteActions';
import { Card, CardContent } from '../ui/Card';
import type { QuoteItem } from '../../types';
import type { QuoteResult } from '../../services/calculator';

interface QuoteItemsListProps {
  items: QuoteItem[];
  currentResult: QuoteResult | null;
  grandTotal: number;
  onRemoveItem: (id: string) => void;
  onClearAll: () => void;
  onSaveQuote: () => void;
  onExportPdf: () => void;
}

export function QuoteItemsList({
  items,
  currentResult,
  grandTotal,
  onRemoveItem,
  onClearAll,
  onSaveQuote,
  onExportPdf,
}: QuoteItemsListProps) {
  const [expanded, setExpanded] = useState(true);

  if (items.length === 0) return null;

  const displayTotal =
    grandTotal + (currentResult && !currentResult.error ? currentResult.quote_price : 0);

  return (
    <Card className="mt-4">
      <CardContent>
        {/* Grand Total */}
        <div className="space-y-2 mb-4">
          <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
            <span>Items in quote</span>
            <span className="font-medium text-gray-900 dark:text-gray-100">{items.length}</span>
          </div>
          {currentResult && !currentResult.error && (
            <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
              <span>Current item</span>
              <span className="font-medium text-gray-900 dark:text-gray-100">
                ${currentResult.quote_price.toFixed(2)}
              </span>
            </div>
          )}
          <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
            <span>Saved items</span>
            <span className="font-medium text-gray-900 dark:text-gray-100">${grandTotal.toFixed(2)}</span>
          </div>
          <div className="border-t border-gray-200 dark:border-gray-700 pt-2">
            <div className="flex justify-between items-baseline">
              <span className="text-lg font-bold text-gray-900 dark:text-gray-100">Grand Total</span>
              <AnimatedPrice
                value={displayTotal}
                className="text-2xl font-bold text-primary-600"
              />
            </div>
          </div>
        </div>

        {/* Save / Export Actions */}
        <QuoteActions
          onSaveQuote={onSaveQuote}
          onExportPdf={onExportPdf}
          hasItems={items.length > 0}
        />

        {/* Items Accordion */}
        <div className="border-t border-gray-100 dark:border-gray-700 pt-3">
          <button
            onClick={() => setExpanded(!expanded)}
            className="w-full flex items-center justify-between"
          >
            <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
              Line Items ({items.length})
            </span>
            <motion.div animate={{ rotate: expanded ? 180 : 0 }}>
              <ChevronDown className="w-4 h-4 text-gray-500 dark:text-gray-400" />
            </motion.div>
          </button>

          <AnimatePresence>
            {expanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <div className="mt-3 space-y-2">
                  <AnimatePresence mode="popLayout">
                    {items.map((item, index) => (
                      <QuoteItemCard
                        key={item.id}
                        item={item}
                        index={index}
                        onRemove={onRemoveItem}
                      />
                    ))}
                  </AnimatePresence>
                </div>

                {items.length > 0 && (
                  <button
                    onClick={onClearAll}
                    className="mt-3 flex items-center gap-1.5 text-xs text-gray-400 dark:text-gray-500 hover:text-red-500 transition-colors"
                  >
                    <Trash2 className="w-3 h-3" />
                    Clear all items
                  </button>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </CardContent>
    </Card>
  );
}
