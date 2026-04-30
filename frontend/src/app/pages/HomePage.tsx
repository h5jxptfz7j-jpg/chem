import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';
import { motion } from 'motion/react';
import { getProfile } from '../services/api';

export function HomePage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<any>(null);
  const [profileLoading, setProfileLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await getProfile();
        setProfile(response.data);
      } catch (error) {
        console.error('Не удалось загрузить профиль', error);
      } finally {
        setProfileLoading(false);
      }
    };
    fetchProfile();
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-4 p-4">

      {/* Профиль пользователя */}
      <div className="flex items-center gap-3 mb-2 h-14">
        {profileLoading ? (
          // Скелетон пока грузится
          <div className="flex items-center gap-3 animate-pulse">
            <div className="w-12 h-12 rounded-full bg-emerald-200" />
            <div className="w-28 h-5 rounded-lg bg-emerald-100" />
          </div>
        ) : profile ? (
          <>
            {profile.photo_url ? (
              <img
                src={profile.photo_url}
                alt="avatar"
                className="w-15 h-15 rounded-full border-2 border-emerald-400 object-cover"
              />
            ) : (
              <div className="w-15 h-15 rounded-full bg-emerald-500 flex items-center justify-center text-white font-bold text-lg">
                {profile.display_name?.charAt(0).toUpperCase() || 'U'}
              </div>
            )}
            <span className="text-lg font-semibold text-emerald-800">
              {profile.display_name}
            </span>
          </>
        ) : null}
      </div>

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
