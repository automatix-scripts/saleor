// /home/ubuntu/user-panel/pages/_app.tsx
// Autor: Szymon Fuchs
// Data: 14.08.2021 (aktualizacja)
import '../styles/globals.css';
import type { AppProps } from 'next/app';
import { ApolloProvider } from '@apollo/client';
import client from '../lib/apolloClient';

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <ApolloProvider client={client}>
      <Component {...pageProps} />
    </ApolloProvider>
  );
}

export default MyApp;
