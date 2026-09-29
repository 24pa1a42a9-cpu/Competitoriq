import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Send,
  Database,
  ShieldCheck,
  Calendar,
  Layers,
  ArrowRight,
  Eye,
  CheckCircle,
  HelpCircle,
  Clock,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  RefreshCw,
  ExternalLink
} from 'lucide-react';
import { EVENTS } from '../data/mockData';
import { competitorApi } from '../services/api';
import AgentMascot from './AgentMascot';
import CategoryIcon from './CategoryIcon';
import CompanyLogo from './CompanyLogo';

export default function AiAnalystView({ onSelectEvent, onOpenMemory, initialQuery = null }) {
  const [prompt, setPrompt] = useState(initialQuery || '');
  const [selectedCompetitor, setSelectedCompetitor] = useState('Microsoft');
  const [competitors, setCompetitors] = useState([]);
  const [currentAnswer, setCurrentAnswer] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState('');
  const [mascotState, setMascotState] = useState('watching'); // 'watching' | 'thinking' | 'found' | 'explaining'
  const [showMemoryDetails, setShowMemoryDetails] = useState(true);
  const [errorMessage, setErrorMessage] = useState(null);

  // Load real competitors on mount
  useEffect(() => {
    competitorApi.getCompetitors()
      .then(data => {
        if (data && data.length > 0) {
          setCompetitors(data);
          // Set default competitor if current is not in list
          if (!data.some(c => c.name.toLowerCase() === selectedCompetitor.toLowerCase())) {
            setSelectedCompetitor(data[0].name);
          }
        }
      })
      .catch(err => console.warn('Could not load competitors in AiAnalystView:', err));
  }, []);

  const detectCompetitor = (queryText) => {
    const qLower = (queryText || '').toLowerCase();
    for (const c of competitors) {
      if (qLower.includes(c.name.toLowerCase())) return c.name;
    }
    return selectedCompetitor || 'Microsoft';
  };

  const handleRunQuery = async (queryText, targetCompetitor = null) => {
    const q = queryText || prompt;
    if (!q.trim()) return;
    setPrompt(q);
    setIsLoading(true);
    setCurrentAnswer(null);
    setErrorMessage(null);
    setMascotState('thinking');

    const comp = targetCompetitor || detectCompetitor(q);
    if (targetCompetitor) setSelectedCompetitor(targetCompetitor);

    try {
      setLoadingStep('AI agent is recalling competitor history from Hindsight...');
      await new Promise(r => setTimeout(r, 300));

      setLoadingStep('AI agent is connecting multi-hop events across time...');
      await new Promise(r => setTimeout(r, 350));

      setLoadingStep('AI agent is generating intelligence with Groq...');
      const response = await competitorApi.analyzeCompetitor({
        competitor: comp,
        question: q
      });

      setMascotState('found');
      setTimeout(() => {
        setMascotState('explaining');
        setCurrentAnswer(response);
        setIsLoading(false);
      }, 400);
    } catch (err) {
      console.error('AI Analyst Query failed:', err);
      setIsLoading(false);
      setMascotState('watching');
      setErrorMessage(err.message || 'The Competitive Intelligence backend encountered an error while synthesizing historical memory.');
    }
  };

  return (
    <div className="content-body" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '22px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            AI Strategic Analyst Workspace
          </h1>
          <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Persistent intelligence query console. Synthesizes answers using multi-hop Hindsight memory nodes, citing historical moves across months.
          </p>
        </div>

        <div className="cautious-pill">
          <ShieldCheck size={13} color="var(--text-primary)" />
          <span>PERSISTENT HISTORICAL SYNTHESIS</span>
        </div>
      </div>

      {/* Query Formulation Input Box with Mascot Assistant */}
      <div className="card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <AgentMascot size={38} state={mascotState} />
            <div>
              <div style={{ fontSize: '14px', fontWeight: 800, color: 'var(--text-primary)' }}>
                {mascotState === 'thinking' ? 'IQ-Agent: Searching Hindsight Graph...' : 'IQ-Agent Ready for Strategic Inquiry'}
              </div>
              <div style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>
                Ask about competitor strategy, pricing pivots, hiring patterns, or long-term vectors.
              </div>
            </div>
          </div>
          <span className="badge badge-black">Not a Chatbot • Deep CI Engine</span>
        </div>

        {/* Competitor Selector Pills */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginRight: '4px' }}>
            Target Competitor:
          </span>
          {(competitors.length > 0 ? competitors : [
            { id: 'microsoft', name: 'Microsoft' },
            { id: 'google', name: 'Google' },
            { id: 'openai', name: 'OpenAI' },
            { id: 'anthropic', name: 'Anthropic' },
            { id: 'meta', name: 'Meta' },
            { id: 'amazon-aws', name: 'Amazon / AWS' }
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
                  padding: '4px 10px',
                  fontSize: '11.5px',
                  fontWeight: 600,
                  borderRadius: 'var(--radius-sm)',
                  border: isSelected ? '1px solid var(--text-primary)' : '1px solid var(--border-medium)',
                  backgroundColor: isSelected ? 'var(--text-primary)' : 'var(--bg-primary)',
                  color: isSelected ? 'var(--text-inverse)' : 'var(--text-secondary)',
                  cursor: 'pointer'
                }}
              >
                <CompanyLogo competitorId={c.id} size={13} />
                <span>{c.name}</span>
              </button>
            );
          })}
        </div>

        {/* Input Bar */}
        <div style={{ display: 'flex', gap: '10px' }}>
          <input
            type="text"
            placeholder={`e.g. How has ${selectedCompetitor}'s strategy evolved?`}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !isLoading && handleRunQuery()}
            className="input-minimal"
            style={{ fontSize: '14px', padding: '12px 16px' }}
          />

          <button
            onClick={() => handleRunQuery()}
            disabled={isLoading || !prompt.trim()}
            className="btn btn-primary"
            style={{ minWidth: '150px', padding: '12px 20px', gap: '8px' }}
          >
            <Sparkles size={15} />
            <span>{isLoading ? 'Synthesizing...' : 'Run Query'}</span>
          </button>
        </div>

        {/* Preset Strategic Inquiries */}
        <div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '8px', fontWeight: 700 }}>
            Executive Inquiry Presets:
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {[
              { id: 'query-msft', comp: 'Microsoft', prompt: "How has Microsoft's AI strategy evolved?" },
              { id: 'query-goog', comp: 'Google', prompt: "How has Google's foundation model strategy shifted?" },
              { id: 'query-oai', comp: 'OpenAI', prompt: "What is OpenAI's reasoning model trajectory?" },
              { id: 'query-aws', comp: 'Amazon / AWS', prompt: "What is Amazon/AWS's strategy with Bedrock and custom silicon?" }
            ].map((p) => (
              <button
                key={p.id}
                onClick={() => {
                  setSelectedCompetitor(p.comp);
                  handleRunQuery(p.prompt, p.comp);
                }}
                disabled={isLoading}
                className="btn btn-outline btn-sm"
                style={{
                  fontSize: '11.5px',
                  padding: '6px 12px',
                  backgroundColor: 'var(--bg-secondary)',
                  textAlign: 'left'
                }}
              >
                <span>{p.prompt}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error State Banner */}
      {errorMessage && (
        <div style={{
          padding: '16px 20px',
          backgroundColor: '#FFF5F5',
          border: '1px solid #FEB2B2',
          borderRadius: 'var(--radius-md)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          color: '#C53030'
        }}>
          <AlertCircle size={20} />
          <div style={{ flex: 1, fontSize: '13px' }}>
            <strong>Intelligence Query Error:</strong> {errorMessage}
          </div>
          <button
            onClick={() => handleRunQuery()}
            className="btn btn-sm btn-outline"
            style={{ borderColor: '#FEB2B2', color: '#C53030' }}
          >
            Retry Analysis
          </button>
        </div>
      )}

      {/* Loading Reasoning Stepper */}
      {isLoading && (
        <div className="card" style={{ padding: '32px', textAlign: 'center', backgroundColor: 'var(--pink-lightest)', borderColor: 'var(--pink-border)' }}>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '14px' }}>
            <AgentMascot size={54} state="thinking" className="mascot-floating" />
          </div>
          <div style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '6px' }}>
            IQ-Agent Reasoning Across Historical Memory
          </div>
          <div style={{ fontSize: '13px', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
            {loadingStep || 'Connecting multi-hop event dependencies...'}
          </div>
        </div>
      )}

      {/* Answer Container structured per requirements: ANSWER, PATTERN, HISTORICAL CONTEXT, EVIDENCE, WHY IT MATTERS */}
      {!isLoading && currentAnswer && (
        <div className="card" style={{ padding: '32px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Header & Query Info */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '12px',
            paddingBottom: '18px',
            borderBottom: '1px solid var(--border-subtle)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <AgentMascot size={46} state="explaining" />
              <div>
                <span style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 800 }}>
                  Strategic Query Evaluated
                </span>
                <div style={{ fontSize: '17px', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>
                  "{currentAnswer.query}"
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="badge badge-black">{currentAnswer.confidence}</span>
              <span className="badge badge-pink">{currentAnswer.dateRange}</span>
            </div>
          </div>

          {/* 1. ANSWER (Strategic Insight) */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
              <span className="badge badge-black" style={{ fontSize: '10px' }}>SECTION 1</span>
              <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                ANSWER: EXECUTIVE SYNTHESIS
              </div>
            </div>
            <div style={{
              padding: '18px 22px',
              backgroundColor: 'var(--pink-lightest)',
              border: '1.5px solid var(--pink-border)',
              borderRadius: 'var(--radius-md)',
              fontSize: '14.5px',
              lineHeight: 1.6,
              color: 'var(--text-primary)',
              fontWeight: 500
            }}>
              {currentAnswer.strategicInsight}
            </div>
          </div>

          {/* 2. PATTERN (Detected Strategic Trajectory) */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
              <span className="badge badge-black" style={{ fontSize: '10px' }}>SECTION 2</span>
              <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                PATTERN: BEHAVIORAL VECTOR
              </div>
            </div>
            <div style={{
              padding: '14px 18px',
              backgroundColor: 'var(--bg-secondary)',
              border: '1px solid var(--border-medium)',
              borderRadius: 'var(--radius-md)',
              fontSize: '13.5px',
              color: 'var(--text-primary)',
              lineHeight: 1.55
            }}>
              <div>{currentAnswer.pattern || 'Evolving operational and commercial trajectory.'}</div>
              {currentAnswer.strategicSignal && (
                <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid var(--border-subtle)', fontSize: '13px' }}>
                  <span style={{ fontWeight: 800, color: 'var(--text-primary)' }}>Strategic Signal: </span>
                  <span style={{ color: 'var(--text-secondary)' }}>{currentAnswer.strategicSignal}</span>
                </div>
              )}
            </div>
          </div>

          {/* 3. HISTORICAL CONTEXT (Chronological Milestones) */}
          {currentAnswer.analysisPoints && currentAnswer.analysisPoints.length > 0 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
                <span className="badge badge-black" style={{ fontSize: '10px' }}>SECTION 3</span>
                <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                  HISTORICAL CONTEXT: MULTI-MONTH CHRONOLOGY
                </div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {currentAnswer.analysisPoints.map((pt, i) => (
                  <div
                    key={i}
                    style={{
                      padding: '12px 16px',
                      backgroundColor: 'var(--bg-secondary)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '13px',
                      color: 'var(--text-primary)',
                      lineHeight: 1.55
                    }}
                  >
                    {typeof pt === 'string' ? pt : (pt.explanation || JSON.stringify(pt))}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 4. EVIDENCE (Supporting Events) */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
              <span className="badge badge-black" style={{ fontSize: '10px' }}>SECTION 4</span>
              <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                EVIDENCE: CORROBORATED EVENT CITATIONS ({currentAnswer.supportingEvents?.length || 0})
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {(!currentAnswer.supportingEvents || currentAnswer.supportingEvents.length === 0) ? (
                <div className="card" style={{ padding: '16px', color: 'var(--text-muted)', fontSize: '12.5px' }}>
                  No isolated database events cited for this specific question context.
                </div>
              ) : (
                currentAnswer.supportingEvents.map((item, idx) => {
                  const evt = (typeof item === 'object' && item !== null)
                    ? item
                    : (EVENTS.find(e => e.id === item) || { id: item, title: String(item), category: 'Milestone', date: 'Historical' });

                  return (
                    <div
                      key={evt.id || idx}
                      onClick={() => onSelectEvent(evt)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '12px 16px',
                        backgroundColor: 'var(--bg-secondary)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-sm)',
                        cursor: 'pointer'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = 'var(--text-primary)';
                        e.currentTarget.style.backgroundColor = 'var(--pink-lightest)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = 'var(--border-subtle)';
                        e.currentTarget.style.backgroundColor = 'var(--bg-secondary)';
                      }}
                    >
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px', marginBottom: '2px' }}>
                          <CompanyLogo competitorId={evt.competitorId || currentAnswer.competitor} size={14} />
                          <span style={{ fontWeight: 800 }}>{evt.competitorName || currentAnswer.competitor}</span>
                          <span>•</span>
                          <span className="badge badge-black" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                            <CategoryIcon category={evt.category} size={11} />
                            <span>{evt.category || 'Milestone'}</span>
                          </span>
                          <span style={{ color: 'var(--text-muted)' }}>{evt.date}</span>
                          {evt.sourceName && (
                            <span style={{ color: 'var(--text-muted)' }}>• {evt.sourceName}</span>
                          )}
                        </div>
                        <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                          {evt.title}
                        </div>
                      </div>

                      <button className="btn btn-outline btn-sm" style={{ pointerEvents: 'none' }}>
                        <Eye size={12} />
                        <span>View Evidence</span>
                      </button>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* 5. WHY IT MATTERS (Strategic Implications) */}
          {currentAnswer.implications && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                <span className="badge badge-pink" style={{ fontSize: '10px' }}>SECTION 5</span>
                <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                  WHY IT MATTERS & STRATEGIC RECOMMENDATION
                </div>
              </div>
              <div style={{
                padding: '16px 20px',
                backgroundColor: 'var(--bg-secondary)',
                border: '1.5px solid var(--border-dark)',
                borderRadius: 'var(--radius-md)'
              }}>
                <p style={{ fontSize: '13.5px', color: 'var(--text-primary)', lineHeight: 1.55 }}>
                  {currentAnswer.implications}
                </p>
              </div>
            </div>
          )}

          {/* Limitations & Insufficient Memory Warning */}
          {(currentAnswer.limitations?.length > 0 || currentAnswer.isInsufficientMemory) && (
            <div style={{
              padding: '14px 18px',
              backgroundColor: 'var(--bg-secondary)',
              border: '1px solid var(--border-medium)',
              borderRadius: 'var(--radius-md)',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <AlertCircle size={14} color="var(--text-muted)" />
                <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                  Intelligence Limitations & Memory Bounds
                </span>
              </div>
              <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                {currentAnswer.limitations?.map((lim, idx) => (
                  <li key={idx}>{lim}</li>
                ))}
                {currentAnswer.isInsufficientMemory && !currentAnswer.limitations?.length && (
                  <li>No verified historical milestones were retained in Hindsight for this competitor. Responses are restricted to prevent speculative fabrication.</li>
                )}
              </ul>
            </div>
          )}

          {/* Expandable Memory Used Section */}
          <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '16px' }}>
            <button
              onClick={() => setShowMemoryDetails(!showMemoryDetails)}
              style={{
                background: 'none',
                border: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                width: '100%',
                cursor: 'pointer',
                padding: 0
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Database size={14} color="var(--text-primary)" />
                <span style={{ fontSize: '12px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-primary)' }}>
                  Retrieved Hindsight Memory Nodes ({currentAnswer.memoryUsed?.length || 0})
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--text-muted)' }}>
                <span>{showMemoryDetails ? 'Hide Nodes' : 'Show Nodes'}</span>
                {showMemoryDetails ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </div>
            </button>

            {showMemoryDetails && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '12px' }}>
                {currentAnswer.memoryUsed?.map((mem) => (
                  <div
                    key={mem.id}
                    onClick={() => onOpenMemory && onOpenMemory(mem.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      padding: '8px 12px',
                      backgroundColor: 'var(--bg-primary)',
                      border: '1px solid var(--border-medium)',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '11.5px',
                      cursor: 'pointer'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = 'var(--text-primary)';
                      e.currentTarget.style.backgroundColor = 'var(--pink-lightest)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = 'var(--border-medium)';
                      e.currentTarget.style.backgroundColor = 'var(--bg-primary)';
                    }}
                  >
                    <Database size={12} color="var(--text-primary)" />
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 800 }}>{mem.id}</span>
                    <span style={{ color: 'var(--text-secondary)' }}>• {mem.label}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>
      )}

    </div>
  );
}
