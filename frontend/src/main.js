import React from 'react';
import { createRoot } from 'react-dom/client';
import { Dashboard } from './components/Dashboard.js';

createRoot(document.getElementById('root')).render(
  React.createElement(React.StrictMode, null, React.createElement(Dashboard)),
);
