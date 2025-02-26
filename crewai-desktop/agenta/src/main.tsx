import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './App.css';

// Ensure proper error handling for the entire app
window.onerror = (message, source, lineno, colno, error) => {
  console.error('Global error:', { message, source, lineno, colno, error });
  // You could also send this to your error tracking service
  return false;
};

// Handle unhandled promise rejections
window.onunhandledrejection = (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  // You could also send this to your error tracking service
  event.preventDefault();
};

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
