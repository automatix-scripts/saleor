// /home/ubuntu/user-panel/pages/dashboard/profile.tsx
// Autor: Szymon Fuchs
// Data: 21.08.2021
import React, { useState, useEffect } from 'react';
import Layout from '../../components/layout/Layout';
import { useQuery, useMutation, gql } from '@apollo/client';
import client from '../../lib/apolloClient';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';

const ME_QUERY = gql`
  query Me {
    me {
      id
      email
      firstName
      lastName
      metadata {
        key
        value
      }
      defaultShippingAddress {
        companyName
        streetAddress1
        streetAddress2
        city
        postalCode
        country { code }
        phone
      }
    }
  }
`;

const USER_UPDATE_MUTATION = gql`
  mutation AccountUpdate($input: AccountInput!) {
    accountUpdate(input: $input) {
      user {
        id
        firstName
        lastName
        email
      }
      errors {
        field
        message
      }
    }
  }
`;

const PASSWORD_CHANGE_MUTATION = gql`
    mutation PasswordChange($oldPassword: String!, $newPassword: String!) {
        passwordChange(oldPassword: $oldPassword, newPassword1: $newPassword, newPassword2: $newPassword) {
            user {
                id
            }
            errors {
                field
                message
            }
        }
    }
`;

const ADDRESS_UPDATE_MUTATION = gql`
    mutation AccountAddressUpdate($addressId: ID!, $input: AddressInput!) {
        accountAddressUpdate(id: $addressId, input: $input) {
            address {
                id
                companyName
            }
            errors {
                field
                message
            }
        }
    }
`;

interface ProfileFormState {
  firstName: string;
  lastName: string;
  companyName: string;
  companyStreet: string;
  companyCity: string;
  companyZip: string;
  companyPhone: string;
}

interface PasswordFormState {
    oldPassword: string;
    newPassword: string;
    confirmNewPassword: string;
}

