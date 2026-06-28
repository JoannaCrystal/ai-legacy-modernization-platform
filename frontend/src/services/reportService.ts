import { apiGet, downloadFromApi } from './api';
import type {
  ProjectHistoryItem,
  ReportMetadata,
} from '../types/api';

export async function getProjectHistory(): Promise<ProjectHistoryItem[]> {
  return apiGet<ProjectHistoryItem[]>('/projects/history');
}

export async function getProjectReports(
  projectId: number,
): Promise<ReportMetadata[]> {
  return apiGet<ReportMetadata[]>(`/projects/${projectId}/reports`);
}

export async function generateProjectReport(
  projectId: number,
): Promise<{ blob: Blob; filename: string }> {
  return downloadFromApi(
    `/projects/${projectId}/reports/generate`,
    'POST',
  );
}

export async function downloadProjectReport(
  projectId: number,
  reportId: number,
): Promise<{ blob: Blob; filename: string }> {
  return downloadFromApi(
    `/projects/${projectId}/reports/${reportId}/download`,
  );
}

export function triggerBrowserDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
