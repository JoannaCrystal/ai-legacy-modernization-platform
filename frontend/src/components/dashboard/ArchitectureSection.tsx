import AccountTreeIcon from '@mui/icons-material/AccountTree';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Chip from '@mui/material/Chip';
import Grid from '@mui/material/Grid2';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

import type { ArchitectureSummary } from '../../types/api';

interface ArchitectureSectionProps {
  architectureSummary: ArchitectureSummary;
  reportOverview?: string;
}

export default function ArchitectureSection({
  architectureSummary,
  reportOverview,
}: ArchitectureSectionProps) {
  const components = architectureSummary.components ?? [];

  return (
    <Box>
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
        <AccountTreeIcon color="primary" />
        <Typography variant="h5">Architecture</Typography>
      </Stack>

      {reportOverview && (
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          {reportOverview}
        </Typography>
      )}

      {components.length === 0 ? (
        <Typography color="text.secondary">
          No architecture components were inferred for this project.
        </Typography>
      ) : (
        <Grid container spacing={2}>
          {components.map((component) => (
            <Grid size={{ xs: 12, md: 6 }} key={component.name}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {component.name}
                  </Typography>

                  <Typography
                    variant="subtitle2"
                    color="text.secondary"
                    gutterBottom
                  >
                    Responsibility
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    {component.responsibility}
                  </Typography>

                  <Typography
                    variant="subtitle2"
                    color="text.secondary"
                    gutterBottom
                  >
                    Classes
                  </Typography>
                  <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
                    {component.classes.map((className) => (
                      <Chip
                        key={className}
                        label={className}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
