import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FileText, Eye, Trash2 } from 'lucide-react';
import { Card, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Spinner } from '../components/ui/Spinner';
import { getQuotes, deleteQuote } from '../services/quoteApi';
import { formatCurrency } from '../utils/formatting';
import type { SavedQuote } from '../types/quote';

const statusVariant: Record<string, 'default' | 'success' | 'warning' | 'danger'> = {
  draft: 'default',
  sent: 'warning',
  accepted: 'success',
  declined: 'danger',
};

export function QuotesList() {
  const [quotes, setQuotes] = useState<SavedQuote[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<string | null>(null);

  const fetchQuotes = async () => {
    try {
      const data = await getQuotes();
      setQuotes(data);
    } catch (err) {
      console.error('Failed to load quotes:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuotes();
  }, []);

  const handleDelete = async (id: string) => {
    setDeleting(id);
    try {
      await deleteQuote(id);
      setQuotes((prev) => prev.filter((q) => q.id !== id));
    } catch (err) {
      console.error('Failed to delete quote:', err);
    } finally {
      setDeleting(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Spinner size="lg" />
      </div>
    );
  }

  if (quotes.length === 0) {
    return (
      <div className="max-w-lg mx-auto mt-12 text-center">
        <Card>
          <CardContent>
            <FileText className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
            <p className="text-gray-600 dark:text-gray-400 font-medium">No quotes yet</p>
            <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
              Create a quote from the calculator to get started.
            </p>
            <Link to="/" className="inline-block mt-4">
              <Button size="sm">Go to Calculator</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">Saved Quotes</h2>
        <span className="text-sm text-gray-500 dark:text-gray-400">{quotes.length} quote{quotes.length !== 1 ? 's' : ''}</span>
      </div>

      <div className="space-y-3">
        {quotes.map((quote, index) => (
          <motion.div
            key={quote.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
          >
            <Card>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 min-w-0">
                    <div className="flex-shrink-0 w-10 h-10 bg-primary-50 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
                      <FileText className="w-5 h-5 text-primary-600" />
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-gray-900 dark:text-gray-100">
                          #{quote.quote_number}
                        </span>
                        <Badge variant={statusVariant[quote.status] ?? 'default'}>
                          {quote.status}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
                        {quote.po_number
                          ? `PO: ${quote.po_number}`
                          : [quote.customer_first_name, quote.customer_last_name].filter(Boolean).join(' ') || 'No customer name'}
                      </p>
                      <p className="text-xs text-gray-400 dark:text-gray-500">
                        {new Date(quote.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="text-lg font-bold text-gray-900 dark:text-gray-100">
                      {formatCurrency(quote.grand_total)}
                    </span>
                    <Link to={`/quotes/${quote.id}`}>
                      <Button variant="ghost" size="sm">
                        <Eye className="w-4 h-4" />
                      </Button>
                    </Link>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(quote.id)}
                      disabled={deleting === quote.id}
                    >
                      <Trash2 className="w-4 h-4 text-red-400" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
