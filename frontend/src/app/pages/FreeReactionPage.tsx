import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router';
import { toast } from 'sonner';
import type { Molecule } from '../services/api';
import { getElements, executeReaction } from '../services/api';
import { MoleculeCard } from '../components/MoleculeCard';
import { ReactionResult } from '../components/ReactionResult';

export function FreeReactionPage() {
  const navigate = useNavigate();
  const [elements, setElements] = useState<Molecule[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchElements = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getElements(0, 50);
      const data = response.data.map(el => ({
        ...el,
        name: el.name_ru || el.symbol || '—',
        symbol: el.symbol || '',
      }));
      setElements(data);
    } catch {
      toast.error('Не удалось загрузить элементы');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchElements();
  }, [fetchElements]);

  const toggleSelect = (id: number) => {
    setSelectedIds(prev => {
      if (prev.includes(id)) return prev.filter(i => i !== id);
      if (prev.length >= 2) return prev;
      return [...prev, id];
    });
  };

  const handleExecute = async () => {
    try {
      const response = await executeReaction(
        selectedIds.map(id => ({ id })),
        'independent'
      );
      setResult(response.data);
      if (response.data.hint) {
        toast.info(response.data.hint);
      } else if (response.data.suggestions?.length) {
        toast.info('Реакция не найдена. Посмотри подсказки в результате.');
      } else {
        toast.success('Реакция успешно выполнена!');
      }
    } catch {
      toast.error('Ошибка при выполнении реакции');
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      {/* Кнопка назад */}
      <button
        onClick={() => navigate('/')}
        className="flex items-center gap-1 text-emerald-600 hover:text-emerald-800 text-sm mb-4"
      >
        <img src="/icons/arrow-left.svg" className="w-5 h-5" />
        На главную
      </button>

      <h2 className="text-2xl font-bold text-emerald-700 mb-1">Самостоятельная реакция</h2>
      <p className="text-sm text-gray-500 mb-4">
        Выбери два элемента из таблицы и нажми «Запустить реакцию», чтобы узнать продукт.
      </p>

      {loading ? (
        <div className="text-center py-10 text-gray-500">Загрузка элементов...</div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-2 justify-items-center">
          {elements.map(el => (
            <MoleculeCard
              key={el.id}
              id={el.id}
              name={el.name}
              symbol={el.symbol}
              isSelected={selectedIds.includes(el.id)}
              onSelect={toggleSelect}
            />
          ))}
        </div>
      )}

      <div className="mt-5 flex items-center justify-between">
        <span className="text-gray-600 text-sm">Выбрано: {selectedIds.length}/2</span>
        <button
          disabled={selectedIds.length !== 2}
          onClick={handleExecute}
          className="bg-emerald-600 text-white py-2 px-6 rounded-xl disabled:opacity-50 hover:bg-emerald-700 shadow-lg shadow-emerald-200 font-semibold transition-colors"
        >
          Запустить реакцию
        </button>
      </div>

      {result && <ReactionResult result={result} onClose={() => setResult(null)} />}
    </div>
  );
}
