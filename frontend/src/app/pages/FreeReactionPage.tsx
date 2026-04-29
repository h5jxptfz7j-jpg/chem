import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router';
import { toast } from 'sonner';
import type { Molecule } from '../services/api';
import { getElements, executeReaction } from '../services/api';
import { MoleculeCard } from '../components/MoleculeCard';
import { ReactionResult } from '../components/ReactionResult';
 
const limit = 20;
 
export function FreeReactionPage() {
  const navigate = useNavigate();
  const [elements, setElements] = useState<Molecule[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
 
  const fetchElements = useCallback(async (currentPage: number) => {
    setLoading(true);
    try {
      const response = await getElements(currentPage * limit, limit);
      const data = response.data.map(el => ({
        ...el,
        name: el.name_ru || el.symbol || '—',
        symbol: el.symbol || '',
      }));
      setElements(data);
      setHasMore(data.length === limit);
    } catch {
      toast.error('Не удалось загрузить элементы');
    } finally {
      setLoading(false);
    }
  }, []);
 
  useEffect(() => { fetchElements(0); }, []);
 
  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    setSelectedIds([]);
    fetchElements(newPage);
  };
 
  const toggleSelect = (id: number) => {
    setSelectedIds(prev => {
      if (prev.includes(id)) return prev.filter(i => i !== id);
      if (prev.length >= 2) return prev;
      return [...prev, id];
    });
  };
 
  const handleExecute = async () => {
    try {
      const response = await executeReaction(selectedIds, 'independent');
      setResult(response.data);
      if (response.data.hint) {
        toast.info(response.data.hint);
      } else if (response.data.suggestions?.length) {
        toast.info('Реакция не найдена. Посмотри подсказки в результате.');
      } else if (response.data.product_name) {
        toast.success('Реакция успешно выполнена!');
      } else {
        toast.info('Реакция не дала результата');
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
        className="flex items-center gap-1 text-emerald-700 font-semibold mb-4 hover:text-emerald-900 transition-colors"
      >
        ← Назад
      </button>
 
      <h2 className="text-2xl font-bold text-emerald-700 mb-1">Самостоятельная реакция</h2>
 
      {/* Подсказка для пользователя */}
      <p className="text-sm text-gray-500 mb-4">
        Выбери два элемента из таблицы и нажми «Запустить реакцию», чтобы узнать продукт.
      </p>
 
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
 
      {/* Пагинация */}
      <div className="flex items-center justify-center gap-3 mt-5">
        <button
          onClick={() => handlePageChange(page - 1)}
          disabled={page === 0 || loading}
          className="px-4 py-2 rounded-lg bg-gray-200 hover:bg-gray-300 disabled:opacity-40 font-semibold transition-colors"
        >
          ‹ Пред.
        </button>
        <span className="text-gray-600 text-sm font-medium">Стр. {page + 1}</span>
        <button
          onClick={() => handlePageChange(page + 1)}
          disabled={!hasMore || loading}
          className="px-4 py-2 rounded-lg bg-gray-200 hover:bg-gray-300 disabled:opacity-40 font-semibold transition-colors"
        >
          След. ›
        </button>
      </div>
 
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