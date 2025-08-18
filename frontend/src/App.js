import React, { useState } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, Container, AppBar, Toolbar, Typography, IconButton, Button } from '@mui/material';
import { Brightness4, Brightness7 } from '@mui/icons-material';
import { lightTheme, darkTheme } from './theme';
import Dashboard from './pages/Dashboard';

function App() {
  const [darkMode, setDarkMode] = useState(false);

  const theme = darkMode ? darkTheme : lightTheme;

  const handleThemeToggle = () => {
    setDarkMode(!darkMode);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              AIRISS v4.0 - AI 인사 분석 시스템
            </Typography>
            <IconButton color="inherit" onClick={handleThemeToggle}>
              {darkMode ? <Brightness7 /> : <Brightness4 />}
            </IconButton>
          </Toolbar>
        </AppBar>
        
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          <Dashboard />
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;