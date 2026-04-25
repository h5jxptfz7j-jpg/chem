import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider, createBrowserRouter } from 'react-router'
import './index.css'
import { Layout } from './app/components/Layout'
import { HomePage } from './app/pages/HomePage'
import { FreeReactionPage } from './app/pages/FreeReactionPage'
import { StatesPage } from './app/pages/StatesPage'
import { ReactionPage } from './app/pages/ReactionPage'
import { CatalogPage } from './app/pages/CatalogPage'

const router = createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      { index: true, Component: HomePage },
      { path: "free-reaction", Component: FreeReactionPage },
      { path: "states", Component: StatesPage },
      { path: "reaction/:state", Component: ReactionPage },
      { path: "catalog", Component: CatalogPage },
    ],
  },
]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
);