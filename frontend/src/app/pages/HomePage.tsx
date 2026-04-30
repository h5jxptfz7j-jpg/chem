import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';
import { motion } from 'motion/react';
import { getProfile } from '../services/api';

export function HomePage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<any>(null);
  const [error, setError] = useState<string>('');
  const [initDataPreview, setInitDataPreview] = useState<string>('');

  useEffect(() => {
    // Показываем первые 150 символов initData прямо на экране
    const raw = window.Telegram?.WebApp?.initData || '';
    setInitDataPreview(raw ? raw.substring(0, 150) : 'НЕТ ДАННЫХ (initData пустой)');

    const fetchProfile = async () => {
      try {
        const response = await getProfile();
        setProfile(response.data);
      } catch (err: any) {
        const msg =
          err?.response?.data?.detail ||
          err?.response?.status ||
          err?.message ||
          'Неизвестная ошибка';
        setError(String(msg));
      }
    };
    fetchProfile();
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4 p-4">

      {/* ── DEBUG БЛОК (удали после проверки) ── */}
      <div className="w-full max-w-sm bg-gray-100 rounded-xl p-3 text-xs text-gray-700 break-all space-y-1">
        <p className="font-bold text-gray-500">DEBUG</p>
        <p><span className="font-semibold">initData:</span> {initDataPreview}</p>
        {error && <p className="text-red-600"><span className="font-semibold">Ошибка профиля:</span> {error}</p>}
        {profile && <p className="text-green-600"><span className="font-semibold">Профиль:</span> {JSON.stringify(profile)}</p>}
      </div>
      {/* ── КОНЕЦ DEBUG БЛОКА ── */}

      {/* Профиль пользователя */}
      {profile && (
        <div className="flex items-center gap-3 mb-4">
          {profile.photo_url ? (
            <img src={profile.photo_url} alt="avatar" className="w-12 h-12 rounded-full border-2 border-emerald-400" />
          ) : (
            <div className="w-12 h-12 rounded-full bg-emerald-500 flex items-center justify-center text-white font-bold">
              {profile.display_name?.charAt(0).toUpperCase() || 'U'}
            </div>
          )}
          <span className="text-lg font-semibold text-emerald-800">{profile.display_name}</span>
        </div>
      )}

      <h1 className="text-3xl font-bold text-emerald-800">ChemLab</h1>

      <div className="flex flex-col gap-4 w-full max-w-sm">
        <motion.button
          whileHover={{ scale: 1.05 }}
          onClick={() => navigate('/free-reaction')}
          className="bg-emerald-500 text-white py-4 px-6 rounded-2xl shadow-lg shadow-emerald-200 text-lg font-semibold flex items-center justify-center gap-3"
        >
          <img src="/icons/flask-conical.svg" className="w-7 h-7 brightness-0 invert" />
          Самостоятельная реакция
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.05 }}
          onClick={() => navigate('/states')}
          className="bg-lime-500 text-white py-4 px-6 rounded-2xl shadow-lg shadow-lime-200 text-lg font-semibold flex items-center justify-center gap-3"
        >
          <img src="/icons/layers.svg" className="w-7 h-7 brightness-0 invert" />
          Агрегатные состояния
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.05 }}
          onClick={() => navigate('/catalog')}
          className="bg-teal-500 text-white py-4 px-6 rounded-2xl shadow-lg shadow-teal-200 text-lg font-semibold flex items-center justify-center gap-3"
        >
          <img src="/icons/book-open.svg" className="w-7 h-7 brightness-0 invert" />
          Мой каталог реакций
        </motion.button>
      </div>
    </div>
  );
}
