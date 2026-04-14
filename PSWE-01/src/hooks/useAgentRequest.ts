import { useState } from 'react';
import type { IaCFormData } from '../types/iac';

type AgentResponse = Record<string, unknown>;

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.trim();

function logAgentPipeline(payload: IaCFormData, data: AgentResponse) {
  const build =
    typeof data.build === 'object' && data.build !== null ? (data.build as Record<string, unknown>) : null;

  console.group('Multiagent generation');
  console.info('Payload enviado:', payload);
  console.info('Input normalizado por backend:', data.input ?? null);
  console.info('Builder:', {
    output_dir: build?.output_dir ?? null,
    zip_path: build?.zip_path ?? null,
    download_url: build?.download_url ?? null,
    copied_assets: build?.copied_assets ?? []
  });
  console.groupEnd();
}

function buildResponseLogs(payload: IaCFormData, data: AgentResponse): string[] {
  const build =
    typeof data.build === 'object' && data.build !== null ? (data.build as Record<string, unknown>) : null;

  return [
    `Payload enviado para ${payload.project_name}.`,
    'IaC Terraform generada lista para validar.',
    `ZIP generado en ${String(build?.zip_path ?? 'ruta no disponible')}.`
  ];
}

function getDownloadUrl(data: AgentResponse): string | null {
  const build =
    typeof data.build === 'object' && data.build !== null ? (data.build as Record<string, unknown>) : null;
  const downloadPath = build && typeof build.download_url === 'string' ? build.download_url : null;

  if (!downloadPath || !API_BASE_URL) {
    return null;
  }

  return new URL(downloadPath, API_BASE_URL).toString();
}

async function triggerZipDownload(data: AgentResponse) {
  const downloadUrl = getDownloadUrl(data);

  if (!downloadUrl) {
    return;
  }

  const response = await fetch(downloadUrl);

  if (!response.ok) {
    throw new Error(`No se pudo descargar el ZIP generado (${response.status}).`);
  }

  const blob = await response.blob();
  const objectUrl = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  const fileName =
    typeof (data.build as Record<string, unknown> | undefined)?.project_name === 'string'
      ? `${String((data.build as Record<string, unknown>).project_name)}.zip`
      : 'generated-project.zip';

  link.href = objectUrl;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(objectUrl);
}

export function useAgentRequest() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [responseData, setResponseData] = useState<AgentResponse | null>(null);
  const [activityLogs, setActivityLogs] = useState<string[]>([]);

  const submitPayload = async (payload: IaCFormData) => {
    if (!API_BASE_URL) {
      throw new Error('La variable VITE_API_BASE_URL no está configurada en el archivo .env.');
    }

    const liveMessages = [
      'Enviando payload al backend...',
      'Planner analizando la solicitud...',
      'Retriever reuniendo contexto Terraform...',
      'Generator armando archivos y modulos...',
      'Builder empaquetando el proyecto...',
      'Ejecutando validacion Terraform...'
    ];

    let liveIndex = 0;
    setActivityLogs([liveMessages[0]]);
    setIsSubmitting(true);
    setSubmitError(null);
    const intervalId = window.setInterval(() => {
      liveIndex += 1;
      if (liveIndex < liveMessages.length) {
        setActivityLogs((current) =>
          current[current.length - 1] === liveMessages[liveIndex] ? current : [...current, liveMessages[liveIndex]]
        );
      }
    }, 1400);

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
      logAgentPipeline(payload, data);
      setActivityLogs(buildResponseLogs(payload, data));
      await triggerZipDownload(data);
      setResponseData(data);
      return data;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Ocurrió un error inesperado al enviar la solicitud.';
      setSubmitError(message);
      setActivityLogs((current) => [...current, `Error: ${message}`]);
      throw error;
    } finally {
      window.clearInterval(intervalId);
      setIsSubmitting(false);
    }
  };

  return {
    isSubmitting,
    responseData,
    submitError,
    activityLogs,
    submitPayload
  };
}
