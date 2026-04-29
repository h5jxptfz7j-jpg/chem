import axios from 'axios';

export {};

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData?: string;
      };
    };
  }
}

const getInitData = (): string => {
  if (window.Telegram?.WebApp?.initData) {
    return window.Telegram.WebApp.initData;
  }
  return 'user=12345&hash=test';
};

const api = axios.create({
  baseURL: 'https://chem-tgxe.onrender.com',
});

api.interceptors.request.use((config) => {
  config.headers['Authorization'] = `Bearer ${getInitData()}`;
  return config;
});

export interface Molecule {
  id: number;
  name: string;
  formula?: string;
  image_url?: string;
  symbol?: string;
  name_ru?: string;
}

export interface ReactionResult {
  product_name: string;
  product_formula: string;
  product_image_url?: string;
  cid?: number;
  reaction_key?: string;
  hint?: string;
  suggestions?: Array<{ symbol: string; name_ru: string }>;
  reaction_date: string;
}

export interface CatalogItem {
  id: number;
  reactant1: string;
  reactant2: string;
  product_name: string;
  product_formula: string;
  product_image_url?: string;
  date_added: string;
  mode: string;
}

export const getMolecules = (state: string, skip: number = 0, limit: number = 20) =>
  api.get<Molecule[]>(`/molecules?state=${state}&skip=${skip}&limit=${limit}`);

export const getElements = (skip: number = 0, limit: number = 50) =>
  api.get<Molecule[]>(`/elements?skip=${skip}&limit=${limit}`);

export function executeReaction(
  reagents: number[],
  mode: string,
  state?: string
): Promise<any>; // сигнатура для обратной совместимости
export function executeReaction(
  reagents: { id: number; state?: string }[],
  mode: string,
  state?: string
): Promise<any>;
export function executeReaction(
  reagents: number[] | { id: number; state?: string }[],
  mode: string,
  state?: string
) {
  // нормализуем: если передан массив чисел, превращаем в объекты
  const normalized = reagents.map((r) =>
    typeof r === 'number' ? { id: r } : r
  );
  return api.post<ReactionResult>('/reactions/execute', {
    reagents: normalized,
    mode,
    state,
  });
}

export const getCatalog = () =>
  api.get<CatalogItem[]>('/catalog');

export const deleteReaction = (id: number) =>
  api.delete(`/catalog/${id}`);

export const getProfile = () =>
  api.get('/profile');
