import { motion } from 'framer-motion';
import { AnimatedPrice } from './AnimatedPrice';
import { Card, CardContent } from '../ui/Card';
import type { QuoteResult } from '../../services/calculator';
import type { CalculatorConfig } from '../../services/calculator';
import { decimalToFraction } from '../../utils/fractions';

interface PriceSummaryProps {
  result: QuoteResult | null;
  config: CalculatorConfig | null;
  hasItems: boolean;
}

function PriceRow({
  label,
  value,
  variant = 'default',
}: {
  label: string;
  value: number;
  variant?: 'default' | 'discount' | 'total';
}) {
  return (
    <div
      className={`flex justify-between text-sm ${
        variant === 'discount'
          ? 'text-green-600'
          : variant === 'total'
            ? 'text-gray-900 font-semibold'
            : 'text-gray-600'
      }`}
    >
      <span>{label}</span>
      <span className={variant === 'default' ? 'font-medium text-gray-900' : 'font-medium'}>
        {variant === 'discount' ? '-' : ''}
        <AnimatedPrice value={Math.abs(value)} />
      </span>
    </div>
  );
}

export function PriceSummary({ result, config, hasItems }: PriceSummaryProps) {
  const showMinWarning =
    result && result.actual_sq_ft < (config?.settings.minimum_sq_ft || 3.0);

  // Markup ratio to convert wholesale → retail for display
  const markupRatio =
    result && !result.error && result.total > 0
      ? result.quote_price / result.total
      : 1;

  const retail = (wholesale: number) => wholesale * markupRatio;

  return (
    <Card>
      <CardContent>
        <h2 className="text-base font-semibold text-gray-900 mb-4">
          {hasItems ? 'Current Item' : 'Price Summary'}
        </h2>

        {!result ? (
          <div className="py-8 text-center">
            <p className="text-sm text-gray-500">Enter dimensions to see pricing</p>
          </div>
        ) : result.error ? (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-3 bg-red-50 border border-red-200 rounded-lg"
          >
            <p className="text-sm text-red-700">{result.error}</p>
          </motion.div>
        ) : (
          <div className="space-y-2">
            {/* Area */}
            {showMinWarning ? (
              <>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Actual Area:</span>
                  <span className="font-medium text-gray-900">
                    {result.actual_sq_ft.toFixed(2)} sq ft
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-yellow-700 font-medium">Minimum Charge:</span>
                  <span className="font-medium text-yellow-700">
                    {config?.settings.minimum_sq_ft} sq ft
                  </span>
                </div>
              </>
            ) : (
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Area:</span>
                <span className="font-medium text-gray-900">
                  {decimalToFraction(result.billable_sq_ft)} sq ft
                </span>
              </div>
            )}

            {/* Per sq ft price */}
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Price per sq ft:</span>
              <span className="font-medium text-gray-900">
                <AnimatedPrice value={retail(result.base_price) / result.billable_sq_ft} />
              </span>
            </div>

            {/* Retail line items */}
            <div className="border-t border-gray-100 pt-2 mt-1">
              <PriceRow label="Glass" value={retail(result.base_price)} />
              {result.polish_price != null && (
                <PriceRow label="Flat Polish" value={retail(result.polish_price)} />
              )}
              {result.beveled_price != null && (
                <PriceRow label="Beveled Edge" value={retail(result.beveled_price)} />
              )}
              {result.clipped_corners_price != null && (
                <PriceRow label="Clipped Corners" value={retail(result.clipped_corners_price)} />
              )}
              {result.tempered_price != null && (
                <PriceRow label="Tempered" value={retail(result.tempered_price)} />
              )}
              {result.shape_price != null && (
                <PriceRow label="Shape Surcharge" value={retail(result.shape_price)} />
              )}
            </div>

            {/* Subtotal */}
            <div className="border-t border-gray-100 pt-2">
              <PriceRow label="Subtotal" value={retail(result.subtotal)} variant="total" />
            </div>

            {/* Contractor Discount */}
            {result.contractor_discount != null && (
              <PriceRow
                label="Contractor Discount (15%)"
                value={retail(result.contractor_discount)}
                variant="discount"
              />
            )}

            {/* Quote Price */}
            <div className="border-t border-gray-200 pt-3 mt-1">
              <div className="flex justify-between items-baseline">
                <span className="text-lg font-bold text-gray-900">Quote Price</span>
                <AnimatedPrice
                  value={result.quote_price}
                  className="text-2xl font-bold text-primary-600"
                />
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
