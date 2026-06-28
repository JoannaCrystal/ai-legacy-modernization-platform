const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

export class ApiRequestError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiRequestError';
    this.status = status;
  }
}

async function parseError(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body.detail === 'string') {
      return body.detail;
    }
    return response.statusText || 'Request failed';
  } catch {
    return response.statusText || 'Request failed';
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);

  if (!response.ok) {
    throw new ApiRequestError(await parseError(response), response.status);
  }

  return response.json() as Promise<T>;
}

export async function apiPostForm<T>(
  path: string,
  formData: FormData,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new ApiRequestError(await parseError(response), response.status);
  }

  return response.json() as Promise<T>;
}

function extractFilename(contentDisposition: string | null): string | null {
  if (!contentDisposition) {
    return null;
  }

  const match = contentDisposition.match(/filename="(.+)"/);
  return match?.[1] ?? null;
}

export async function downloadFromApi(
  path: string,
  method: 'GET' | 'POST' = 'GET',
): Promise<{ blob: Blob; filename: string }> {
  const response = await fetch(`${API_BASE_URL}${path}`, { method });

  if (!response.ok) {
    throw new ApiRequestError(await parseError(response), response.status);
  }

  const blob = await response.blob();
  const filename =
    extractFilename(response.headers.get('Content-Disposition')) ??
    'modernization-report.pdf';

  return { blob, filename };
}

export { API_BASE_URL };
