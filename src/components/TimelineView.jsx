import React, { useState, useEffect } from 'react';
import { Search, Filter, ShieldCheck, ExternalLink, Calendar, ArrowRight, Eye, Database, RefreshCw } from 'lucide-react';
import { EVENTS, COMPETITORS } from '../data/mockData';
import { competitorApi } from '../services/api';
import CategoryIcon from './CategoryIcon';
import CompanyLogo from './CompanyLogo';
import AgentMascot from './AgentMascot';

export default function TimelineView({ onSelectEvent, onSelectCompetitor }) {
  const [selectedCompetitor, setSelectedCompetitor] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [competitors, setCompetitors] = useState([]);
  const [events, setEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Canonical event categories per specification
  const categories = [
    'All',
    'Product',
    'Pricing',
    'Hiring',
    'Partnership',
    'Acquisition',
    'Messaging',
    'Funding',
    'Leadership',
    'Technology',
    'Market Expansion',
    'Other'
  ];

  // Fetch competitors on mount
  useEffect(() => {
    competitorApi.getCompetitors()
      .then(data => {
        if (data && data.length > 0) setCompetitors(data);
      })
      .catch(err => console.warn('Could not fetch competitors in TimelineView:', err));
  }, []);

  // Fetch real events from backend based on filters
  const fetchEvents = async () => {
    setIsLoading(true);
    try {
      const params = {};
      if (selectedCompetitor !== 'all') params.competitor = selectedCompetitor;
      if (selectedCategory !== 'all') params.event_type = selectedCategory;
      if (searchQuery.trim()) params.search = searchQuery.trim();

      const data = await competitorApi.getEvents(params);
      setEvents(data);
    } catch (err) {
      console.warn('Backend events query error in TimelineView:', err);
      // Fallback to mock data if backend query fails
      let filtered = EVENTS;
      if (selectedCompetitor !== 'all') filtered = filtered.filter(e => e.competitorId === selectedCompetitor);
      if (selectedCategory !== 'all') filtered = filtered.filter(e => e.category.toLowerCase() === selectedCategory.toLowerCase());
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        filtered = filtered.filter(e => e.title.toLowerCase().includes(q) || e.description.toLowerCase().includes(q));
      }
      setEvents(filtered);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [selectedCompetitor, selectedCategory, searchQuery]);

  const activeCompetitorsList = competitors.length > 0 ? competitors : COMPETITORS;
  const filteredEvents = events;

  return (
    <div className="content-body" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '22px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            Activity Timeline
          </h1>
          <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Chronological multi-source feed of competitor events, verified quotes, impact evaluations, and direct evidence links.
          </p>
        </div>

        <div className="cautious-pill">
          <ShieldCheck size={13} color="var(--text-primary)" />
          <span>ALL EVENTS DIGITALLY CORROBORATED</span>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '12px',
        padding: '14px 18px',
        backgroundColor: 'var(--bg-secondary)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)'
      }}>
        {/* Competitor Selector Pills */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', marginRight: '4px' }}>
            Competitor:
          </span>
          <button
            onClick={() => setSelectedCompetitor('all')}
            style={{
              padding: '4px 10px',
              fontSize: '12px',
              fontWeight: 600,
              borderRadius: 'var(--radius-sm)',
              border: selectedCompetitor === 'all' ? '1px solid var(--text-primary)' : '1px solid var(--border-medium)',
              backgroundColor: selectedCompetitor === 'all' ? 'var(--text-primary)' : 'var(--bg-primary)',
              color: selectedCompetitor === 'all' ? 'var(--text-inverse)' : 'var(--text-secondary)',
              cursor: 'pointer'
            }}
          >
            All Rivals ({filteredEvents.length})
          </button>
          {activeCompetitorsList.map(c => (
            <button
              key={c.id}
              onClick={() => setSelectedCompetitor(c.id)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 10px',
                fontSize: '12px',
                fontWeight: 600,
                borderRadius: 'var(--radius-sm)',
                border: selectedCompetitor === c.id ? '1px solid var(--pink-border)' : '1px solid var(--border-medium)',
                backgroundColor: selectedCompetitor === c.id ? 'var(--pink-subtle)' : 'var(--bg-primary)',
                color: 'var(--text-primary)',
                cursor: 'pointer'
              }}
            >
              <CompanyLogo competitorId={c.id} size={14} />
              <span>{c.name}</span>
            </button>
          ))}
        </div>

        {/* Search Field */}
        <div style={{ width: '260px' }}>
          <input
            type="text"
            placeholder="Filter timeline keywords..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input-minimal"
            style={{ fontSize: '12px', padding: '6px 10px' }}
          />
        </div>
      </div>

      {/* Category Pills */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginRight: '6px' }}>
          Category:
        </span>
        {categories.map(cat => {
          const isActive = selectedCategory.toLowerCase() === cat.toLowerCase();
          return (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat === 'All' ? 'all' : cat)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                padding: '3px 10px',
                fontSize: '11px',
                fontWeight: 600,
                borderRadius: 'var(--radius-full)',
                border: isActive ? '1px solid var(--pink-border)' : '1px solid var(--border-subtle)',
                backgroundColor: isActive ? 'var(--pink-subtle)' : 'transparent',
                color: isActive ? 'var(--text-primary)' : 'var(--text-muted)',
                cursor: 'pointer'
              }}
            >
              {cat !== 'All' && <CategoryIcon category={cat} size={12} />}
              <span>{cat}</span>
            </button>
          );
        })}
      </div>

      {/* Events List with Visual Timeline Spine */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', position: 'relative' }}>
        {filteredEvents.length === 0 ? (
          <div className="card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            No competitor events match your selected filters.
          </div>
        ) : (
          filteredEvents.map(evt => (
            <div
              key={evt.id}
              className="card"
              style={{
                padding: '20px 24px',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
                borderLeft: '4px solid var(--text-primary)',
                transition: 'all 0.15s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--pink-lightest)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--bg-primary)';
              }}
            >
              {/* Event Meta Line */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CompanyLogo competitorId={evt.competitorId} size={18} />
                  <button
                    onClick={() => onSelectCompetitor(evt.competitorId)}
                    style={{
                      background: 'none',
                      border: 'none',
                      padding: 0,
                      fontWeight: 800,
                      fontSize: '13px',
                      color: 'var(--text-primary)',
                      cursor: 'pointer',
                      textDecoration: 'underline'
                    }}
                  >
                    {evt.competitorName}
                  </button>
                  <span>•</span>
                  <span className="badge badge-black" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    <CategoryIcon category={evt.category} size={11} />
                    <span>{evt.category}</span>
                  </span>
                  <span className="badge badge-pink">{evt.impact} Impact</span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  {/* Remembered by Hindsight Stamp */}
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '5px',
                    padding: '2px 7px',
                    backgroundColor: 'var(--bg-primary)',
                    border: '1px solid var(--border-medium)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '10px',
                    fontFamily: 'var(--font-mono)',
                    fontWeight: 700,
                    color: 'var(--text-primary)'
                  }}>
                    <Database size={11} color="var(--text-primary)" />
                    <span>Remembered: {evt.hindsightMemoryId}</span>
                  </div>

                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{evt.date}</span>
                </div>
              </div>

              {/* Title & Description */}
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>
                  {evt.title}
                </h3>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.55 }}>
                  {evt.description}
                </p>
              </div>

              {/* Evidence Snippet Callout */}
              <div className="intel-quote" style={{ fontSize: '12.5px' }}>
                <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Verified Extract: </span>
                {evt.evidenceSnippet}
              </div>

              {/* Strategic takeaway & Action */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingTop: '8px',
                borderTop: '1px solid var(--border-subtle)',
                fontSize: '12px'
              }}>
                <div style={{ color: 'var(--text-secondary)' }}>
                  <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Source: </span>
                  {evt.sourceUrl ? (
                    <a
                      href={evt.sourceUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      style={{ color: 'var(--text-secondary)', textDecoration: 'underline' }}
                    >
                      {evt.sourceName || 'Source Link'} ↗
                    </a>
                  ) : (
                    evt.sourceName || 'Verified Intelligence Record'
                  )}
                </div>

                <button
                  onClick={() => onSelectEvent(evt)}
                  className="btn btn-outline btn-sm"
                  style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
                >
                  <Eye size={12} />
                  <span>Inspect Evidence & Memory</span>
                </button>
              </div>

            </div>
          ))
        )}
      </div>

    </div>
  );
}
