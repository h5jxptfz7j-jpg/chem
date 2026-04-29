import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider, createBrowserRouter } from 'react-router'
import './index.css'
import { Layout } from './app/components/Layout'
import { HomePage } from './app/pages/HomePage'
import { FreeReactionPage } from './app/pages/FreeReactionPage'
import { CatalogPage } from './app/pages/CatalogPage'
import { ReactionTypesPage } from './app/pages/ReactionTypesPage'
import { ReactionTypePage } from './app/pages/ReactionTypePage'

const router = createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      { index: true, Component: HomePage },
      { path: "free-reaction", Component: FreeReactionPage },
      { path: "states", Component: ReactionTypesPage },            
      { path: "reaction-types", Component: ReactionTypesPage },    
      { path: "reaction-types/:type", Component: ReactionTypePage },
      { path: "catalog", Component: CatalogPage },
    ],
  },
]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
);