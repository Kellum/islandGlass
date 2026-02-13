import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent } from '../ui/Card';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { Toggle } from '../ui/Toggle';
import { ShapeSelector } from './ShapeSelector';
import { DimensionInputs } from './DimensionInputs';
import { EdgeProcessing } from './EdgeProcessing';
import { AddItemButton } from './AddItemButton';
import { PriceSummary } from './PriceSummary';
import { QuoteItemsList } from './QuoteItemsList';
import { SaveQuoteModal } from './SaveQuoteModal';
import { useSupabaseConfig } from '../../hooks/useSupabaseConfig';
import { useCalculator } from '../../hooks/useCalculator';
import { useQuoteItems } from '../../hooks/useQuoteItems';
import { Spinner } from '../ui/Spinner';
import { saveQuote } from '../../services/quoteApi';
import { generateQuotePdf } from '../../utils/pdfExport';
import type { CalculatorConfig } from '../../services/calculator';
import type { SaveQuoteFormData } from '../../types/quote';
import type { SaveModalData } from './SaveQuoteModal';

const GLASS_TYPES = [
  { value: 'clear', label: 'Clear' },
  { value: 'bronze', label: 'Bronze' },
  { value: 'gray', label: 'Gray' },
  { value: 'mirror', label: 'Mirror' },
];

const THICKNESS_OPTIONS = [
  { value: '1/8"', label: '1/8"' },
  { value: '3/16"', label: '3/16"' },
  { value: '1/4"', label: '1/4"' },
  { value: '3/8"', label: '3/8"' },
  { value: '1/2"', label: '1/2"' },
];

function getAvailableThicknesses(glassType: string, config: CalculatorConfig | null) {
  if (!config) return THICKNESS_OPTIONS;
  return THICKNESS_OPTIONS.filter((opt) => {
    const key = `${opt.value}_${glassType}`;
    return config.glass_config[key] !== undefined;
  });
}

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.4, ease: 'easeOut' as const },
  }),
};

