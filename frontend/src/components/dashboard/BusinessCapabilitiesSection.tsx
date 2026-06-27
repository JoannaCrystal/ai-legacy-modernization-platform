import BusinessCenterIcon from '@mui/icons-material/BusinessCenter';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Grid from '@mui/material/Grid2';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

import type { BusinessCapabilities } from '../../types/api';

interface BusinessCapabilitiesSectionProps {
  businessCapabilities: BusinessCapabilities;
}

export default function BusinessCapabilitiesSection({
  businessCapabilities,
}: BusinessCapabilitiesSectionProps) {
  const capabilities = businessCapabilities.capabilities ?? [];

  return (
    <Box>
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
        <BusinessCenterIcon color="primary" />
        <Typography variant="h5">Business Capabilities</Typography>
      </Stack>

      {capabilities.length === 0 ? (
        <Typography color="text.secondary">
          No business capabilities were inferred for this project.
        </Typography>
      ) : (
        <Grid container spacing={2}>
          {capabilities.map((capability) => (
            <Grid size={{ xs: 12, md: 6, lg: 4 }} key={capability.name}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {capability.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {capability.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
