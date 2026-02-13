import { motion } from 'framer-motion';
import { Square, Circle, Pentagon } from 'lucide-react';
import { cn } from '../../utils/cn';

type Shape = 'rectangular' | 'circular' | 'custom';

interface ShapeSelectorProps {
  value: Shape;
  onChange: (shape: Shape) => void;
}

const shapes: { id: Shape; label: string; icon: typeof Square }[] = [
  { id: 'rectangular', label: 'Rectangular', icon: Square },
  { id: 'circular', label: 'Circular', icon: Circle },
  { id: 'custom', label: 'Custom', icon: Pentagon },
];

export function ShapeSelector({ value, onChange }: ShapeSelectorProps) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">Shape</label>
      <div className="grid grid-cols-3 gap-2 relative">
        {shapes.map((shape) => {
          const Icon = shape.icon;
          const isSelected = value === shape.id;
          return (
            <button
              key={shape.id}
              type="button"
              onClick={() => onChange(shape.id)}
              className={cn(
                'relative flex flex-col items-center gap-1.5 py-3 px-2 rounded-lg text-sm font-medium transition-colors z-10',
                isSelected ? 'text-primary-700' : 'text-gray-600 hover:text-gray-800'
              )}
            >
              {isSelected && (
                <motion.div
                  layoutId="shape-pill"
                  className="absolute inset-0 bg-primary-50 border-2 border-primary-200 rounded-lg"
                  transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                />
              )}
              <Icon className="w-5 h-5 relative z-10" />
              <span className="relative z-10">{shape.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
