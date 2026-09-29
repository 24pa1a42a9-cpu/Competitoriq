import React from 'react';
import { X, ExternalLink, ShieldCheck, Database, Calendar, Tag, ArrowRight, Activity, AlertCircle } from 'lucide-react';

export default function EvidenceDrawer({
  event,
  onClose,
  onOpenCompetitor,
  onOpenMemory
}) {
  if (!event) return null;

  return (
    <>
      <div className="overlay-backdrop" onClick={onClose} />
      <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
        {/* Drawer Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          backgroundColor: 'var(--bg-primary)'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span className="badge badge-black">{event.category}</span>
              <span className="badge badge-pink">{event.impact} Impact</span>
              <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                Confidence: {event.confidence}
              </span>
            </div>
            <h2 style={{ fontSize: '17px', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.3 }}>
              {event.title}
            </h2>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--text-secondary)',
              padding: '6px',
              borderRadius: 'var(--radius-sm)'
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Drawer Content */}
        <div style={{ padding: '24px', flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Cautious Intelligence Notice */}
          <div className="cautious-pill" style={{ width: 'fit-content' }}>
            <ShieldCheck size={13} color="var(--text-primary)" />
            <span>CAUTIOUS INTELLIGENCE ASSESSMENT // CORROBORATED</span>
          </div>

          {/* Competitor Banner */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '12px 16px',
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)'
          }}>
            <div>
              <div style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>
                Subject Entity
              </div>
              <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)' }}>
                {event.competitorName}
              </div>
            </div>
            <button
              onClick={() => onOpenCompetitor(event.competitorId)}
              className="btn btn-outline btn-sm"
              style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <span>View Dossier</span>
              <ArrowRight size={12} />
            </button>
          </div>

          {/* Description */}
          <div>
            <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '6px' }}>
              Recorded Event Summary
            </div>
            <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              {event.description}
            </p>
          </div>

          {/* Verbatim Evidence Snippet */}
          <div>
            <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '6px' }}>
              Primary Verified Evidence Snippet
            </div>
            <div className="intel-quote" style={{ fontSize: '13px', lineHeight: 1.5 }}>
              {event.evidenceSnippet}
            </div>
          </div>

          {/* Source Attribution */}
          <div style={{
            padding: '12px 14px',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--bg-secondary)'
          }}>
            <div style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '4px' }}>
              Corroborated Source
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                  {event.sourceName}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  Captured on {event.date}
                </div>
              </div>
              <a
                href={event.sourceUrl}
                target="_blank"
                rel="noreferrer"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontSize: '11px',
                  fontWeight: 600,
                  color: 'var(--text-primary)',
                  textDecoration: 'none',
                  padding: '4px 8px',
                  border: '1px solid var(--border-medium)',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--bg-primary)'
                }}
              >
                <span>Inspect URL</span>
                <ExternalLink size={11} />
              </a>
            </div>
          </div>

          {/* Strategic Analysis - Why This Matters */}
          <div>
            <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '6px' }}>
              Strategic Synthesis: Why This Matters
            </div>
            <div style={{
              padding: '14px',
              backgroundColor: 'var(--pink-lightest)',
              border: '1px solid var(--pink-border)',
              borderRadius: 'var(--radius-md)',
              fontSize: '13px',
              color: 'var(--text-primary)',
              lineHeight: 1.55
            }}>
              <p style={{ fontWeight: 600, marginBottom: '6px' }}>
                Evidence suggests:
              </p>
              <p style={{ color: 'var(--text-secondary)' }}>
                {event.whyItMatters}
              </p>
            </div>
          </div>

          {/* Hindsight Memory Link & Payload */}
          <div style={{
            border: '1px solid var(--border-dark)',
            borderRadius: 'var(--radius-md)',
            padding: '14px',
            backgroundColor: 'var(--bg-primary)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Database size={13} color="var(--text-primary)" />
                <span style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase' }}>
                  Persistent Hindsight Memory Node
                </span>
              </div>
              <button
                onClick={() => onOpenMemory(event.hindsightMemoryId)}
                className="btn btn-pink btn-sm"
                style={{ padding: '3px 8px', fontSize: '11px' }}
              >
                Inspect in Graph
              </button>
            </div>

            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '11px',
              backgroundColor: 'var(--bg-secondary)',
              padding: '10px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-secondary)',
              wordBreak: 'break-all'
            }}>
              {event.rawMemoryPayload}
            </div>
          </div>

        </div>

        {/* Footer Actions */}
        <div style={{
          padding: '16px 24px',
          borderTop: '1px solid var(--border-subtle)',
          backgroundColor: 'var(--bg-secondary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            EVENT_REF: {event.id}
          </span>
          <button onClick={onClose} className="btn btn-outline btn-sm">
            Close Panel
          </button>
        </div>
      </div>
    </>
  );
}
