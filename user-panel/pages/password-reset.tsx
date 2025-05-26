// /home/ubuntu/user-panel/pages/password-reset.tsx
// Autor: Szymon Fuchs
// Data: 06.08.2021
import React, { useState } from 'react';
import { useMutation, gql } from '@apollo/client';
import Link from 'next/link';
import client from '../lib/apolloClient';

const REQUEST_PASSWORD_RESET_MUTATION = gql`
  mutation RequestPasswordReset($email: String!, $redirectUrl: String!) {
    requestPasswordReset(email: $email, redirectUrl: $redirectUrl) {
      errors {
        field
        message
      }
    }
  }
`;

const PasswordResetPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');

  const [requestPasswordReset, { loading }] = useMutation(REQUEST_PASSWORD_RESET_MUTATION, {
    client: client,
    onCompleted: (data) => {
      if (data.requestPasswordReset.errors && data.requestPasswordReset.errors.length > 0) {
        setMessage(`Błąd: ${data.requestPasswordReset.errors.map((e:any) => e.message).join(', ')}`);
      } else {
        setMessage('Jeśli konto o podanym adresie email istnieje, wysłaliśmy instrukcję resetowania hasła.');
      }
    },
    onError: (err) => {
      setMessage('Wystąpił błąd serwera. Spróbuj ponownie.');
      console.error('Password reset request error:', err);
    }
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('');
    // Ważne: redirectUrl musi wskazywać na stronę w Twoim user-panel, która obsłuży token
    // np. http://twojadomena.pl/password-reset/confirm/
    // Saleor dołączy token do tego URL-a
    const redirectUrl = typeof window !== 'undefined' ? `${window.location.origin}/password-reset/confirm` : '';
    requestPasswordReset({ variables: { email, redirectUrl } });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 p-10 bg-white shadow-lg rounded-xl">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Zresetuj hasło
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Podaj adres e-mail powiązany z Twoim kontem, a wyślemy Ci link do zresetowania hasła.
          </p>
        </div>
        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email-address" className="sr-only">Adres email</label>
              <input
                id="email-address"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Adres email"
              />
            </div>
          </div>
          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? 'Wysyłanie...' : 'Wyślij link do resetowania'}
            </button>
          </div>
          {message && <p className={`text-sm mt-4 text-center ${message.includes('Błąd') ? 'text-red-500' : 'text-gray-700'}`}>{message}</p>}
        </form>
        <div className="text-sm text-center mt-8">
          <Link href="/login">
            <a className="font-medium text-indigo-600 hover:text-indigo-500">
              Wróć do logowania
            </a>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default PasswordResetPage;
