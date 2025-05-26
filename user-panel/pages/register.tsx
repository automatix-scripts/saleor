// /home/ubuntu/user-panel/pages/register.tsx
// Autor: Szymon Fuchs
// Data: 05.08.2021
import React, { useState } from 'react';
import { useMutation, gql } from '@apollo/client';
import { useRouter } from 'next/router';
import Link from 'next/link';
import client from '../lib/apolloClient';

const ACCOUNT_REGISTER_MUTATION = gql`
  mutation AccountRegister($input: AccountRegisterInput!) {
    accountRegister(input: $input) {
      requiresConfirmation
      errors {
        field
        message
      }
      user {
        id
        email
      }
    }
  }
`;

const RegisterPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [message, setMessage] = useState('');
  const router = useRouter();

  const [accountRegister, { loading, error }] = useMutation(ACCOUNT_REGISTER_MUTATION, {
    client: client,
    onCompleted: (data) => {
      if (data.accountRegister.errors && data.accountRegister.errors.length > 0) {
        setMessage(`Błąd rejestracji: ${data.accountRegister.errors.map((e: any) => e.message).join(', ')}`);
      } else if (data.accountRegister.user) {
        if (data.accountRegister.requiresConfirmation) {
          setMessage('Rejestracja udana! Sprawdź email, aby potwierdzić konto.');
          setTimeout(() => router.push('/login'), 3000);
        } else {
          setMessage('Rejestracja udana! Możesz się teraz zalogować.');
          setTimeout(() => router.push('/login'), 3000);
        }
      }
    },
    onError: (err) => {
      setMessage('Wystąpił błąd serwera. Spróbuj ponownie.');
      console.error('Registration error:', err);
    }
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('');
    // W Saleor 2.x redirectUrl był często używany do potwierdzenia email
    // Ustaw go na stronę w user-panel, która poinformuje o sukcesie potwierdzenia
    const redirectUrl = typeof window !== 'undefined' ? `${window.location.origin}/account-confirmed` : '';
    accountRegister({
      variables: {
        input: {
          email,
          password,
          firstName,
          lastName,
          redirectUrl: redirectUrl, 
          // Możesz dodać 'channel: "default-channel"' jeśli jest wymagane przez Twoją konfigurację Saleor
        }
      }
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 p-10 bg-white shadow-lg rounded-xl">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Utwórz nowe konto
          </h2>
        </div>
        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <input name="firstName" type="text" required value={firstName} onChange={(e) => setFirstName(e.target.value)} className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm" placeholder="Imię" />
            </div>
            <div>
              <input name="lastName" type="text" required value={lastName} onChange={(e) => setLastName(e.target.value)} className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm" placeholder="Nazwisko" />
            </div>
            <div>
              <input name="email" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm" placeholder="Adres email" />
            </div>
            <div>
              <input id="password" name="password" type="password" autoComplete="new-password" required value={password} onChange={(e) => setPassword(e.target.value)} className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm" placeholder="Hasło" />
            </div>
          </div>
          <div>
            <button type="submit" disabled={loading} className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50">
              {loading ? 'Rejestrowanie...' : 'Zarejestruj się'}
            </button>
          </div>
          {message && <p className={`text-sm mt-2 text-center ${error || message.includes('Błąd') ? 'text-red-500' : 'text-green-500'}`}>{message}</p>}
        </form>
        <div className="text-sm text-center mt-8">
          Masz już konto?{' '}
          <Link href="/login">
            <a className="font-medium text-indigo-600 hover:text-indigo-500">
              Zaloguj się
            </a>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
