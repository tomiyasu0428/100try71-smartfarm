import React, { ReactNode, useState } from 'react';
import { 
  AppBar, 
  Box, 
  CssBaseline, 
  Divider, 
  Drawer, 
  IconButton, 
  List, 
  ListItem, 
  ListItemButton, 
  ListItemIcon, 
  ListItemText, 
  Toolbar, 
  Typography,
  useMediaQuery,
  useTheme
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import DashboardIcon from '@mui/icons-material/Dashboard';
import MapIcon from '@mui/icons-material/Map';
import AgricultureIcon from '@mui/icons-material/Agriculture';
import EventNoteIcon from '@mui/icons-material/EventNote';
import InventoryIcon from '@mui/icons-material/Inventory';
import ChatIcon from '@mui/icons-material/Chat';
import BarChartIcon from '@mui/icons-material/BarChart';
import SettingsIcon from '@mui/icons-material/Settings';
import LogoutIcon from '@mui/icons-material/Logout';
import { useRouter } from 'next/router';
import { useAuth } from '@/contexts/AuthContext';

const drawerWidth = 240;

interface LayoutProps {
  children: ReactNode;
  title: string;
}

interface MenuItem {
  text: string;
  icon: React.ReactElement;
  path: string;
  divider?: boolean;
}

const Layout: React.FC<LayoutProps> = ({ children, title }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const router = useRouter();
  const { logout, user } = useAuth();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const menuItems: MenuItem[] = [
    { text: 'ダッシュボード', icon: <DashboardIcon />, path: '/dashboard' },
    { text: '圃場管理', icon: <MapIcon />, path: '/fields' },
    { text: '作物マスタ', icon: <AgricultureIcon />, path: '/crops' },
    { text: '作業管理', icon: <EventNoteIcon />, path: '/tasks' },
    { text: '資材・農機', icon: <InventoryIcon />, path: '/resources' },
    { text: 'AIチャット', icon: <ChatIcon />, path: '/chat' },
    { text: 'レポート', icon: <BarChartIcon />, path: '/reports', divider: true },
    { text: '設定', icon: <SettingsIcon />, path: '/settings' },
    { text: 'ログアウト', icon: <LogoutIcon />, path: '/logout' },
  ];

  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          SmartFarm
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item, index) => (
          <React.Fragment key={item.text}>
            <ListItem disablePadding>
              <ListItemButton 
                selected={router.pathname === item.path}
                onClick={() => {
                  if (item.path === '/logout') {
                    logout();
                  } else {
                    router.push(item.path);
                  }
                  if (isMobile) {
                    setMobileOpen(false);
                  }
                }}
              >
                <ListItemIcon>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
            {item.divider && <Divider />}
          </React.Fragment>
        ))}
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            {title}
          </Typography>
          <Box sx={{ flexGrow: 1 }} />
          {user && (
            <Typography variant="body2" sx={{ mr: 2 }}>
              {user.name} ({user.role})
            </Typography>
          )}
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="mailbox folders"
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{ 
          flexGrow: 1, 
          p: 3, 
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          backgroundColor: theme.palette.background.default
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};

export default Layout;
