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
        <h2 className="text-lg font-bold text-emerald-700 mb-4">
          {result.product_name ? 'Результат реакции' : 'Подсказка'}
        </h2>

        {result.product_name && (
          <>
            {result.product_image_url && (
              <img src={result.product_image_url} alt={result.product_name} className="w-48 h-48 max-w-xs mx-auto my-4 object-contain" />
            )}
            <p><strong>Название:</strong> {result.product_name}</p>
            <p><strong>Формула:</strong> {result.product_formula}</p>
            <p><strong>CID:</strong> {result.cid ?? '—'}</p>
            <p><strong>Ключ:</strong> {result.reaction_key ?? '—'}</p>
          </>
        )}

        {result.suggestions && result.suggestions.length > 0 && (
          <div className="mt-3">
            <p className="font-medium text-emerald-800">С этим элементом лучше всего сочетаются:</p>
            <div className="flex flex-wrap gap-2 mt-2">
              {result.suggestions.map((el, idx) => (
                <span key={idx} className="bg-emerald-100 text-emerald-800 px-2 py-1 rounded-full text-xs">
                  {el.symbol} – {el.name_ru}
                </span>
              ))}
            </div>
          </div>
        )}

        {result.hint && !result.suggestions && (
          <p className="text-blue-600 mt-2">{result.hint}</p>
        )}

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