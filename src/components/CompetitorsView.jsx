import React, { useState, useEffect } from 'react';
import { Building2, ArrowRight, Activity, TrendingUp, Zap, Clock, ShieldAlert, RefreshCw, AlertCircle } from 'lucide-react';
import { competitorApi } from '../services/api';
import CompanyLogo from './CompanyLogo';
import CategoryIcon from './CategoryIcon';

export default function CompetitorsView({
  onSelectCompetitor,
  onSelectView
}) {
  const [competitors, setCompetitors] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCompetitors = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await competitorApi.getCompetitors();
      setCompetitors(data);
    } catch (err) {
      console.error('Failed to load competitors:', err);
      setError(err.message || 'Unable to connect to CompetitorIQ backend.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCompetitors();
  }, []);

  return (
    <div className="content-body" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Header Banner */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '22px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            Monitored Competitors
          </h1>
          <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Continuous persistent intelligence surveillance across pricing, product commits, messaging shifts, and talent migrations.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={fetchCompetitors}
            className="btn btn-outline btn-sm"
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            title="Refresh database records"
          >
            <RefreshCw size={12} className={isLoading ? 'spin-icon' : ''} />
            <span>Refresh</span>
          </button>
          <button
            onClick={() => onSelectView('comparison')}
            className="btn btn-outline btn-sm"
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <span>Compare All in Matrix</span>
            <ArrowRight size={13} />
          </button>
        </div>
      </div>

      {/* Error State Banner */}
      {error && (
        <div style={{
          padding: '14px 18px',
          backgroundColor: '#FFF5F5',
          border: '1px solid #FEB2B2',
          borderRadius: 'var(--radius-md)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          color: '#C53030',
          fontSize: '13px'
        }}>
          <AlertCircle size={16} />
          <div style={{ flex: 1 }}>
            <strong>Connection Error:</strong> {error}
          </div>
          <button
            onClick={fetchCompetitors}
            className="btn btn-sm btn-outline"
            style={{ borderColor: '#FEB2B2', color: '#C53030' }}
          >
            Retry
          </button>
        </div>
      )}

      {/* Loading Skeleton */}
      {isLoading && competitors.length === 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '20px' }}>
          {[1, 2, 3, 4, 5, 6].map(n => (
            <div key={n} className="card" style={{ padding: '24px', minHeight: '260px', opacity: 0.6 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: 'var(--border-subtle)' }} />
                <div style={{ flex: 1 }}>
                  <div style={{ width: '120px', height: '18px', backgroundColor: 'var(--border-subtle)', borderRadius: '4px', marginBottom: '6px' }} />
                  <div style={{ width: '80px', height: '12px', backgroundColor: 'var(--border-subtle)', borderRadius: '4px' }} />
                </div>
              </div>
              <div style={{ width: '100%', height: '40px', backgroundColor: 'var(--border-subtle)', borderRadius: '4px', marginBottom: '16px' }} />
              <div style={{ width: '100%', height: '50px', backgroundColor: 'var(--border-subtle)', borderRadius: '4px' }} />
            </div>
          ))}
        </div>
      )}

      {/* Competitor Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '20px' }}>
        {competitors.map(comp => (
          <div
            key={comp.id}
            className="card"
            style={{
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              gap: '18px',
              cursor: 'pointer',
              border: '1px solid var(--border-subtle)',
              transition: 'all 0.15s ease'
            }}
            onClick={() => onSelectCompetitor(comp.id)}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--text-primary)';
              e.currentTarget.style.boxShadow = 'var(--shadow-md)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border-subtle)';
              e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
            }}
          >
            {/* Top Info */}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <CompanyLogo competitorId={comp.id} size={32} />
                  <div>
                    <h2 style={{ fontSize: '19px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
                      {comp.name}
                    </h2>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{comp.hq}</span>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span className="badge badge-black">{comp.stage}</span>
                  <span className="badge badge-pink">{comp.threatLevel}</span>
                </div>
              </div>

              <div style={{ fontSize: '12.5px', color: 'var(--text-muted)', marginBottom: '12px', lineHeight: 1.4 }}>
                {comp.tagline}
              </div>

              {/* Strategy Thesis Box */}
              <div style={{
                padding: '12px 14px',
                backgroundColor: 'var(--pink-lightest)',
                border: '1px solid var(--pink-border)',
                borderRadius: 'var(--radius-md)',
                fontSize: '12.5px',
                color: 'var(--text-primary)',
                lineHeight: 1.5,
                marginBottom: '14px'
              }}>
                <span style={{ fontWeight: 800, display: 'block', marginBottom: '2px', fontSize: '10.5px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Agent Strategic Thesis:
                </span>
                {comp.strategySummary}
              </div>

              {/* Metrics Row */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '8px',
                padding: '10px 0',
                borderTop: '1px solid var(--border-subtle)',
                borderBottom: '1px solid var(--border-subtle)',
                marginBottom: '14px'
              }}>
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Est. ARR</div>
                  <div style={{ fontSize: '13px', fontWeight: 700 }}>{comp.arrEstimate}</div>
                </div>
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Tracked Events</div>
                  <div style={{ fontSize: '13px', fontWeight: 700 }}>{comp.eventCount} Events</div>
                </div>
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Pattern Score</div>
                  <div style={{ fontSize: '13px', fontWeight: 700 }}>{comp.patternScore}% Match</div>
                </div>
              </div>

              {/* Major Tracked Categories with Category Icons */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {comp.categories.map((cat, i) => (
                  <span
                    key={i}
                    className="badge badge-outline"
                    style={{ fontSize: '10.5px', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                  >
                    <CategoryIcon category={cat} size={11} />
                    <span>{cat}</span>
                  </span>
                ))}
              </div>
            </div>

            {/* Bottom Actions */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              paddingTop: '12px',
              borderTop: '1px solid var(--border-subtle)'
            }}>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                Updated {comp.lastUpdate}
              </span>
              <span style={{
                fontSize: '12px',
                fontWeight: 700,
                color: 'var(--text-primary)',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}>
                <span>Full Intelligence Dossier</span>
                <ArrowRight size={13} />
              </span>
            </div>

          </div>
        ))}
      </div>

    </div>
  );
}
