// /home/ubuntu/user-panel/pages/dashboard/domains.tsx
// Autor: Szymon Fuchs
// Data: 19.08.2021
import React, { useEffect, useState } from 'react';
import Layout from '../../components/layout/Layout';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';

interface Domain {
  id: string;
  name: string;
  status: 'active' | 'pending_verification' | 'error';
  storeId?: string;
}

const DomainsPage: React.FC = () => {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [newDomainName, setNewDomainName] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitLoading, setSubmitLoading] = useState(false);

  const fetchDomains = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(process.env.NEXT_PUBLIC_DOMAINS_API_URL!);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setDomains(data.domains || []);
    } catch (e: any) {
      setError(e.message || 'Nie udało się pobrać domen.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDomains();
  }, []);

  const handleAddDomain = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDomainName.trim()) return;
    setSubmitLoading(true);
    setError(null);
    try {
      const response = await fetch(process.env.NEXT_PUBLIC_DOMAINS_API_URL!, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: newDomainName }),
      });
      if (!response.ok) {
         const errorData = await response.json();
         throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }
      setNewDomainName('');
      fetchDomains();
    } catch (e: any) {
      setError(e.message || 'Nie udało się dodać domeny.');
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleDeleteDomain = async (domainId: string) => {
    if (!confirm("Czy na pewno chcesz usunąć tę domenę?")) return;
    setError(null);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_DOMAINS_API_URL}/${domainId}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      fetchDomains();
    } catch (e: any) {
      setError(e.message || 'Nie udało się usunąć domeny.');
    }
  }

  if (loading) return <Layout><p>Ładowanie domen...</p></Layout>;

  return (
    <Layout>
      <h1 className="text-2xl font-bold mb-6">Zarządzanie Domenami</h1>

      <form onSubmit={handleAddDomain} className="mb-8 p-4 bg-white shadow rounded-lg">
        <h2 className="text-xl font-semibold mb-3">Dodaj nową domenę</h2>
        <div className="flex space-x-2">
          <Input
            type="text"
            value={newDomainName}
            onChange={(e) => setNewDomainName(e.target.value)}
            placeholder="np. mojasklepnadomena.pl"
            className="flex-grow"
            required
          />
          <Button type="submit" variant="primary" disabled={submitLoading}>
            {submitLoading ? 'Dodawanie...' : 'Dodaj Domenę'}
          </Button>
        </div>
        {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
      </form>

      {domains.length === 0 && !error ? (
        <p>Nie masz jeszcze żadnych domen.</p>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <ul className="divide-y divide-gray-200">
            {domains.map((domain) => (
              <li key={domain.id} className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-lg font-medium text-indigo-600 truncate">{domain.name}</p>
                    <p className="text-sm text-gray-500">Status: {domain.status}</p>
                    {domain.storeId && <p className="text-sm text-gray-500">Sklep: {domain.storeId}</p>}
                  </div>
                  <Button onClick={() => handleDeleteDomain(domain.id)} variant="secondary">
                    Usuń
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </Layout>
  );
};

export default DomainsPage;
