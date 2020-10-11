import React from 'react';
import ReactDOM from 'react-dom';
import './tailwind.output.css';
import "@fortawesome/fontawesome-free/css/all.min.css";
import { AppContextProvider } from './context';
import App from './App';

ReactDOM.render(
  <React.StrictMode>
    <AppContextProvider>
      <App />
    </AppContextProvider>
  </React.StrictMode>,
  document.getElementById('root')
);
