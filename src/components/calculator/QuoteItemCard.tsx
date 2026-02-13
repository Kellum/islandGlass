import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, X } from 'lucide-react';
import { decimalToFraction } from '../../utils/fractions';
import type { QuoteItem } from '../../types';

interface QuoteItemCardProps {
  item: QuoteItem;
  index: number;
  onRemove: (id: string) => void;
}

export function QuoteItemCard({ item, index, onRemove }: QuoteItemCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="p-3 bg-gray-50 rounded-lg border border-gray-200"
    >
      <div className="flex items-start justify-between">
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-start gap-2 flex-1 text-left"
        >
          <motion.div animate={{ rotate: expanded ? 90 : 0 }} className="mt-0.5">
            <ChevronRight className="w-4 h-4 text-gray-500" />
          </motion.div>
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900">
              {index + 1}. {item.description}
            </p>
            {!expanded && (
              <p className="text-sm font-semibold text-primary-600 mt-0.5">
                ${item.result.quote_price.toFixed(2)}
              </p>
            )}
          </div>
        </button>
        <button
          onClick={() => onRemove(item.id)}
          className="p-1 text-gray-400 hover:text-red-500 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="ml-6 mt-2 space-y-1 pl-3 border-l-2 border-gray-200">
              <Row label="Area" value={`${decimalToFraction(item.result.billable_sq_ft)} sq ft`} />
              <Row label="Base" value={`$${item.result.base_price.toFixed(2)}`} />
              {item.result.polish_price != null && (
                <Row label="Polish" value={`$${item.result.polish_price.toFixed(2)}`} />
              )}
              {item.result.beveled_price != null && (
                <Row label="Beveled" value={`$${item.result.beveled_price.toFixed(2)}`} />
              )}
              {item.result.clipped_corners_price != null && (
                <Row label="Clipped" value={`$${item.result.clipped_corners_price.toFixed(2)}`} />
              )}
              {item.result.tempered_price != null && (
                <Row label="Tempered" value={`$${item.result.tempered_price.toFixed(2)}`} />
              )}
              {item.result.shape_price != null && (
                <Row label="Shape" value={`$${item.result.shape_price.toFixed(2)}`} />
              )}
              {item.result.contractor_discount != null && (
                <Row
                  label="Discount"
                  value={`-$${item.result.contractor_discount.toFixed(2)}`}
                  className="text-green-600"
                />
              )}
              <div className="pt-1 border-t border-gray-200">
                <Row
                  label="Quote Price"
                  value={`$${item.result.quote_price.toFixed(2)}`}
                  className="font-semibold text-primary-600"
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function Row({
  label,
  value,
  className = '',
}: {
  label: string;
  value: string;
  className?: string;
}) {
  return (
    <div className={`flex justify-between text-xs ${className || 'text-gray-600'}`}>
      <span>{label}</span>
      <span>{value}</span>
    </div>
  );
}
