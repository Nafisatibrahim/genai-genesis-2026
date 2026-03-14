import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Auth0Provider } from '@auth0/auth0-react'
import './index.css'
import App from './App.jsx'
import PosturePage from './pages/PosturePage.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Auth0Provider
      domain="dev-wrrmvshcm6okdzli.us.auth0.com"
      clientId="yIPztIyEwQM1x7BXxQKRmisnPGhB48w7"
      authorizationParams={{ redirect_uri: window.location.origin }}
    >
      <BrowserRouter>
        <Routes>
          <Route path="/"        element={<App />} />
          <Route path="/posture" element={<PosturePage />} />
        </Routes>
      </BrowserRouter>
    </Auth0Provider>
  </StrictMode>
)
