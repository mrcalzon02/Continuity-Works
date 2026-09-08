import React from 'react';
import { createRoot } from 'react-dom/client';
import { Dashboard } from './components/Dashboard.js';
import { ManualCapabilityWorkbench } from './components/ManualCapabilityWorkbench.js';

class ContinuityWorksErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error('Continuity Works frontend error:', error, info);
  }

  render() {
    if (!this.state.error) return this.props.children;

    return React.createElement(
      'div',
      { className: 'app-shell' },
      React.createElement(
        'header',
        { className: 'topbar' },
        React.createElement(
          'div',
          { className: 'brand-lockup' },
          React.createElement('div', { className: 'brand-mark', 'aria-hidden': 'true' }, 'CW'),
          React.createElement(
            'div',
            null,
            React.createElement('h1', null, 'Continuity Works'),
            React.createElement('p', null, 'The interface hit a recoverable frontend rendering error.'),
          ),
        ),
      ),
      React.createElement(
        'main',
        { className: 'workspace-grid' },
        React.createElement(
          'section',
          { className: 'panel progression-panel', role: 'alert' },
          React.createElement(
            'div',
            { className: 'panel-heading' },
            React.createElement('span', { className: 'eyebrow' }, 'Frontend diagnostic'),
            React.createElement('h2', null, 'Continuity Works did not initialize completely'),
            React.createElement(
              'p',
              null,
              'The page has been kept visible instead of collapsing to a blank background. Reload once, and if this persists inspect the browser console for the recorded error.',
            ),
          ),
          React.createElement('pre', null, String(this.state.error?.message || this.state.error || 'Unknown rendering error')),
        ),
      ),
    );
  }
}

const rootElement = document.getElementById('root');
if (!rootElement) throw new Error('Continuity Works root element is missing.');

createRoot(rootElement).render(
  React.createElement(
    React.StrictMode,
    null,
    React.createElement(
      ContinuityWorksErrorBoundary,
      null,
      React.createElement(
        React.Fragment,
        null,
        React.createElement(ManualCapabilityWorkbench),
        React.createElement(Dashboard),
      ),
    ),
  ),
);
