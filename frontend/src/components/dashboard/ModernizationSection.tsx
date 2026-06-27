import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Grid from '@mui/material/Grid2';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

import type { ModernizationPlan } from '../../types/api';

interface ModernizationSectionProps {
  modernizationPlan: ModernizationPlan;
}

function NumberedList({ items }: { items: string[] }) {
  if (items.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        None identified.
      </Typography>
    );
  }

  return (
    <List dense disablePadding>
      {items.map((item, index) => (
        <ListItem key={`${index}-${item}`} disableGutters sx={{ py: 0.5 }}>
          <ListItemText
            primary={`${index + 1}. ${item}`}
            primaryTypographyProps={{ variant: 'body2' }}
          />
        </ListItem>
      ))}
    </List>
  );
}

export default function ModernizationSection({
  modernizationPlan,
}: ModernizationSectionProps) {
  const keyRisks = modernizationPlan.key_risks ?? [];
  const recommendedSteps = modernizationPlan.recommended_steps ?? [];
  const fallbackRecommendations = modernizationPlan.recommendations ?? [];

  return (
    <Box>
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
        <RocketLaunchIcon color="primary" />
        <Typography variant="h5">Modernization Plan</Typography>
      </Stack>

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Architecture Assessment
              </Typography>
              <Typography variant="body1" sx={{ mb: 2 }}>
                {modernizationPlan.architecture_assessment ??
                  modernizationPlan.summary ??
                  'No assessment available.'}
              </Typography>

              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Target Architecture
              </Typography>
              <Typography variant="body1">
                {modernizationPlan.target_architecture ??
                  'No target architecture provided.'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Key Risks
              </Typography>
              <Box sx={{ mb: 2 }}>
                <NumberedList items={keyRisks} />
              </Box>

              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Recommended Steps
              </Typography>
              <NumberedList
                items={
                  recommendedSteps.length > 0
                    ? recommendedSteps
                    : fallbackRecommendations
                }
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
