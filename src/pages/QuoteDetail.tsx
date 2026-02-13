import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, FileDown, Check } from 'lucide-react';
import { Card, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Spinner } from '../components/ui/Spinner';
import { getQuoteWithItems, updateQuoteStatus } from '../services/quoteApi';
import { generateQuotePdf } from '../utils/pdfExport';
import { formatCurrency } from '../utils/formatting';
import type { SavedQuoteWithItems, SavedQuote } from '../types/quote';

const statusVariant: Record<string, 'default' | 'success' | 'warning' | 'danger'> = {
  draft: 'default',
  sent: 'warning',
  accepted: 'success',
  declined: 'danger',
};

const statusActions: { label: string; value: SavedQuote['status']; variant: 'primary' | 'secondary' | 'danger' }[] = [
  { label: 'Mark Sent', value: 'sent', variant: 'secondary' },
  { label: 'Accept', value: 'accepted', variant: 'primary' },
  { label: 'Decline', value: 'declined', variant: 'danger' },
];

export function QuoteDetail() {
  const { id } = useParams<{ id: string }>();
  const [quote, setQuote] = useState<SavedQuoteWithItems | null>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    if (!id) return;
    getQuoteWithItems(id)
      .then(setQuote)
      .catch((err) => console.error('Failed to load quote:', err))
      .finally(() => setLoading(false));
  }, [id]);

  const handleStatusChange = async (status: SavedQuote['status']) => {
    if (!quote) return;
    try {
      await updateQuoteStatus(quote.id, status);
      setQuote({ ...quote, status });
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  };

  const handleExportPdf = async () => {
    if (!quote) return;
    setExporting(true);
    try {
      await generateQuotePdf({
        quoteNumber: quote.quote_number,
        poNumber: quote.po_number ?? '',
        customerFirstName: quote.customer_first_name,
        customerLastName: quote.customer_last_name,
        customerPhone: quote.customer_phone ?? '',
        customerEmail: quote.customer_email ?? '',
        customerNotes: quote.customer_notes ?? '',
        items: quote.line_items.map((li) => ({
          id: li.id,
          description: li.description,
          formData: li.form_data,
          result: li.result,
          widthInput: li.width_input,
          heightInput: li.height_input,
          diameterInput: li.diameter_input,
        })),
        grandTotal: quote.grand_total,
        isContractor: quote.is_contractor,
        createdAt: quote.created_at,
        expiresAt: quote.expires_at,
      });
    } catch (err) {
      console.error('Failed to export PDF:', err);
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!quote) {
    return (
      <div className="max-w-lg mx-auto mt-12 text-center">
        <Card>
          <CardContent>
            <p className="text-gray-600 dark:text-gray-400">Quote not found.</p>
            <Link to="/quotes" className="inline-block mt-4">
              <Button size="sm" variant="secondary">Back to Quotes</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      {/* Back link */}
      <Link
        to="/quotes"
        className="inline-flex items-center gap-1.5 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 mb-4"
      >
        <ArrowLeft className="w-4 h-4" />
        All Quotes
      </Link>

      {/* Quote Header */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <Card>
          <CardContent>
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="flex items-center gap-3">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                    Quote #{quote.quote_number}
                  </h2>
                  <Badge variant={statusVariant[quote.status] ?? 'default'}>
                    {quote.status}
                  </Badge>
                </div>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Created {new Date(quote.created_at).toLocaleDateString()}
                  {quote.expires_at && (
                    <> &middot; Valid until {new Date(quote.expires_at).toLocaleDateString()}</>
                  )}
                </p>
              </div>
              <Button onClick={handleExportPdf} disabled={exporting} size="sm">
                <FileDown className="w-4 h-4 mr-1.5" />
                {exporting ? 'Exporting...' : 'Export PDF'}
              </Button>
            </div>

            {/* Customer Info */}
            {(quote.customer_first_name || quote.customer_last_name) && (
              <div className="border-t border-gray-100 dark:border-gray-700 pt-4 mt-4">
                <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Customer</h3>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Name: </span>
                    <span className="text-gray-900 dark:text-gray-100">
                      {[quote.customer_first_name, quote.customer_last_name].filter(Boolean).join(' ')}
                    </span>
                  </div>
                  {quote.po_number && (
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">PO #: </span>
                      <span className="text-gray-900 dark:text-gray-100 font-medium">{quote.po_number}</span>
                    </div>
                  )}
                  {quote.customer_phone && (
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Phone: </span>
                      <span className="text-gray-900 dark:text-gray-100">{quote.customer_phone}</span>
                    </div>
                  )}
                  {quote.customer_email && (
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Email: </span>
                      <span className="text-gray-900 dark:text-gray-100">{quote.customer_email}</span>
                    </div>
                  )}
                </div>
                {quote.customer_notes && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 italic">{quote.customer_notes}</p>
                )}
              </div>
            )}

            {/* Status Actions */}
            <div className="flex gap-2 mt-4 border-t border-gray-100 dark:border-gray-700 pt-4">
              {statusActions
                .filter((a) => a.value !== quote.status)
                .map((action) => (
                  <Button
                    key={action.value}
                    variant={action.variant}
                    size="sm"
                    onClick={() => handleStatusChange(action.value)}
                  >
                    {action.value === 'accepted' && <Check className="w-3.5 h-3.5 mr-1" />}
                    {action.label}
                  </Button>
                ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Line Items */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mt-4"
      >
        <Card>
          <CardContent>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3">
              Line Items ({quote.line_items.length})
            </h3>
            <div className="space-y-3">
              {quote.line_items.map((item, index) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between py-2 border-b border-gray-50 dark:border-gray-700 last:border-0"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-400 dark:text-gray-500 font-mono">{index + 1}.</span>
                      <span className="text-sm font-medium text-gray-900 dark:text-gray-100">{item.description}</span>
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 ml-5 mt-0.5">
                      {item.form_data.thickness} {item.form_data.glass_type}
                      {item.form_data.is_tempered ? ' | tempered' : ''}
                      {item.form_data.is_polished ? ' | polished' : ''}
                      {item.form_data.is_beveled ? ' | beveled' : ''}
                    </div>
                  </div>
                  <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                    {formatCurrency(item.line_total)}
                  </span>
                </div>
              ))}
            </div>

            {/* Totals */}
            <div className="border-t border-gray-200 dark:border-gray-700 mt-4 pt-4">
              <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-1">
                <span>Subtotal</span>
                <span>{formatCurrency(quote.subtotal)}</span>
              </div>
              {quote.is_contractor && (
                <div className="flex justify-between text-xs text-primary-600 mb-1">
                  <span>Contractor pricing applied</span>
                </div>
              )}
              <div className="flex justify-between items-baseline mt-2 pt-2 border-t border-gray-100 dark:border-gray-700">
                <span className="text-lg font-bold text-gray-900 dark:text-gray-100">Grand Total</span>
                <span className="text-xl font-bold text-primary-600">
                  {formatCurrency(quote.grand_total)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
