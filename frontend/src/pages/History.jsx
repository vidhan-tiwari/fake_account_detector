import React, { useState, useEffect } from 'react';
import { Trash2, AlertCircle, Calendar, ShieldCheck, ShieldAlert, Cpu, User, RefreshCw } from 'lucide-react';
import api from '../services/api';

export default function History() {
  const [history, setHistory] = useState([]);
  const [filteredHistory, setFilteredHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterType, setFilterType] = useState('all'); // 'all', 'auto', 'manual'
  const [filterResult, setFilterResult] = useState('all'); // 'all', 'fake', 'real'

  const fetchHistory = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.history.list();
      setHistory(data);
    } catch (err) {
      setError(err.message || 'Failed to load history log.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  useEffect(() => {
    let result = [...history];

    if (filterType !== 'all') {
      result = result.filter(item => item.type === filterType);
    }

    if (filterResult !== 'all') {
      const wantFake = filterResult === 'fake';
      result = result.filter(item => item.is_fake === wantFake);
    }

    setFilteredHistory(result);
  }, [history, filterType, filterResult]);

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this scan record?')) {
      return;
    }
    
    try {
      await api.history.delete(id);
      setHistory(history.filter(item => item.id !== id));
    } catch (err) {
      alert(err.message || 'Failed to delete record.');
    }
  };

  const formatDate = (dateString) => {
    const d = new Date(dateString);
    return d.toLocaleDateString(undefined, { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="container">
      <div className="history-header flex justify-between items-center mb-4">
        <div>
          <h1>Scan History Log</h1>
          <p>Review the results of your past account analysis scans.</p>
        </div>
        <button className="btn btn-secondary" onClick={fetchHistory} title="Refresh Log">
          <RefreshCw size={18} className={loading ? 'spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter panel */}
      <div className="filter-panel glass-panel mb-4">
        <div className="flex-row">
          <div className="form-group">
            <label className="form-label">Scan Method</label>
            <select 
              className="form-input" 
              value={filterType} 
              onChange={(e) => setFilterType(e.target.value)}
            >
              <option value="all">All Methods</option>
              <option value="auto">Automatic Fetch</option>
              <option value="manual">Manual Entry</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Classification</label>
            <select 
              className="form-input" 
              value={filterResult} 
              onChange={(e) => setFilterResult(e.target.value)}
            >
              <option value="all">All Results</option>
              <option value="fake">Fake Accounts</option>
              <option value="real">Real Accounts</option>
            </select>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-panel glass-panel mb-4">
          <AlertCircle size={20} className="error-icon" />
          <p>{error}</p>
        </div>
      )}

      {loading ? (
        <div className="loader-panel glass-panel text-center">
          <Cpu className="spin loader-icon" size={48} />
          <h3 className="mt-4">Loading history log...</h3>
        </div>
      ) : filteredHistory.length === 0 ? (
        <div className="glass-panel text-center padding-large">
          <Calendar size={48} className="text-muted mb-4" />
          <h3>No scan records found</h3>
          <p className="text-muted mt-2">
            {history.length === 0 
              ? "You haven't run any account checks yet. Go back to the Scanner to start!" 
              : "No scans match your current filter selections."}
          </p>
        </div>
      ) : (
        <div className="history-grid">
          {filteredHistory.map((record) => (
            <div key={record.id} className="history-item glass-panel flex-row justify-between items-center">
              <div className="history-main">
                <div className="flex items-center gap-2">
                  <span className="history-username">@{record.username}</span>
                  <span className={`badge badge-method ${record.type}`}>
                    {record.type === 'auto' ? 'Auto Scan' : 'Manual Scan'}
                  </span>
                  {record.is_verified && (
                    <span className="badge badge-verified">Verified</span>
                  )}
                </div>
                
                <div className="history-meta mt-2">
                  <span className="meta-item">
                    <Calendar size={14} />
                    {formatDate(record.scanned_at)}
                  </span>
                  <span className="meta-item">
                    <User size={14} />
                    Fullname: {record.features?.fullname || 'Not recorded'}
                  </span>
                </div>
              </div>

              <div className="history-actions flex items-center gap-4">
                <div className="text-right">
                  <div 
                    className="history-status" 
                    style={{ color: record.is_fake ? 'var(--status-fake)' : 'var(--status-real)' }}
                  >
                    {record.is_fake ? (
                      <span className="flex items-center gap-1">
                        <ShieldAlert size={16} /> Likely Fake
                      </span>
                    ) : (
                      <span className="flex items-center gap-1">
                        <ShieldCheck size={16} /> Likely Real
                      </span>
                    )}
                  </div>
                  <div className="text-muted" style={{ fontSize: '0.8rem', marginTop: '2px' }}>
                    {Math.round((record.is_fake ? record.probability : (1 - record.probability)) * 100)}% confidence
                  </div>
                </div>

                <button 
                  className="btn btn-danger delete-btn" 
                  onClick={() => handleDelete(record.id)}
                  title="Delete Record"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
