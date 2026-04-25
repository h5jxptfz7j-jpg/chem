import { motion } from 'motion/react';

interface Props {
  id: number;
  name: string;
  formula?: string;
  imageUrl?: string;
  isSelected: boolean;
  onSelect: (id: number) => void;
}

export function MoleculeCard({ id, name, formula, imageUrl, isSelected, onSelect }: Props) {
  // Если formula передана, берём её заглавные буквы, иначе первую букву имени
  const placeholder = formula
    ? formula.replace(/\d/g, '').substring(0, 2)
    : name.substring(0, 2);

  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={() => onSelect(id)}
      className={`relative cursor-pointer rounded-xl border-2 p-3 flex flex-col items-center gap-1 transition-colors ${
        isSelected
          ? 'border-emerald-500 bg-emerald-50 shadow-lg shadow-emerald-200'
          : 'border-gray-200 bg-white hover:border-emerald-300'
      }`}
    >
      {isSelected && (
        <span className="absolute top-1 right-2 text-emerald-600 text-lg font-bold">✓</span>
      )}
      {imageUrl ? (
        <img src={imageUrl} alt={name} className="w-16 h-16 object-contain" />
      ) : (
        <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-800 font-bold text-lg">
          {placeholder}
        </div>
      )}
      <strong className="text-xs text-gray-800 text-center">{name}</strong>
      {formula && <span className="text-xs text-gray-500">{formula}</span>}
    </motion.div>
  );
}