import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ShieldCheck, History, LogOut, User, Activity } from 'lucide-react';
import api from '../services/api';

export default function Navbar({ user, setUser }) {
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    api.auth.logout();
    setUser(null);
    navigate('/login');
  };

  if (!user) return null;

  return (
    <header className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <ShieldCheck className="logo-icon" size={24} />
          <span>FakeIG Detector</span>
        </Link>
        
        <nav className="navbar-menu">
          <Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>
            <Activity size={18} />
            <span>Scan Profile</span>
          </Link>
          <Link to="/history" className={`nav-link ${location.pathname === '/history' ? 'active' : ''}`}>
            <History size={18} />
            <span>History Log</span>
          </Link>
        </nav>

        <div className="navbar-user">
          <div className="user-info">
            <User size={16} />
            <span className="user-name">{user.username}</span>
          </div>
          <button className="btn btn-secondary logout-btn" onClick={handleLogout} title="Log Out">
            <LogOut size={16} />
            <span className="logout-text">Log Out</span>
          </button>
        </div>
      </div>
    </header>
  );
}
