import React, { useState, useEffect } from 'react';
import {
  Building2,
  TrendingUp,
  Database,
  ArrowRight,
  ShieldCheck,
  Zap,
  Clock,
  ExternalLink,
  ChevronRight,
  CheckCircle2,
  GitBranch,
  Sparkles
} from 'lucide-react';
import { COMPETITORS, EVENTS, STRATEGIC_PATTERNS, ALERTS } from '../data/mockData';
import { competitorApi } from '../services/api';
import AgentMascot from './AgentMascot';
import CategoryIcon from './CategoryIcon';
import CompanyLogo from './CompanyLogo';

export default function OverviewView({
  onSelectView,
  onSelectCompetitor,
  onSelectEvent,
  onSelectPattern
}) {
  const [competitors, setCompetitors] = useState([]);
  const [events, setEvents] = useState([]);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    competitorApi.getCompetitors()
      .then(d => { if (d && d.length > 0) setCompetitors(d); })
      .catch(e => console.warn('Could not load competitors in Overview:', e));

    competitorApi.getEvents({ limit: 10 })
      .then(evts => { if (evts && evts.length > 0) setEvents(evts); })
      .catch(e => console.warn('Could not load events in Overview:', e));

    competitorApi.getAlerts({ limit: 5 })
      .then(alts => { if (alts && alts.length > 0) setAlerts(alts); })
      .catch(e => console.warn('Could not load alerts in Overview:', e));
  }, []);

  const displayCompetitors = competitors.length > 0 ? competitors : COMPETITORS;
  const displayEvents = events.length > 0 ? events : EVENTS;
  const recentEvents = displayEvents.slice(0, 4);
  const unreadAlerts = alerts.length > 0 ? alerts.filter(a => a.status === 'Unread') : ALERTS.filter(a => a.status === 'Unread');
  const topPatterns = STRATEGIC_PATTERNS.slice(0, 3);
  const flagshipEvent = displayEvents[0] || EVENTS[0];

  return (
    <div className="content-body" style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      
      {/* Top Banner: Core Intelligence Story */}
      <div className="intel-story-banner">
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <span style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.08em' }}>
            INTELLIGENCE PIPELINE:
          </span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div className="intel-step active">
              <span className="intel-step-dot" />
              <span>EVENT</span>
            </div>
            <span style={{ color: 'var(--border-medium)' }}>➔</span>
            <div className="intel-step active">
              <span className="intel-step-dot" />
              <span>MEMORY</span>
            </div>
            <span style={{ color: 'var(--border-medium)' }}>➔</span>
            <div className="intel-step active">
              <span className="intel-step-dot" />
              <span>CONNECTION</span>
            </div>
            <span style={{ color: 'var(--border-medium)' }}>➔</span>
            <div className="intel-step active">
              <span className="intel-step-dot" />
              <span>PATTERN</span>
            </div>
            <span style={{ color: 'var(--border-medium)' }}>➔</span>
            <div className="intel-step active">
              <span className="intel-step-dot" />
              <span>INSIGHT</span>
            </div>
          </div>
        </div>
        <div className="cautious-pill">
          <ShieldCheck size={12} color="var(--text-primary)" />
          <span>AUTONOMOUS PERSISTENT REASONING</span>
        </div>
      </div>

      {/* SIGNATURE SECTION: "Choose a competitor to begin" Initial State with Mascot */}
      <div
        className="card"
        style={{
          padding: '24px 28px',
          backgroundColor: 'var(--pink-lightest)',
          border: '2px solid var(--text-primary)',
          boxShadow: 'var(--shadow-md)',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '20px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
            <AgentMascot
              size={58}
              state="curious"
              showBubble={false}
              className="mascot-floating"
            />
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <span className="badge badge-black" style={{ fontSize: '10.5px' }}>
                  System Ready
                </span>
                <span className="badge badge-pink" style={{ fontSize: '10.5px' }}>
                  Hindsight Memory Active
                </span>
                <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                  {displayCompetitors.length} Monitored Entities Initialized
                </span>
              </div>
              <h2 style={{ fontSize: '19px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
                Choose a competitor to begin intelligence analysis
              </h2>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                Select a monitored entity to trace chronological activity, connect multi-hop strategic dots, and recall verified episodic memories.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button
              onClick={() => onSelectView('competitors')}
              className="btn btn-outline btn-sm"
            >
              Browse Directory
            </button>
            <button
              onClick={() => onSelectView('timeline')}
              className="btn btn-primary btn-sm"
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <span>Explore Timeline</span>
              <ArrowRight size={13} />
            </button>
          </div>
        </div>

        {/* Competitor Quick-Pick Selector Strip */}
        <div style={{
          marginTop: '20px',
          padding: '16px 20px',
          backgroundColor: 'var(--bg-primary)',
          border: '1px solid var(--pink-border)',
          borderRadius: 'var(--radius-md)'
        }}>
          <div style={{ fontSize: '10px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: '10px' }}>
            Select a Rival to Begin Tracking:
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            {displayCompetitors.map(comp => (
              <button
                key={comp.id || comp.name}
                type="button"
                onClick={() => onSelectCompetitor(comp.id)}
                className="btn btn-outline btn-sm"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  backgroundColor: 'var(--bg-primary)',
                  borderColor: 'var(--border-medium)',
                  padding: '7px 12px',
                  borderRadius: 'var(--radius-sm)'
                }}
              >
                <CompanyLogo competitorId={comp.id} size={16} />
                <span style={{ fontWeight: 700, fontSize: '12px' }}>{comp.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Status Callout */}
        <div style={{
          marginTop: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '12.5px',
          color: 'var(--text-primary)'
        }}>
          <div>
            <span style={{ fontWeight: 800 }}>Status: </span>
            <span style={{ color: 'var(--text-secondary)' }}>
              Nothing selected yet — choose a competitor above to inspect verified milestones and episodic recall.
            </span>
          </div>
        </div>
      </div>

      {/* Top Metric Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '16px'
      }}>
        {/* Card 1 */}
        <div className="card" onClick={() => onSelectView('competitors')} style={{ cursor: 'pointer' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
              Monitored Competitors
            </span>
            <Building2 size={16} color="var(--text-primary)" />
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
            <span style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.03em' }}>
              {displayCompetitors.length}
            </span>
            <span className="badge badge-pink">All Active</span>
          </div>
          <div style={{ fontSize: '11.5px', color: 'var(--text-secondary)', marginTop: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <CompanyLogo competitorId="microsoft" size={16} />
            <CompanyLogo competitorId="google" size={16} />
            <CompanyLogo competitorId="openai" size={16} />
            <span style={{ marginLeft: '4px' }}>Microsoft, Google, OpenAI, AWS, Meta, Anthropic</span>
          </div>
        </div>

        {/* Card 2 */}
        <div className="card" onClick={() => onSelectView('timeline')} style={{ cursor: 'pointer' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
              Source-Backed Events
            </span>
            <Zap size={16} color="var(--text-primary)" />
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
            <span style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.03em' }}>
              {displayEvents.length}
            </span>
            <span className="badge badge-outline">100% Verified</span>
          </div>
          <div style={{ fontSize: '11.5px', color: 'var(--text-secondary)', marginTop: '8px' }}>
            Across products, pricing, talent & models
          </div>
        </div>

        {/* Card 3 */}
        <div className="card" onClick={() => onSelectView('memory')} style={{ cursor: 'pointer' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
              Persistent Hindsight Banks
            </span>
            <Database size={16} color="var(--text-primary)" />
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
            <span style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.03em' }}>
              6 Banks
            </span>
            <span className="badge badge-pink">Strictly Isolated</span>
          </div>
          <div style={{ fontSize: '11.5px', color: 'var(--text-secondary)', marginTop: '8px' }}>
            Zero cross-competitor memory contamination
          </div>
        </div>

        {/* Card 4 */}
        <div className="card" onClick={() => onSelectView('patterns')} style={{ cursor: 'pointer' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
              Detected Patterns
            </span>
            <TrendingUp size={16} color="var(--text-primary)" />
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
            <span style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.03em' }}>
              {topPatterns.length}
            </span>
            <span className="badge badge-black">98% Confidence</span>
          </div>
          <div style={{ fontSize: '11.5px', color: 'var(--text-secondary)', marginTop: '8px' }}>
            Multi-event causal hypotheses
          </div>
        </div>
      </div>

      {/* Two Column Strategic Delta Cards: "What changed recently?" & "What did we miss?" */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', gap: '20px' }}>
        
        {/* Section 1: What changed recently? */}
        <div className="card" style={{ borderColor: 'var(--pink-border)', backgroundColor: 'var(--pink-lightest)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: 'var(--text-primary)'
              }} />
              <h3 style={{ fontSize: '14px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                What changed recently?
              </h3>
            </div>
            <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
              Verified Ingestion Delta
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {recentEvents.length > 0 ? (
              recentEvents.slice(0, 2).map(evt => (
                <div
                  key={evt.id}
                  onClick={() => onSelectEvent(evt)}
                  style={{
                    backgroundColor: 'var(--bg-primary)',
                    padding: '12px 14px',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-subtle)',
                    cursor: 'pointer'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <CompanyLogo competitorId={evt.competitorId || evt.competitor_id} size={18} />
                      <span className="badge badge-black">{evt.competitorName || evt.competitor_name}</span>
                      <CategoryIcon category={evt.category || evt.event_type} size={14} />
                      <span style={{ fontSize: '11px', fontWeight: 600 }}>{evt.category || evt.event_type}</span>
                    </div>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{evt.date || evt.event_date}</span>
                  </div>
                  <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                    {evt.title}
                  </div>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                    {(evt.description || '').slice(0, 130)}...
                  </p>
                </div>
              ))
            ) : (
              <div style={{
                backgroundColor: 'var(--bg-primary)',
                padding: '16px',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-muted)',
                fontSize: '12px',
                textAlign: 'center'
              }}>
                No recent competitor changes logged in the database yet.
              </div>
            )}
          </div>
        </div>

        {/* Section 2: What did we miss? (Hindsight Synthesis) */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <GitBranch size={16} color="var(--text-primary)" />
              <h3 style={{ fontSize: '14px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                What did we miss? (Hindsight Synthesis)
              </h3>
            </div>
            <span className="badge badge-pink">Persistent Memory</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{
              backgroundColor: 'var(--bg-secondary)',
              padding: '12px 14px',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)'
            }}>
              <div style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', marginBottom: '4px' }}>
                MULTI-HOP CHRONOLOGICAL CONNECTION
              </div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                Connecting disparate events across multi-month horizons
              </div>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px', lineHeight: 1.5 }}>
                Without memory, point-in-time tools treat announcements as isolated events. CompetitorIQ retains events in Hindsight episodic banks, discovering hidden strategic transitions between partnerships, pricing updates, and executive hires.
              </p>
              <button
                onClick={() => onSelectView('dots')}
                style={{
                  marginTop: '8px',
                  background: 'none',
                  border: 'none',
                  fontSize: '11.5px',
                  fontWeight: 700,
                  color: 'var(--text-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  cursor: 'pointer',
                  padding: 0
                }}
              >
                <span>Explore Dot Connection workspace</span>
                <ChevronRight size={13} />
              </button>
            </div>

            <div style={{
              backgroundColor: 'var(--bg-secondary)',
              padding: '12px 14px',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)'
            }}>
              <div style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', marginBottom: '4px' }}>
                ISOLATED PERSISTENT MEMORY BANKS
              </div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                Zero cross-competitor memory contamination
              </div>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px', lineHeight: 1.5 }}>
                Each competitor possesses a strictly isolated Hindsight memory bank. Grounded reasoning prevents multi-tenant hallucinations while preserving verbatim source citations and timestamps.
              </p>
              <button
                onClick={() => onSelectView('memory')}
                style={{
                  marginTop: '8px',
                  background: 'none',
                  border: 'none',
                  fontSize: '11.5px',
                  fontWeight: 700,
                  color: 'var(--text-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  cursor: 'pointer',
                  padding: 0
                }}
              >
                <span>Inspect Hindsight Memory Banks</span>
                <ChevronRight size={13} />
              </button>
            </div>
          </div>
        </div>

      </div>

      {/* Main Grid: Recent Strategic Moves & Emerging Patterns */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px' }}>
        
        {/* Left: Recent Strategic Moves Feed */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <h3 style={{ fontSize: '15px', fontWeight: 700, letterSpacing: '-0.01em' }}>
              Recent Strategic Moves
            </h3>
            <button
              onClick={() => onSelectView('timeline')}
              className="btn btn-ghost btn-sm"
              style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <span>View Full Timeline</span>
              <ChevronRight size={14} />
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {recentEvents.map(evt => (
              <div
                key={evt.id}
                onClick={() => onSelectEvent(evt)}
                className="card"
                style={{
                  padding: '14px 16px',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'var(--text-primary)';
                  e.currentTarget.style.backgroundColor = 'var(--pink-lightest)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border-subtle)';
                  e.currentTarget.style.backgroundColor = 'var(--bg-primary)';
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CompanyLogo competitorId={evt.competitorId || evt.competitor_id} size={18} />
                    <span style={{ fontWeight: 700, fontSize: '12.5px' }}>{evt.competitorName || evt.competitor_name}</span>
                    <span className="badge badge-pink" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <CategoryIcon category={evt.category || evt.event_type} size={12} />
                      <span>{evt.category || evt.event_type}</span>
                    </span>
                  </div>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{evt.date || evt.event_date}</span>
                </div>
                <div style={{ fontSize: '13.5px', fontWeight: 600, color: 'var(--text-primary)' }}>
                  {evt.title}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span>Source: {evt.sourceName || evt.source_name}</span>
                  <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>View Evidence →</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Emerging Strategic Patterns */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <h3 style={{ fontSize: '15px', fontWeight: 700, letterSpacing: '-0.01em' }}>
              Detected Strategic Patterns
            </h3>
            <button
              onClick={() => onSelectView('patterns')}
              className="btn btn-ghost btn-sm"
              style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <span>All Patterns</span>
              <ChevronRight size={14} />
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {topPatterns.map(pat => (
              <div
                key={pat.id}
                onClick={() => onSelectPattern(pat)}
                className="card"
                style={{
                  padding: '16px',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'var(--text-primary)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border-subtle)';
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span className="badge badge-outline">{pat.competitorName || pat.competitor}</span>
                  <span className="badge badge-pink">{pat.confidenceScore || 95}% Match</span>
                </div>
                <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>
                  {pat.patternName || pat.name}
                </div>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.45, marginBottom: '10px' }}>
                  {(pat.whyItMatters || pat.summary || '').slice(0, 110)}...
                </p>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)' }}>
                  <span>Spans: {pat.timeframe || pat.timePeriod}</span>
                  <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Analyze Pattern →</span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
}
