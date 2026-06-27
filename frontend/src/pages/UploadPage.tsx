import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import LinearProgress from '@mui/material/LinearProgress';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { ApiRequestError } from '../services/api';
import { uploadProject } from '../services/projectService';

export default function UploadPage() {
  const navigate = useNavigate();
  const [projectName, setProjectName] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);
    setError(null);
    setSuccessMessage(null);
  };

  const handleUpload = async () => {
    if (!projectName.trim()) {
      setError('Please enter a project name.');
      return;
    }

    if (!selectedFile) {
      setError('Please select a ZIP file to upload.');
      return;
    }

    if (!selectedFile.name.toLowerCase().endsWith('.zip')) {
      setError('Only ZIP files are accepted.');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const result = await uploadProject(projectName.trim(), selectedFile);
      setSuccessMessage(
        `Upload successful. ${result.files_processed} files processed.`,
      );
      navigate(`/dashboard/${result.project_id}`);
    } catch (err) {
      const message =
        err instanceof ApiRequestError
          ? err.message
          : 'Upload failed. Please try again.';
      setError(message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Stack spacing={4} alignItems="center">
      <Box sx={{ textAlign: 'center', maxWidth: 720 }}>
        <Typography variant="h3" gutterBottom>
          AI Legacy Modernization Platform
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ fontWeight: 400 }}>
          Upload a legacy application to trigger AI-powered architecture analysis,
          business capability extraction, and modernization planning.
        </Typography>
      </Box>

      <Card sx={{ width: '100%', maxWidth: 640 }}>
        <CardContent sx={{ p: 4 }}>
          <Stack spacing={3}>
            <TextField
              label="Project Name"
              placeholder="e.g. Customer Portal Legacy App"
              value={projectName}
              onChange={(event) => setProjectName(event.target.value)}
              fullWidth
              disabled={uploading}
            />

            <Box>
              <Button
                component="label"
                variant="outlined"
                startIcon={<CloudUploadIcon />}
                disabled={uploading}
              >
                Select ZIP File
                <input
                  type="file"
                  hidden
                  accept=".zip,application/zip"
                  onChange={handleFileChange}
                />
              </Button>
              {selectedFile && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Selected: {selectedFile.name}
                </Typography>
              )}
            </Box>

            {uploading && (
              <Box>
                <LinearProgress />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Uploading and analyzing legacy application...
                </Typography>
              </Box>
            )}

            {error && <Alert severity="error">{error}</Alert>}
            {successMessage && <Alert severity="success">{successMessage}</Alert>}

            <Button
              variant="contained"
              size="large"
              onClick={() => void handleUpload()}
              disabled={uploading}
            >
              Upload & Analyze
            </Button>
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  );
}
