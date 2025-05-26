// /home/ubuntu/user-panel/pages/login.tsx
// Autor: Szymon Fuchs
// Data: 14.08.2021 (aktualizacja dla Fazy 1 - 05.08.2021)
import React, { useState } from 'react';
import { useMutation, gql } from '@apollo/client';
import { useRouter } from 'next/router';
import Link from 'next/link';
import client from '../lib/apolloClient';

const TOKEN_AUTH_MUTATION = gql`
  mutation TokenAuth($email: String!, $password: String!) {
    tokenCreate(email: $email, password: $password) {
      token
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

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const router = useRouter();
  const [tokenAuth, { loading, error }] = useMutation(TOKEN_AUTH_MUTATION, {
    client: client,
    onCompleted: (data) => {
      if (data.tokenCreate.token) {
        localStorage.setItem('saleorAuthToken', data.tokenCreate.token);
        router.push('/dashboard');
      } else {
        const apiErrors = data.tokenCreate.errors.map((e: any) => e.message).join(', ');
        alert(`Błąd logowania: ${apiErrors}`);
        console.error('Login errors:', data.tokenCreate.errors);
      }
    },
    onError: (err) => {
      alert('Wystąpił błąd sieci lub serwera. Spróbuj ponownie.');
      console.error('Network/GraphQL Error:', err);
    }
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    tokenAuth({ variables: { email, password } });
  };

  const handleFacebookLogin = () => {
    // Docelowo, to przekieruje do endpointu backendowego Saleor (np. /plugins/facebook/login/ lub podobnego),
    // który obsłuży proces OAuth2 z Facebookiem. Po pomyślnej autoryzacji,
    // backend powinien przekierować użytkownika z powrotem do user-panel,
    // np. z tokenem JWT Saleor w parametrze URL lub ustawiając ciasteczko sesyjne.
    // Na potrzeby demonstracji:
    alert("Logowanie przez Facebooka wymaga konfiguracji backendu Saleor i przepływu OAuth2.");
    // Przykład: window.location.href = `${process.env.NEXT_PUBLIC_SALEOR_API_URL}/auth/facebook`;
  };


  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 p-10 bg-white shadow-lg rounded-xl">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Zaloguj się do panelu
          </h2>
        </div>
        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          <input type="hidden" name="remember" defaultValue="true" />
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
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Adres email"
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">Hasło</label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Hasło"
              />
            </div>
          </div>

          <div className="flex items-center justify-between text-sm">
            <div className="text-sm">
              <Link href="/password-reset">
                <a className="font-medium text-indigo-600 hover:text-indigo-500">
                  Zapomniałeś hasła?
                </a>
              </Link>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? 'Logowanie...' : 'Zaloguj się'}
            </button>
          </div>
          {error && <p className="text-red-500 text-xs italic mt-2 text-center">{error.message.includes("Please, enter valid credentials") ? "Niepoprawny email lub hasło." : "Wystąpił błąd."}</p>}
        </form>
        
        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">
                Lub kontynuuj z
              </span>
            </div>
          </div>

          <div className="mt-6">
            <button
              onClick={handleFacebookLogin}
              type="button"
              className="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
            >
              <span className="sr-only">Zaloguj przez Facebook</span>
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path fillRule="evenodd" d="M20 10c0-5.523-4.477-10-10-10S0 4.477 0 10c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V10h2.54V7.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V10h2.773l-.443 2.89h-2.33v6.988C16.343 19.128 20 14.991 20 10z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>

         <div className="text-sm text-center mt-8">
            Nie masz konta?{' '}
            <Link href="/register">
              <a className="font-medium text-indigo-600 hover:text-indigo-500">
                Zarejestruj się
              </a>
            </Link>
          </div>
      </div>
    </div>
  );
};

export default LoginPage;
