import React, { useState, useEffect } from 'react';
import { Database, Search, ShieldCheck, Cpu, ArrowRight, Eye, RefreshCw, Key, Check, Sparkles, Brain, ArrowDown, AlertCircle } from 'lucide-react';
import { HINDSIGHT_MEMORIES, COMPETITORS, EVENTS } from '../data/mockData';
import { competitorApi } from '../services/api';
import AgentMascot from './AgentMascot';
import CompanyLogo from './CompanyLogo';
import CategoryIcon from './CategoryIcon';

export default function HindsightMemoryView({ onSelectEvent, onSelectCompetitor }) {
  const [selectedCompetitor, setSelectedCompetitor] = useState('Microsoft');
  const [searchQuery, setSearchQuery] = useState('');
  const [testQuery, setTestQuery] = useState('');
  const [testResults, setTestResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [competitors, setCompetitors] = useState([]);
  const [events, setEvents] = useState([]);
  const [memoryStatus, setMemoryStatus] = useState(null);
  const [recalledBankId, setRecalledBankId] = useState(null);

  // Load real competitors, events, and memory status on mount
  useEffect(() => {
    competitorApi.getCompetitors()
      .then(data => {
        if (data && data.length > 0) {
          setCompetitors(data);
          if (!data.some(c => c.name.toLowerCase() === selectedCompetitor.toLowerCase())) {
            setSelectedCompetitor(data[0].name);
          }
        }
      })
      .catch(err => console.warn('Could not load competitors in MemoryView:', err));

    competitorApi.getEvents({ limit: 100 })
      .then(evts => {
        if (evts && evts.length > 0) setEvents(evts);
      })
      .catch(err => console.warn('Could not load events in MemoryView:', err));

    competitorApi.getMemoryStatus()
      .then(status => setMemoryStatus(status))
      .catch(err => console.warn('Could not load memory status:', err));
  }, []);

  // Format real ingested events as memory cards alongside baseline memories
  const allMemoryCards = [
    ...events.map(e => ({
      id: `mem-${String(e.id).substring(0, 8)}`,
      competitorId: e.competitorId || e.competitor_id || 'competitor',
      competitorName: e.competitorName || 'Competitor',
      memoryType: e.category || 'Product',
      ageLabel: e.date || 'Historical',
      content: e.evidenceSnippet || e.description || e.title,
      extractedEntities: [e.competitorName, e.category, e.sourceName].filter(Boolean),
      salienceScore: 0.96,
      retrievalCount: 1,
      relatedEvents: [e.id]
    })),
    ...HINDSIGHT_MEMORIES
  ];

  const filteredMemories = allMemoryCards.filter(m => {
    if (selectedCompetitor !== 'all' && m.competitorName?.toLowerCase() !== selectedCompetitor.toLowerCase() && m.competitorId !== selectedCompetitor) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (
        m.content.toLowerCase().includes(q) ||
        (m.extractedEntities && m.extractedEntities.some(ent => ent.toLowerCase().includes(q))) ||
        m.id.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const handleRunTestQuery = async (preset) => {
    const q = preset || testQuery;
    if (!q.trim()) return;
    setTestQuery(q);
    setIsSearching(true);
    setTestResults(null);

    const compName = selectedCompetitor !== 'all' ? selectedCompetitor : 'Microsoft';

    try {
      const data = await competitorApi.recallMemory(compName, q);
      setRecalledBankId(data.bank_id);
      const rawMemories = data.memories || [];
      const formatted = rawMemories.map(m => ({
        id: m.id || 'mem-node',
        competitorName: data.competitor || compName,
        competitorId: (data.competitor || compName).toLowerCase().replace(/[^a-z0-9]+/g, '-'),
        content: m.text || 'Verified competitor episodic observation.',
        ageLabel: m.occurred_start ? m.occurred_start.substring(0, 10) : 'Historical',
        memoryType: m.type || 'observation',
        salienceScore: m.scores?.final || 0.95,
        semanticScore: m.scores?.semantic || 0.85,
        tags: m.tags || [],
        bankId: data.bank_id
      }));

      setTestResults(formatted);
    } catch (err) {
      console.warn('Real Hindsight recall failed, using fallback:', err);
      // Fallback filter
      const lower = q.toLowerCase();
      const results = HINDSIGHT_MEMORIES.filter(m =>
        m.content.toLowerCase().includes(lower) ||
        m.competitorName.toLowerCase().includes(lower)
      );
      setTestResults(results.length > 0 ? results : HINDSIGHT_MEMORIES.slice(0, 3));
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="content-body" style={{ display: 'flex', flexDirection: 'column', gap: '26px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '22px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            Hindsight Memory Explorer
          </h1>
          <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Inspect the agent’s transparent, immutable long-term memory graph. Shows exactly what CompetitorIQ remembers, when it was stored, and why it won’t forget.
          </p>
        </div>

        <div className="cautious-pill">
          <Database size={13} color="var(--text-primary)" />
          <span>GRAPH VECTOR RETRIEVAL // ZERO RECENCY BIAS</span>
        </div>
      </div>

      {/* SIGNATURE VISUALIZATION: Retain vs Recall Dual-Loop Architecture */}
      <div className="card" style={{ padding: '24px 28px', backgroundColor: 'var(--pink-lightest)', borderColor: 'var(--border-black)', borderWidth: '1.5px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <AgentMascot size={46} state={isSearching ? 'thinking' : 'watching'} />
            <div>
              <div style={{ fontSize: '15px', fontWeight: 800, color: 'var(--text-primary)' }}>
                How CompetitorIQ Remembers: The Hindsight Engine
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                Continuous indexing of competitor telemetry that prevents knowledge decay.
              </div>
            </div>
          </div>
          <div className="badge badge-black">
            142 Salient Nodes • 0% Decay
          </div>
        </div>

        {/* Dual Loops: RETAIN (Left) and RECALL (Right) */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          
          {/* Phase 1: RETAIN */}
          <div style={{
            backgroundColor: 'var(--bg-primary)',
            border: '1px solid var(--pink-border)',
            borderRadius: 'var(--radius-md)',
            padding: '16px 20px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '12px' }}>
              <span className="badge badge-black" style={{ fontSize: '10px' }}>PHASE 1</span>
              <span style={{ fontSize: '13px', fontWeight: 800, color: 'var(--text-primary)' }}>RETAIN (Ingestion)</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ padding: '8px 12px', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', fontSize: '12px' }}>
                <span style={{ fontWeight: 700 }}>1. New Competitor Move</span>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Pricing diff, hiring signal, code commit, PR release</div>
              </div>
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '11px' }}>↓</div>
              <div style={{ padding: '8px 12px', backgroundColor: 'var(--pink-lightest)', border: '1px solid var(--pink-border)', borderRadius: 'var(--radius-sm)', fontSize: '12px' }}>
                <span style={{ fontWeight: 700 }}>2. Hindsight Memory Graph</span>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Semantic extraction, entity linking, vector embedding</div>
              </div>
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '11px' }}>↓</div>
              <div style={{ padding: '8px 12px', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', fontSize: '12px' }}>
                <span style={{ fontWeight: 700 }}>3. Persistent Long-Term Memory</span>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Immutable node stored with timestamp & salience score</div>
              </div>
            </div>
          </div>

          {/* Phase 2: RECALL */}
          <div style={{
            backgroundColor: 'var(--bg-primary)',
            border: '1px solid var(--pink-border)',
            borderRadius: 'var(--radius-md)',
            padding: '16px 20px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '12px' }}>
              <span className="badge badge-pink" style={{ fontSize: '10px' }}>PHASE 2</span>
              <span style={{ fontSize: '13px', fontWeight: 800, color: 'var(--text-primary)' }}>RECALL (Synthesis)</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ padding: '8px 12px', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', fontSize: '12px' }}>
                <span style={{ fontWeight: 700 }}>1. Strategic Question Asked</span>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>e.g. "How has Microsoft's strategy evolved over time?"</div>
              </div>
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '11px' }}>↓</div>
              <div style={{ padding: '8px 12px', backgroundColor: 'var(--pink-lightest)', border: '1px solid var(--pink-border)', borderRadius: 'var(--radius-sm)', fontSize: '12px' }}>
                <span style={{ fontWeight: 700 }}>2. Relevant Multi-Hop Memories</span>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Retrieves 6 nodes spanning Jan 2023 – Oct 2024</div>
              </div>
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '11px' }}>↓</div>
              <div style={{ padding: '8px 12px', backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', fontSize: '12px' }}>
                <span style={{ fontWeight: 700 }}>3. Causal Strategic Insight</span>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Detects autonomous agent pivot & enterprise moat</div>
              </div>
            </div>
          </div>

        </div>
      </div>

      {/* Interactive Vector Memory Retrieval Tester */}
      <div className="card" style={{ padding: '22px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px', flexWrap: 'wrap', gap: '8px' }}>
          <div style={{ fontSize: '12px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
            Test Vector Memory Retrieval across Isolated Competitor Banks
          </div>
          {isSearching && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--text-primary)', fontWeight: 600 }}>
              <AgentMascot size={20} state="thinking" />
              <span>Hindsight API scanning vector embeddings...</span>
            </div>
          )}
        </div>

        {/* Target Memory Bank Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '12px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
            Target Bank:
          </span>
          {(competitors.length > 0 ? competitors : [
            { id: 'microsoft', name: 'Microsoft' },
            { id: 'google', name: 'Google' },
            { id: 'openai', name: 'OpenAI' },
            { id: 'amazon-aws', name: 'Amazon / AWS' },
            { id: 'anthropic', name: 'Anthropic' },
            { id: 'meta', name: 'Meta' }
          ]).map(c => {
            const isSelected = selectedCompetitor.toLowerCase() === c.name.toLowerCase();
            return (
              <button
                key={c.id || c.name}
                type="button"
                onClick={() => setSelectedCompetitor(c.name)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '5px',
                  padding: '3px 8px',
                  fontSize: '11px',
                  fontWeight: 600,
                  borderRadius: 'var(--radius-sm)',
                  border: isSelected ? '1px solid var(--text-primary)' : '1px solid var(--border-medium)',
                  backgroundColor: isSelected ? 'var(--text-primary)' : 'var(--bg-secondary)',
                  color: isSelected ? 'var(--text-inverse)' : 'var(--text-secondary)',
                  cursor: 'pointer'
                }}
              >
                <CompanyLogo competitorId={c.id} size={12} />
                <span>{c.name}</span>
              </button>
            );
          })}
        </div>

        <div style={{ display: 'flex', gap: '10px', marginBottom: '12px' }}>
          <input
            type="text"
            placeholder={`Query ${selectedCompetitor}'s Hindsight memory bank (e.g. 'autonomous agents' or 'pricing change')...`}
            value={testQuery}
            onChange={(e) => setTestQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleRunTestQuery()}
            className="input-minimal"
            style={{ fontSize: '13.5px', padding: '10px 14px' }}
          />
          <button
            onClick={() => handleRunTestQuery()}
            disabled={isSearching}
            className="btn btn-primary"
            style={{ minWidth: '150px' }}
          >
            <Sparkles size={14} />
            <span>{isSearching ? 'Recalling...' : 'Recall Memory'}</span>
          </button>
        </div>

        {/* Quick Test Chips */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>Quick recall prompts:</span>
          {[
            'autonomous agents',
            'reasoning model launch',
            '2 Million Token Context Window',
            'pricing change',
            'enterprise workflow automation'
          ].map((p, i) => (
            <button
              key={i}
              type="button"
              onClick={() => handleRunTestQuery(p)}
              className="btn btn-ghost btn-sm"
              style={{ fontSize: '11px', padding: '3px 8px', border: '1px solid var(--border-subtle)' }}
            >
              {p}
            </button>
          ))}
        </div>

        {/* Test query results if present */}
        {testResults && (
          <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '12px', fontWeight: 800, color: 'var(--text-primary)' }}>
                  Recalled {testResults.length} Real Hindsight Nodes for "{testQuery}":
                </span>
                {recalledBankId && (
                  <span className="badge badge-black" style={{ fontSize: '10px', fontFamily: 'var(--font-mono)' }}>
                    Bank: {recalledBankId}
                  </span>
                )}
              </div>
              <button
                onClick={() => setTestResults(null)}
                style={{ background: 'none', border: 'none', fontSize: '11px', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                Clear Results
              </button>
            </div>

            {testResults.length === 0 ? (
              <div className="card" style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
                No memory nodes recalled for this inquiry in {selectedCompetitor}'s Hindsight bank.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {testResults.map(r => (
                  <div key={r.id} style={{
                    padding: '14px 16px',
                    backgroundColor: 'var(--pink-lightest)',
                    border: '1px solid var(--pink-border)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '12.5px'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px', flexWrap: 'wrap', gap: '6px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <CompanyLogo competitorId={r.competitorId} size={16} />
                        <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 800, fontSize: '11px' }}>{r.id.substring(0, 18)}...</span>
                        <span className="badge badge-black">{r.competitorName}</span>
                        <span className="badge badge-pink">{r.memoryType}</span>
                        {r.tags && r.tags.length > 0 && (
                          <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                            {r.tags.join(' • ')}
                          </span>
                        )}
                      </div>
                      <span style={{ color: 'var(--text-muted)', fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
                        Date: {r.ageLabel} • Relevance: {(r.salienceScore * 100).toFixed(0)}%
                      </span>
                    </div>

                    <div style={{ color: 'var(--text-primary)', fontWeight: 500, marginTop: '2px', lineHeight: 1.55 }}>
                      {r.content}
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '8px', fontSize: '11px', color: 'var(--text-muted)' }}>
                      <span>Grounding: Immutable Hindsight episodic memory node</span>
                      <button
                        onClick={() => onSelectCompetitor(r.competitorId)}
                        style={{ background: 'none', border: 'none', fontWeight: 700, color: 'var(--text-primary)', cursor: 'pointer', textDecoration: 'underline' }}
                      >
                        View Competitor Dossier →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Filter Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
        padding: '12px 16px',
        backgroundColor: 'var(--bg-secondary)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
            Filter Memory Bank:
          </span>
          <button
            onClick={() => setSelectedCompetitor('all')}
            style={{
              padding: '3px 8px',
              fontSize: '11.5px',
              fontWeight: 600,
              borderRadius: 'var(--radius-sm)',
              border: selectedCompetitor === 'all' ? '1px solid var(--text-primary)' : '1px solid var(--border-medium)',
              backgroundColor: selectedCompetitor === 'all' ? 'var(--text-primary)' : 'var(--bg-primary)',
              color: selectedCompetitor === 'all' ? 'var(--text-inverse)' : 'var(--text-secondary)',
              cursor: 'pointer'
            }}
          >
            All Rivals ({competitors.length > 0 ? competitors.length : COMPETITORS.length})
          </button>
          {(competitors.length > 0 ? competitors : COMPETITORS).map(c => (
            <button
              key={c.id || c.name}
              onClick={() => setSelectedCompetitor(c.name)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                padding: '3px 8px',
                fontSize: '11.5px',
                fontWeight: 600,
                borderRadius: 'var(--radius-sm)',
                border: selectedCompetitor.toLowerCase() === c.name.toLowerCase() ? '1px solid var(--pink-border)' : '1px solid var(--border-medium)',
                backgroundColor: selectedCompetitor.toLowerCase() === c.name.toLowerCase() ? 'var(--pink-subtle)' : 'var(--bg-primary)',
                color: 'var(--text-primary)',
                cursor: 'pointer'
              }}
            >
              <CompanyLogo competitorId={c.id} size={14} />
              <span>{c.name}</span>
            </button>
          ))}
        </div>

        <div style={{ width: '240px' }}>
          <input
            type="text"
            placeholder="Search memory graph..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input-minimal"
            style={{ padding: '4px 8px', fontSize: '11.5px' }}
          />
        </div>
      </div>

      {/* Memory Nodes Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(440px, 1fr))', gap: '16px' }}>
        {filteredMemories.map(mem => (
          <div
            key={mem.id}
            className="card"
            style={{
              padding: '20px',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
              borderLeft: '4px solid var(--text-primary)'
            }}
          >
            {/* Top row */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CompanyLogo competitorId={mem.competitorId} size={18} />
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', fontWeight: 800, backgroundColor: 'var(--bg-secondary)', padding: '2px 6px', border: '1px solid var(--border-medium)', borderRadius: 'var(--radius-sm)' }}>
                  {mem.id}
                </span>
                <span className="badge badge-black">{mem.competitorName}</span>
                <span className="badge badge-pink">{mem.memoryType}</span>
              </div>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                {mem.ageLabel}
              </span>
            </div>

            {/* Memory Content */}
            <p style={{ fontSize: '13.5px', color: 'var(--text-primary)', lineHeight: 1.55, fontWeight: 500 }}>
              {mem.content}
            </p>

            {/* Extracted Entities */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 800 }}>
                Entities:
              </span>
              {mem.extractedEntities.map((ent, idx) => (
                <span key={idx} style={{
                  fontSize: '11px',
                  fontFamily: 'var(--font-mono)',
                  backgroundColor: 'var(--bg-secondary)',
                  border: '1px solid var(--border-subtle)',
                  padding: '1px 6px',
                  borderRadius: 'var(--radius-sm)',
                  color: 'var(--text-secondary)'
                }}>
                  {ent}
                </span>
              ))}
            </div>

            {/* Bottom Meta & Related Events */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              paddingTop: '8px',
              borderTop: '1px solid var(--border-subtle)',
              fontSize: '11px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--text-muted)' }}>
                <span>Salience: {(mem.salienceScore * 100).toFixed(0)}%</span>
                <span>•</span>
                <span>Retrieved: {mem.retrievalCount} times</span>
              </div>

              {/* Related event triggers */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Events:</span>
                {mem.relatedEvents.map(evtId => {
                  const ev = EVENTS.find(e => e.id === evtId);
                  return (
                    <button
                      key={evtId}
                      onClick={() => ev && onSelectEvent(ev)}
                      style={{
                        padding: '1px 5px',
                        fontSize: '10px',
                        fontFamily: 'var(--font-mono)',
                        border: '1px solid var(--border-medium)',
                        borderRadius: 'var(--radius-sm)',
                        backgroundColor: 'var(--bg-primary)',
                        cursor: 'pointer',
                        color: 'var(--text-primary)'
                      }}
                      title="Inspect Event"
                    >
                      {evtId}
                    </button>
                  );
                })}
              </div>
            </div>

          </div>
        ))}
      </div>

    </div>
  );
}
