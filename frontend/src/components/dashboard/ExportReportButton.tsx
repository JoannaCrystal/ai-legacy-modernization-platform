import DownloadIcon from '@mui/icons-material/Download';
import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Stack from '@mui/material/Stack';
import { useState } from 'react';

import {
  generateProjectReport,
  triggerBrowserDownload,
} from '../../services/reportService';
import { ApiRequestError } from '../../services/api';

interface ExportReportButtonProps {
  projectId: number;
}

export default function ExportReportButton({
  projectId,
}: ExportReportButtonProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleExport = async () => {
    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const { blob, filename } = await generateProjectReport(projectId);
      triggerBrowserDownload(blob, filename);
      setSuccessMessage('Enterprise report downloaded successfully.');
    } catch (err) {
      const message =
        err instanceof ApiRequestError
          ? err.message
          : 'Failed to generate enterprise report.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack spacing={1}>
      <Button
        variant="contained"
        color="secondary"
        startIcon={
          loading ? <CircularProgress size={18} color="inherit" /> : <DownloadIcon />
        }
        onClick={() => void handleExport()}
        disabled={loading}
      >
        {loading ? 'Generating Report...' : 'Export Report'}
      </Button>
      {error && <Alert severity="error">{error}</Alert>}
      {successMessage && <Alert severity="success">{successMessage}</Alert>}
    </Stack>
  );
}
