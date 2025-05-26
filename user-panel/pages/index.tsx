// /home/ubuntu/user-panel/pages/index.tsx
// Autor: Szymon Fuchs
// Data: 03.08.2021
import { useEffect } from 'react';
import { useRouter } from 'next/router';

const HomePage = () => {
  const router = useRouter();

  useEffect(() => {
    router.replace('/login');
  }, [router]);

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <p>Przekierowywanie...</p>
    </div>
  );
};

export default HomePage;
