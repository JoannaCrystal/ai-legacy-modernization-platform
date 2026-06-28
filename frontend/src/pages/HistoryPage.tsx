import DownloadIcon from '@mui/icons-material/Download';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import { useCallback, useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';

import {
  downloadProjectReport,
  generateProjectReport,
  getProjectHistory,
  triggerBrowserDownload,
} from '../services/reportService';
import { ApiRequestError } from '../services/api';
import type { ProjectHistoryItem } from '../types/api';

function formatDate(value: string | null): string {
  if (!value) {
    return '—';
  }
  return new Date(value).toLocaleString();
}

function riskColor(risk: string | null): 'error' | 'success' | 'default' {
  if (risk?.toUpperCase() === 'HIGH') {
    return 'error';
  }
  if (risk?.toUpperCase() === 'LOW') {
    return 'success';
  }
  return 'default';
}

export default function HistoryPage() {
  const [history, setHistory] = useState<ProjectHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloadingProjectId, setDownloadingProjectId] = useState<
    number | null
  >(null);

  const loadHistory = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const items = await getProjectHistory();
      setHistory(items);
    } catch (err) {
      const message =
        err instanceof ApiRequestError
          ? err.message
          : 'Failed to load project history.';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadHistory();
  }, [loadHistory]);

  const handleDownload = async (item: ProjectHistoryItem) => {
    setDownloadingProjectId(item.project_id);
    setError(null);

    try {
      const { blob, filename } = item.latest_report_id
        ? await downloadProjectReport(item.project_id, item.latest_report_id)
        : await generateProjectReport(item.project_id);
      triggerBrowserDownload(blob, filename);
      await loadHistory();
    } catch (err) {
      const message =
        err instanceof ApiRequestError
          ? err.message
          : 'Failed to download report.';
      setError(message);
    } finally {
      setDownloadingProjectId(null);
    }
  };

  if (loading) {
    return (
      <Stack alignItems="center" spacing={2} sx={{ py: 10 }}>
        <CircularProgress />
        <Typography color="text.secondary">Loading project history...</Typography>
      </Stack>
    );
  }

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" gutterBottom>
          Project History
        </Typography>
        <Typography color="text.secondary">
          Review previously analyzed projects and download enterprise reports
          without rerunning the AI workflow.
        </Typography>
      </Box>

      {error && <Alert severity="error">{error}</Alert>}

      {history.length === 0 ? (
        <Alert severity="info">
          No analyzed projects yet. Upload a legacy application to get started.
        </Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Project</TableCell>
                <TableCell>Upload Date</TableCell>
                <TableCell>Analysis Completed</TableCell>
                <TableCell>Overall Risk</TableCell>
                <TableCell>Report Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {history.map((item) => (
                <TableRow key={item.project_id}>
                  <TableCell>
                    <Typography fontWeight={600}>{item.project_name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Project #{item.project_id}
                    </Typography>
                  </TableCell>
                  <TableCell>{formatDate(item.upload_date)}</TableCell>
                  <TableCell>
                    {formatDate(item.analysis_completed_at)}
                  </TableCell>
                  <TableCell>
                    {item.overall_risk ? (
                      <Chip
                        label={item.overall_risk}
                        color={riskColor(item.overall_risk)}
                        size="small"
                      />
                    ) : (
                      '—'
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={item.report_status.replace('_', ' ')}
                      color={
                        item.report_status === 'GENERATED' ? 'success' : 'default'
                      }
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={1} justifyContent="flex-end">
                      <Button
                        component={RouterLink}
                        to={`/dashboard/${item.project_id}`}
                        size="small"
                        startIcon={<OpenInNewIcon />}
                        disabled={item.analysis_status !== 'COMPLETED'}
                      >
                        Open
                      </Button>
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={
                          downloadingProjectId === item.project_id ? (
                            <CircularProgress size={16} />
                          ) : (
                            <DownloadIcon />
                          )
                        }
                        disabled={
                          item.analysis_status !== 'COMPLETED' ||
                          downloadingProjectId === item.project_id
                        }
                        onClick={() => void handleDownload(item)}
                      >
                        PDF
                      </Button>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Stack>
  );
}
