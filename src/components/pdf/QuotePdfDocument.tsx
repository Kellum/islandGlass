import {
  Document,
  Page,
  Text,
  View,
  StyleSheet,
} from '@react-pdf/renderer';
import type { QuoteItem } from '../../types';

const styles = StyleSheet.create({
  page: {
    padding: 40,
    fontSize: 10,
    fontFamily: 'Helvetica',
    color: '#1f2937',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 30,
    borderBottom: '2px solid #0369a1',
    paddingBottom: 15,
  },
  companyName: {
    fontSize: 22,
    fontFamily: 'Helvetica-Bold',
    color: '#0369a1',
  },
  companyTagline: {
    fontSize: 9,
    color: '#6b7280',
    marginTop: 2,
  },
  quoteInfo: {
    textAlign: 'right' as const,
  },
  quoteLabel: {
    fontSize: 16,
    fontFamily: 'Helvetica-Bold',
    color: '#374151',
  },
  quoteNumber: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 2,
  },
  quoteDate: {
    fontSize: 9,
    color: '#6b7280',
    marginTop: 2,
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 11,
    fontFamily: 'Helvetica-Bold',
    color: '#374151',
    marginBottom: 6,
    borderBottom: '1px solid #e5e7eb',
    paddingBottom: 4,
  },
  customerRow: {
    flexDirection: 'row',
    marginBottom: 3,
  },
  customerLabel: {
    width: 60,
    fontFamily: 'Helvetica-Bold',
    color: '#6b7280',
  },
  customerValue: {
    flex: 1,
    color: '#1f2937',
  },
  tableHeader: {
    flexDirection: 'row',
    backgroundColor: '#f3f4f6',
    padding: '6 8',
    borderRadius: 3,
    marginBottom: 4,
  },
  tableHeaderText: {
    fontFamily: 'Helvetica-Bold',
    fontSize: 9,
    color: '#374151',
  },
  tableRow: {
    flexDirection: 'row',
    padding: '5 8',
    borderBottom: '1px solid #f3f4f6',
  },
  colIndex: { width: 25 },
  colDescription: { flex: 1 },
  colDetails: { width: 140 },
  colTotal: { width: 70, textAlign: 'right' as const },
  detailText: {
    fontSize: 8,
    color: '#6b7280',
  },
  totalsSection: {
    marginTop: 15,
    borderTop: '2px solid #e5e7eb',
    paddingTop: 10,
    alignItems: 'flex-end' as const,
  },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginBottom: 4,
    width: 200,
  },
  totalLabel: {
    flex: 1,
    textAlign: 'right' as const,
    paddingRight: 15,
    color: '#6b7280',
  },
  totalValue: {
    width: 80,
    textAlign: 'right' as const,
    fontFamily: 'Helvetica-Bold',
  },
  grandTotalRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    width: 200,
    borderTop: '1px solid #d1d5db',
    paddingTop: 6,
  },
  grandTotalLabel: {
    flex: 1,
    textAlign: 'right' as const,
    paddingRight: 15,
    fontSize: 13,
    fontFamily: 'Helvetica-Bold',
    color: '#1f2937',
  },
  grandTotalValue: {
    width: 80,
    textAlign: 'right' as const,
    fontSize: 13,
    fontFamily: 'Helvetica-Bold',
    color: '#0369a1',
  },
  footer: {
    position: 'absolute' as const,
    bottom: 30,
    left: 40,
    right: 40,
    borderTop: '1px solid #e5e7eb',
    paddingTop: 10,
  },
  footerText: {
    fontSize: 8,
    color: '#9ca3af',
    textAlign: 'center' as const,
    marginBottom: 2,
  },
});

