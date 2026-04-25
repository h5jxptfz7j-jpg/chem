import { motion } from 'motion/react';

interface Props {
  id: number;
  name: string;
  symbol?: string;
  isSelected: boolean;
  onSelect: (id: number) => void;
}

export function MoleculeCard({ id, name, symbol, isSelected, onSelect }: Props) {
  const display = symbol || name.substring(0, 2);

  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={() => onSelect(id)}
      className={`relative cursor-pointer rounded-xl border-2 p-3 flex flex-col items-center justify-between w-24 h-28 transition-colors ${
        isSelected
          ? 'border-emerald-500 bg-emerald-50 shadow-lg shadow-emerald-200'
          : 'border-gray-200 bg-white hover:border-emerald-300'
      }`}
    >
      {isSelected && (
        <span className="absolute top-1 right-2 text-emerald-600 text-lg font-bold">✓</span>
      )}
      <div className="w-14 h-14 bg-emerald-500 rounded-full flex items-center justify-center text-white font-bold text-xl shadow-md">
        {display}
      </div>
      <strong className="text-xs text-gray-800 text-center leading-tight mt-1">
        {name}
      </strong>
    </motion.div>
  );
}
