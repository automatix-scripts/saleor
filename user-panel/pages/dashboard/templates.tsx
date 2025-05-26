// /home/ubuntu/user-panel/pages/dashboard/templates.tsx
// Autor: Szymon Fuchs
// Data: 19.08.2021
import React, { useEffect, useState } from 'react';
import Layout from '../../components/layout/Layout';
import { useMutation, gql, useQuery } from '@apollo/client';
import client from '../../lib/apolloClient';

interface Template {
  id: string;
  name: string;
  thumbnailUrl: string;
  description: string;
}

const GET_CURRENT_CHANNEL = gql`
  query GetCurrentChannel {
    shop {
      defaultChannel {
         id
         metadata {
            key
            value
         }
      }
    }
  }
`;

const UPDATE_CHANNEL_METADATA = gql`
  mutation UpdateChannelMetadata($channelId: ID!, $input: [MetadataInput!]!) {
    updateChannelMetadata(id: $channelId, input: $input) {
      item {
        id
        metadata {
          key
          value
        }
      }
      errors {
        field
        message
      }
    }
  }
`;


const TemplatesPage: React.FC = () => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loadingTemplates, setLoadingTemplates] = useState(true);
  const [errorTemplates, setErrorTemplates] = useState<string | null>(null);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null);

  const { data: channelData, loading: loadingChannel } = useQuery(GET_CURRENT_CHANNEL, {
      client,
      onCompleted: (data) => {
          const currentTemplateMeta = data?.shop?.defaultChannel?.metadata.find((meta: any) => meta.key === 'selectedTemplateId');
          if (currentTemplateMeta) {
              setSelectedTemplateId(currentTemplateMeta.value);
          }
      }
  });
  const channelId = channelData?.shop?.defaultChannel?.id;

  const [updateChannelMetadata, { loading: updatingMetadata }] = useMutation(UPDATE_CHANNEL_METADATA, { client });

  useEffect(() => {
    const fetchTemplates = async () => {
      setLoadingTemplates(true);
      setErrorTemplates(null);
      try {
        const mockData: Template[] = [
          { id: 'template1', name: 'Szablon Klasyczny', thumbnailUrl: 'https://via.placeholder.com/150/FF0000/FFFFFF?Text=Szablon1', description: 'Elegancki i prosty szablon.' },
          { id: 'template2', name: 'Szablon Nowoczesny', thumbnailUrl: 'https://via.placeholder.com/150/00FF00/FFFFFF?Text=Szablon2', description: 'Dynamiczny i świeży wygląd.' },
          { id: 'template3', name: 'Szablon Minimalistyczny', thumbnailUrl: 'https://via.placeholder.com/150/0000FF/FFFFFF?Text=Szablon3', description: 'Czystość i funkcjonalność.' },
        ];
        setTemplates(mockData);

      } catch (e: any) {
        setErrorTemplates(e.message || 'Nie udało się pobrać szablonów.');
      } finally {
        setLoadingTemplates(false);
      }
    };
    fetchTemplates();
  }, []);

  const handleSelectTemplate = async (templateId: string) => {
    if (!channelId) {
        alert("Nie można zidentyfikować kanału sprzedaży.");
        return;
    }
    try {
        const { data } = await updateChannelMetadata({
            variables: {
                channelId: channelId,
                input: [{ key: 'selectedTemplateId', value: templateId }]
            }
        });
        if (data?.updateChannelMetadata?.errors?.length) {
            throw new Error(data.updateChannelMetadata.errors.map((e: any) => e.message).join(', '));
        }
        setSelectedTemplateId(templateId);
        alert('Szablon został pomyślnie przypisany!');
    } catch (error: any) {
        console.error("Błąd przy przypisywaniu szablonu:", error);
        alert(`Nie udało się przypisać szablonu: ${error.message}`);
    }
  };


  if (loadingTemplates || loadingChannel) return <Layout><p>Ładowanie szablonów...</p></Layout>;
  if (errorTemplates) return <Layout><p className="text-red-500">Błąd: {errorTemplates}</p></Layout>;

  return (
    <Layout>
      <h1 className="text-2xl font-bold mb-6">Zarządzanie Szablonami Graficznymi</h1>
      <p className="mb-4">Wybierz szablon graficzny dla swojego sklepu.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map((template) => (
          <div
            key={template.id}
            className={`p-4 border rounded-lg shadow-md cursor-pointer ${
              selectedTemplateId === template.id ? 'border-blue-500 ring-2 ring-blue-500' : 'border-gray-300'
            }`}
            onClick={() => handleSelectTemplate(template.id)}
          >
            <img src={template.thumbnailUrl} alt={template.name} className="w-full h-40 object-cover rounded-md mb-3" />
            <h2 className="text-xl font-semibold">{template.name}</h2>
            <p className="text-sm text-gray-600 mt-1">{template.description}</p>
            {selectedTemplateId === template.id && (
              <p className="text-sm text-blue-600 font-semibold mt-2">Aktualnie wybrany</p>
            )}
          </div>
        ))}
      </div>
      {updatingMetadata && <p className="mt-4">Aktualizowanie szablonu...</p>}
    </Layout>
  );
};

export default TemplatesPage;
