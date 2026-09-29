import React, { useState, useEffect } from 'react';
import {
  Columns,
  ShieldCheck,
  AlertCircle,
  CheckCircle,
  ArrowRight,
  Sparkles,
  Database,
  ExternalLink,
  Calendar,
  Link2,
  RefreshCw,
  Zap,
  Clock,
  TrendingUp,
  FileText
} from 'lucide-react';
import AgentMascot from './AgentMascot';
import competitorApi from '../services/api';

const DEFAULT_COMPETITORS = [
  { id: 'Microsoft', name: 'Microsoft', defaultQuery: "How has Microsoft's AI strategy evolved?" },
  { id: 'Google', name: 'Google', defaultQuery: "How has Google's AI strategy evolved?" },
  { id: 'OpenAI', name: 'OpenAI', defaultQuery: "How has OpenAI's AI strategy evolved?" },
  { id: 'Amazon / AWS', name: 'Amazon / AWS', defaultQuery: "What is Amazon/AWS's strategy with Bedrock and custom silicon?" },
  { id: 'Anthropic', name: 'Anthropic', defaultQuery: "How has Anthropic's AI strategy evolved?" },
  { id: 'Meta', name: 'Meta', defaultQuery: "What is Meta's open-weight foundation model strategy?" }
];

export default function BeforeAfterView() {
  const [selectedCompetitor, setSelectedCompetitor] = useState('Microsoft');
  const [queryInput, setQueryInput] = useState("How has Microsoft's AI strategy evolved?");
  const [loading, setLoading] = useState(false);
  const [comparisonData, setComparisonData] = useState(null);
  const [error, setError] = useState(null);

  // Benchmark comparison runs when the user explicitly triggers it
  const handleSelectCompetitor = (comp) => {
    setSelectedCompetitor(comp.name);
    setQueryInput(comp.defaultQuery);
  };

  const handleRunBenchmark = async (compName = selectedCompetitor, query = queryInput) => {
    setLoading(true);
    setError(null);
    try {
      const res = await competitorApi.getBeforeAfterAnalysis(compName, query);
      setComparisonData(res);
    } catch (err) {
      console.error('Failed to load Before/After comparison:', err);
      setError(err.message || 'Failed to fetch benchmark analysis from backend.');
    } finally {
      setLoading(false);
    }
  };

  const isInsufficient = comparisonData?.insufficient_memory === true;
  const before = comparisonData?.before;
  const after = comparisonData?.after;
  const improvement = comparisonData?.improvement;

  return (
    <div className="content-body" style={{ display: 'flex', flexDirection: 'column', gap: '26px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            Why Memory Changes Intelligence
          </h1>
          <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Core product demonstration: how single-event vacuum summarization fails, and how Hindsight persistent episodic memory connects moves across time into strategic foresight.
          </p>
        </div>

        <div className="cautious-pill">
          <Columns size={13} color="var(--text-primary)" />
          <span>BENCHMARK COMPARISON</span>
        </div>
      </div>

      {/* Competitor Selector Tabs */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '12px'
      }}>
        {DEFAULT_COMPETITORS.map(comp => {
          const isSelected = comp.name.toLowerCase() === selectedCompetitor.toLowerCase();
          return (
            <div
              key={comp.id}
              onClick={() => handleSelectCompetitor(comp)}
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
                {comp.name === 'Anthropic' ? 'Edge Case Test' : 'Monitored Target'}
              </div>
              <div style={{ fontSize: '14px', fontWeight: 800, color: 'var(--text-primary)' }}>
                {comp.name}
              </div>
            </div>
          );
        })}
      </div>

      {/* Strategic Query Inquiry Bar */}
      <div style={{
        padding: '16px 20px',
        backgroundColor: 'var(--bg-secondary)',
        border: '1px solid var(--border-medium)',
        borderRadius: 'var(--radius-md)',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        flexWrap: 'wrap'
      }}>
        <div style={{ flex: 1, minWidth: '280px' }}>
          <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '4px' }}>
            Evaluation Inquiry:
          </div>
          <input
            type="text"
            value={queryInput}
            onChange={(e) => setQueryInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleRunBenchmark()}
            placeholder="Ask a strategic evolution question..."
            style={{
              width: '100%',
              padding: '8px 12px',
              fontSize: '13.5px',
              border: '1px solid var(--border-medium)',
              borderRadius: '6px',
              backgroundColor: 'var(--bg-primary)',
              color: 'var(--text-primary)',
              fontWeight: 600,
              outline: 'none'
            }}
          />
        </div>
        <button
          onClick={() => handleRunBenchmark()}
          disabled={loading}
          className="btn btn-primary"
          style={{ padding: '9px 18px', display: 'flex', alignItems: 'center', gap: '8px' }}
        >
          {loading ? (
            <>
              <RefreshCw size={14} className="spin" />
              <span>Synthesizing...</span>
            </>
          ) : (
            <>
              <Zap size={14} />
              <span>Run Benchmark</span>
            </>
          )}
        </button>
      </div>

      {/* CORE VISUAL FORMULA WITH MASCOT */}
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          <div style={{ padding: '8px 12px', backgroundColor: 'var(--bg-primary)', border: '1px solid var(--border-medium)', borderRadius: '6px', fontSize: '11.5px', fontWeight: 800 }}>
            EVENT
          </div>
          <span style={{ fontWeight: 800 }}>➔</span>
          <div style={{ padding: '8px 12px', backgroundColor: 'var(--bg-primary)', border: '1px solid var(--border-medium)', borderRadius: '6px', fontSize: '11.5px', fontWeight: 800 }}>
            MEMORY
          </div>
          <span style={{ fontWeight: 800 }}>➔</span>
          <div style={{ padding: '8px 12px', backgroundColor: 'var(--bg-primary)', border: '1px solid var(--border-medium)', borderRadius: '6px', fontSize: '11.5px', fontWeight: 800 }}>
            RECALL
          </div>
          <span style={{ fontWeight: 800 }}>➔</span>
          <div style={{ padding: '8px 12px', backgroundColor: 'var(--bg-primary)', border: '1px solid var(--border-medium)', borderRadius: '6px', fontSize: '11.5px', fontWeight: 800 }}>
            CONNECTION
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <AgentMascot size={46} state={loading ? 'searching' : isInsufficient ? 'cautious' : 'found'} />
          <span style={{ fontSize: '18px', fontWeight: 900 }}>➔</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          <div style={{ padding: '8px 12px', backgroundColor: 'var(--text-primary)', color: 'var(--text-inverse)', borderRadius: '6px', fontSize: '11.5px', fontWeight: 800 }}>
            PATTERN
          </div>
          <span style={{ fontWeight: 800 }}>➔</span>
          <div style={{ padding: '8px 12px', backgroundColor: '#ea96a5', color: '#0a0a0a', border: '1px solid var(--border-black)', borderRadius: '6px', fontSize: '11.5px', fontWeight: 800 }}>
            STRATEGIC INSIGHT
          </div>
        </div>
      </div>

      {/* ERROR BANNER */}
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

      {/* INSUFFICIENT MEMORY STATE (Requirement 14) */}
      {isInsufficient && !loading && (
        <div className="card" style={{
          padding: '24px',
          backgroundColor: 'var(--bg-primary)',
          border: '2px solid var(--border-medium)',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '16px'
        }}>
          <AgentMascot size={52} state="cautious" />
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span className="badge badge-outline">Insufficient Memory Baseline</span>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Bank: {comparisonData.bank_id || 'isolated'}</span>
            </div>
            <h3 style={{ fontSize: '17px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '6px' }}>
              Not enough historical memory yet for {comparisonData.competitor}.
            </h3>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '12px' }}>
              {comparisonData.guidance || 'Add more source-backed competitor events to demonstrate how persistent memory improves analysis.'}
            </p>
            <div style={{
              padding: '10px 14px',
              backgroundColor: 'var(--pink-lightest)',
              border: '1px solid var(--pink-border)',
              borderRadius: '6px',
              fontSize: '12px',
              color: 'var(--text-primary)',
              fontWeight: 600
            }}>
              💡 Notice: CompetitorIQ never fabricates historical facts when telemetry is absent. Genuine persistent memory requires real event ingestion.
            </div>
          </div>
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
          backgroundColor: 'var(--bg-primary)',
          border: '1px solid var(--border-subtle)'
        }}>
          <AgentMascot size={64} state="searching" />
          <div style={{ textAlign: 'center' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)' }}>
              Executing Real-Time Benchmark...
            </h3>
            <p style={{ fontSize: '12.5px', color: 'var(--text-muted)', marginTop: '4px' }}>
              1. Simulating limited context baseline • 2. Recalling Hindsight episodic memory • 3. Groq temporal synthesis
            </p>
          </div>
        </div>
      )}

      {/* INITIAL READY STATE */}
      {!loading && !comparisonData && (
        <div className="card" style={{
          padding: '48px 24px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '12px',
          backgroundColor: 'var(--bg-secondary)',
          border: '1px solid var(--border-subtle)',
          textAlign: 'center'
        }}>
          <AgentMascot size={58} state="curious" />
          <h3 style={{ fontSize: '17px', fontWeight: 800, color: 'var(--text-primary)' }}>
            Choose a competitor and click 'Run Benchmark'
          </h3>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', maxWidth: '520px', lineHeight: 1.5 }}>
            Compare how standard stateless LLMs with limited context analyze competitor moves versus CompetitorIQ with persistent Hindsight episodic memory.
          </p>
          <button
            onClick={() => handleRunBenchmark(selectedCompetitor, queryInput)}
            className="btn btn-primary"
            style={{ marginTop: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}
          >
            <Sparkles size={15} />
            <span>Run Benchmark for {selectedCompetitor}</span>
          </button>
        </div>
      )}

      {/* SIDE-BY-SIDE BEFORE VS AFTER COMPARISON */}
      {!loading && !isInsufficient && before && after && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
            
            {/* LEFT COLUMN: BEFORE (Limited Context) */}
            <div className="card" style={{
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
              backgroundColor: 'var(--bg-secondary)',
              border: '1px solid var(--border-medium)'
            }}>
              {/* Header */}
              <div style={{ borderBottom: '1px solid var(--border-subtle)', paddingBottom: '14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <AlertCircle size={15} color="var(--text-muted)" />
                    <span className="badge badge-outline">Standard LLM / Limited Context</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <AgentMascot size={26} state="cautious" />
                    <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)' }}>
                      "I have limited context"
                    </span>
                  </div>
                </div>

                <h3 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-secondary)' }}>
                  BEFORE MEMORY
                </h3>
                <div style={{ fontSize: '11.5px', color: 'var(--text-muted)', marginTop: '2px' }}>
                  Context Type: <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{before.context_type}</span> • Memories Recalled: <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{before.memory_used?.count || 0}</span>
                </div>
              </div>

              {/* Observable Baseline Event (if any) */}
              {before.key_events && before.key_events.length > 0 && (
                <div style={{
                  padding: '12px 14px',
                  backgroundColor: 'var(--bg-primary)',
                  border: '1px solid var(--border-medium)',
                  borderRadius: 'var(--radius-sm)'
                }}>
                  <div style={{ fontSize: '10.5px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '3px' }}>
                    Isolated Observable Move:
                  </div>
                  <div style={{ fontSize: '13px', fontWeight: 800, color: 'var(--text-primary)' }}>
                    {before.key_events[0].title}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                    Date: {before.key_events[0].date} • Type: {before.key_events[0].event_type}
                  </div>
                </div>
              )}

              {/* Answer Preview */}
              <div style={{
                padding: '16px',
                backgroundColor: 'var(--bg-primary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                fontSize: '13px',
                lineHeight: 1.6,
                color: 'var(--text-secondary)'
              }}>
                {before.answer}
              </div>

              {/* Limitations */}
              <div>
                <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '8px' }}>
                  Critical Intelligence Failures:
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {before.limitations && before.limitations.map((lim, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                      <span style={{ color: 'var(--text-primary)', fontWeight: 800 }}>✕</span>
                      <span>{lim}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div style={{
                marginTop: 'auto',
                padding: '10px 12px',
                backgroundColor: 'var(--bg-primary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                fontSize: '11px',
                color: 'var(--text-muted)'
              }}>
                Verdict: Recency-biased news summarization with zero historical trajectory or pattern foresight.
              </div>
            </div>

            {/* RIGHT COLUMN: AFTER (Hindsight Memory) */}
            <div className="card" style={{
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
              backgroundColor: 'var(--pink-lightest)',
              border: '2px solid var(--text-primary)'
            }}>
              {/* Header */}
              <div style={{ borderBottom: '1px solid var(--pink-border)', paddingBottom: '14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Database size={15} color="var(--text-primary)" />
                    <span className="badge badge-black">Hindsight Persistent Memory</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <AgentMascot size={26} state="found" />
                    <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-primary)' }}>
                      "I found connections across your competitor's history."
                    </span>
                  </div>
                </div>

                <h3 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)' }}>
                  AFTER HINDSIGHT
                </h3>
                <div style={{ fontSize: '11.5px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  Context Type: <span style={{ fontWeight: 700 }}>{after.context_type}</span> • Recalled: <span style={{ fontWeight: 700 }}>{after.memory_used?.count || 0} memories</span> ({after.memory_used?.earliest || 'Past'} → {after.memory_used?.latest || 'Present'})
                </div>
              </div>

              {/* Detected Pattern Highlight */}
              {after.pattern && (
                <div style={{
                  padding: '12px 14px',
                  backgroundColor: 'var(--bg-primary)',
                  border: '1px solid var(--pink-border)',
                  borderRadius: 'var(--radius-sm)'
                }}>
                  <div style={{ fontSize: '10.5px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '3px' }}>
                    Detected Behavioral Pattern:
                  </div>
                  <div style={{ fontSize: '14px', fontWeight: 800, color: 'var(--text-primary)' }}>
                    {after.pattern}
                  </div>
                  {after.strategic_signal && (
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px', lineHeight: 1.4 }}>
                      <span style={{ fontWeight: 700 }}>Signal:</span> {after.strategic_signal}
                    </div>
                  )}
                </div>
              )}

              {/* Answer Preview */}
              <div style={{
                padding: '16px',
                backgroundColor: 'var(--bg-primary)',
                border: '1px solid var(--pink-border)',
                borderRadius: 'var(--radius-sm)',
                fontSize: '13px',
                lineHeight: 1.6,
                color: 'var(--text-primary)',
                fontWeight: 500
              }}>
                {after.answer}
              </div>

              {/* Temporal Connections */}
              {after.connections && after.connections.length > 0 && (
                <div>
                  <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '8px' }}>
                    Temporal Connections Across History:
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {after.connections.slice(0, 3).map((conn, i) => (
                      <div key={i} style={{
                        padding: '10px 12px',
                        backgroundColor: 'var(--bg-primary)',
                        border: '1px solid var(--pink-border)',
                        borderRadius: '6px',
                        fontSize: '12px',
                        lineHeight: 1.4
                      }}>
                        <div style={{ fontWeight: 800, color: 'var(--text-primary)', marginBottom: '2px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <Link2 size={12} />
                          <span>{Array.isArray(conn.events) ? conn.events.join(' ➔ ') : conn.relationship || 'Connected Milestone'}</span>
                        </div>
                        <div style={{ color: 'var(--text-secondary)', fontSize: '11.5px' }}>
                          {conn.explanation || conn.relationship}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Strategic Value Footer */}
              <div style={{
                marginTop: 'auto',
                padding: '10px 12px',
                backgroundColor: 'var(--text-primary)',
                color: 'var(--text-inverse)',
                borderRadius: 'var(--radius-sm)',
                fontSize: '11px',
                fontWeight: 700
              }}>
                Confidence: {String(after.confidence || 'HIGH').toUpperCase()} • Grounded in {after.memory_used?.count || 0} isolated Hindsight memories.
              </div>
            </div>

          </div>

          {/* VISUAL MEMORY TRAIL (Requirement 11) */}
          <div className="card" style={{ padding: '24px', backgroundColor: 'var(--bg-primary)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)' }}>
                  Hindsight Episodic Memory Trail
                </h3>
                <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  Visualizing how discrete events retained across months converge into unified recall.
                </p>
              </div>
              <span className="badge badge-black">
                {after.memory_used?.count || 0} Stored Nodes
              </span>
            </div>

            {/* Trail nodes diagram */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '12px',
              overflowX: 'auto',
              padding: '16px 8px'
            }}>
              {/* Retain Label */}
              <div style={{
                padding: '8px 14px',
                backgroundColor: 'var(--bg-secondary)',
                border: '1px solid var(--border-medium)',
                borderRadius: '6px',
                fontSize: '12px',
                fontWeight: 800,
                textAlign: 'center',
                whiteSpace: 'nowrap'
              }}>
                RETAIN ➔
              </div>

              {/* Historical Nodes */}
              {(after.key_events || []).slice(0, 4).map((ke, idx) => (
                <React.Fragment key={idx}>
                  <div style={{
                    padding: '10px 14px',
                    backgroundColor: 'var(--pink-lightest)',
                    border: '1px solid var(--pink-border)',
                    borderRadius: '8px',
                    minWidth: '160px',
                    maxWidth: '220px'
                  }}>
                    <div style={{ fontSize: '10px', fontWeight: 800, color: 'var(--text-muted)' }}>
                      {ke.date || 'Historical Node'}
                    </div>
                    <div style={{ fontSize: '12px', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px', lineHeight: 1.3 }}>
                      {ke.title?.length > 45 ? ke.title.substring(0, 45) + '...' : ke.title}
                    </div>
                    <span className="badge badge-outline" style={{ marginTop: '6px', fontSize: '9.5px' }}>
                      {ke.event_type || 'Milestone'}
                    </span>
                  </div>

                  <ArrowRight size={16} color="var(--text-muted)" style={{ flexShrink: 0 }} />
                </React.Fragment>
              ))}

              {/* Recall & Insight Box */}
              <div style={{
                padding: '10px 16px',
                backgroundColor: 'var(--text-primary)',
                color: 'var(--text-inverse)',
                borderRadius: '8px',
                textAlign: 'center',
                whiteSpace: 'nowrap',
                flexShrink: 0
              }}>
                <div style={{ fontSize: '10px', textTransform: 'uppercase', opacity: 0.8, fontWeight: 700 }}>
                  RECALL ➔ INSIGHT
                </div>
                <div style={{ fontSize: '13px', fontWeight: 800 }}>
                  Strategic Foresight
                </div>
              </div>
            </div>
          </div>

          {/* "WHAT HINDSIGHT ADDED" SECTION (Requirement 12) */}
          <div className="card" style={{ padding: '24px', backgroundColor: 'var(--pink-lightest)', border: '2px solid var(--border-black)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
              <Sparkles size={18} color="var(--text-primary)" />
              <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)' }}>
                What Hindsight Added
              </h3>
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '16px'
            }}>
              <div style={{ padding: '12px', backgroundColor: 'var(--bg-primary)', borderRadius: '6px', border: '1px solid var(--pink-border)' }}>
                <div style={{ fontSize: '10.5px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 800 }}>
                  Historical Context
                </div>
                <div style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>
                  {after.memory_used?.count || 0} memories
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                  {after.memory_used?.earliest ? `${after.memory_used.earliest} → ${after.memory_used.latest}` : 'Multi-quarter span'}
                </div>
              </div>

              <div style={{ padding: '12px', backgroundColor: 'var(--bg-primary)', borderRadius: '6px', border: '1px solid var(--pink-border)' }}>
                <div style={{ fontSize: '10.5px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 800 }}>
                  Additional Events
                </div>
                <div style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>
                  +{improvement?.additional_events || 0} analyzed
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                  Compared to 1 isolated move
                </div>
              </div>

              <div style={{ padding: '12px', backgroundColor: 'var(--bg-primary)', borderRadius: '6px', border: '1px solid var(--pink-border)' }}>
                <div style={{ fontSize: '10.5px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 800 }}>
                  Connections Discovered
                </div>
                <div style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>
                  {improvement?.new_connections || 0} relationships
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                  Connecting products, hiring, pricing
                </div>
              </div>

              <div style={{ padding: '12px', backgroundColor: 'var(--bg-primary)', borderRadius: '6px', border: '1px solid var(--pink-border)' }}>
                <div style={{ fontSize: '10.5px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 800 }}>
                  Pattern Identified
                </div>
                <div style={{ fontSize: '14px', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>
                  {after.pattern || 'Trajectory Detected'}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                  Visible only across timeline
                </div>
              </div>
            </div>
          </div>

          {/* EVIDENCE EXPLORER (Requirement 13) */}
          <div className="card" style={{ padding: '24px', backgroundColor: 'var(--bg-primary)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)' }}>
                  Supporting Evidence Explorer
                </h3>
                <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  Inspect every verified source-backed milestone powering this synthesis. Zero fabricated links.
                </p>
              </div>
              <span className="badge badge-outline">
                {after.evidence ? after.evidence.length : (after.key_events ? after.key_events.length : 0)} Sources Grounded
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {(after.evidence && after.evidence.length > 0 ? after.evidence : after.key_events || []).map((ev, idx) => {
                const title = ev.title || ev.text || 'Intelligence Citation';
                const date = ev.date || 'Historical';
                const type = ev.category || ev.event_type || 'Product';
                const source = ev.source || 'Official Corporate Record';
                const url = ev.source_url;

                return (
                  <div
                    key={idx}
                    style={{
                      padding: '12px 16px',
                      backgroundColor: 'var(--bg-secondary)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      gap: '16px'
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '3px' }}>
                        <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-muted)' }}>
                          {date}
                        </span>
                        <span className="badge badge-outline" style={{ fontSize: '10px' }}>
                          {type}
                        </span>
                        <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                          • {source}
                        </span>
                      </div>
                      <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.4 }}>
                        {title}
                      </div>
                    </div>

                    {url ? (
                      <a
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-outline"
                        style={{
                          padding: '6px 12px',
                          fontSize: '11.5px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                          flexShrink: 0
                        }}
                      >
                        <span>View Source</span>
                        <ExternalLink size={12} />
                      </a>
                    ) : (
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)', flexShrink: 0 }}>
                        Verified Internal Telemetry
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}

    </div>
  );
}
