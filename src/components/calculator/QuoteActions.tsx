import { Button } from '../ui/Button';
import { Save, FileDown } from 'lucide-react';

interface QuoteActionsProps {
  onSaveQuote: () => void;
  onExportPdf: () => void;
  hasItems: boolean;
}

export function QuoteActions({ onSaveQuote, onExportPdf, hasItems }: QuoteActionsProps) {
  if (!hasItems) return null;

  return (
    <div className="flex gap-2 mt-4">
      <Button
        variant="secondary"
        size="sm"
        className="flex-1"
        onClick={onSaveQuote}
      >
        <Save className="w-4 h-4 mr-1.5" />
        Save Quote
      </Button>
      <Button
        size="sm"
        className="flex-1"
        onClick={onExportPdf}
      >
        <FileDown className="w-4 h-4 mr-1.5" />
        Export PDF
      </Button>
    </div>
  );
}
