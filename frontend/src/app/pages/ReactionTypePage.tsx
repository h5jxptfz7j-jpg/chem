import { useParams, useNavigate } from 'react-router';
import { useEffect, useState, useCallback } from 'react';
import { toast } from 'sonner';
import { getMolecules, executeReaction, type Molecule } from '../services/api';
import { ReactionResult } from '../components/ReactionResult';

interface ReactionTypeConfig {
  leftState: string;
  rightState: string;
  leftLabel: string;
  rightLabel: string;
}

const typeConfig: Record<string, ReactionTypeConfig> = {
  'gas-liquid': { leftState: 'gas', rightState: 'liquid', leftLabel: 'Газы', rightLabel: 'Жидкости' },
  'liquid-solid': { leftState: 'liquid', rightState: 'solid', leftLabel: 'Жидкости', rightLabel: 'Твёрдые вещества' },
  'solution-solution': { leftState: 'liquid', rightState: 'liquid', leftLabel: 'Первый раствор', rightLabel: 'Второй раствор' },
  'metal-acid': { leftState: 'solid', rightState: 'liquid', leftLabel: 'Металлы', rightLabel: 'Кислоты' },
};

// === Списки разрешённых названий для режима Металл + Кислота ===
const pureMetals = ['Железо', 'Медь', 'Цинк', 'Алюминий', 'Натрий', 'Калий'];
const pureAcids = [
  'Серная кислота',
  'Азотная кислота',
  'Соляная кислота',
  'Уксусная кислота',
  'Ортофосфорная кислота',
  'Пропионовая кислота',
];

const limit = 20;

