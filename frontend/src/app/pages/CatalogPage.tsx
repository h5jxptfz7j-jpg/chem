import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import type { CatalogItem } from '../services/api';
import { getCatalog, deleteReaction } from '../services/api';
import { useNavigate } from 'react-router';

export function CatalogPage() {
  const navigate = useNavigate(); // <-- эта строка отсутствовала, из-за неё была ошибка
  const [items, setItems] = useState<CatalogItem[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchCatalog = async () => {
    setLoading(true);
    try {
      const response = await getCatalog();
      setItems(response.data);
    } catch {
      toast.error('Ошибка загрузки каталога');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchCatalog(); }, []);

  const handleDelete = async (id: number) => {
    try {
      await deleteReaction(id);
      setItems(prev => prev.filter(item => item.id !== id));
      toast.success('Запись удалена');
    } catch {
      toast.error('Не удалось удалить');
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <button
        onClick={() => navigate('/')}
        className="flex items-center gap-1 text-emerald-600 hover:text-emerald-800 text-sm mb-4"
      >
        <img src="/icons/arrow-left.svg" className="w-5 h-5" />
        На главную
      </button>

      <h2 className="text-2xl font-bold text-emerald-700">Мой каталог реакций</h2>
      {loading ? (
        <p className="mt-4 text-gray-500">Загрузка...</p>
      ) : items.length === 0 ? (
        <p className="mt-4 text-gray-500">Нет сохранённых реакций</p>
      ) : (
        <div className="mt-4 space-y-4">
          {items.map(item => (
            <div key={item.id} className="bg-white rounded-xl p-4 shadow-md border border-emerald-200">
              <div className="flex items-center gap-4">
                {item.product_image_url && (
                  <img src={item.product_image_url} alt={item.product_name} className="w-12 h-12 object-contain" />
                )}
                <div className="flex-1">
                  <p className="font-semibold">{item.reactant1} + {item.reactant2} → {item.product_formula}</p>
                  <p className="text-sm text-gray-500">{item.product_name}</p>
                  <p className="text-xs text-gray-400">
                    {new Date(item.date_added).toLocaleString()} &bull; {item.mode === 'independent' ? 'Самостоятельная' : 'Агрегатная'}
                  </p>
                </div>
                <button onClick={() => handleDelete(item.id)} className="text-red-500 hover:text-red-700" title="Удалить">
                  <img src="/icons/trash.svg" className="w-5 h-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}