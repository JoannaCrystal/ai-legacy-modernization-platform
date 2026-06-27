import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider } from '@mui/material/styles';
import { BrowserRouter, Navigate, Route, Routes, useParams } from 'react-router-dom';

import AppLayout from './components/layout/AppLayout';
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import theme from './theme';

function DashboardRoute() {
  const { projectId } = useParams();
  const parsedProjectId = projectId ? Number(projectId) : null;

  return (
    <AppLayout projectId={parsedProjectId}>
      <DashboardPage />
    </AppLayout>
  );
}

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route
            path="/"
            element={
              <AppLayout>
                <UploadPage />
              </AppLayout>
            }
          />
          <Route path="/dashboard/:projectId" element={<DashboardRoute />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