export function ReactionTypePage() {
  const { type } = useParams<{ type: string }>();
  const navigate = useNavigate();
  const config = type ? typeConfig[type] : null;

  const [leftMolecules, setLeftMolecules] = useState<Molecule[]>([]);
  const [rightMolecules, setRightMolecules] = useState<Molecule[]>([]);
  const [selectedLeft, setSelectedLeft] = useState<number | null>(null);
  const [selectedRight, setSelectedRight] = useState<number | null>(null);
  const [result, setResult] = useState<any>(null);
  const [loadingLeft, setLoadingLeft] = useState(false);
  const [loadingRight, setLoadingRight] = useState(false);
  const [leftPage, setLeftPage] = useState(0);
  const [rightPage, setRightPage] = useState(0);
  const [leftHasMore, setLeftHasMore] = useState(true);
  const [rightHasMore, setRightHasMore] = useState(true);

  const fetchLeft = useCallback(async (page: number) => {
    if (!config) return;
    setLoadingLeft(true);
    try {
      const resp = await getMolecules(config.leftState, page * limit, limit);
      let data = resp.data.map(m => ({
        ...m,
        symbol: m.formula?.replace(/\d/g, '') || m.name.substring(0, 2),
      }));
      if (type === 'metal-acid' && config.leftState === 'solid') {
        data = data.filter(m => pureMetals.includes(m.name));
      }
      if (page === 0) setLeftMolecules(data);
      else setLeftMolecules(prev => [...prev, ...data]);
      setLeftHasMore(data.length === limit);
    } catch { toast.error('Не удалось загрузить ' + config.leftLabel); }
    finally { setLoadingLeft(false); }
  }, [config, type]);

  const fetchRight = useCallback(async (page: number) => {
    if (!config) return;
    setLoadingRight(true);
    try {
      const resp = await getMolecules(config.rightState, page * limit, limit);
      let data = resp.data.map(m => ({
        ...m,
        symbol: m.formula?.replace(/\d/g, '') || m.name.substring(0, 2),
      }));
      if (type === 'metal-acid' && config.rightState === 'liquid') {
        data = data.filter(m => pureAcids.includes(m.name));
      }
      if (page === 0) setRightMolecules(data);
      else setRightMolecules(prev => [...prev, ...data]);
      setRightHasMore(data.length === limit);
    } catch { toast.error('Не удалось загрузить ' + config.rightLabel); }
    finally { setLoadingRight(false); }
  }, [config, type]);

  useEffect(() => {
    if (!config) return;
    setSelectedLeft(null);
    setSelectedRight(null);
    setResult(null);
    setLeftPage(0);
    setRightPage(0);
    fetchLeft(0);
    fetchRight(0);
  }, [type, fetchLeft, fetchRight, config]);

  const handleLeftSelect = (id: number) => setSelectedLeft(prev => prev === id ? null : id);
  const handleRightSelect = (id: number) => setSelectedRight(prev => prev === id ? null : id);

  const canExecute = selectedLeft && selectedRight;

  const handleExecute = async () => {
    if (!canExecute || !config) return;
    const reagents = [
        { id: selectedLeft!, state: config.leftState },
        { id: selectedRight!, state: config.rightState },
    ];
    try {
      const response = await executeReaction(reagents, 'aggregate');
      setResult(response.data);
      if (response.data.hint) toast.info(response.data.hint);
      else toast.success('Реакция успешно выполнена!');
    } catch { toast.error('Ошибка при выполнении реакции'); }
  };

  if (!config) return <div className="p-4 text-red-500">Неизвестный тип реакции</div>;

  return (
    <div className="max-w-4xl mx-auto p-4 flex flex-col min-h-screen">
      <button onClick={() => navigate('/reaction-types')} className="flex items-center gap-1 text-emerald-600 hover:text-emerald-800 text-sm mb-4">
        <img src="/icons/arrow-left.svg" className="w-5 h-5" />
        Назад
      </button>
      <h2 className="text-2xl font-bold text-emerald-700 mb-1">{config.leftLabel} + {config.rightLabel}</h2>
      <p className="text-sm text-gray-500 mb-4">Выберите по одному веществу из каждого списка</p>

      <div className="flex flex-col md:flex-row gap-4 flex-1">
        <div className="flex-1">
          <h3 className="font-semibold text-emerald-600 mb-2">{config.leftLabel}</h3>
          <div className="grid grid-cols-2 gap-2 max-h-[60vh] overflow-y-auto">
            {leftMolecules.map(m => (
              <div
                key={m.id}
                onClick={() => handleLeftSelect(m.id)}
                className={`p-2 rounded-lg border text-center cursor-pointer text-sm ${selectedLeft === m.id ? 'border-emerald-500 bg-emerald-50' : 'border-gray-200 hover:border-emerald-300'}`}
              >
                <span className="font-medium">{m.name}</span><br />
                <span className="text-xs text-gray-500">{m.formula}</span>
              </div>
            ))}
          </div>
          {leftHasMore && (
            <button onClick={() => { setLeftPage(p => p+1); fetchLeft(leftPage+1); }} disabled={loadingLeft}
              className="mt-2 text-sm text-emerald-600 hover:text-emerald-800">Загрузить ещё</button>
          )}
        </div>

        <div className="flex-1">
          <h3 className="font-semibold text-emerald-600 mb-2">{config.rightLabel}</h3>
          <div className="grid grid-cols-2 gap-2 max-h-[60vh] overflow-y-auto">
            {rightMolecules.map(m => (
              <div
                key={m.id}
                onClick={() => handleRightSelect(m.id)}
                className={`p-2 rounded-lg border text-center cursor-pointer text-sm ${selectedRight === m.id ? 'border-emerald-500 bg-emerald-50' : 'border-gray-200 hover:border-emerald-300'}`}
              >
                <span className="font-medium">{m.name}</span><br />
                <span className="text-xs text-gray-500">{m.formula}</span>
              </div>
            ))}
          </div>
          {rightHasMore && (
            <button onClick={() => { setRightPage(p => p+1); fetchRight(rightPage+1); }} disabled={loadingRight}
              className="mt-2 text-sm text-emerald-600 hover:text-emerald-800">Загрузить ещё</button>
          )}
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <span className="text-gray-600 text-sm">
          Выбрано: {selectedLeft ? '1' : '0'} / {selectedRight ? '1' : '0'}
        </span>
        <button
          disabled={!canExecute}
          onClick={handleExecute}
          className="bg-emerald-600 text-white py-2 px-6 rounded-xl disabled:opacity-50 hover:bg-emerald-700 shadow-lg shadow-emerald-200 font-semibold"
        >
          Запустить реакцию
        </button>
      </div>

      {result && <ReactionResult result={result} onClose={() => setResult(null)} />}
    </div>
  );
}
