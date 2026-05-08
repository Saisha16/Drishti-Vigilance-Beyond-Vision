import { createBrowserRouter, Navigate } from 'react-router';
import { Layout } from './components/Layout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Alerts } from './pages/Alerts';
import { ThreatAnalysis } from './pages/ThreatAnalysis';
import { UserAnalysis } from './pages/UserAnalysis';
import { Heatmap } from './pages/Heatmap';
import { Reports } from './pages/Reports';
import { Configuration } from './pages/Configuration';
import { Settings } from './pages/Settings';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Login />,
  },
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        path: 'dashboard',
        element: <Dashboard />,
      },
      {
        path: 'alerts',
        element: <Alerts />,
      },
      {
        path: 'threat-analysis',
        element: <ThreatAnalysis />,
      },
      {
        path: 'user-intelligence',
        element: <UserAnalysis />,
      },
      {
        path: 'heatmap',
        element: <Heatmap />,
      },
      {
        path: 'reports',
        element: <Reports />,
      },
      {
        path: 'configuration',
        element: <Configuration />,
      },
      {
        path: 'settings',
        element: <Settings />,
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);
