import { useNavigate } from 'react-router';
import { motion } from 'motion/react';

export function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-8 p-4">
      <h1 className="text-3xl font-bold text-emerald-800">ChemLab</h1>
      <div className="flex flex-col gap-4 w-full max-w-sm">
        <motion.button
          whileHover={{ scale: 1.05 }}
          onClick={() => navigate('/free-reaction')}
          className="bg-emerald-500 text-white py-4 px-6 rounded-2xl shadow-lg shadow-emerald-200 text-lg font-semibold"
        >
          Самостоятельная реакция
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          onClick={() => navigate('/states')}
          className="bg-lime-500 text-white py-4 px-6 rounded-2xl shadow-lg shadow-lime-200 text-lg font-semibold"
        >
          Агрегатные состояния
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          onClick={() => navigate('/catalog')}
          className="bg-teal-500 text-white py-4 px-6 rounded-2xl shadow-lg shadow-teal-200 text-lg font-semibold"
        >
          Мой каталог реакций
        </motion.button>
      </div>
    </div>
  );
}