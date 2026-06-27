import Box from '@mui/material/Box';
import Container from '@mui/material/Container';

import Navbar from './Navbar';

interface AppLayoutProps {
  children: React.ReactNode;
  projectId?: number | null;
}

export default function AppLayout({ children, projectId }: AppLayoutProps) {
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <Navbar projectId={projectId} />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {children}
      </Container>
    </Box>
  );
}
