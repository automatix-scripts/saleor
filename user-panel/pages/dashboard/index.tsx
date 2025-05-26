// /home/ubuntu/user-panel/pages/dashboard/index.tsx
// Autor: Szymon Fuchs
// Data: 17.08.2021
import React from 'react';
import Layout from '../../components/layout/Layout';

const DashboardPage: React.FC = () => {
  return (
    <Layout>
      <h1 className="text-3xl font-bold">Witaj w Panelu Użytkownika!</h1>
      <p className="mt-4">Wybierz opcję z menu, aby rozpocząć.</p>
    </Layout>
  );
};

export default DashboardPage;
