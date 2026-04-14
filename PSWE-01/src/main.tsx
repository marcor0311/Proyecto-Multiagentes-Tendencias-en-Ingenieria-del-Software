import React from 'react';
import ReactDOM from 'react-dom/client';
import 'bootstrap/dist/css/bootstrap.min.css';
import App from './App';

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('No se encontro el elemento root para montar la aplicacion.');
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
