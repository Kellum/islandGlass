import { useState, useMemo } from 'react';
import { GlassPriceCalculator } from '../services/calculator';
import type { CalculatorConfig, QuoteParams, QuoteResult } from '../services/calculator';
import { fractionToDecimal } from '../utils/fractions';

const DEFAULT_FORM: QuoteParams = {
  width: 0,
  height: 0,
  thickness: '1/4"',
  glass_type: 'clear',
  quantity: 1,
  is_polished: false,
  is_beveled: false,
  num_clipped_corners: 0,
  clip_size: 'under_1',
  is_tempered: false,
  is_non_rectangular: false,
  is_circular: false,
  is_contractor: false,
};

export function useCalculator(config: CalculatorConfig | null) {
  const [formData, setFormData] = useState<QuoteParams>(DEFAULT_FORM);
  const [widthInput, setWidthInput] = useState('');
  const [heightInput, setHeightInput] = useState('');
  const [diameterInput, setDiameterInput] = useState('');

  const result: QuoteResult | null = useMemo(() => {
    if (!config) return null;

    const hasValidDimensions = formData.is_circular
      ? formData.diameter && formData.diameter > 0
      : formData.width && formData.width > 0 && formData.height && formData.height > 0;

    if (!hasValidDimensions) return null;

    const calculator = new GlassPriceCalculator(config);
    return calculator.calculateQuote(formData);
  }, [config, formData]);

  const updateField = <K extends keyof QuoteParams>(field: K, value: QuoteParams[K]) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleWidthChange = (input: string) => {
    setWidthInput(input);
    setFormData((prev) => ({ ...prev, width: fractionToDecimal(input) }));
  };

  const handleHeightChange = (input: string) => {
    setHeightInput(input);
    setFormData((prev) => ({ ...prev, height: fractionToDecimal(input) }));
  };

  const handleDiameterChange = (input: string) => {
    setDiameterInput(input);
    setFormData((prev) => ({ ...prev, diameter: fractionToDecimal(input) }));
  };

  const resetForm = (keepContractor: boolean = true) => {
    setWidthInput('');
    setHeightInput('');
    setDiameterInput('');
    setFormData({
      ...DEFAULT_FORM,
      is_contractor: keepContractor ? formData.is_contractor : false,
    });
  };

  return {
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
  };
}
