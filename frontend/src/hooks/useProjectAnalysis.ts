import { useCallback, useEffect, useState } from 'react';

import { ApiRequestError } from '../services/api';
import {
  getModernizationPlan,
  getProjectAnalysis,
} from '../services/projectService';
import type {
  ModernizationPlanResponse,
  ProjectAnalysisResponse,
} from '../types/api';

interface UseProjectAnalysisResult {
  analysis: ProjectAnalysisResponse | null;
  modernization: ModernizationPlanResponse | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useProjectAnalysis(
  projectId: number | null,
): UseProjectAnalysisResult {
  const [analysis, setAnalysis] = useState<ProjectAnalysisResponse | null>(
    null,
  );
  const [modernization, setModernization] =
    useState<ModernizationPlanResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    if (projectId === null) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const [analysisResult, modernizationResult] = await Promise.all([
        getProjectAnalysis(projectId),
        getModernizationPlan(projectId),
      ]);

      setAnalysis(analysisResult);
      setModernization(modernizationResult);
    } catch (err) {
      const message =
        err instanceof ApiRequestError
          ? err.message
          : 'Failed to load project analysis';
      setError(message);
      setAnalysis(null);
      setModernization(null);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void refetch();
  }, [refetch]);

  return {
    analysis,
    modernization,
    loading,
    error,
    refetch,
  };
}
