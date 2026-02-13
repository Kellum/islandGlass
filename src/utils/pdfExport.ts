import type { QuotePdfProps } from '../components/pdf/QuotePdfDocument';

function formatDateForFilename(dateStr: string): string {
  const d = new Date(dateStr);
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  const yyyy = d.getFullYear();
  return `${mm}-${dd}-${yyyy}`;
}

export async function generateQuotePdf(props: QuotePdfProps): Promise<void> {
  // Lazy-load @react-pdf/renderer to avoid bloating initial bundle
  const [{ pdf }, { QuotePdfDocument }] = await Promise.all([
    import('@react-pdf/renderer'),
    import('../components/pdf/QuotePdfDocument'),
  ]);

  const doc = QuotePdfDocument(props);
  const blob = await pdf(doc).toBlob();

  const datePart = formatDateForFilename(props.createdAt);
  let filename: string;

  if (props.poNumber) {
    // e.g. Kellum-Ryan-02-13-2026.pdf
    filename = `${props.poNumber}-${datePart}.pdf`;
  } else if (props.quoteNumber) {
    filename = `Island-Glass-Quote-${props.quoteNumber}-${datePart}.pdf`;
  } else {
    filename = `Island-Glass-Quote-${datePart}.pdf`;
  }

  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
