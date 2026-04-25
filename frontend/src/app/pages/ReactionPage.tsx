import { useParams } from 'react-router';
import { useEffect, useState, useCallback } from 'react';
import { toast } from 'sonner';
import type { Molecule } from '../services/api';
import { getMolecules, executeReaction } from '../services/api';
import { MoleculeCard } from '../components/MoleculeCard';
import { ReactionResult } from '../components/ReactionResult';

export function ReactionPage() {
  const { state } = useParams<{ state: string }>();
  const [molecules, setMolecules] = useState<Molecule[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const limit = 20;

  const fetchMolecules = useCallback(async (reset = false) => {
    if (!state) return;
    setLoading(true);
    try {
      const response = await getMolecules(state, reset ? 0 : skip, limit);
      const data = response.data.map(m => ({
        ...m,
        symbol: m.formula?.replace(/\d/g, '') || m.name.substring(0, 2), // для кружка
        name: m.name,
      }));
      if (reset) {
        setMolecules(data);
        setSkip(data.length);
      } else {
        setMolecules(prev => [...prev, ...data]);
        setSkip(prev => prev + data.length);
      }
      if (data.length < limit) setHasMore(false);
    } catch {
      toast.error('Не удалось загрузить молекулы');
    } finally {
      setLoading(false);
    }
  }, [state, skip]);

  useEffect(() => {
    setSelectedIds([]);
    setResult(null);
    setSkip(0);
    fetchMolecules(true);
  }, [state]);

  const toggleSelect = (id: number) => {
    setSelectedIds(prev => {
      if (prev.includes(id)) return prev.filter(i => i !== id);
      if (prev.length >= 3) return prev;
      return [...prev, id];
    });
  };

  const handleExecute = async () => {
    try {
      const response = await executeReaction(selectedIds, 'aggregate');
      setResult(response.data);
      toast.success('Реакция успешно выполнена!');
    } catch (err) {
      toast.error('Ошибка при выполнении реакции');
    }
  };

  const labels: Record<string, string> = { gas: 'Газы', liquid: 'Жидкости', solid: 'Твёрдые вещества' };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h2 className="text-2xl font-bold text-emerald-700">{labels[state ?? 'gas']}</h2>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-4 justify-items-center">
        {molecules.map(mol => (
          <MoleculeCard
            key={mol.id}
            id={mol.id}
            name={mol.name}
            symbol={mol.symbol}
            isSelected={selectedIds.includes(mol.id)}
            onSelect={toggleSelect}
          />
        ))}
      </div>
      {hasMore && (
        <button onClick={() => fetchMolecules(false)} disabled={loading}
          className="mt-4 w-full bg-gray-200 py-2 rounded-lg hover:bg-gray-300">Загрузить ещё</button>
      )}
      <div className="mt-4 flex items-center justify-between">
        <span>Выбрано: {selectedIds.length}/3</span>
        <button
          disabled={selectedIds.length < 2}
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