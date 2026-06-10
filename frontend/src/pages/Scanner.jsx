import React, { useState } from 'react';
import { ShieldAlert, ShieldCheck, Cpu, User, FileText, Globe, Key, AlertCircle, Eye, EyeOff } from 'lucide-react';
import api from '../services/api';
import VisualGauge from '../components/VisualGauge';

export default function Scanner() {
  const [activeTab, setActiveTab] = useState('auto'); // 'auto' or 'manual'
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  // Auto path states
  const [autoUsername, setAutoUsername] = useState('');

  // Manual path states
  const [mUsername, setMUsername] = useState('');
  const [mFullname, setMFullname] = useState('');
  const [mBioInput, setMBioInput] = useState('');
  const [mPosts, setMPosts] = useState(0);
  const [mFollowers, setMFollowers] = useState(0);
  const [mFollows, setMFollows] = useState(0);
  const [mHasPic, setMHasPic] = useState(true);
  const [mIsPrivate, setMIsPrivate] = useState(false);
  const [mHasUrl, setMHasUrl] = useState(false);
  const [mIsVerified, setMIsVerified] = useState(false);

  const handleAutoScan = async (e) => {
    e.preventDefault();
    if (!autoUsername.trim()) {
      setError('Please enter a username.');
      return;
    }
    setError('');
    setResult(null);
    setLoading(true);
    setStatusMessage('Connecting to Instagram API...');

    try {
      // Simulate loading phases like Streamlit
      setTimeout(() => setStatusMessage('Fetching profile metadata...'), 1500);
      setTimeout(() => setStatusMessage('Analyzing account features...'), 3000);
      
      const res = await api.scan.auto(autoUsername);
      setResult(res);
    } catch (err) {
      setError(err.message || 'An error occurred during scanning.');
    } finally {
      setLoading(false);
      setStatusMessage('');
    }
  };

  const handleManualScan = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);

    // Validation
    const missing = [];
    if (!mUsername.trim()) missing.push('Username');
    if (!mFullname.trim()) missing.push('Full Name');
    
    if (missing.length > 0) {
      setError(`Missing required fields: ${missing.join(', ')}. The model requires these to perform calculations.`);
      return;
    }

    setLoading(true);
    setStatusMessage('Computing manual data details...');

    const payload = {
      username: mUsername,
      fullname: mFullname,
      bio_input: mBioInput || '0', // Fallback
      posts: parseInt(mPosts) || 0,
      followers: parseInt(mFollowers) || 0,
      follows: parseInt(mFollows) || 0,
      has_pic: mHasPic,
      is_private: mIsPrivate,
      has_url: mHasUrl,
      is_verified: mIsVerified
    };

    try {
      const res = await api.scan.manual(payload);
      setResult(res);
    } catch (err) {
      setError(err.message || 'An error occurred during prediction.');
    } finally {
      setLoading(false);
      setStatusMessage('');
    }
  };

  return (
    <div className="container">
      <div className="scanner-hero text-center mb-4">
        <h1>Detect Bot & Fake Accounts</h1>
        <p>Analyze Instagram profiles using deep learning. Choose between automatic scan or manual inputs.</p>
      </div>

      <div className="tabs-header">
        <button
          className={`tab-btn ${activeTab === 'auto' ? 'active' : ''}`}
          onClick={() => { setActiveTab('auto'); setResult(null); setError(''); }}
          disabled={loading}
        >
          Automatic Fetching
        </button>
        <button
          className={`tab-btn ${activeTab === 'manual' ? 'active' : ''}`}
          onClick={() => { setActiveTab('manual'); setResult(null); setError(''); }}
          disabled={loading}
        >
          Manual Data Entry
        </button>
      </div>

      {error && (
        <div className="error-panel glass-panel mb-4">
          <AlertCircle size={20} className="error-icon" />
          <div>
            <h4 className="error-title">Analysis Interrupted</h4>
            <p className="error-desc">{error}</p>
          </div>
        </div>
      )}

      {loading && (
        <div className="loader-panel glass-panel mb-4 text-center">
          <div className="spinner-container">
            <Cpu className="spin loader-icon" size={48} />
          </div>
          <h3 className="mt-4">{statusMessage}</h3>
          <p className="text-muted">Please hold tight, this may take a few seconds...</p>
        </div>
      )}

      {!loading && !result && activeTab === 'auto' && (
        <div className="scanner-form-card glass-panel">
          <h2>Auto Profile Scanner</h2>
          <p className="mb-4">Instagram may restrict frequent anonymous scans. If it fails, please use the manual route.</p>
          
          <form onSubmit={handleAutoScan} className="flex-row items-center">
            <div className="form-group flex-grow">
              <label className="form-label">Target IG Username</label>
              <div className="input-with-icon">
                <User size={18} className="input-icon" />
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. instagram"
                  value={autoUsername}
                  onChange={(e) => setAutoUsername(e.target.value)}
                  required
                />
              </div>
            </div>
            <div className="form-group btn-group-align">
              <button type="submit" className="btn btn-primary btn-scan-submit">
                Scan Profile
              </button>
            </div>
          </form>
        </div>
      )}

      {!loading && !result && activeTab === 'manual' && (
        <div className="scanner-form-card glass-panel">
          <h2>Manual Entry Parameters</h2>
          <p className="mb-4">Enter profile parameters directly to evaluate the prediction algorithm.</p>
          
          <form onSubmit={handleManualScan}>
            <div className="flex-row">
              {/* Col 1 */}
              <div>
                <div className="form-group">
                  <label className="form-label">Username</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. vidh.an__01"
                    value={mUsername}
                    onChange={(e) => setMUsername(e.target.value)}
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Full Name</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Vidhan Tiwari"
                    value={mFullname}
                    onChange={(e) => setMFullname(e.target.value)}
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Bio (Text or Length)</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. 'I love travel' OR '150'"
                    value={mBioInput}
                    onChange={(e) => setMBioInput(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Number of Posts</label>
                  <input
                    type="number"
                    min="0"
                    className="form-input"
                    value={mPosts}
                    onChange={(e) => setMPosts(e.target.value)}
                  />
                </div>
              </div>

              {/* Col 2 */}
              <div>
                <div className="form-group">
                  <label className="form-label">Number of Followers</label>
                  <input
                    type="number"
                    min="0"
                    className="form-input"
                    value={mFollowers}
                    onChange={(e) => setMFollowers(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Number Following</label>
                  <input
                    type="number"
                    min="0"
                    className="form-input"
                    value={mFollows}
                    onChange={(e) => setMFollows(e.target.value)}
                  />
                </div>

                <div className="switch-container">
                  <div className="switch-label-group">
                    <span className="form-label" style={{ marginBottom: 0 }}>Has Profile Picture?</span>
                    <span className="text-muted" style={{ fontSize: '0.75rem' }}>Avatar is visible</span>
                  </div>
                  <label className="switch">
                    <input type="checkbox" checked={mHasPic} onChange={(e) => setMHasPic(e.target.checked)} />
                    <span className="slider"></span>
                  </label>
                </div>

                <div className="switch-container">
                  <div className="switch-label-group">
                    <span className="form-label" style={{ marginBottom: 0 }}>Is Private Account?</span>
                    <span className="text-muted" style={{ fontSize: '0.75rem' }}>Only approved followers see posts</span>
                  </div>
                  <label className="switch">
                    <input type="checkbox" checked={mIsPrivate} onChange={(e) => setMIsPrivate(e.target.checked)} />
                    <span className="slider"></span>
                  </label>
                </div>

                <div className="switch-container">
                  <div className="switch-label-group">
                    <span className="form-label" style={{ marginBottom: 0 }}>Has External URL?</span>
                    <span className="text-muted" style={{ fontSize: '0.75rem' }}>Link in bio</span>
                  </div>
                  <label className="switch">
                    <input type="checkbox" checked={mHasUrl} onChange={(e) => setMHasUrl(e.target.checked)} />
                    <span className="slider"></span>
                  </label>
                </div>

                <div className="switch-container">
                  <div className="switch-label-group">
                    <span className="form-label" style={{ marginBottom: 0 }}>Is Verified (Blue Tick)?</span>
                    <span className="text-muted" style={{ fontSize: '0.75rem' }}>Bypasses AI model validation</span>
                  </div>
                  <label className="switch">
                    <input type="checkbox" checked={mIsVerified} onChange={(e) => setMIsVerified(e.target.checked)} />
                    <span className="slider"></span>
                  </label>
                </div>
              </div>
            </div>

            <button type="submit" className="btn btn-primary w-full mt-4">
              Predict Account Risk
            </button>
          </form>
        </div>
      )}

      {/* Result Presentation */}
      {result && (
        <div className="result-display mt-4">
          <div className="flex-row">
            {/* Visual Gauge */}
            <VisualGauge probability={result.probability} isVerified={result.is_verified} />

            {/* Scanned Attributes */}
            <div className="glass-panel">
              <div className="flex justify-between items-center mb-4 border-b pb-2">
                <h2>Profile: @{result.username}</h2>
                {result.is_verified && <span className="badge badge-verified">Verified</span>}
              </div>

              <div className="result-features-list">
                <div className="feature-item">
                  <User size={16} />
                  <span className="feature-name">Full Name:</span>
                  <span className="feature-val">{result.features.fullname || 'None'}</span>
                </div>
                <div className="feature-item">
                  <FileText size={16} />
                  <span className="feature-name">Bio / Description:</span>
                  <span className="feature-val truncate" title={result.features.bio_input}>
                    {result.features.bio_input}
                  </span>
                </div>
                <div className="feature-item">
                  <Globe size={16} />
                  <span className="feature-name">Followers:</span>
                  <span className="feature-val">{result.features.followers.toLocaleString()}</span>
                </div>
                <div className="feature-item">
                  <Globe size={16} />
                  <span className="feature-name">Following:</span>
                  <span className="feature-val">{result.features.follows.toLocaleString()}</span>
                </div>
                <div className="feature-item">
                  <FileText size={16} />
                  <span className="feature-name">Number of Posts:</span>
                  <span className="feature-val">{result.features.posts.toLocaleString()}</span>
                </div>
                <div className="feature-item">
                  <Globe size={16} />
                  <span className="feature-name">Has Profile Picture:</span>
                  <span className="feature-val">{result.features.has_pic ? 'Yes' : 'No'}</span>
                </div>
                <div className="feature-item">
                  <Key size={16} />
                  <span className="feature-name">Account Type:</span>
                  <span className="feature-val">{result.features.is_private ? 'Private' : 'Public'}</span>
                </div>
                <div className="feature-item">
                  <Globe size={16} />
                  <span className="feature-name">Has Bio URL:</span>
                  <span className="feature-val">{result.features.has_url ? 'Yes' : 'No'}</span>
                </div>
              </div>

              <button className="btn btn-secondary w-full mt-4" onClick={() => setResult(null)}>
                Run Another Scan
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
