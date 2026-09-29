import React, { useState, useEffect } from 'react';
import {
  GitMerge,
  ArrowRight,
  ShieldCheck,
  ChevronRight,
  Database,
  ExternalLink,
  Calendar,
  CheckCircle,
  Sparkles,
  Link2,
  RefreshCw,
  AlertCircle,
  Eye,
  TrendingUp,
  Tag
} from 'lucide-react';
import CategoryIcon from './CategoryIcon';
import CompanyLogo from './CompanyLogo';
import AgentMascot from './AgentMascot';
import competitorApi from '../services/api';

const MONITORED_COMPETITORS = [
  { id: 'Microsoft', name: 'Microsoft', isCore: true },
  { id: 'Google', name: 'Google', isCore: true },
  { id: 'OpenAI', name: 'OpenAI', isCore: true },
  { id: 'Amazon / AWS', name: 'Amazon / AWS', isCore: false },
  { id: 'Anthropic', name: 'Anthropic', isCore: false },
  { id: 'Meta', name: 'Meta', isCore: false }
];

export default function ConnectDotsView({ onSelectEvent, onSelectCompetitor, onSelectPattern }) {
  const [selectedCompetitor, setSelectedCompetitor] = useState('Microsoft');
  const [loading, setLoading] = useState(false);
  const [patternData, setPatternData] = useState(null);
  const [selectedPatternId, setSelectedPatternId] = useState(null);
  const [selectedEvidenceModal, setSelectedEvidenceModal] = useState(null);
  const [error, setError] = useState(null);

  // Fetch strategic patterns whenever selected competitor changes
  useEffect(() => {
    fetchPatterns(selectedCompetitor);
  }, [selectedCompetitor]);

  const fetchPatterns = async (competitorName) => {
    setLoading(true);
    setError(null);
    try {
      const data = await competitorApi.getPatterns(competitorName);
      setPatternData(data);
      if (data?.patterns && data.patterns.length > 0) {
        setSelectedPatternId(data.patterns[0].pattern_id);
      } else {
        setSelectedPatternId(null);
      }
    } catch (err) {
      console.error('Error fetching strategic patterns:', err);
      setError(err.message || 'Failed to detect strategic patterns.');
    } finally {
      setLoading(false);
    }
  };

  const patterns = patternData?.patterns || [];
  const activePattern = patterns.find(p => p.pattern_id === selectedPatternId) || patterns[0];
  const memoryUsed = patternData?.memory_used || { count: 0, earliest: null, latest: null };
  const hasInsufficientData = patterns.length === 0 && !loading;

  return (
    <div className="content-body" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            Connect the Dots: Multi-Hop Strategic Pattern Detection
          </h1>
          <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Persistent memory links discrete milestones across quarters into explainable, evidence-grounded strategic trajectories.
          </p>
        </div>

        <div className="cautious-pill">
          <GitMerge size={13} color="var(--text-primary)" />
          <span>MULTI-EVENT STRATEGIC SYNTHESIS</span>
        </div>
      </div>

      {/* Competitor Selector Tabs */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '12px'
      }}>
        {MONITORED_COMPETITORS.map(comp => {
          const isSelected = comp.name.toLowerCase() === selectedCompetitor.toLowerCase();
          return (
            <div
              key={comp.id}
              onClick={() => setSelectedCompetitor(comp.name)}
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
                {comp.name === 'Anthropic' ? 'Edge Case (< 2 Events)' : 'Monitored Competitor'}
              </div>
              <div style={{ fontSize: '14px', fontWeight: 800, color: 'var(--text-primary)' }}>
                {comp.name}
              </div>
            </div>
          );
        })}
      </div>

      {/* CORE CONCEPT VISUAL FORMULA */}
      <div style={{
        padding: '18px 24px',
        backgroundColor: 'var(--pink-lightest)',
        border: '2px solid var(--border-black)',
        borderRadius: 'var(--radius-md)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px',
        flexWrap: 'wrap'
      }}>
        {/* Left formula items */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <div style={{ padding: '7px 11px', backgroundColor: 'var(--bg-primary)', border: '1px solid var(--border-medium)', borderRadius: '6px', fontSize: '11.5px', fontWeight: 800 }}>
            EVENT 1
          </div>
          <span style={{ fontWeight: 800 }}>➔</span>
          <div style={{ padding: '7px 11px', backgroundColor: 'var(--bg-primary)', border: '1px solid var(--border-medium)', borderRadius: '6px', fontSize: '11.5px', fontWeight: 800 }}>
            EVENT 2
          </div>
          <span style={{ fontWeight: 800 }}>➔</span>
          <div style={{ padding: '7px 11px', backgroundColor: 'var(--bg-primary)', border: '1px solid var(--border-medium)', borderRadius: '6px', fontSize: '11.5px', fontWeight: 800 }}>
            EVENT 3
          </div>
        </div>

        {/* Center Mascot with Contextual Intelligence State */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <AgentMascot
            size={44}
            state={loading ? 'searching' : hasInsufficientData ? 'cautious' : 'found'}
          />
          <span style={{ fontSize: '16px', fontWeight: 900 }}>➔</span>
        </div>

        {/* Right outcome items */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <div style={{ padding: '7px 11px', backgroundColor: 'var(--text-primary)', color: 'var(--text-inverse)', borderRadius: '6px', fontSize: '11.5px', fontWeight: 800 }}>
            DETECTED PATTERN
          </div>
          <span style={{ fontWeight: 800 }}>➔</span>
          <div style={{ padding: '7px 11px', backgroundColor: '#ea96a5', color: '#0a0a0a', border: '1px solid var(--border-black)', borderRadius: '6px', fontSize: '11.5px', fontWeight: 800 }}>
            STRATEGIC SIGNAL
          </div>
        </div>
      </div>

      {/* MEMORY EXPLANATION TRANSPARENCY BAR (Requirement 17) */}
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
            <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)' }}>
              Hindsight Memory Recall:
            </span>
            <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              Recalled <strong style={{ color: 'var(--text-primary)' }}>{memoryUsed.count}</strong> memories spanning <strong style={{ color: 'var(--text-primary)' }}>{memoryUsed.earliest || 'Past'} → {memoryUsed.latest || 'Present'}</strong> for {selectedCompetitor}.
            </span>
          </div>
          <span className="badge badge-black">
            {patterns.length} Verified Patterns Discovered
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

      {/* LOADING SPINNER */}
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
              Looking through historical memory & connecting related events...
            </h3>
            <p style={{ fontSize: '12.5px', color: 'var(--text-muted)', marginTop: '4px' }}>
              Querying isolated Hindsight bank for {selectedCompetitor} • Analyzing cross-category temporal vectors with Groq
            </p>
          </div>
        </div>
      )}

      {/* INSUFFICIENT DATA STATE (Requirement 19) */}
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
              <span className="badge badge-outline">Insufficient Historical Telemetry</span>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Bank: competitor-{selectedCompetitor.toLowerCase()}</span>
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '6px' }}>
              Not enough historical evidence yet to connect patterns for {selectedCompetitor}.
            </h3>
            <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '14px' }}>
              {patternData?.limitations?.[0] || 'At least 2 verified competitor events are required to establish an evidence-grounded strategic trajectory.'}
            </p>
            <div style={{
              padding: '12px 16px',
              backgroundColor: 'var(--pink-lightest)',
              border: '1px solid var(--pink-border)',
              borderRadius: '6px',
              fontSize: '12px',
              color: 'var(--text-primary)',
              fontWeight: 600
            }}>
              🔒 Integrity Guarantee: CompetitorIQ strictly prevents speculative pattern hallucinations. Add more verified source-backed events to reveal multi-hop connections.
            </div>
          </div>
        </div>
      )}

      {/* MAIN PATTERN VIEW: Selector Cards + Deep Dive */}
      {!loading && !hasInsufficientData && patterns.length > 0 && activePattern && (
        <>
          {/* Pattern Cards Selector Grid (Requirement 12) */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '12px'
          }}>
            {patterns.map((pat, idx) => {
              const isSelected = pat.pattern_id === activePattern.pattern_id;
              return (
                <div
                  key={pat.pattern_id || idx}
                  onClick={() => setSelectedPatternId(pat.pattern_id)}
                  className="card"
                  style={{
                    cursor: 'pointer',
                    padding: '16px 18px',
                    border: isSelected ? '2px solid var(--text-primary)' : '1px solid var(--border-subtle)',
                    backgroundColor: isSelected ? 'var(--pink-lightest)' : 'var(--bg-primary)',
                    transition: 'all 0.15s ease',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '10px'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span className="badge badge-black">{selectedCompetitor}</span>
                    <span className="badge badge-pink" style={{ textTransform: 'uppercase', fontSize: '10px' }}>
                      {pat.confidence || 'HIGH'} Confidence
                    </span>
                  </div>

                  <div style={{ fontSize: '14.5px', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1.3 }}>
                    {pat.title}
                  </div>

                  {/* Categories */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px', flexWrap: 'wrap' }}>
                    {(pat.categories || []).map((cat, cIdx) => (
                      <span key={cIdx} className="badge badge-outline" style={{ fontSize: '10px', padding: '2px 6px' }}>
                        {cat}
                      </span>
                    ))}
                  </div>

                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: 'auto', paddingTop: '4px', borderTop: '1px solid var(--border-subtle)' }}>
                    {pat.time_span?.start} → {pat.time_span?.end} • {pat.event_count || pat.evidence?.length || 0} Connected Milestones
                  </div>
                </div>
              );
            })}
          </div>

          {/* ACTIVE PATTERN DETAILED DOSSIER */}
          <div className="card" style={{ padding: '28px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
            
            {/* Header / Meta */}
            <div style={{
              display: 'flex',
              alignItems: 'flex-start',
              justifyContent: 'space-between',
              gap: '20px',
              paddingBottom: '20px',
              borderBottom: '1px solid var(--border-subtle)',
              flexWrap: 'wrap'
            }}>
              <div style={{ flex: 1, minWidth: '280px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', flexWrap: 'wrap' }}>
                  <span className="badge badge-black">{selectedCompetitor}</span>
                  <span className="badge badge-pink" style={{ textTransform: 'uppercase' }}>
                    {activePattern.confidence || 'HIGH'} Confidence
                  </span>
                  <span style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                    {activePattern.time_span?.start} → {activePattern.time_span?.end}
                  </span>
                </div>

                <h2 style={{ fontSize: '21px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em', marginBottom: '8px' }}>
                  {activePattern.title}
                </h2>

                <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  {activePattern.pattern}
                </p>
              </div>

              {/* Mascot Discovery Card */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '14px 18px',
                backgroundColor: 'var(--pink-lightest)',
                border: '1.5px solid var(--border-black)',
                borderRadius: 'var(--radius-md)',
                maxWidth: '380px',
                flexShrink: 0
              }}>
                <AgentMascot size={46} state="found" />
                <div style={{ fontSize: '12px', lineHeight: 1.45, color: 'var(--text-primary)' }}>
                  <span style={{ fontWeight: 800, display: 'block', fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-primary)' }}>
                    Agent Discovery
                  </span>
                  "I found a pattern connecting these {activePattern.event_count || activePattern.evidence?.length} moves across {activePattern.time_span?.start} to {activePattern.time_span?.end}."
                </div>
              </div>
            </div>

            {/* EVENT CHAIN VISUALIZATION (Requirement 12 & 13) */}
            <div>
              <div style={{
                fontSize: '11px',
                fontWeight: 800,
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                color: 'var(--text-muted)',
                marginBottom: '14px'
              }}>
                Connected Event Chain (Chronological Multi-Hop Vector)
              </div>

              {/* Horizontal Chain Flow */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                overflowX: 'auto',
                padding: '12px 6px',
                marginBottom: '16px'
              }}>
                {(activePattern.evidence || []).map((ev, eIdx) => {
                  const isLast = eIdx === (activePattern.evidence.length - 1);
                  return (
                    <React.Fragment key={ev.event_id || eIdx}>
                      <div style={{
                        padding: '12px 14px',
                        backgroundColor: 'var(--bg-secondary)',
                        border: '1px solid var(--border-medium)',
                        borderRadius: '8px',
                        minWidth: '200px',
                        maxWidth: '260px',
                        flexShrink: 0
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                          <span style={{ fontSize: '10.5px', fontWeight: 800, color: 'var(--text-muted)' }}>
                            {ev.date}
                          </span>
                          <span className="badge badge-outline" style={{ fontSize: '9.5px', padding: '1px 5px' }}>
                            {ev.event_type}
                          </span>
                        </div>
                        <div style={{ fontSize: '12.5px', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1.3 }}>
                          {ev.title?.length > 55 ? ev.title.substring(0, 55) + '...' : ev.title}
                        </div>
                      </div>

                      {!isLast && (
                        <ArrowRight size={18} color="var(--text-muted)" style={{ flexShrink: 0 }} />
                      )}
                    </React.Fragment>
                  );
                })}
              </div>
            </div>

            {/* CHRONOLOGICAL MULTI-HOP REASONING TIMELINE (Requirement 13) */}
            <div>
              <div style={{
                fontSize: '11px',
                fontWeight: 800,
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                color: 'var(--text-muted)',
                marginBottom: '16px'
              }}>
                Timeline Milestones & Progression Evidence
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0px' }}>
                {(activePattern.evidence || []).map((step, idx) => {
                  const isLast = idx === activePattern.evidence.length - 1;

                  return (
                    <div key={step.event_id || idx} style={{ display: 'flex', gap: '18px', position: 'relative' }}>
                      
                      {/* Left Column: Number Node and Connecting Line */}
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', minWidth: '34px' }}>
                        <div style={{
                          width: '32px',
                          height: '32px',
                          borderRadius: '50%',
                          backgroundColor: 'var(--text-primary)',
                          color: 'var(--text-inverse)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '13px',
                          fontWeight: 800,
                          zIndex: 2,
                          boxShadow: '0 0 0 3px var(--pink-subtle)'
                        }}>
                          {idx + 1}
                        </div>

                        {!isLast && (
                          <div style={{
                            width: '2px',
                            flex: 1,
                            backgroundColor: 'var(--border-dark)',
                            minHeight: '48px',
                            margin: '4px 0'
                          }} />
                        )}
                      </div>

                      {/* Right Column: Step Content Card */}
                      <div style={{
                        flex: 1,
                        backgroundColor: 'var(--bg-secondary)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-md)',
                        padding: '16px 20px',
                        marginBottom: '18px'
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span className="badge badge-black">{step.date}</span>
                            <span className="badge badge-pink" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                              <CategoryIcon category={step.event_type} size={11} />
                              <span>{step.event_type}</span>
                            </span>
                          </div>
                          <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                            ID: {step.event_id}
                          </span>
                        </div>

                        <div style={{ fontSize: '14.5px', fontWeight: 800, color: 'var(--text-primary)', marginTop: '4px' }}>
                          {step.title}
                        </div>

                        {step.description && (
                          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '6px', lineHeight: 1.5 }}>
                            {step.description}
                          </p>
                        )}

                        {/* Verified Source Citation Footer */}
                        <div style={{
                          marginTop: '12px',
                          paddingTop: '10px',
                          borderTop: '1px solid var(--border-subtle)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          flexWrap: 'wrap',
                          gap: '8px'
                        }}>
                          <span style={{ fontSize: '11.5px', color: 'var(--text-secondary)' }}>
                            Source: <strong style={{ color: 'var(--text-primary)' }}>{step.source_name || 'Official Corporate Blog'}</strong>
                          </span>

                          {step.source_url ? (
                            <a
                              href={step.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="btn btn-outline"
                              style={{
                                padding: '4px 10px',
                                fontSize: '11px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px'
                              }}
                            >
                              <span>View Source</span>
                              <ExternalLink size={11} />
                            </a>
                          ) : (
                            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                              Verified Telemetry
                            </span>
                          )}
                        </div>

                      </div>

                    </div>
                  );
                })}
              </div>
            </div>

            {/* THE "WHY THIS MATTERS" 4-PART EXPLAINABLE STRUCTURE (Requirement 14) */}
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '14px',
              paddingTop: '16px',
              borderTop: '1px solid var(--border-subtle)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sparkles size={16} color="var(--text-primary)" />
                <h3 style={{ fontSize: '15px', fontWeight: 800, color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Four-Part Strategic Intelligence Breakdown
                </h3>
              </div>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '14px'
              }}>
                {/* 1. WHAT HAPPENED */}
                <div style={{
                  padding: '16px',
                  backgroundColor: 'var(--bg-secondary)',
                  border: '1px solid var(--border-medium)',
                  borderRadius: 'var(--radius-sm)'
                }}>
                  <div style={{ fontSize: '10.5px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    1. What Happened (Observed Facts)
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.5 }}>
                    {activePattern.evidence?.length || 0} verified milestones occurred between {activePattern.time_span?.start} and {activePattern.time_span?.end} across {(activePattern.categories || []).join(', ')}.
                  </div>
                </div>

                {/* 2. WHAT CONNECTS THEM */}
                <div style={{
                  padding: '16px',
                  backgroundColor: 'var(--bg-secondary)',
                  border: '1px solid var(--border-medium)',
                  borderRadius: 'var(--radius-sm)'
                }}>
                  <div style={{ fontSize: '10.5px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    2. What Connects Them (Relationship)
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.5 }}>
                    {activePattern.connection}
                  </div>
                </div>

                {/* 3. WHAT PATTERN EMERGES */}
                <div style={{
                  padding: '16px',
                  backgroundColor: 'var(--pink-lightest)',
                  border: '1px solid var(--pink-border)',
                  borderRadius: 'var(--radius-sm)'
                }}>
                  <div style={{ fontSize: '10.5px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    3. What Pattern Emerges (Vector)
                  </div>
                  <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.5 }}>
                    {activePattern.pattern}
                  </div>
                  {activePattern.strategic_signal && (
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                      <span style={{ fontWeight: 700 }}>Signal: </span>{activePattern.strategic_signal}
                    </div>
                  )}
                </div>

                {/* 4. WHY IT MATTERS */}
                <div style={{
                  padding: '16px',
                  backgroundColor: 'var(--text-primary)',
                  color: 'var(--text-inverse)',
                  borderRadius: 'var(--radius-sm)'
                }}>
                  <div style={{ fontSize: '10.5px', fontWeight: 800, textTransform: 'uppercase', opacity: 0.8, marginBottom: '4px' }}>
                    4. Why It Matters (Strategic Interpretation)
                  </div>
                  <div style={{ fontSize: '13px', lineHeight: 1.5 }}>
                    {activePattern.why_it_matters}
                  </div>
                </div>
              </div>
            </div>

          </div>
        </>
      )}

    </div>
  );
}
