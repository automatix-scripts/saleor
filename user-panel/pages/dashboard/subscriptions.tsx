// /home/ubuntu/user-panel/pages/dashboard/subscriptions.tsx
// Autor: Szymon Fuchs
// Data: 18.08.2021
import React, { useEffect, useState } from 'react';
import Layout from '../../components/layout/Layout';

interface Subscription {
  id: string;
  planName: string;
  status: 'active' | 'canceled' | 'pending';
  endDate: string;
}

const SubscriptionsPage: React.FC = () => {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSubscriptions = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(process.env.NEXT_PUBLIC_SUBSCRIPTIONS_API_URL!, {
          headers: {
          }
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setSubscriptions(data.subscriptions || []);
      } catch (e: any) {
        console.error("Failed to fetch subscriptions:", e);
        setError(e.message || 'Nie udało się pobrać subskrypcji.');
      } finally {
        setLoading(false);
      }
    };

    fetchSubscriptions();
  }, []);

  const handleChangePlan = (subscriptionId: string) => {
    alert(`TODO: Zmień plan dla subskrypcji ${subscriptionId}`);
  };

  const handleCancelSubscription = (subscriptionId: string) => {
    alert(`TODO: Anuluj subskrypcję ${subscriptionId}`);
  };


  if (loading) return <Layout><p>Ładowanie subskrypcji...</p></Layout>;
  if (error) return <Layout><p className="text-red-500">Błąd: {error}</p></Layout>;

  return (
    <Layout>
      <h1 className="text-2xl font-bold mb-6">Zarządzanie Subskrypcjami</h1>
      {subscriptions.length === 0 ? (
        <p>Nie masz aktywnych subskrypcji.</p>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <ul className="divide-y divide-gray-200">
            {subscriptions.map((sub) => (
              <li key={sub.id} className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-lg font-medium text-indigo-600 truncate">{sub.planName}</p>
                    <p className="text-sm text-gray-500">Status: <span className={`font-semibold ${sub.status === 'active' ? 'text-green-600' : 'text-red-600'}`}>{sub.status}</span></p>
                    <p className="text-sm text-gray-500">Ważna do: {new Date(sub.endDate).toLocaleDateString()}</p>
                  </div>
                  <div className="ml-2 flex-shrink-0 flex space-x-2">
                    <button
                      onClick={() => handleChangePlan(sub.id)}
                      className="px-3 py-1 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      Zmień Plan
                    </button>
                    {sub.status === 'active' && (
                       <button
                       onClick={() => handleCancelSubscription(sub.id)}
                       className="px-3 py-1 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                     >
                       Anuluj
                     </button>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </Layout>
  );
};

export default SubscriptionsPage;
