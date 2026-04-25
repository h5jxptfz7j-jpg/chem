import { useNavigate } from 'react-router';
import { motion } from 'motion/react';

export function StatesPage() {
  const navigate = useNavigate();
  const states = [
    { key: 'gas', label: 'Газы', color: 'bg-emerald-500', hover: 'hover:bg-emerald-600' },
    { key: 'liquid', label: 'Жидкости', color: 'bg-lime-500', hover: 'hover:bg-lime-600' },
    { key: 'solid', label: 'Твёрдые', color: 'bg-teal-500', hover: 'hover:bg-teal-600' },
  ];

  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-6">
      <h2 className="text-2xl font-bold text-emerald-800">Выберите агрегатное состояние</h2>
      {states.map(s => (
        <motion.button
          key={s.key}
          whileHover={{ scale: 1.05 }}
          onClick={() => navigate(`/reaction/${s.key}`)}
          className={`${s.color} ${s.hover} text-white py-4 px-8 rounded-2xl shadow-lg w-48 text-lg font-semibold`}
        >
          {s.label}
        </motion.button>
      ))}
    </div>
  );
}