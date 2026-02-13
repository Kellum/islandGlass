import { useState, useEffect } from 'react';
import { Clock } from 'lucide-react';
import { Card, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Spinner } from '../ui/Spinner';
import { getAuditLog } from '../../services/adminApi';
import type { PricingFormulaAuditRow } from '../../types';

interface AuditLogProps {
  onToast: (type: 'success' | 'error', message: string) => void;
}

export function AuditLog({ onToast }: AuditLogProps) {
  const [entries, setEntries] = useState<PricingFormulaAuditRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await getAuditLog();
        setEntries(data);
      } catch {
        onToast('error', 'Failed to load audit log');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner />
      </div>
    );
  }

  if (entries.length === 0) {
    return (
      <div className="text-center py-16">
        <Clock className="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-1">No Changes Yet</h3>
        <p className="text-sm text-gray-500">
          Changes to pricing configuration will appear here.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {entries.map((entry) => (
        <Card key={entry.id}>
          <CardContent className="py-3">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <Badge
                    variant={
                      entry.action === 'INSERT'
                        ? 'success'
                        : entry.action === 'DELETE'
                          ? 'danger'
                          : 'default'
                    }
                  >
                    {entry.action}
                  </Badge>
                  <span className="text-sm font-medium text-gray-900">
                    {entry.table_name}
                  </span>
                  {entry.record_id && (
                    <span className="text-xs text-gray-400">#{entry.record_id}</span>
                  )}
                </div>

                {/* Value diff */}
                <div className="flex flex-wrap gap-4 text-xs">
                  {entry.old_values && (
                    <div>
                      <span className="text-gray-500">Old: </span>
                      <span className="text-red-600 font-mono">
                        {formatValues(entry.old_values)}
                      </span>
                    </div>
                  )}
                  {entry.new_values && (
                    <div>
                      <span className="text-gray-500">New: </span>
                      <span className="text-green-600 font-mono">
                        {formatValues(entry.new_values)}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              <time className="text-xs text-gray-400 whitespace-nowrap">
                {new Date(entry.changed_at).toLocaleString()}
              </time>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function formatValues(values: Record<string, unknown>): string {
  const interesting = Object.entries(values).filter(
    ([k]) => !['id', 'created_at', 'updated_at', 'created_by', 'company_id', 'is_active'].includes(k)
  );
  if (interesting.length === 0) return JSON.stringify(values);
  return interesting.map(([k, v]) => `${k}: ${v}`).join(', ');
}
