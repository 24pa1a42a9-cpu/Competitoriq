import React, { useState, useEffect } from 'react';
import { TrendingUp, ShieldCheck, CheckCircle2, ArrowRight, Eye, Calendar, Database, ExternalLink, Sparkles, AlertCircle } from 'lucide-react';
import competitorApi from '../services/api';
import AgentMascot from './AgentMascot';
import CategoryIcon from './CategoryIcon';

const MONITORED_COMPETITORS = ['Microsoft', 'Google', 'OpenAI', 'Amazon / AWS', 'Anthropic', 'Meta'];

export default function PatternsView({ onSelectEvent, onSelectCompetitor }) {
  const [selectedCompetitor, setSelectedCompetitor] = useState('Microsoft');
  const [loading, setLoading] = useState(false);
  const [patternData, setPatternData] = useState(null);
  const [selectedPatternId, setSelectedPatternId] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPatterns(selectedCompetitor);
  }, [selectedCompetitor]);

  const fetchPatterns = async (compName) => {
    setLoading(true);
    setError(null);
    try {
      const data = await competitorApi.getPatterns(compName);
      setPatternData(data);
      if (data?.patterns && data.patterns.length > 0) {
        setSelectedPatternId(data.patterns[0].pattern_id);
      } else {
        setSelectedPatternId(null);
      }
    } catch (err) {
      console.error('Error fetching patterns:', err);
      setError(err.message || 'Failed to detect patterns.');
    } finally {
      setLoading(false);
    }
  };

  const patterns = patternData?.patterns || [];
  const activePattern = patterns.find(p => p.pattern_id === selectedPatternId) || patterns[0];
  const hasInsufficientData = patterns.length === 0 && !loading;

  return (
    <div className="content-body" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            Detected Strategic Patterns
          </h1>
          <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Multi-month behavioral trajectories corroborated by persistent episodic memory and cross-category intelligence telemetry.
          </p>
        </div>

        <div className="cautious-pill">
          <TrendingUp size={13} color="var(--text-primary)" />
          <span>STATISTICAL CORROBORATION: HIGH</span>
        </div>
      </div>

      {/* Competitor Selector Tabs */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '12px'
      }}>
        {MONITORED_COMPETITORS.map(comp => {
          const isSelected = comp.toLowerCase() === selectedCompetitor.toLowerCase();
          return (
            <div
              key={comp}
              onClick={() => setSelectedCompetitor(comp)}
              className="card"
              style={{
                cursor: 'pointer',
                padding: '14px 16px',
                border: isSelected ? '2px solid var(--text-primary)' : '1px solid var(--border-subtle)',
                backgroundColor: isSelected ? 'var(--pink-lightest)' : 'var(--bg-primary)',
                transition: 'all 0.15s ease'
              }}
            >
              <div style={{ fontSize: '10.5px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 800, marginBottom: '2px' }}>
                {comp === 'Anthropic' ? 'Edge Case (< 2 Events)' : 'Monitored Competitor'}
              </div>
              <div style={{ fontSize: '14px', fontWeight: 800, color: 'var(--text-primary)' }}>
                {comp}
              </div>
            </div>
          );
        })}
      </div>

      {/* Memory Callout */}
      {!loading && !hasInsufficientData && (
        <div style={{
          padding: '12px 18px',
          backgroundColor: 'var(--bg-secondary)',
          border: '1px solid var(--border-medium)',
          borderRadius: 'var(--radius-sm)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Database size={15} color="var(--text-primary)" />
            <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              Hindsight persistent memory grounded across <strong style={{ color: 'var(--text-primary)' }}>{patternData?.memory_used?.count || 0} recalled memories</strong> ({patternData?.memory_used?.earliest || 'Past'} → {patternData?.memory_used?.latest || 'Present'}).
            </span>
          </div>
          <span className="badge badge-black">
            {patterns.length} Active Vectors
          </span>
        </div>
      )}

      {/* ERROR MESSAGE */}
      {error && (
        <div style={{
          padding: '14px 18px',
          backgroundColor: '#fff0f2',
          border: '1px solid #fecdd3',
          borderRadius: 'var(--radius-md)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          color: '#be123c',
          fontSize: '13px'
        }}>
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* LOADING STATE */}
      {loading && (
        <div className="card" style={{
          padding: '48px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '16px',
          backgroundColor: 'var(--bg-primary)'
        }}>
          <AgentMascot size={64} state="searching" />
          <div style={{ textAlign: 'center' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)' }}>
              Detecting Strategic Vectors for {selectedCompetitor}...
            </h3>
            <p style={{ fontSize: '12.5px', color: 'var(--text-muted)', marginTop: '4px' }}>
              Synthesizing historical milestones into persistent cross-category trajectories
            </p>
          </div>
        </div>
      )}

      {/* INSUFFICIENT DATA STATE */}
      {hasInsufficientData && (
        <div className="card" style={{
          padding: '32px',
          backgroundColor: 'var(--bg-primary)',
          border: '1.5px solid var(--border-medium)',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '18px'
        }}>
          <AgentMascot size={52} state="cautious" />
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span className="badge badge-outline">Insufficient Data</span>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Bank: competitor-{selectedCompetitor.toLowerCase()}</span>
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '6px' }}>
              No strong cross-event pattern was identified for {selectedCompetitor}.
            </h3>
            <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '14px' }}>
              {patternData?.limitations?.[0] || 'At least 2 verified competitor events are required to establish an evidence-grounded strategic trajectory.'}
            </p>
          </div>
        </div>
      )}

      {/* Main Grid: Pattern List (Left) & Deep Dive Dossier (Right) */}
      {!loading && !hasInsufficientData && patterns.length > 0 && activePattern && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.4fr', gap: '24px' }}>
          
          {/* Left Column: Pattern Cards */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {patterns.map((pat, idx) => {
              const isSelected = pat.pattern_id === activePattern.pattern_id;
              return (
                <div
                  key={pat.pattern_id || idx}
                  onClick={() => setSelectedPatternId(pat.pattern_id)}
                  className="card"
                  style={{
                    padding: '18px 20px',
                    cursor: 'pointer',
                    border: isSelected ? '2px solid var(--text-primary)' : '1px solid var(--border-subtle)',
                    backgroundColor: isSelected ? 'var(--pink-lightest)' : 'var(--bg-primary)',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <span className="badge badge-black">{selectedCompetitor}</span>
                    <span className="badge badge-pink" style={{ textTransform: 'uppercase', fontSize: '10px' }}>
                      {pat.confidence || 'HIGH'} Confidence
                    </span>
                  </div>

                  <div style={{ fontSize: '14.5px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px', lineHeight: 1.3 }}>
                    {pat.title}
                  </div>

                  {/* Categories */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', flexWrap: 'wrap', marginBottom: '6px' }}>
                    {(pat.categories || []).map((cat, cIdx) => (
                      <span key={cIdx} className="badge badge-outline" style={{ fontSize: '9.5px', padding: '1px 5px' }}>
                        {cat}
                      </span>
                    ))}
                  </div>

                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    Timeframe: {pat.time_span?.start} → {pat.time_span?.end} • {pat.event_count || pat.evidence?.length || 0} Milestones
                  </div>
                </div>
              );
            })}
          </div>

          {/* Right Column: Pattern Deep Dive */}
          <div className="card" style={{ padding: '28px', display: 'flex', flexDirection: 'column', gap: '22px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px', flexWrap: 'wrap', gap: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span className="badge badge-black">{selectedCompetitor}</span>
                  <span className="badge badge-pink" style={{ textTransform: 'uppercase' }}>
                    {activePattern.confidence || 'HIGH'} Confidence
                  </span>
                </div>
                <span style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                  Observed: {activePattern.time_span?.start} → {activePattern.time_span?.end}
                </span>
              </div>

              <h2 style={{ fontSize: '20px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em', marginBottom: '10px' }}>
                {activePattern.title}
              </h2>

              <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '14px' }}>
                {activePattern.pattern}
              </p>

              <div style={{
                padding: '14px 18px',
                backgroundColor: 'var(--pink-lightest)',
                border: '1px solid var(--pink-border)',
                borderRadius: 'var(--radius-md)',
                fontSize: '13px',
                lineHeight: 1.55,
                color: 'var(--text-primary)'
              }}>
                <span style={{ fontWeight: 700, display: 'block', marginBottom: '4px', textTransform: 'uppercase', fontSize: '11px' }}>
                  Why This Matters To Market Positioning:
                </span>
                {activePattern.why_it_matters}
              </div>
            </div>

            {/* Supporting Evidence Chain */}
            <div>
              <div style={{
                fontSize: '11px',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                color: 'var(--text-muted)',
                marginBottom: '12px'
              }}>
                Supporting Evidence Chain ({activePattern.evidence?.length || 0} Direct Findings)
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {(activePattern.evidence || []).map((ev, idx) => (
                  <div
                    key={ev.event_id || idx}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      justifyContent: 'space-between',
                      gap: '12px',
                      padding: '12px 16px',
                      backgroundColor: 'var(--bg-secondary)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)'
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '3px' }}>
                        <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-muted)' }}>
                          {ev.date}
                        </span>
                        <span className="badge badge-outline" style={{ fontSize: '9.5px', padding: '1px 5px' }}>
                          {ev.event_type}
                        </span>
                        <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                          • {ev.source_name || 'Corporate Blog'}
                        </span>
                      </div>
                      <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.4 }}>
                        {ev.title}
                      </div>
                    </div>

                    {ev.source_url && (
                      <a
                        href={ev.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-outline"
                        style={{
                          padding: '4px 10px',
                          fontSize: '11px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                          flexShrink: 0
                        }}
                      >
                        <span>View Source</span>
                        <ExternalLink size={11} />
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Strategic Signal Card */}
            {activePattern.strategic_signal && (
              <div style={{
                padding: '16px 20px',
                backgroundColor: 'var(--text-primary)',
                color: 'var(--text-inverse)',
                borderRadius: 'var(--radius-md)'
              }}>
                <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', opacity: 0.8, marginBottom: '4px' }}>
                  Strategic Signal & Competitive Implication
                </div>
                <p style={{ fontSize: '13px', lineHeight: 1.5 }}>
                  {activePattern.strategic_signal}
                </p>
              </div>
            )}

          </div>

        </div>
      )}

    </div>
  );
}
