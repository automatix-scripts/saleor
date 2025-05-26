// /home/ubuntu/user-panel/pages/dashboard/allegro.tsx
// Autor: Szymon Fuchs
// Data: 19.08.2021
import React, { useState, useEffect } from 'react';
import Layout from '../../components/layout/Layout';
import Button from '../../components/ui/Button';

const ALLEGRO_AUTH_START_URL = `${process.env.NEXT_PUBLIC_ALLEGRO_API_URL}/auth/allegro`;
const ALLEGRO_CHECK_STATUS_URL = `${process.env.NEXT_PUBLIC_ALLEGRO_API_URL}/allegro/status`;
const ALLEGRO_DISCONNECT_URL = `${process.env.NEXT_PUBLIC_ALLEGRO_API_URL}/allegro/disconnect`;


const AllegroIntegrationPage: React.FC = () => {
  const [isAllegroConnected, setIsAllegroConnected] = useState(false);
  const [allegroUsername, setAllegroUsername] = useState<string | null>(null);
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checkAllegroStatus = async () => {
    setLoadingStatus(true);
    setError(null);
    try {
      const response = await fetch(ALLEGRO_CHECK_STATUS_URL!, {
         headers: {
         }
      });
      if (!response.ok) {
        if (response.status === 404 || response.status === 401) {
             setIsAllegroConnected(false);
             setAllegroUsername(null);
             return;
        }
        throw new Error(`Błąd serwera: ${response.status}`);
      }
      const data = await response.json();
      setIsAllegroConnected(data.isConnected);
      setAllegroUsername(data.username || null);
    } catch (err: any) {
      console.error("Błąd sprawdzania statusu Allegro:", err);
      setError("Nie udało się sprawdzić statusu połączenia z Allegro.");
      setIsAllegroConnected(false);
    } finally {
      setLoadingStatus(false);
    }
  };

  useEffect(() => {
    checkAllegroStatus();

    const urlParams = new URLSearchParams(window.location.search);
    const oauthStatus = urlParams.get('allegro_oauth_status');
    if (oauthStatus === 'success') {
        alert('Pomyślnie połączono z Allegro!');
        window.history.replaceState({}, document.title, window.location.pathname);
        checkAllegroStatus();
    } else if (oauthStatus === 'error') {
        const errorMessage = urlParams.get('message') || 'Nieznany błąd.';
        setError(`Błąd podczas łączenia z Allegro: ${decodeURIComponent(errorMessage)}`);
        window.history.replaceState({}, document.title, window.location.pathname);
    }

  }, []);

  const handleConnectAllegro = () => {
    window.location.href = ALLEGRO_AUTH_START_URL!;
  };

  const handleDisconnectAllegro = async () => {
    if (!confirm("Czy na pewno chcesz rozłączyć konto Allegro?")) return;
    setError(null);
    try {
        const response = await fetch(ALLEGRO_DISCONNECT_URL!, {
            method: 'POST',
        });
        if (!response.ok) throw new Error('Nie udało się rozłączyć konta.');
        setIsAllegroConnected(false);
        setAllegroUsername(null);
        alert('Pomyślnie rozłączono konto Allegro.');
    } catch (err: any) {
        console.error("Błąd rozłączania Allegro:", err);
        setError(err.message || "Wystąpił błąd podczas rozłączania.");
    }
  };

  if (loadingStatus) {
    return <Layout><p>Sprawdzanie statusu połączenia z Allegro...</p></Layout>;
  }

  return (
    <Layout>
      <h1 className="text-2xl font-bold mb-6">Integracja z Allegro</h1>
      {error && <p className="text-red-500 bg-red-100 p-3 rounded-md mb-4">{error}</p>}
      {isAllegroConnected ? (
        <div className="p-6 bg-white shadow rounded-lg">
          <p className="text-lg text-green-600 font-semibold">
            Twoje konto Allegro jest połączone!
            {allegroUsername && ` (Użytkownik: ${allegroUsername})`}
          </p>
          <p className="mt-2 text-gray-600">Możesz teraz zarządzać swoimi aukcjami i zamówieniami przez nasz system (funkcjonalność do zaimplementowania).</p>
          <Button onClick={handleDisconnectAllegro} variant="secondary" className="mt-4">
            Rozłącz konto Allegro
          </Button>
        </div>
      ) : (
        <div className="p-6 bg-white shadow rounded-lg">
          <p className="text-lg text-gray-700">Połącz swoje konto Allegro, aby zintegrować sprzedaż.</p>
          <Button onClick={handleConnectAllegro} variant="primary" className="mt-4">
            Połącz z Allegro
          </Button>
          <p className="text-sm text-gray-500 mt-3">
            Zostaniesz przekierowany na stronę Allegro w celu autoryzacji.
          </p>
        </div>
      )}
    </Layout>
  );
};

export default AllegroIntegrationPage;
