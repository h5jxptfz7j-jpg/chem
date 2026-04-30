import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';
import { motion } from 'motion/react';
import { getProfile } from '../services/api';

export function HomePage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<any>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await getProfile();
        setProfile(response.data);
      } catch (error) {
        console.error('Не удалось загрузить профиль', error);
      }
    };
    fetchProfile();
  }, []);

  return (
    <div className="relative flex flex-col items-center justify-between min-h-screen p-6 overflow-hidden bg-gradient-to-b from-gray-900 via-purple-900 to-gray-900">
      {/* Декоративный фон */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-10 left-5 w-40 h-40 bg-emerald-500 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-5 w-60 h-60 bg-purple-500 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/3 w-32 h-32 bg-blue-400 rounded-full blur-3xl" />
      </div>

      {/* Верхняя часть — аватар */}
      {profile && (
        <div className="relative z-10 flex flex-col items-center gap-2 mt-8">
          {profile.photo_url ? (
            <img src={profile.photo_url} alt="avatar" className="w-16 h-16 rounded-full border-2 border-emerald-400 shadow-lg" />
          ) : (
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-emerald-400 to-purple-500 flex items-center justify-center text-white font-bold text-xl shadow-lg">
              {profile.display_name?.charAt(0).toUpperCase() || 'U'}
            </div>
          )}
          <span className="text-white/80 text-sm font-medium">{profile.display_name || 'Пользователь'}</span>
        </div>
      )}

      {/* Пустое пространство по центру */}
      <div className="flex-1" />

      {/* Нижняя часть — кнопки */}
      <div className="relative z-10 flex flex-col items-center gap-6 mb-8 w-full max-w-sm">
        <motion.h1 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl font-bold text-white tracking-wider"
        >
          ChemLab
        </motion.h1>

        <div className="flex flex-col gap-4 w-full">
          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => navigate('/free-reaction')}
            className="bg-gradient-to-r from-emerald-500 to-teal-500 text-white py-4 px-6 rounded-2xl shadow-lg shadow-emerald-500/25 text-base font-semibold flex items-center justify-center gap-3"
          >
            <img src="/icons/flask-conical.svg" className="w-6 h-6 brightness-0 invert" />
            Самостоятельная реакция
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => navigate('/states')}
            className="bg-gradient-to-r from-lime-500 to-green-500 text-white py-4 px-6 rounded-2xl shadow-lg shadow-lime-500/25 text-base font-semibold flex items-center justify-center gap-3"
          >
            <img src="/icons/layers.svg" className="w-6 h-6 brightness-0 invert" />
            Агрегатные состояния
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => navigate('/catalog')}
            className="bg-gradient-to-r from-teal-500 to-cyan-500 text-white py-4 px-6 rounded-2xl shadow-lg shadow-teal-500/25 text-base font-semibold flex items-center justify-center gap-3"
          >
            <img src="/icons/book-open.svg" className="w-6 h-6 brightness-0 invert" />
            Мой каталог реакций
          </motion.button>
        </div>
      </div>
    </div>
  );
}
