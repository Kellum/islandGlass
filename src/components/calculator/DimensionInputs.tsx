import { Input } from '../ui/Input';

interface DimensionInputsProps {
  isCircular: boolean;
  widthInput: string;
  heightInput: string;
  diameterInput: string;
  quantity: number;
  onWidthChange: (val: string) => void;
  onHeightChange: (val: string) => void;
  onDiameterChange: (val: string) => void;
  onQuantityChange: (val: number) => void;
}

export function DimensionInputs({
  isCircular,
  widthInput,
  heightInput,
  diameterInput,
  quantity,
  onWidthChange,
  onHeightChange,
  onDiameterChange,
  onQuantityChange,
}: DimensionInputsProps) {
  return (
    <div className="space-y-4">
      {isCircular ? (
        <Input
          label="Diameter (inches)"
          value={diameterInput}
          onChange={(e) => onDiameterChange(e.target.value)}
          placeholder='e.g., 24, 24 1/2, 3/4'
          hint="Enter as fraction (e.g., 24 1/2) or decimal"
        />
      ) : (
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Width (inches)"
            value={widthInput}
            onChange={(e) => onWidthChange(e.target.value)}
            placeholder='e.g., 24'
            hint="Fractions OK (24 1/2)"
          />
          <Input
            label="Height (inches)"
            value={heightInput}
            onChange={(e) => onHeightChange(e.target.value)}
            placeholder='e.g., 36'
            hint="Fractions OK (36 3/4)"
          />
        </div>
      )}

      <Input
        label="Quantity"
        type="number"
        value={quantity}
        onChange={(e) => onQuantityChange(Math.max(1, Number(e.target.value)))}
        min={1}
      />
    </div>
  );
}
