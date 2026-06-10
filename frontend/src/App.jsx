import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ShieldCheck, Cpu } from 'lucide-react';

import api from './services/api';
import Navbar from './components/Navbar';
import PrivateRoute from './components/PrivateRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import Scanner from './pages/Scanner';
import History from './pages/History';

export default function App() {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  // Authenticate user on app mount if token exists
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setAuthLoading(false);
        return;
      }
      try {
        const currentUser = await api.auth.me();
        setUser(currentUser);
      } catch (err) {
        console.error('Session validation failed:', err);
        // Token expired or server offline
        localStorage.removeItem('token');
      } finally {
        setAuthLoading(false);
      }
    };
    checkAuth();
  }, []);

  if (authLoading) {
    return (
      <div className="auth-loading-screen">
        <div className="loader-panel glass-panel text-center">
          <ShieldCheck className="spin loader-icon" size={48} style={{ color: 'var(--status-real)' }} />
          <h3 className="mt-4">Validating Secure Session...</h3>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <Navbar user={user} setUser={setUser} />
      <main>
        <Routes>
          {/* Public Authentication routes (Redirects to dashboard if logged in) */}
          <Route 
            path="/login" 
            element={user ? <Navigate to="/" replace /> : <Login setUser={setUser} />} 
          />
          <Route 
            path="/register" 
            element={user ? <Navigate to="/" replace /> : <Register />} 
          />

          {/* Protected Main routes */}
          <Route 
            path="/" 
            element={
              <PrivateRoute>
                <Scanner />
              </PrivateRoute>
            } 
          />
          <Route 
            path="/history" 
            element={
              <PrivateRoute>
                <History />
              </PrivateRoute>
            } 
          />

          {/* Redirect any other path to dashboard */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </Router>
  );
}