function formatCurrency(value: number): string {
  return `$${value.toFixed(2)}`;
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

function getItemDetails(item: QuoteItem): string {
  const parts: string[] = [];
  const fd = item.formData;
  parts.push(`${fd.thickness} ${fd.glass_type}`);
  if (fd.is_tempered) parts.push('tempered');
  if (fd.is_polished) parts.push('polished');
  if (fd.is_beveled) parts.push('beveled');
  if ((fd.num_clipped_corners ?? 0) > 0) parts.push(`${fd.num_clipped_corners} clipped`);
  if ((fd.quantity ?? 1) > 1) parts.push(`qty: ${fd.quantity}`);
  return parts.join(' | ');
}

export interface QuotePdfProps {
  quoteNumber: number | null;
  poNumber: string;
  customerFirstName: string;
  customerLastName: string;
  customerPhone: string;
  customerEmail: string;
  customerNotes: string;
  items: QuoteItem[];
  grandTotal: number;
  isContractor: boolean;
  createdAt: string;
  expiresAt: string | null;
}

export function QuotePdfDocument(props: QuotePdfProps) {
  const {
    quoteNumber,
    poNumber,
    customerFirstName,
    customerLastName,
    customerPhone,
    customerEmail,
    customerNotes,
    items,
    grandTotal,
    isContractor,
    createdAt,
    expiresAt,
  } = props;

  const customerFullName = [customerFirstName, customerLastName].filter(Boolean).join(' ');

  return (
    <Document>
      <Page size="LETTER" style={styles.page}>
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.companyName}>Island Glass</Text>
            <Text style={styles.companyTagline}>Custom Glass Solutions</Text>
          </View>
          <View style={styles.quoteInfo}>
            <Text style={styles.quoteLabel}>QUOTE</Text>
            {quoteNumber && (
              <Text style={styles.quoteNumber}>#{quoteNumber}</Text>
            )}
            {poNumber && (
              <Text style={styles.quoteNumber}>{poNumber}</Text>
            )}
            <Text style={styles.quoteDate}>Date: {formatDate(createdAt)}</Text>
            {expiresAt && (
              <Text style={styles.quoteDate}>Valid until: {formatDate(expiresAt)}</Text>
            )}
          </View>
        </View>

        {/* Customer Info */}
        {customerFullName && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Customer</Text>
            <View style={styles.customerRow}>
              <Text style={styles.customerLabel}>Name:</Text>
              <Text style={styles.customerValue}>{customerFullName}</Text>
            </View>
            {customerPhone && (
              <View style={styles.customerRow}>
                <Text style={styles.customerLabel}>Phone:</Text>
                <Text style={styles.customerValue}>{customerPhone}</Text>
              </View>
            )}
            {customerEmail && (
              <View style={styles.customerRow}>
                <Text style={styles.customerLabel}>Email:</Text>
                <Text style={styles.customerValue}>{customerEmail}</Text>
              </View>
            )}
            {customerNotes && (
              <View style={styles.customerRow}>
                <Text style={styles.customerLabel}>Notes:</Text>
                <Text style={styles.customerValue}>{customerNotes}</Text>
              </View>
            )}
          </View>
        )}

        {/* Pricing Type */}
        {isContractor && (
          <View style={{ marginBottom: 10 }}>
            <Text style={{ fontSize: 9, color: '#0369a1', fontFamily: 'Helvetica-Bold' }}>
              Contractor Pricing Applied
            </Text>
          </View>
        )}

        {/* Line Items Table */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Line Items</Text>

          {/* Table Header */}
          <View style={styles.tableHeader}>
            <Text style={[styles.tableHeaderText, styles.colIndex]}>#</Text>
            <Text style={[styles.tableHeaderText, styles.colDescription]}>Description</Text>
            <Text style={[styles.tableHeaderText, styles.colDetails]}>Details</Text>
            <Text style={[styles.tableHeaderText, styles.colTotal]}>Total</Text>
          </View>

          {/* Table Rows */}
          {items.map((item, index) => (
            <View key={item.id} style={styles.tableRow}>
              <Text style={styles.colIndex}>{index + 1}</Text>
              <Text style={styles.colDescription}>{item.description}</Text>
              <Text style={[styles.colDetails, styles.detailText]}>
                {getItemDetails(item)}
              </Text>
              <Text style={styles.colTotal}>
                {formatCurrency(item.result.quote_price)}
              </Text>
            </View>
          ))}
        </View>

        {/* Totals */}
        <View style={styles.totalsSection}>
          <View style={styles.totalRow}>
            <Text style={styles.totalLabel}>Subtotal:</Text>
            <Text style={styles.totalValue}>{formatCurrency(grandTotal)}</Text>
          </View>
          <View style={styles.grandTotalRow}>
            <Text style={styles.grandTotalLabel}>Grand Total:</Text>
            <Text style={styles.grandTotalValue}>{formatCurrency(grandTotal)}</Text>
          </View>
        </View>

        {/* Footer */}
        <View style={styles.footer} fixed>
          <Text style={styles.footerText}>
            This quote is valid for 30 days from the date of issue.
          </Text>
          <Text style={styles.footerText}>
            Prices are subject to change based on glass availability.
          </Text>
          <Text style={styles.footerText}>
            Island Glass - Custom Glass Solutions
          </Text>
        </View>
      </Page>
    </Document>
  );
}
