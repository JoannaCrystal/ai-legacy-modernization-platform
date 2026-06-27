import Divider from '@mui/material/Divider';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { useParams } from 'react-router-dom';

import ArchitectureDiagram from '../components/dashboard/ArchitectureDiagram';
import ArchitectureSection from '../components/dashboard/ArchitectureSection';
import BusinessCapabilitiesSection from '../components/dashboard/BusinessCapabilitiesSection';
import DependencySection from '../components/dashboard/DependencySection';
import ErrorAlert from '../components/dashboard/ErrorAlert';
import LoadingState from '../components/dashboard/LoadingState';
import ModernizationSection from '../components/dashboard/ModernizationSection';
import RiskSection from '../components/dashboard/RiskSection';
import { useProjectAnalysis } from '../hooks/useProjectAnalysis';

export default function DashboardPage() {
  const { projectId } = useParams();
  const parsedProjectId = projectId ? Number(projectId) : null;
  const validProjectId =
    parsedProjectId !== null && !Number.isNaN(parsedProjectId)
      ? parsedProjectId
      : null;

  const { analysis, modernization, loading, error, refetch } =
    useProjectAnalysis(validProjectId);

  if (validProjectId === null) {
    return <ErrorAlert message="Invalid project ID." />;
  }

  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorAlert message={error} onRetry={() => void refetch()} />;
  }

  if (!analysis || !modernization) {
    return <ErrorAlert message="No analysis data available for this project." />;
  }

  return (
    <Stack spacing={4}>
      <BoxHeader
        projectName={analysis.project_name}
        projectId={analysis.project_id}
        summary={analysis.summary}
      />

      <ArchitectureSection
        architectureSummary={modernization.architecture_summary}
        reportOverview={modernization.architecture_report.application_overview}
      />

      <Divider />

      <BusinessCapabilitiesSection
        businessCapabilities={modernization.business_capabilities}
      />

      <Divider />

      <Stack spacing={2}>
        <Typography variant="h5">Architecture Diagram</Typography>
        <ArchitectureDiagram
          architectureSummary={modernization.architecture_summary}
        />
      </Stack>

      <Divider />

      <DependencySection dependencies={analysis.dependencies} />

      <Divider />

      <RiskSection
        riskAnalysis={modernization.risk_analysis}
        dependencyAnalysis={modernization.dependency_analysis}
      />

      <Divider />

      <ModernizationSection
        modernizationPlan={modernization.modernization_plan}
      />
    </Stack>
  );
}

function BoxHeader({
  projectName,
  projectId,
  summary,
}: {
  projectName: string;
  projectId: number;
  summary: {
    total_files: number;
    total_classes: number;
    total_methods: number;
    total_dependencies: number;
  };
}) {
  return (
    <Stack spacing={1}>
      <Typography variant="h4">{projectName}</Typography>
      <Typography variant="body1" color="text.secondary">
        Project #{projectId} · {summary.total_files} files ·{' '}
        {summary.total_classes} classes · {summary.total_methods} methods ·{' '}
        {summary.total_dependencies} dependencies
      </Typography>
    </Stack>
  );
}