export function CalculatorForm() {
  const { config, loading, error: configError } = useSupabaseConfig();
  const {
    formData,
    widthInput,
    heightInput,
    diameterInput,
    result,
    updateField,
    handleWidthChange,
    handleHeightChange,
    handleDiameterChange,
    resetForm,
  } = useCalculator(config);
  const { items, addItem, removeItem, clearItems, grandTotal } = useQuoteItems();
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [saving, setSaving] = useState(false);

  // Customer info lives in the main form
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [poNumber, setPoNumber] = useState('');
  const [poManuallyEdited, setPoManuallyEdited] = useState(false);

  const handleFirstNameChange = (value: string) => {
    setFirstName(value);
    if (!poManuallyEdited) {
      setPoNumber([lastName, value].filter(Boolean).join('-'));
    }
  };

  const handleLastNameChange = (value: string) => {
    setLastName(value);
    if (!poManuallyEdited) {
      setPoNumber([value, firstName].filter(Boolean).join('-'));
    }
  };

  const handlePoChange = (value: string) => {
    setPoManuallyEdited(true);
    setPoNumber(value);
  };

  const buildFullFormData = (modalData: SaveModalData): SaveQuoteFormData => ({
    po_number: poNumber,
    customer_first_name: firstName,
    customer_last_name: lastName,
    ...modalData,
  });

  const handleSaveQuote = async (modalData: SaveModalData) => {
    if (items.length === 0) return;
    setSaving(true);
    try {
      const full = buildFullFormData(modalData);
      await saveQuote(full, items, formData.is_contractor ?? false);
      setShowSaveModal(false);
      clearItems();
    } catch (err) {
      console.error('Failed to save quote:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleSaveAndExport = async (modalData: SaveModalData) => {
    if (items.length === 0) return;
    setSaving(true);
    try {
      const full = buildFullFormData(modalData);
      const saved = await saveQuote(full, items, formData.is_contractor ?? false);
      setShowSaveModal(false);
      await generateQuotePdf({
        quoteNumber: saved.quote_number,
        poNumber: full.po_number,
        customerFirstName: full.customer_first_name,
        customerLastName: full.customer_last_name,
        customerPhone: full.customer_phone,
        customerEmail: full.customer_email,
        customerNotes: full.customer_notes,
        items,
        grandTotal,
        isContractor: formData.is_contractor ?? false,
        createdAt: saved.created_at,
        expiresAt: saved.expires_at,
      });
      clearItems();
    } catch (err) {
      console.error('Failed to save/export quote:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleExportPdfOnly = async () => {
    if (items.length === 0) return;
    try {
      await generateQuotePdf({
        quoteNumber: null,
        poNumber,
        customerFirstName: firstName,
        customerLastName: lastName,
        customerPhone: '',
        customerEmail: '',
        customerNotes: '',
        items,
        grandTotal,
        isContractor: formData.is_contractor ?? false,
        createdAt: new Date().toISOString(),
        expiresAt: null,
      });
    } catch (err) {
      console.error('Failed to export PDF:', err);
    }
  };

  const handleAddItem = () => {
    if (!result || result.error) return;
    addItem(formData, result, widthInput, heightInput, diameterInput);
    resetForm(true);
  };

  // Determine current shape for the selector
  const currentShape = formData.is_circular
    ? 'circular'
    : formData.is_non_rectangular
      ? 'custom'
      : 'rectangular';

  const handleShapeChange = (shape: 'rectangular' | 'circular' | 'custom') => {
    updateField('is_circular', shape === 'circular');
    updateField('is_non_rectangular', shape === 'custom');
    updateField('num_clipped_corners', 0);
  };

  // Available thicknesses based on selected glass type
  const availableThicknesses = getAvailableThicknesses(formData.glass_type, config);

  // Current glass config flags from DB
  const currentGlassKey = `${formData.thickness}_${formData.glass_type}`;
  const currentGlassFlags = config?.glass_config[currentGlassKey];
  const noPolish = currentGlassFlags?.no_polish ?? false;
  const neverTempered = currentGlassFlags?.never_tempered ?? false;

  // Reset incompatible options based on DB flags
  const resetForFlags = (thickness: string, glassType: string) => {
    const key = `${thickness}_${glassType}`;
    const flags = config?.glass_config[key];
    if (!flags) return;
    if (flags.no_polish) {
      updateField('is_polished', false);
      updateField('is_beveled', false);
    }
    if (flags.never_tempered) {
      updateField('is_tempered', false);
    }
  };

  // Auto-correct thickness if current one isn't available for selected glass type
  const handleGlassTypeChange = (glassType: string) => {
    updateField('glass_type', glassType);
    const available = getAvailableThicknesses(glassType, config);
    let activeThickness = formData.thickness;
    if (!available.find((t) => t.value === formData.thickness) && available.length > 0) {
      activeThickness = available[0].value;
      updateField('thickness', activeThickness);
    }
    resetForFlags(activeThickness, glassType);
  };

  const handleThicknessChange = (thickness: string) => {
    updateField('thickness', thickness);
    resetForFlags(thickness, formData.glass_type);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Spinner size="lg" />
      </div>
    );
  }

  if (configError) {
    return (
      <div className="max-w-lg mx-auto mt-12">
        <Card>
          <CardContent>
            <p className="text-center text-gray-600">
              Unable to load pricing configuration. Please check your Supabase connection.
            </p>
            <p className="text-center text-sm text-gray-400 mt-2">{configError}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-7 gap-6">
      {/* Left Column - Form */}
      <div className="lg:col-span-4 space-y-5">
        {/* Customer Info */}
        <motion.div custom={0} initial="hidden" animate="visible" variants={cardVariants}>
          <Card>
            <CardContent>
              <h2 className="text-base font-semibold text-gray-900 mb-4">Customer</h2>
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="First Name"
                  placeholder="Ryan"
                  value={firstName}
                  onChange={(e) => handleFirstNameChange(e.target.value)}
                />
                <Input
                  label="Last Name"
                  placeholder="Kellum"
                  value={lastName}
                  onChange={(e) => handleLastNameChange(e.target.value)}
                />
              </div>
              <div className="mt-3">
                <Input
                  label="PO #"
                  placeholder="Kellum-Ryan"
                  hint="Auto-filled as Lastname-Firstname"
                  value={poNumber}
                  onChange={(e) => handlePoChange(e.target.value)}
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Basic Info */}
        <motion.div custom={1} initial="hidden" animate="visible" variants={cardVariants}>
          <Card>
            <CardContent>
              <h2 className="text-base font-semibold text-gray-900 mb-4">Glass Type</h2>
              <div className="grid grid-cols-2 gap-4">
                <Select
                  label="Type"
                  value={formData.glass_type}
                  onChange={(e) => handleGlassTypeChange(e.target.value)}
                  options={GLASS_TYPES}
                />
                <Select
                  label="Thickness"
                  value={formData.thickness}
                  onChange={(e) => handleThicknessChange(e.target.value)}
                  options={availableThicknesses}
                />
              </div>
              <div className="mt-4 space-y-1">
                <Toggle
                  checked={formData.is_tempered ?? false}
                  onChange={(v) => updateField('is_tempered', v)}
                  label="Tempered Glass"
                  disabled={neverTempered}
                />
                <Toggle
                  checked={formData.is_contractor ?? false}
                  onChange={(v) => updateField('is_contractor', v)}
                  label="Contractor Pricing (15% discount)"
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Dimensions */}
        <motion.div custom={2} initial="hidden" animate="visible" variants={cardVariants}>
          <Card>
            <CardContent>
              <h2 className="text-base font-semibold text-gray-900 mb-4">Dimensions</h2>
              <ShapeSelector value={currentShape} onChange={handleShapeChange} />
              <div className="mt-4">
                <DimensionInputs
                  isCircular={formData.is_circular ?? false}
                  widthInput={widthInput}
                  heightInput={heightInput}
                  diameterInput={diameterInput}
                  quantity={formData.quantity ?? 1}
                  onWidthChange={handleWidthChange}
                  onHeightChange={handleHeightChange}
                  onDiameterChange={handleDiameterChange}
                  onQuantityChange={(v) => updateField('quantity', v)}
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Edge Processing */}
        <motion.div custom={3} initial="hidden" animate="visible" variants={cardVariants}>
          <Card>
            <CardContent>
              <h2 className="text-base font-semibold text-gray-900 mb-4">Edge Processing</h2>
              <EdgeProcessing
                isPolished={formData.is_polished ?? false}
                isBeveled={formData.is_beveled ?? false}
                numClippedCorners={formData.num_clipped_corners ?? 0}
                clipSize={formData.clip_size ?? 'under_1'}
                noPolish={noPolish}
                isCircular={formData.is_circular ?? false}
                onPolishedChange={(v) => updateField('is_polished', v)}
                onBeveledChange={(v) => updateField('is_beveled', v)}
                onClippedCornersChange={(v) => updateField('num_clipped_corners', v)}
                onClipSizeChange={(v) => updateField('clip_size', v)}
              />
            </CardContent>
          </Card>
        </motion.div>

        {/* Add Item */}
        <motion.div custom={4} initial="hidden" animate="visible" variants={cardVariants}>
          <Card>
            <CardContent>
              <AddItemButton
                disabled={!result || !!result?.error}
                onClick={handleAddItem}
              />
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Right Column - Summary (sticky) */}
      <div className="lg:col-span-3">
        <div className="lg:sticky lg:top-20 space-y-0">
          <motion.div custom={0} initial="hidden" animate="visible" variants={cardVariants}>
            <PriceSummary result={result} config={config} hasItems={items.length > 0} />
          </motion.div>

          <QuoteItemsList
            items={items}
            currentResult={result}
            grandTotal={grandTotal}
            onRemoveItem={removeItem}
            onClearAll={clearItems}
            onSaveQuote={() => setShowSaveModal(true)}
            onExportPdf={handleExportPdfOnly}
          />
        </div>
      </div>

      <SaveQuoteModal
        open={showSaveModal}
        onClose={() => setShowSaveModal(false)}
        onSave={handleSaveQuote}
        onSaveAndExport={handleSaveAndExport}
        saving={saving}
      />
    </div>
  );
}
