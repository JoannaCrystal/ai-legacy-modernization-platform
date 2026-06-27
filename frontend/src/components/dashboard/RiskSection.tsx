import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Chip from '@mui/material/Chip';
import Grid from '@mui/material/Grid2';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

import type {
  DependencyAnalysisResult,
  RiskAnalysis,
} from '../../types/api';

interface RiskSectionProps {
  riskAnalysis: RiskAnalysis;
  dependencyAnalysis: DependencyAnalysisResult;
}

function riskColor(riskLevel: string): 'error' | 'success' {
  return riskLevel.toUpperCase() === 'HIGH' ? 'error' : 'success';
}

export default function RiskSection({
  riskAnalysis,
  dependencyAnalysis,
}: RiskSectionProps) {
  const highRiskDependencies =
    dependencyAnalysis.high_risk_dependencies ?? [];

  return (
    <Box>
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
        <WarningAmberIcon color="primary" />
        <Typography variant="h5">Risk Analysis</Typography>
      </Stack>

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card
            sx={{
              height: '100%',
              borderTop: 4,
              borderColor:
                riskAnalysis.overall_risk === 'HIGH'
                  ? 'error.main'
                  : 'success.main',
            }}
          >
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">
                Overall Risk
              </Typography>
              <Chip
                label={riskAnalysis.overall_risk}
                color={riskColor(riskAnalysis.overall_risk)}
                sx={{ mt: 1, fontWeight: 700, fontSize: '1rem', py: 2 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 8 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Risk Explanation
              </Typography>
              <Typography variant="body1" sx={{ mb: 2 }}>
                {riskAnalysis.reason}
              </Typography>

              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                High-Risk Dependencies
              </Typography>
              {highRiskDependencies.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No high-risk dependencies detected.
                </Typography>
              ) : (
                <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
                  {highRiskDependencies.map((dependency) => (
                    <Chip
                      key={dependency.dependency}
                      label={`${dependency.technology} (${dependency.risk_level})`}
                      color="error"
                      variant="outlined"
                      size="small"
                    />
                  ))}
                </Stack>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
