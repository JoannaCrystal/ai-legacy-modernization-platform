import HubIcon from '@mui/icons-material/Hub';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';

import type { DependencyAnalysis } from '../../types/api';

interface DependencySectionProps {
  dependencies: DependencyAnalysis[];
}

function riskColor(riskLevel: string): 'error' | 'warning' | 'success' | 'default' {
  const normalized = riskLevel.toUpperCase();
  if (normalized === 'HIGH') {
    return 'error';
  }
  if (normalized === 'MEDIUM') {
    return 'warning';
  }
  if (normalized === 'LOW') {
    return 'success';
  }
  return 'default';
}

export default function DependencySection({
  dependencies,
}: DependencySectionProps) {
  return (
    <Box>
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
        <HubIcon color="primary" />
        <Typography variant="h5">Dependency Analysis</Typography>
      </Stack>

      {dependencies.length === 0 ? (
        <Typography color="text.secondary">
          No dependencies were detected for this project.
        </Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Technology</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Risk</TableCell>
                <TableCell>Dependency</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {dependencies.map((dependency) => (
                <TableRow key={dependency.dependency}>
                  <TableCell>{dependency.technology}</TableCell>
                  <TableCell>{dependency.category}</TableCell>
                  <TableCell>
                    <Chip
                      label={dependency.risk_level}
                      color={riskColor(dependency.risk_level)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {dependency.dependency}
                    </Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
