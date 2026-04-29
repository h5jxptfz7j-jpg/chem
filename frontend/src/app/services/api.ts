import axios from 'axios';
let savedInitData = '';

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData?: string;
      };
    };
  }
}

export function initTelegramData() {
  if (window.Telegram?.WebApp?.initData) {
    savedInitData = window.Telegram.WebApp.initData;
  }
}

const api = axios.create({
  baseURL: 'https://chem-tgxe.onrender.com/api',  // ← прямой URL бэкенда
});

api.interceptors.request.use((config) => {
  if (savedInitData) {
    config.headers['Authorization'] = `Bearer ${savedInitData}`;
  }
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

export const executeReaction = (reagents: number[], mode: string, state?: string) => {
  return api.post<ReactionResult>('/reactions/execute', { reagents, mode, state });
};

export const getCatalog = () => api.get<CatalogItem[]>('/catalog');

export const deleteReaction = (id: number) => api.delete(`/catalog/${id}`);

export const getProfile = () => api.get('/profile');
