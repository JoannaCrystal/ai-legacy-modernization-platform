import { apiGet, apiPostForm } from './api';
import type {
  ModernizationPlanResponse,
  ProjectAnalysisResponse,
  UploadResponse,
} from '../types/api';

export async function uploadProject(
  name: string,
  file: File,
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('name', name);
  formData.append('file', file);

  return apiPostForm<UploadResponse>('/projects/upload', formData);
}

export async function getProjectAnalysis(
  projectId: number,
): Promise<ProjectAnalysisResponse> {
  return apiGet<ProjectAnalysisResponse>(`/projects/${projectId}/analysis`);
}

export async function getModernizationPlan(
  projectId: number,
): Promise<ModernizationPlanResponse> {
  return apiGet<ModernizationPlanResponse>(
    `/projects/${projectId}/modernization-plan`,
  );
}
