import React, { useState } from 'react';
import { X, Settings, ShieldCheck, Database, Server, Check } from 'lucide-react';

export default function SettingsModal({ onClose }) {
  const [flaskUrl, setFlaskUrl] = useState(import.meta.env.VITE_API_URL || 'http://localhost:5000');
  const [llmModel, setLlmModel] = useState('Gemini 2.5 Pro (Strategic Reasoning)');
  const [decayThreshold, setDecayThreshold] = useState('0.00% (Zero Decay - Persistent)');
  const [crawlFrequency, setCrawlFrequency] = useState('Every 30 minutes');
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => {
      setSaved(false);
      onClose();
    }, 900);
  };

  return (
    <>
      <div className="overlay-backdrop" onClick={onClose} />
      <div
        style={{
          position: 'fixed',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '560px',
          maxWidth: '92vw',
          backgroundColor: 'var(--bg-primary)',
          border: '1px solid var(--border-black)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-lg)',
          zIndex: 70,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: 'var(--bg-primary)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Settings size={18} color="var(--text-primary)" />
            <h2 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)' }}>
              CompetitorIQ Agent Configuration
            </h2>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)' }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '18px' }}>
          
          {/* Flask Backend URL */}
          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-primary)', marginBottom: '6px' }}>
              Flask Backend API Endpoint (Optional)
            </label>
            <input
              type="text"
              value={flaskUrl}
              onChange={(e) => setFlaskUrl(e.target.value)}
              placeholder="http://localhost:5000"
              className="input-minimal"
            />
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px', display: 'block' }}>
              Leave blank or default to run on built-in autonomous simulation engine.
            </span>
          </div>

          {/* Strategic LLM Engine */}
          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-primary)', marginBottom: '6px' }}>
              Strategic Reasoning LLM Model
            </label>
            <select
              value={llmModel}
              onChange={(e) => setLlmModel(e.target.value)}
              className="input-minimal"
              style={{ cursor: 'pointer' }}
            >
              <option value="Gemini 2.5 Pro (Strategic Reasoning)">Gemini 2.5 Pro (Strategic Reasoning)</option>
              <option value="Claude 3.7 Sonnet (Extended Thinking)">Claude 3.7 Sonnet (Extended Thinking)</option>
              <option value="GPT-4.5 Orion (Multi-Hop Causal)">GPT-4.5 Orion (Multi-Hop Causal)</option>
            </select>
          </div>

          {/* Memory Decay Parameter */}
          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-primary)', marginBottom: '6px' }}>
              Hindsight Memory Salience & Retention Policy
            </label>
            <select
              value={decayThreshold}
              onChange={(e) => setDecayThreshold(e.target.value)}
              className="input-minimal"
              style={{ cursor: 'pointer' }}
            >
              <option value="0.00% (Zero Decay - Persistent)">0.00% (Zero Decay - Permanent Archive)</option>
              <option value="0.05% (Linear Decay / 24 Months)">0.05% (Linear Decay / 24 Months)</option>
              <option value="0.10% (Salience Weighted Only)">0.10% (Salience Weighted Only)</option>
            </select>
          </div>

          {/* Surveillance Frequency */}
          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-primary)', marginBottom: '6px' }}>
              Automated Surveillance Frequency
            </label>
            <select
              value={crawlFrequency}
              onChange={(e) => setCrawlFrequency(e.target.value)}
              className="input-minimal"
              style={{ cursor: 'pointer' }}
            >
              <option value="Every 15 minutes">Every 15 minutes (High-frequency)</option>
              <option value="Every 30 minutes">Every 30 minutes (Standard)</option>
              <option value="Every 2 hours">Every 2 hours (Batch)</option>
            </select>
          </div>

          {/* System Status Callout */}
          <div style={{
            padding: '12px 14px',
            backgroundColor: 'var(--pink-lightest)',
            border: '1px solid var(--pink-border)',
            borderRadius: 'var(--radius-sm)',
            fontSize: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--text-primary)' }} />
              <span style={{ fontWeight: 700 }}>Hindsight Memory Engine</span>
            </div>
            <span style={{ fontFamily: 'var(--font-mono)' }}>142 Nodes Synced</span>
          </div>

        </div>

        {/* Footer */}
        <div style={{
          padding: '16px 24px',
          borderTop: '1px solid var(--border-subtle)',
          backgroundColor: 'var(--bg-secondary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'flex-end',
          gap: '10px'
        }}>
          <button onClick={onClose} className="btn btn-outline btn-sm">
            Cancel
          </button>
          <button onClick={handleSave} className="btn btn-primary btn-sm">
            {saved ? 'Settings Saved!' : 'Save Configuration'}
          </button>
        </div>
      </div>
    </>
  );
}
