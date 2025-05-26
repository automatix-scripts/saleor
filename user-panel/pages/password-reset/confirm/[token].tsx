// /home/ubuntu/user-panel/pages/password-reset/confirm/[token].tsx
// Autor: Szymon Fuchs
// Data: 06.08.2021
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useMutation, gql } from '@apollo/client';
import Link from 'next/link';
import client from '../../../lib/apolloClient';

const SET_PASSWORD_MUTATION = gql`
  mutation SetPassword($email: String!, $token: String!, $newPassword: String!) {
    setPassword(email: $email, token: $token, newPassword: $newPassword) {
      user {
        id
      }
      errors {
        field
        message
      }
      accountErrors { # Saleor 2.x używał accountErrors zamiast errors dla setPassword
        field
        message
        code
      }
    }
  }
`;

const ConfirmPasswordResetPage: React.FC = () => {
  const router = useRouter();
  const { token, email } = router.query; // Email może być przekazany jako parametr URL przez Saleor

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [userEmail, setUserEmail] = useState(''); // Stan na email, jeśli nie ma w URL
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (email && typeof email === 'string') {
      setUserEmail(email);
    }
  }, [email]);

  const [setPassword, { loading }] = useMutation(SET_PASSWORD_MUTATION, {
    client: client,
    onCompleted: (data) => {
      const errors = data.setPassword.errors || data.setPassword.accountErrors;
      if (errors && errors.length > 0) {
        setMessage(`Błąd: ${errors.map((e:any) => e.message).join(', ')}`);
      } else if (data.setPassword.user) {
        setMessage('Hasło zostało pomyślnie zmienione! Możesz się teraz zalogować.');
        setTimeout(() => router.push('/login'), 3000);
      } else {
        setMessage('Nie udało się zmienić hasła. Token może być nieprawidłowy lub wygasł.');
      }
    },
    onError: (err) => {
      setMessage('Wystąpił błąd serwera. Spróbuj ponownie.');
      console.error('Set password error:', err);
    }
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('');
    if (newPassword !== confirmPassword) {
      setMessage('Hasła nie są zgodne.');
      return;
    }
    if (!token || typeof token !== 'string' || !userEmail) {
      setMessage('Brak tokenu lub adresu email. Spróbuj ponownie poprosić o reset hasła.');
      return;
    }
    setPassword({ variables: { email: userEmail, token, newPassword } });
  };

  if (!token) {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <div className="max-w-md w-full text-center p-6 bg-white shadow-md rounded-lg">
                <p className="text-red-500">Nieprawidłowy link do resetowania hasła.</p>
                <Link href="/password-reset">
                    <a className="font-medium text-indigo-600 hover:text-indigo-500">Poproś o nowy link</a>
                </Link>
            </div>
        </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 p-10 bg-white shadow-lg rounded-xl">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Ustaw nowe hasło
          </h2>
        </div>
        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
           {!email && ( // Jeśli email nie jest w URL, poproś użytkownika o jego podanie
            <div className="rounded-md shadow-sm">
                 <label htmlFor="user-email" className="block text-sm font-medium text-gray-700 mb-1">Adres email powiązany z resetem</label>
                <input
                    id="user-email"
                    name="userEmail"
                    type="email"
                    required
                    value={userEmail}
                    onChange={(e) => setUserEmail(e.target.value)}
                    className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="Twój adres email"
                />
            </div>
           )}
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="new-password" className="sr-only">Nowe hasło</label>
              <input
                id="new-password"
                name="newPassword"
                type="password"
                required
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Nowe hasło"
              />
            </div>
            <div>
              <label htmlFor="confirm-password" className="sr-only">Potwierdź nowe hasło</label>
              <input
                id="confirm-password"
                name="confirmPassword"
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Potwierdź nowe hasło"
              />
            </div>
          </div>
          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? 'Ustawianie...' : 'Ustaw nowe hasło'}
            </button>
          </div>
          {message && <p className={`text-sm mt-4 text-center ${message.includes('Błąd') || message.includes('Nie udało') ? 'text-red-500' : 'text-green-500'}`}>{message}</p>}
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

export default ConfirmPasswordResetPage;
