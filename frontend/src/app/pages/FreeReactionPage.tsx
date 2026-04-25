import { useEffect, useState, useCallback } from 'react';
import { toast } from 'sonner';
import type { Molecule } from '../services/api';
import { getElements, executeReaction } from '../services/api';
import { MoleculeCard } from '../components/MoleculeCard';
import { ReactionResult } from '../components/ReactionResult';

export function FreeReactionPage() {
  const [elements, setElements] = useState<Molecule[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const limit = 20;

  const fetchElements = useCallback(async (reset = false) => {
    setLoading(true);
    try {
      const response = await getElements(reset ? 0 : skip, limit);
      // Преобразуем: name = name_ru, symbol = symbol
      const data = response.data.map(el => ({
        ...el,
        name: el.name_ru || el.symbol || '—',
        symbol: el.symbol || '',
      }));
      if (reset) {
        setElements(data);
        setSkip(data.length);
      } else {
        setElements(prev => [...prev, ...data]);
        setSkip(prev => prev + data.length);
      }
      if (data.length < limit) setHasMore(false);
    } catch (err) {
      toast.error('Не удалось загрузить элементы');
    } finally {
      setLoading(false);
    }
  }, [skip]);

  useEffect(() => { fetchElements(true); }, []);

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
      } else {
        toast.success('Реакция успешно выполнена!');
      }
    } catch (err) {
      toast.error('Ошибка при выполнении реакции');
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h2 className="text-2xl font-bold text-emerald-700">Самостоятельная реакция</h2>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-4 justify-items-center">
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
      {hasMore && (
        <button onClick={() => fetchElements(false)} disabled={loading}
          className="mt-4 w-full bg-gray-200 py-2 rounded-lg hover:bg-gray-300 disabled:opacity-50">Загрузить ещё</button>
      )}
      <div className="mt-4 flex items-center justify-between">
        <span>Выбрано: {selectedIds.length}/2</span>
        <button
          disabled={selectedIds.length !== 2}
          onClick={handleExecute}
          className="bg-emerald-600 text-white py-2 px-6 rounded-xl disabled:opacity-50 hover:bg-emerald-700 shadow-lg shadow-emerald-200"
        >
          Запустить реакцию
        </button>
      </div>
      {result && <ReactionResult result={result} onClose={() => setResult(null)} />}
    </div>
  );
}