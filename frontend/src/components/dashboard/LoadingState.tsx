import CircularProgress from '@mui/material/CircularProgress';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

interface LoadingStateProps {
  message?: string;
}

export default function LoadingState({
  message = 'Running AI analysis pipeline...',
}: LoadingStateProps) {
  return (
    <Stack
      alignItems="center"
      justifyContent="center"
      spacing={2}
      sx={{ py: 10 }}
    >
      <CircularProgress size={48} />
      <Typography variant="h6" color="text.secondary">
        {message}
      </Typography>
      <Typography variant="body2" color="text.secondary" align="center">
        Analyzing architecture, business capabilities, dependencies, and
        modernization opportunities.
      </Typography>
    </Stack>
  );
}