const ProfilePage: React.FC = () => {
  const { data, loading, error: queryError, refetch } = useQuery(ME_QUERY, { client, fetchPolicy: "cache-and-network" });
  const [updateAccount, { loading: updatingAccount, error: updateAccError }] = useMutation(USER_UPDATE_MUTATION, { client });
  const [changePassword, { loading: changingPassword, error: changePassError }] = useMutation(PASSWORD_CHANGE_MUTATION, { client });


  const [profileForm, setProfileForm] = useState<ProfileFormState>({
    firstName: '', lastName: '', companyName: '', companyStreet: '', companyCity: '', companyZip: '', companyPhone: ''
  });
  const [passwordForm, setPasswordForm] = useState<PasswordFormState>({ oldPassword: '', newPassword: '', confirmNewPassword: '' });
  const [activeTab, setActiveTab] = useState<'personal' | 'company' | 'password' | 'avatar'>('personal');
  const [feedback, setFeedback] = useState<{type: 'success' | 'error', message: string} | null>(null);


  useEffect(() => {
    if (data?.me) {
      setProfileForm({
        firstName: data.me.firstName || '',
        lastName: data.me.lastName || '',
        companyName: data.me.defaultShippingAddress?.companyName || '',
        companyStreet: data.me.defaultShippingAddress?.streetAddress1 || '',
        companyCity: data.me.defaultShippingAddress?.city || '',
        companyZip: data.me.defaultShippingAddress?.postalCode || '',
        companyPhone: data.me.defaultShippingAddress?.phone || '',
      });
    }
  }, [data]);

  const handleProfileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setProfileForm(prev => ({ ...prev, [name]: value }));
  };

  const handlePasswordInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setPasswordForm(prev => ({ ...prev, [name]: value }));
  };

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedback(null);
    try {
      const { data: updateData } = await updateAccount({
        variables: {
          input: {
            firstName: profileForm.firstName,
            lastName: profileForm.lastName,
          }
        }
      });
      if (updateData?.accountUpdate?.errors?.length) {
        throw new Error(updateData.accountUpdate.errors.map((err: any) => err.message).join(', '));
      }

      if (data?.me?.defaultShippingAddress?.id) {
        console.log("TODO: Update company address data for address ID:", data.me.defaultShippingAddress.id);
      }

      setFeedback({type: 'success', message: 'Dane profilu zaktualizowane!'});
      refetch();
    } catch (err: any) {
      setFeedback({type: 'error', message: `Błąd: ${err.message}`});
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedback(null);
    if (passwordForm.newPassword !== passwordForm.confirmNewPassword) {
      setFeedback({type: 'error', message: 'Nowe hasła nie są zgodne.'});
      return;
    }
    try {
      const { data: passData } = await changePassword({
        variables: {
          oldPassword: passwordForm.oldPassword,
          newPassword: passwordForm.newPassword,
        }
      });
      if (passData?.passwordChange?.errors?.length) {
        throw new Error(passData.passwordChange.errors.map((err: any) => err.message).join(', '));
      }
      setFeedback({type: 'success', message: 'Hasło zostało zmienione.'});
      setPasswordForm({ oldPassword: '', newPassword: '', confirmNewPassword: '' });
    } catch (err: any) {
      setFeedback({type: 'error', message: `Błąd zmiany hasła: ${err.message}`});
    }
  };

  if (loading) return <Layout><p>Ładowanie danych profilu...</p></Layout>;
  if (queryError) return <Layout><p className="text-red-500">Błąd ładowania danych: {queryError.message}</p></Layout>;


  return (
    <Layout>
      <h1 className="text-2xl font-bold mb-6">Ustawienia Profilu</h1>

      {feedback && (
        <div className={`p-3 mb-4 rounded ${feedback.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
          {feedback.message}
        </div>
      )}

      <div className="mb-6 border-b border-gray-200">
          <nav className="-mb-px flex space-x-8" aria-label="Tabs">
              <button onClick={() => setActiveTab('personal')} className={`${activeTab === 'personal' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}>Dane Osobowe</button>
              <button onClick={() => setActiveTab('company')} className={`${activeTab === 'company' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}>Dane Firmowe</button>
              <button onClick={() => setActiveTab('password')} className={`${activeTab === 'password' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}>Zmiana Hasła</button>
          </nav>
      </div>

      {activeTab === 'personal' && (
        <form onSubmit={handleProfileSubmit} className="space-y-4 p-6 bg-white shadow rounded-lg">
          <h2 className="text-xl font-semibold">Dane Osobowe</h2>
          <div>
            <label htmlFor="firstName" className="block text-sm font-medium text-gray-700">Imię</label>
            <Input type="text" name="firstName" id="firstName" value={profileForm.firstName} onChange={handleProfileInputChange} className="mt-1 block w-full" />
          </div>
          <div>
            <label htmlFor="lastName" className="block text-sm font-medium text-gray-700">Nazwisko</label>
            <Input type="text" name="lastName" id="lastName" value={profileForm.lastName} onChange={handleProfileInputChange} className="mt-1 block w-full" />
          </div>
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email (login)</label>
            <Input type="email" name="email" id="email" value={data?.me?.email || ''} readOnly disabled className="mt-1 block w-full bg-gray-100" />
            <p className="text-xs text-gray-500 mt-1">Zmiana adresu e-mail (loginu) może wymagać kontaktu z administratorem.</p>
          </div>
          <Button type="submit" variant="primary" disabled={updatingAccount}>
            {updatingAccount ? 'Zapisywanie...' : 'Zapisz zmiany osobowe'}
          </Button>
          {updateAccError && <p className="text-red-500 text-sm">{updateAccError.message}</p>}
        </form>
      )}

      {activeTab === 'company' && (
        <form onSubmit={handleProfileSubmit} className="space-y-4 p-6 bg-white shadow rounded-lg">
             <h2 className="text-xl font-semibold">Dane Firmowe (Adres Dostawy/Faktury)</h2>
             <p className="text-sm text-gray-600">Te dane mogą być używane jako domyślny adres rozliczeniowy lub do wysyłki.</p>
            <div>
                <label htmlFor="companyName" className="block text-sm font-medium text-gray-700">Nazwa Firmy</label>
                <Input type="text" name="companyName" id="companyName" value={profileForm.companyName} onChange={handleProfileInputChange} className="mt-1 block w-full" />
            </div>
            <div>
                <label htmlFor="companyStreet" className="block text-sm font-medium text-gray-700">Ulica i numer</label>
                <Input type="text" name="companyStreet" id="companyStreet" value={profileForm.companyStreet} onChange={handleProfileInputChange} className="mt-1 block w-full" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label htmlFor="companyCity" className="block text-sm font-medium text-gray-700">Miejscowość</label>
                    <Input type="text" name="companyCity" id="companyCity" value={profileForm.companyCity} onChange={handleProfileInputChange} className="mt-1 block w-full" />
                </div>
                <div>
                    <label htmlFor="companyZip" className="block text-sm font-medium text-gray-700">Kod pocztowy</label>
                    <Input type="text" name="companyZip" id="companyZip" value={profileForm.companyZip} onChange={handleProfileInputChange} className="mt-1 block w-full" />
                </div>
            </div>
             <div>
                <label htmlFor="companyPhone" className="block text-sm font-medium text-gray-700">Telefon Firmowy</label>
                <Input type="text" name="companyPhone" id="companyPhone" value={profileForm.companyPhone} onChange={handleProfileInputChange} className="mt-1 block w-full" />
            </div>
            <Button type="submit" variant="primary" disabled={updatingAccount}>
                {updatingAccount ? 'Zapisywanie...' : 'Zapisz zmiany firmowe'}
            </Button>
            {updateAccError && <p className="text-red-500 text-sm">{updateAccError.message}</p>}
        </form>
      )}

      {activeTab === 'password' && (
        <form onSubmit={handlePasswordSubmit} className="space-y-4 p-6 bg-white shadow rounded-lg">
          <h2 className="text-xl font-semibold">Zmiana Hasła</h2>
          <div>
            <label htmlFor="oldPassword"className="block text-sm font-medium text-gray-700">Stare Hasło</label>
            <Input type="password" name="oldPassword" id="oldPassword" value={passwordForm.oldPassword} onChange={handlePasswordInputChange} className="mt-1 block w-full" required />
          </div>
          <div>
            <label htmlFor="newPassword"className="block text-sm font-medium text-gray-700">Nowe Hasło</label>
            <Input type="password" name="newPassword" id="newPassword" value={passwordForm.newPassword} onChange={handlePasswordInputChange} className="mt-1 block w-full" required />
          </div>
          <div>
            <label htmlFor="confirmNewPassword"className="block text-sm font-medium text-gray-700">Potwierdź Nowe Hasło</label>
            <Input type="password" name="confirmNewPassword" id="confirmNewPassword" value={passwordForm.confirmNewPassword} onChange={handlePasswordInputChange} className="mt-1 block w-full" required />
          </div>
          <Button type="submit" variant="primary" disabled={changingPassword}>
            {changingPassword ? 'Zmienianie...' : 'Zmień Hasło'}
          </Button>
          {changePassError && <p className="text-red-500 text-sm">{changePassError.message}</p>}
        </form>
      )}
    </Layout>
  );
};

export default ProfilePage;
