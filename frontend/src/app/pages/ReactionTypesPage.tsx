import { useNavigate } from 'react-router';
import { motion } from 'motion/react';

const reactionTypes = [
  { key: 'gas-liquid', title: 'Газ + Жидкость', desc: 'Растворение газов в жидкостях' },
  { key: 'liquid-solid', title: 'Жидкость + Твёрдое', desc: 'Растворение твёрдых веществ' },
  { key: 'solution-solution', title: 'Раствор + Раствор', desc: 'Реакции между растворами' },
  { key: 'metal-acid', title: 'Металл + Кислота', desc: 'Взаимодействие металлов с кислотами' },
];

export function ReactionTypesPage() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center min-h-screen p-4">
      <div className="w-full max-w-sm mb-4">
        <button onClick={() => navigate('/')}
          className="flex items-center gap-1 text-emerald-600 hover:text-emerald-800 text-sm"
        >
          <img src="/icons/arrow-left.svg" className="w-5 h-5" />
          На главную
        </button>
      </div>

      <div className="flex flex-col items-center justify-center flex-1 gap-6">
        <h2 className="text-2xl font-bold text-emerald-800">Типы взаимодействий</h2>
        <p className="text-sm text-gray-500 mb-4">Выберите тип химической реакции</p>
        <div className="flex flex-col gap-4 w-full max-w-sm">
          {reactionTypes.map(t => (
            <motion.button
              key={t.key}
              whileHover={{ scale: 1.05 }}
              onClick={() => navigate(`/reaction-types/${t.key}`)}
              className="bg-white border-2 border-emerald-300 hover:border-emerald-500 text-emerald-800 py-4 px-6 rounded-2xl shadow-md hover:shadow-lg flex flex-col items-start gap-1 transition-colors"
            >
              <span className="font-semibold text-lg">{t.title}</span>
              <span className="text-xs text-gray-500">{t.desc}</span>
            </motion.button>
          ))}
        </div>
      </div>
    </div>
  );
}