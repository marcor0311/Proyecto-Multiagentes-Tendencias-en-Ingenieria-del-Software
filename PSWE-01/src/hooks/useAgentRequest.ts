import { useState } from 'react';
import type { IaCFormData } from '../types/iac';

type AgentResponse = Record<string, unknown>;

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.trim();

export function useAgentRequest() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [responseData, setResponseData] = useState<AgentResponse | null>(null);

  const submitPayload = async (payload: IaCFormData) => {
    if (!API_BASE_URL) {
      throw new Error('La variable VITE_API_BASE_URL no está configurada en el archivo .env.');
    }

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/agent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`La solicitud falló con estado ${response.status}.`);
      }

      const data = (await response.json()) as AgentResponse;
      setResponseData(data);
      return data;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Ocurrió un error inesperado al enviar la solicitud.';
      setSubmitError(message);
      throw error;
    } finally {
      setIsSubmitting(false);
    }
  };

  return {
    isSubmitting,
    responseData,
    submitError,
    submitPayload
  };
}
