import React, { useState, useEffect } from 'react';
import { Search, Sparkles, FileText, Bell, RefreshCw, X, ArrowRight } from 'lucide-react';
import { EVENTS, COMPETITORS, HINDSIGHT_MEMORIES } from '../data/mockData';
import { competitorApi } from '../services/api';

export default function Header({
  currentView,
  onSelectView,
  onSelectCompetitor,
  onSelectEvent,
  alertsCount = 2
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearchModal, setShowSearchModal] = useState(false);
  const [competitors, setCompetitors] = useState([]);

  useEffect(() => {
    competitorApi.getCompetitors()
      .then(data => {
        if (data && data.length > 0) setCompetitors(data);
      })
      .catch(err => console.warn('Could not load competitors in Header:', err));
  }, []);

  // View Title Mapping
  const titles = {
    overview: 'Intelligence Overview',
    competitors: 'Competitor Directory',
    timeline: 'Activity Timeline',
    dots: 'Connect the Dots',
    patterns: 'Strategic Patterns',
    memory: 'Hindsight Memory Explorer',
    analyst: 'AI Analyst Query Interface',
    'before-after': 'Before vs After Reasoning',
    alerts: 'Detected Alerts & Signals',
    comparison: 'Competitive Matrix Comparison',
    report: 'Executive Intelligence Report'
  };

  // Search Results
  const activeCompetitors = competitors.length > 0 ? competitors : COMPETITORS;

  const filteredEvents = searchQuery.trim()
    ? EVENTS.filter(e =>
        e.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        e.competitorName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        e.category.toLowerCase().includes(searchQuery.toLowerCase())
      ).slice(0, 4)
    : [];

  const filteredCompetitors = searchQuery.trim()
    ? activeCompetitors.filter(c =>
        c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (c.strategySummary && c.strategySummary.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (c.description && c.description.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    : [];

  const filteredMemories = searchQuery.trim()
    ? HINDSIGHT_MEMORIES.filter(m =>
        m.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
        m.competitorName.toLowerCase().includes(searchQuery.toLowerCase())
      ).slice(0, 3)
    : [];

  const hasResults = filteredEvents.length > 0 || filteredCompetitors.length > 0 || filteredMemories.length > 0;

  return (
    <header style={{
      height: '60px',
      borderBottom: '1px solid var(--border-subtle)',
      backgroundColor: 'var(--bg-primary)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 32px',
      position: 'sticky',
      top: 0,
      zIndex: 20
    }}>
      {/* Title & Breadcrumbs */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: 'var(--text-muted)' }}>
          <span>CompetitorIQ</span>
          <span>/</span>
          <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
            {titles[currentView] || 'Intelligence'}
          </span>
        </div>

        {/* Live Status Pill */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '2px 8px',
          backgroundColor: 'var(--pink-lightest)',
          border: '1px solid var(--pink-border)',
          borderRadius: 'var(--radius-full)',
          fontSize: '11px',
          fontFamily: 'var(--font-mono)',
          color: 'var(--text-secondary)'
        }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: 'var(--text-primary)' }} />
          <span>Sync: {activeCompetitors.length} active rivals • Hindsight Active</span>
        </div>
      </div>

      {/* Center Search Input */}
      <div style={{ position: 'relative', width: '360px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          backgroundColor: 'var(--bg-secondary)',
          border: '1px solid var(--border-medium)',
          borderRadius: 'var(--radius-md)',
          padding: '6px 12px'
        }}>
          <Search size={14} color="var(--text-muted)" />
          <input
            type="text"
            placeholder="Search events, competitors, memories..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setShowSearchModal(true);
            }}
            onFocus={() => setShowSearchModal(true)}
            style={{
              border: 'none',
              background: 'transparent',
              fontSize: '12px',
              fontFamily: 'var(--font-sans)',
              color: 'var(--text-primary)',
              outline: 'none',
              width: '100%'
            }}
          />
          {searchQuery && (
            <button
              onClick={() => {
                setSearchQuery('');
                setShowSearchModal(false);
              }}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}
            >
              <X size={14} />
            </button>
          )}
        </div>

        {/* Search Results Dropdown */}
        {showSearchModal && searchQuery.trim() && (
          <div style={{
            position: 'absolute',
            top: '42px',
            left: 0,
            right: 0,
            backgroundColor: 'var(--bg-primary)',
            border: '1px solid var(--border-black)',
            borderRadius: 'var(--radius-md)',
            boxShadow: 'var(--shadow-lg)',
            padding: '12px',
            maxHeight: '420px',
            overflowY: 'auto',
            zIndex: 100
          }}>
            {!hasResults ? (
              <div style={{ padding: '16px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '12px' }}>
                No events or memories found matching "{searchQuery}"
              </div>
            ) : (
              <div>
                {/* Competitors */}
                {filteredCompetitors.length > 0 && (
                  <div style={{ marginBottom: '12px' }}>
                    <div style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '6px' }}>
                      Competitors
                    </div>
                    {filteredCompetitors.map(c => (
                      <div
                        key={c.id}
                        onClick={() => {
                          onSelectCompetitor(c.id);
                          setShowSearchModal(false);
                          setSearchQuery('');
                        }}
                        style={{
                          padding: '6px 8px',
                          borderRadius: 'var(--radius-sm)',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          fontSize: '12px',
                          border: '1px solid transparent'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = 'var(--pink-lightest)';
                          e.currentTarget.style.borderColor = 'var(--pink-border)';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = 'transparent';
                          e.currentTarget.style.borderColor = 'transparent';
                        }}
                      >
                        <span style={{ fontWeight: 600 }}>{c.name}</span>
                        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{c.arrEstimate}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Events */}
                {filteredEvents.length > 0 && (
                  <div style={{ marginBottom: '12px' }}>
                    <div style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '6px' }}>
                      Corroborated Events
                    </div>
                    {filteredEvents.map(e => (
                      <div
                        key={e.id}
                        onClick={() => {
                          onSelectEvent(e);
                          setShowSearchModal(false);
                          setSearchQuery('');
                        }}
                        style={{
                          padding: '6px 8px',
                          borderRadius: 'var(--radius-sm)',
                          cursor: 'pointer',
                          marginBottom: '4px',
                          border: '1px solid transparent'
                        }}
                        onMouseEnter={(el) => {
                          el.currentTarget.style.backgroundColor = 'var(--pink-lightest)';
                          el.currentTarget.style.borderColor = 'var(--pink-border)';
                        }}
                        onMouseLeave={(el) => {
                          el.currentTarget.style.backgroundColor = 'transparent';
                          el.currentTarget.style.borderColor = 'transparent';
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--text-muted)' }}>
                          <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{e.competitorName}</span>
                          <span>•</span>
                          <span>{e.date}</span>
                        </div>
                        <div style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-primary)' }}>
                          {e.title}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Memories */}
                {filteredMemories.length > 0 && (
                  <div>
                    <div style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '6px' }}>
                      Hindsight Memory Nodes
                    </div>
                    {filteredMemories.map(m => (
                      <div
                        key={m.id}
                        onClick={() => {
                          onSelectView('memory');
                          setShowSearchModal(false);
                          setSearchQuery('');
                        }}
                        style={{
                          padding: '6px 8px',
                          borderRadius: 'var(--radius-sm)',
                          cursor: 'pointer',
                          marginBottom: '4px',
                          border: '1px solid transparent'
                        }}
                        onMouseEnter={(el) => {
                          el.currentTarget.style.backgroundColor = 'var(--pink-lightest)';
                          el.currentTarget.style.borderColor = 'var(--pink-border)';
                        }}
                        onMouseLeave={(el) => {
                          el.currentTarget.style.backgroundColor = 'transparent';
                          el.currentTarget.style.borderColor = 'transparent';
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '10px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                          <span>{m.id}</span>
                          <span>•</span>
                          <span>{m.competitorName}</span>
                        </div>
                        <div style={{ fontSize: '11.5px', color: 'var(--text-secondary)' }}>
                          {m.content.slice(0, 90)}...
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Right Quick Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <button
          onClick={() => onSelectView('analyst')}
          className="btn btn-outline btn-sm"
          style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
        >
          <Sparkles size={13} />
          <span>Ask Analyst</span>
        </button>

        <button
          onClick={() => onSelectView('report')}
          className="btn btn-primary btn-sm"
          style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
        >
          <FileText size={13} />
          <span>Executive Briefing</span>
        </button>

        <button
          onClick={() => onSelectView('alerts')}
          className="btn btn-ghost btn-sm"
          style={{ position: 'relative', padding: '6px' }}
          title="Alerts Feed"
        >
          <Bell size={16} />
          {alertsCount > 0 && (
            <span style={{
              position: 'absolute',
              top: '4px',
              right: '4px',
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: 'var(--text-primary)',
              border: '2px solid var(--bg-primary)'
            }} />
          )}
        </button>
      </div>
    </header>
  );
}
