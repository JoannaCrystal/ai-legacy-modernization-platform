import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AppBar from '@mui/material/AppBar';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import { Link as RouterLink, useLocation } from 'react-router-dom';

interface NavbarProps {
  projectId?: number | null;
}

export default function Navbar({ projectId }: NavbarProps) {
  const location = useLocation();

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        bgcolor: 'primary.main',
        borderBottom: '1px solid rgba(255,255,255,0.08)',
      }}
    >
      <Container maxWidth="lg">
        <Toolbar disableGutters sx={{ py: 1 }}>
          <AutoAwesomeIcon sx={{ mr: 1.5 }} />
          <Typography
            component={RouterLink}
            to="/"
            variant="h6"
            sx={{
              flexGrow: 1,
              color: 'inherit',
              textDecoration: 'none',
              fontWeight: 700,
            }}
          >
            AI Legacy Modernization Platform
          </Typography>

          <Button
            component={RouterLink}
            to="/"
            color="inherit"
            startIcon={<CloudUploadIcon />}
            sx={{
              mr: 1,
              bgcolor: location.pathname === '/' ? 'rgba(255,255,255,0.12)' : 'transparent',
            }}
          >
            Upload
          </Button>

          {projectId !== null && projectId !== undefined && (
            <Button
              component={RouterLink}
              to={`/dashboard/${projectId}`}
              color="inherit"
              startIcon={<DashboardIcon />}
              sx={{
                bgcolor: location.pathname.startsWith('/dashboard')
                  ? 'rgba(255,255,255,0.12)'
                  : 'transparent',
              }}
            >
              Dashboard
            </Button>
          )}
        </Toolbar>
      </Container>
    </AppBar>
  );
}
