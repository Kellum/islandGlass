import { Toggle } from '../ui/Toggle';
import { Select } from '../ui/Select';
import { Input } from '../ui/Input';

interface EdgeProcessingProps {
  isPolished: boolean;
  isBeveled: boolean;
  numClippedCorners: number;
  clipSize: string;
  noPolish: boolean;
  isCircular: boolean;
  onPolishedChange: (val: boolean) => void;
  onBeveledChange: (val: boolean) => void;
  onClippedCornersChange: (val: number) => void;
  onClipSizeChange: (val: string) => void;
}

export function EdgeProcessing({
  isPolished,
  isBeveled,
  numClippedCorners,
  clipSize,
  noPolish,
  isCircular,
  onPolishedChange,
  onBeveledChange,
  onClippedCornersChange,
  onClipSizeChange,
}: EdgeProcessingProps) {
  return (
    <div className="space-y-3">
      <Toggle
        checked={isPolished}
        onChange={onPolishedChange}
        label="Polished Edges"
        disabled={noPolish}
      />

      <Toggle
        checked={isBeveled}
        onChange={onBeveledChange}
        label="Beveled Edges"
        disabled={noPolish}
      />

      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Clipped Corners"
          type="number"
          value={numClippedCorners}
          onChange={(e) => onClippedCornersChange(Math.min(4, Math.max(0, Number(e.target.value))))}
          min={0}
          max={4}
          disabled={isCircular}
        />
        {numClippedCorners > 0 && (
          <Select
            label="Clip Size"
            value={clipSize}
            onChange={(e) => onClipSizeChange(e.target.value)}
            options={[
              { value: 'under_1', label: 'Under 1"' },
              { value: 'over_1', label: 'Over 1"' },
            ]}
          />
        )}
      </div>
    </div>
  );
}
