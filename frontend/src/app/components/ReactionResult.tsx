import { motion } from 'motion/react';
import type { ReactionResult as ResultType } from '../services/api';

interface Props {
  result: ResultType;
  onClose: () => void;
}

export function ReactionResult({ result, onClose }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={onClose}
    >
      <motion.div
        onClick={(e) => e.stopPropagation()}
        className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-2xl border-2 border-emerald-400"
      >
        <h2 className="text-lg font-bold text-emerald-700">Результат реакции</h2>
        {result.product_image_url && (
          <img src={result.product_image_url} alt={result.product_name} className="w-32 h-32 mx-auto my-4" />
        )}
        <p><strong>Название:</strong> {result.product_name}</p>
        <p><strong>Формула:</strong> {result.product_formula}</p>
        <p><strong>CID:</strong> {result.cid ?? '—'}</p>
        <p><strong>Ключ:</strong> {result.reaction_key ?? '—'}</p>
        {result.hint && <p className="text-blue-600 mt-2">{result.hint}</p>}
        <button
          onClick={onClose}
          className="mt-4 w-full bg-emerald-500 text-white py-2 rounded-lg hover:bg-emerald-600"
        >
          Закрыть
        </button>
      </motion.div>
    </motion.div>
  );
}