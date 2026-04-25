import { Outlet } from 'react-router';
import { Toaster } from 'sonner';

export function Layout() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-lime-50 text-gray-900">
      <Outlet />
      <Toaster position="top-center" />
    </div>
  );
}