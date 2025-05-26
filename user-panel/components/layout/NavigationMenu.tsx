// /home/ubuntu/user-panel/components/layout/NavigationMenu.tsx
// Autor: Szymon Fuchs
// Data: 17.08.2021
import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

const menuItems = [
  { href: '/dashboard', label: 'Panel Główny' },
  { href: '/dashboard/subscriptions', label: 'Moje Subskrypcje' },
  { href: '/dashboard/domains', label: 'Moje Domeny' },
  { href: '/dashboard/templates', label: 'Szablony Graficzne' },
  { href: '/dashboard/allegro', label: 'Integracja Allegro' },
  { href: '/dashboard/profile', label: 'Ustawienia Profilu' },
];

const NavigationMenu: React.FC = () => {
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem('saleorAuthToken');
    router.push('/login');
  };

  return (
    <nav className="bg-gray-800 text-white w-64 min-h-screen p-4 space-y-2 flex flex-col">
      <div>
        <h2 className="text-xl font-semibold mb-4 text-center">UserPanel</h2>
        {menuItems.map((item) => (
          <Link key={item.href} href={item.href} passHref>
            <a
              className={`block py-2.5 px-4 rounded transition duration-200 hover:bg-gray-700 hover:text-white ${
                router.pathname === item.href ? 'bg-gray-900 text-white' : 'text-gray-300'
              }`}
            >
              {item.label}
            </a>
          </Link>
        ))}
      </div>
      <button
        onClick={handleLogout}
        className="w-full mt-auto py-2 px-4 rounded bg-red-600 hover:bg-red-700 text-white text-left transition duration-200"
      >
        Wyloguj
      </button>
    </nav>
  );
};

export default NavigationMenu;
