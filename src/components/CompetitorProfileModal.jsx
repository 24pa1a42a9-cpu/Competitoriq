import React, { useState, useEffect } from 'react';
import {
  X,
  ExternalLink,
  ShieldCheck,
  TrendingUp,
  Database,
  ArrowRight,
  Calendar,
  Zap,
  Activity,
  Sparkles,
  Globe,
  RefreshCw
} from 'lucide-react';
import { EVENTS, STRATEGIC_PATTERNS } from '../data/mockData';
import { competitorApi } from '../services/api';
import CompanyLogo from './CompanyLogo';
import CategoryIcon from './CategoryIcon';
import AgentMascot from './AgentMascot';

export default function CompetitorProfileModal({
  competitor,
  onClose,
  onOpenEvent,
  onOpenAnalyst
}) {
  const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'pricing', 'product', 'messaging', 'hiring', 'events', 'patterns'
  const [profile, setProfile] = useState(competitor);
  const [liveTimeline, setLiveTimeline] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!competitor) return;
    let isMounted = true;
    setIsLoading(true);

    // Fetch real profile details and timeline in parallel
    Promise.all([
      competitorApi.getCompetitor(competitor.id).catch(() => null),
      competitorApi.getCompetitorTimeline(competitor.id).catch(() => ({ timeline: [] }))
    ]).then(([backendProfile, timelineData]) => {
      if (!isMounted) return;
      if (backendProfile) {
        setProfile(prev => ({ ...prev, ...backendProfile }));
      }
      const evts = (timelineData && timelineData.timeline) ? timelineData.timeline : [];
      setLiveTimeline(evts);
      setIsLoading(false);
    });

    return () => { isMounted = false; };
  }, [competitor?.id]);

  if (!competitor) return null;

  // Filter fallback mock events if live timeline is empty and mock data matches
  const fallbackEvents = EVENTS.filter(e => e.competitorId === competitor.id);
  const displayEvents = liveTimeline.length > 0 ? liveTimeline : fallbackEvents;
  const compPatterns = (profile.patterns || STRATEGIC_PATTERNS.filter(p => p.competitorId === competitor.id)) || [];

  return (
    <>
      <div className="overlay-backdrop" onClick={onClose} />
      <div
        style={{
          position: 'fixed',
          top: '30px',
          bottom: '30px',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '960px',
          maxWidth: '94vw',
          backgroundColor: 'var(--bg-primary)',
          border: '1px solid var(--border-black)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-lg)',
          zIndex: 60,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{
          padding: '20px 28px',
          borderBottom: '1px solid var(--border-subtle)',
          backgroundColor: 'var(--bg-primary)',
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <CompanyLogo competitorId={profile.id} size={44} />
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px', flexWrap: 'wrap' }}>
                <span className="badge badge-black">{profile.stage || 'Tracked Entity'}</span>
                <span className="badge badge-pink">{profile.threatLevel || 'Active'} Threat</span>
                <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                  {profile.arrEstimate || 'Enterprise Scale'} • {profile.employeeCount || 'Monitored'}
                </span>
                {profile.website && (
                  <a
                    href={profile.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      fontSize: '11px',
                      color: 'var(--text-secondary)',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                      textDecoration: 'underline'
                    }}
                  >
                    <span>{profile.website.replace(/^https?:\/\//, '')}</span>
                    <ExternalLink size={10} />
                  </a>
                )}
              </div>
              <h1 style={{ fontSize: '22px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
                {profile.name}
              </h1>
              <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                {profile.tagline || profile.description || 'Frontier competitive technology intelligence profile.'}
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button
              onClick={() => onOpenAnalyst(`How has ${profile.name}'s strategy evolved over time?`)}
              className="btn btn-pink btn-sm"
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <Zap size={13} />
              <span>Ask Analyst about {profile.name}</span>
            </button>
            <button
              onClick={onClose}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: 'var(--text-secondary)',
                padding: '6px'
              }}
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Mascot Intelligence Takeaway Banner */}
        <div style={{
          padding: '12px 28px',
          backgroundColor: 'var(--pink-lightest)',
          borderBottom: '1px solid var(--pink-border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '16px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <AgentMascot size={32} state="explaining" />
            <div style={{ fontSize: '12.5px', color: 'var(--text-primary)' }}>
              <span style={{ fontWeight: 800 }}>Agent Takeaway: </span>
              <span>{profile.strategySummary || profile.description || `Autonomous monitoring of ${profile.name} enterprise positioning.`}</span>
            </div>
          </div>
          <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
            {displayEvents.length} TIMELINE MILESTONES
          </span>
        </div>

        {/* Navigation Tabs with Category Illustrations */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
          padding: '0 28px',
          borderBottom: '1px solid var(--border-subtle)',
          backgroundColor: 'var(--bg-secondary)',
          overflowX: 'auto'
        }}>
          {[
            { id: 'overview', label: 'Overview', category: 'strategy' },
            { id: 'events', label: `Timeline Events (${displayEvents.length})`, category: 'announcement' },
            { id: 'pricing', label: 'Pricing Evolution', category: 'pricing' },
            { id: 'product', label: 'Product Evolution', category: 'product' },
            { id: 'messaging', label: 'Messaging Evolution', category: 'messaging' },
            { id: 'hiring', label: 'Hiring Signals', category: 'hiring' },
            { id: 'patterns', label: `Strategic Patterns (${compPatterns.length})`, category: 'strategy' }
          ].map(tab => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '12px 14px',
                  fontSize: '12.5px',
                  fontWeight: isActive ? 700 : 500,
                  color: isActive ? 'var(--text-primary)' : 'var(--text-muted)',
                  borderBottom: isActive ? '2px solid var(--text-primary)' : '2px solid transparent',
                  background: 'none',
                  borderTop: 'none',
                  borderLeft: 'none',
                  borderRight: 'none',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap'
                }}
              >
                <CategoryIcon category={tab.category} size={15} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px 28px' }}>
          
          {/* OVERVIEW TAB */}
          {activeTab === 'overview' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {/* Why This Matters Callout */}
              <div className="card">
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                  <CategoryIcon category="strategy" size={16} />
                  <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                    Strategic Positioning
                  </span>
                </div>
                <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  {profile.whyThisMatters || profile.strategySummary || profile.description || 'Active competitive monitoring within enterprise technology and AI battlegrounds.'}
                </p>
              </div>

              {/* Battleground & Metrics Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '14px' }}>
                <div className="card" style={{ padding: '14px' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 700 }}>Primary Battleground</div>
                  <div style={{ fontSize: '13px', fontWeight: 700, marginTop: '4px' }}>{profile.primaryBattleground || profile.industry || 'Enterprise AI'}</div>
                </div>
                <div className="card" style={{ padding: '14px' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 700 }}>Industry & HQ</div>
                  <div style={{ fontSize: '13px', fontWeight: 700, marginTop: '4px' }}>
                    {profile.industry || 'Technology'} {profile.hq ? `• ${profile.hq}` : ''}
                  </div>
                </div>
                <div className="card" style={{ padding: '14px' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 700 }}>Hindsight Memory Bank</div>
                  <div style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', fontWeight: 700, marginTop: '4px' }}>
                    {profile.hindsightMemoryIdentifier || `competitor-${profile.id}`}
                  </div>
                </div>
              </div>

              {/* Company Narrative */}
              <div>
                <div style={{ fontSize: '12px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '8px' }}>
                  Competitor Intelligence Description
                </div>
                <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  {profile.description || profile.overview || `${profile.name} is continuously tracked across verified operational, commercial, and engineering milestones.`}
                </p>
              </div>
            </div>
          )}

          {/* CORROBORATED EVENTS TAB (Real Stored Timeline Events) */}
          {activeTab === 'events' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {displayEvents.length === 0 ? (
                <div className="card" style={{ padding: '40px 24px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  <AgentMascot size={40} state="watching" />
                  <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '12px' }}>
                    No Stored Events Yet
                  </div>
                  <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                    No timeline milestones have been ingested into Hindsight memory for {profile.name} yet.
                  </p>
                </div>
              ) : (
                displayEvents.map(evt => (
                  <div
                    key={evt.id}
                    onClick={() => onOpenEvent(evt)}
                    className="card"
                    style={{
                      padding: '16px 20px',
                      cursor: 'pointer',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '8px',
                      borderLeft: '4px solid var(--text-primary)'
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
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <CategoryIcon category={evt.category} size={14} />
                        <span className="badge badge-black">{evt.category || 'Milestone'}</span>
                        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{evt.date}</span>
                      </div>
                      {evt.sourceUrl && (
                        <a
                          href={evt.sourceUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={(e) => e.stopPropagation()}
                          style={{
                            fontSize: '11px',
                            color: 'var(--text-muted)',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                            textDecoration: 'underline'
                          }}
                        >
                          <span>{evt.sourceName || 'Source'}</span>
                          <ExternalLink size={10} />
                        </a>
                      )}
                    </div>
                    <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {evt.title}
                    </div>
                    {evt.description && (
                      <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                        {evt.description}
                      </p>
                    )}
                    <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '4px' }}>
                      <span style={{ fontSize: '11.5px', fontWeight: 700, color: 'var(--text-primary)', textDecoration: 'underline' }}>
                        View Corroborated Evidence →
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* PRICING EVOLUTION TAB */}
          {activeTab === 'pricing' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: 'var(--text-muted)' }}>
                <CategoryIcon category="pricing" size={16} />
                <span>Chronological record of public pricing schedule modifications, hidden surcharges, and contract minimums.</span>
              </div>

              {(!profile.pricingEvolution || profile.pricingEvolution.length === 0) ? (
                <div className="card" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
                  No historical pricing tiers logged yet in memory for {profile.name}.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {profile.pricingEvolution.map((p, idx) => (
                    <div
                      key={idx}
                      className="card"
                      style={{
                        borderLeft: '3px solid var(--text-primary)',
                        padding: '14px 18px',
                        backgroundColor: idx === profile.pricingEvolution.length - 1 ? 'var(--pink-lightest)' : 'var(--bg-primary)'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <span className="badge badge-black">{p.date}</span>
                        {idx === profile.pricingEvolution.length - 1 && (
                          <span className="badge badge-pink">Current Posture</span>
                        )}
                      </div>
                      <div style={{ fontSize: '14.5px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {p.tier}
                      </div>
                      <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                        {p.notes}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* PRODUCT EVOLUTION TAB */}
          {activeTab === 'product' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: 'var(--text-muted)' }}>
                <CategoryIcon category="product" size={16} />
                <span>Major architectural milestones, capability additions, and compliance certifications.</span>
              </div>

              {(!profile.productEvolution || profile.productEvolution.length === 0) ? (
                <div className="card" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
                  No isolated product evolution milestones logged yet in memory for {profile.name}.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {profile.productEvolution.map((p, idx) => (
                    <div key={idx} className="card" style={{ padding: '14px 18px', display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
                      <span className="badge badge-outline" style={{ marginTop: '2px' }}>{p.date}</span>
                      <div style={{ fontSize: '13.5px', fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.5 }}>
                        {p.milestone}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* MESSAGING EVOLUTION TAB */}
          {activeTab === 'messaging' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: 'var(--text-muted)' }}>
                <CategoryIcon category="messaging" size={16} />
                <span>How {profile.name} shifted their public hero banner and GTM pitch over time.</span>
              </div>

              {(!profile.messagingEvolution || profile.messagingEvolution.length === 0) ? (
                <div className="card" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
                  No messaging revisions logged yet in memory for {profile.name}.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {profile.messagingEvolution.map((m, idx) => (
                    <div
                      key={idx}
                      className="card"
                      style={{
                        padding: '16px 20px',
                        backgroundColor: idx === profile.messagingEvolution.length - 1 ? 'var(--pink-lightest)' : 'var(--bg-primary)',
                        borderColor: idx === profile.messagingEvolution.length - 1 ? 'var(--pink-border)' : 'var(--border-subtle)'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                        <span className="badge badge-black">{m.date}</span>
                        {idx === profile.messagingEvolution.length - 1 && (
                          <span className="badge badge-pink">Active Headline</span>
                        )}
                      </div>
                      <div style={{ fontSize: '15px', fontWeight: 700, fontStyle: 'italic', color: 'var(--text-primary)' }}>
                        {m.headline}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* HIRING SIGNALS TAB */}
          {activeTab === 'hiring' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: 'var(--text-muted)' }}>
                <CategoryIcon category="hiring" size={16} />
                <span>Key executive recruitment, team expansion trends, and department restructuring.</span>
              </div>

              {(!profile.hiringSignals || profile.hiringSignals.length === 0) ? (
                <div className="card" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
                  No executive hiring records logged yet in memory for {profile.name}.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {profile.hiringSignals.map((h, idx) => (
                    <div key={idx} className="card" style={{ padding: '14px 18px', display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
                      <span className="badge badge-pink" style={{ marginTop: '2px' }}>{h.date}</span>
                      <div style={{ fontSize: '13.5px', fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.5 }}>
                        {h.role}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* STRATEGIC PATTERNS TAB */}
          {activeTab === 'patterns' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {compPatterns.length === 0 ? (
                <div className="card" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
                  No multi-event strategic patterns identified yet for {profile.name}.
                </div>
              ) : (
                compPatterns.map(pat => (
                  <div key={pat.id} className="card" style={{ padding: '18px 20px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span className="badge badge-black">{pat.status || 'Active'}</span>
                      <span className="badge badge-pink">{pat.confidence || '90%'} Match</span>
                    </div>
                    <div style={{ fontSize: '15px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '6px' }}>
                      {pat.name}
                    </div>
                    <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '10px' }}>
                      {pat.whyItMatters || pat.description}
                    </p>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                      Observed timeframe: {pat.timePeriod || 'Continuous surveillance'}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

        </div>

        {/* Modal Footer */}
        <div style={{
          padding: '14px 28px',
          borderTop: '1px solid var(--border-subtle)',
          backgroundColor: 'var(--bg-secondary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <span style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>
            Hindsight Tracking Active • {displayEvents.length} events recorded
          </span>
          <button onClick={onClose} className="btn btn-outline btn-sm">
            Close Dossier
          </button>
        </div>
      </div>
    </>
  );
}
