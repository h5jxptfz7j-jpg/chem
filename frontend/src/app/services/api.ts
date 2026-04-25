import axios from 'axios';

const getInitData = (): string => {
  if (window.Telegram?.WebApp?.initData) {
    return window.Telegram.WebApp.initData;
  }
  return 'user=12345&hash=test';
};

const api = axios.create({
  baseURL: '/api',
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

export const executeReaction = (reagents: number[], mode: string) =>
  api.post<ReactionResult>('/reactions/execute', { reagents, mode });

export const getCatalog = () =>
  api.get<CatalogItem[]>('/catalog');

export const deleteReaction = (id: number) =>
  api.delete(`/catalog/${id}`);
