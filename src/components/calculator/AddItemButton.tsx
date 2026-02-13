import { motion } from 'framer-motion';
import { Plus } from 'lucide-react';

interface AddItemButtonProps {
  disabled: boolean;
  onClick: () => void;
}

export function AddItemButton({ disabled, onClick }: AddItemButtonProps) {
  return (
    <div>
      <motion.button
        whileTap={{ scale: disabled ? 1 : 0.95 }}
        onClick={onClick}
        disabled={disabled}
        className="w-full py-3 px-4 bg-green-600 hover:bg-green-700 active:bg-green-800 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
      >
        <Plus className="w-5 h-5" />
        Add Item to Quote
      </motion.button>
      <p className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
        Add this item and continue adding more pieces
      </p>
    </div>
  );
}
