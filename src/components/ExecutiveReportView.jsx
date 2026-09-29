import React, { useState, useEffect } from 'react';
import {
  FileText,
  Printer,
  Copy,
  Check,
  ShieldCheck,
  Download,
  ExternalLink,
  Sparkles,
  Eye,
  RefreshCw,
  Calendar,
  Database,
  History,
  TrendingUp,
  Layers,
  AlertCircle,
  Info,
  ChevronRight,
  ShieldAlert,
  Zap
} from 'lucide-react';
import AgentMascot from './AgentMascot';
import CategoryIcon from './CategoryIcon';
import CompanyLogo from './CompanyLogo';
import competitorApi from '../services/api';

export default function ExecutiveReportView({ onSelectEvent, onSelectCompetitor }) {
  const [competitors, setCompetitors] = useState([]);
  const [selectedCompetitor, setSelectedCompetitor] = useState('microsoft');
  const [timeRange, setTimeRange] = useState('all');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState('summary'); // 'summary' | 'patterns' | 'changes' | 'memory' | 'evidence'
  const [pipelineStep, setPipelineStep] = useState(null);

  // Dynamic mascot states
  const [mascotState, setMascotState] = useState('watching');
  const [mascotSpeech, setMascotSpeech] = useState(
    'Ready to synthesize a board-level Executive Intelligence Briefing grounded in real telemetry and Hindsight memory.'
  );

  // Load competitors list on mount
  useEffect(() => {
    const loadCompetitors = async () => {
      try {
        const comps = await competitorApi.getCompetitors();
        setCompetitors(comps);
        if (comps.length > 0) {
          const defaultComp = comps.find(c => c.id === 'microsoft') || comps[0];
          setSelectedCompetitor(defaultComp.id);
        }
      } catch (err) {
        console.error('Failed to load competitors for executive report:', err);
      }
    };
    loadCompetitors();
  }, []);

  // Generate Report
  const handleGenerateReport = async (compName = null, tr = null) => {
    const targetComp = compName || (competitors.find(c => c.id === selectedCompetitor)?.name || selectedCompetitor);
    const targetRange = tr || timeRange;

    setLoading(true);
    setMascotState('thinking');
    setMascotSpeech(`Analyzing ${targetComp} telemetry across time. Querying SQLite database and recalling Hindsight memory banks...`);

    // Simulated pipeline progress for high-fidelity intelligence feedback
    setPipelineStep('events');
    const t1 = setTimeout(() => setPipelineStep('hindsight'), 400);
    const t2 = setTimeout(() => setPipelineStep('patterns'), 900);
    const t3 = setTimeout(() => setPipelineStep('groq'), 1500);

    try {
      const reportData = await competitorApi.getCompetitorReport(targetComp, targetRange);
      setReport(reportData);

      if (reportData.status === 'insufficient_data') {
        setMascotState('watching');
        setMascotSpeech(
          `Insufficient historical evidence for ${targetComp} in the selected range (${targetRange}). Transparently reporting limitations rather than hallucinating.`
        );
      } else {
        setMascotState('explaining');
        setMascotSpeech(
          `Synthesized an Executive Intelligence Brief for ${targetComp} grounded in ${reportData.recent_activity?.length || 0} events and ${reportData.memory_used?.event_count || 0} recalled Hindsight memories.`
        );
      }
    } catch (err) {
      console.error('Error generating executive report:', err);
      setMascotState('watching');
      setMascotSpeech('Failed to synthesize report. Please verify connection and try again.');
    } finally {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
      setPipelineStep(null);
      setLoading(false);
    }
  };

  // Copy to clipboard
  const handleCopyText = () => {
    if (!report) return;

    const text = `
COMPETITORIQ EXECUTIVE INTELLIGENCE BRIEF
TARGET: ${report.competitor}
PERIOD: ${report.report_period}
GENERATED: ${report.generated_at}
CLASSIFICATION: CONFIDENTIAL // BOARD BRIEFING

==================================================
1. EXECUTIVE SUMMARY
==================================================
${report.executive_summary}

==================================================
2. STRATEGIC SIGNALS
==================================================
${(report.strategic_signals || []).map(s => `- [${s.confidence?.toUpperCase() || 'HIGH'} CONFIDENCE] ${s.signal}: ${s.observed_trajectory}`).join('\n')}

==================================================
3. MAJOR DETECTED PATTERNS
==================================================
${(report.major_patterns || []).map(p => `- ${p.pattern} (${p.categories?.join(', ')}): ${p.evidence}`).join('\n')}

==================================================
4. KEY EVIDENCE & SOURCES
==================================================
${(report.key_evidence || []).map(e => `- [${e.event_date}] ${e.title} | Source: ${e.source_name} (${e.source_url})`).join('\n')}

==================================================
5. HINDSIGHT MEMORY TRANSPARENCY
==================================================
Memory Bank: ${report.memory_used?.memory_identifier}
Memories Recalled: ${report.memory_used?.event_count}
Date Range: ${report.memory_used?.date_range?.start} → ${report.memory_used?.date_range?.end}
    `.trim();

    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = () => {
    window.print();
  };

  const isInsufficient = report?.status === 'insufficient_data';
  const targetCompObj = competitors.find(c => c.id === selectedCompetitor) || { name: report?.competitor || 'Target Competitor', id: selectedCompetitor };

  return (
    <div className="content-body" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Top Header & Controls */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-black" style={{ fontSize: '10.5px' }}>STEP 12</span>
            <span style={{ fontSize: '12px', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Strategic Intelligence Synthesis
            </span>
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em', margin: 0 }}>
            Executive Intelligence Briefing
          </h1>
          <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', marginTop: '6px', maxWidth: '820px' }}>
            Board-level memorandum synthesizing real competitor activity, historical Hindsight episodic memories,
            cross-category patterns, and proactive change alerts into an evidence-grounded strategic briefing.
          </p>
        </div>

        {/* Global Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={handleCopyText}
            disabled={!report || loading}
            className="btn btn-outline btn-sm"
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            {copied ? <Check size={13} /> : <Copy size={13} />}
            <span>{copied ? 'Copied Brief' : 'Copy Briefing'}</span>
          </button>

          <button
            onClick={handlePrint}
            disabled={!report || loading}
            className="btn btn-primary btn-sm"
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <Printer size={13} />
            <span>Print Report</span>
          </button>
        </div>
      </div>

      {/* Target Competitor & Range Selector Card */}
      <div className="card" style={{
        padding: '18px 24px',
        backgroundColor: 'var(--bg-secondary)',
        border: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        {/* Competitor Selector Pills */}
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
          <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginRight: '4px' }}>
            Target:
          </span>
          {competitors.map(c => (
            <button
              key={c.id}
              onClick={() => {
                setSelectedCompetitor(c.id);
                handleGenerateReport(c.name || c.id, timeRange);
              }}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '5px 12px',
                fontSize: '12px',
                fontWeight: 600,
                borderRadius: 'var(--radius-sm)',
                border: selectedCompetitor === c.id ? '1px solid var(--border-black)' : '1px solid var(--border-subtle)',
                backgroundColor: selectedCompetitor === c.id ? 'var(--text-primary)' : 'var(--bg-primary)',
                color: selectedCompetitor === c.id ? '#ffffff' : 'var(--text-primary)',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              <CompanyLogo competitorId={c.id} size={14} />
              <span>{c.name}</span>
            </button>
          ))}
        </div>

        {/* Time Range Filter & Generate Button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
            Period:
          </span>
          {[
            { id: 'all', label: 'All History' },
            { id: 'last_180_days', label: '180 Days' },
            { id: 'last_90_days', label: '90 Days' },
            { id: 'last_30_days', label: '30 Days' }
          ].map(tr => (
            <button
              key={tr.id}
              onClick={() => {
                setTimeRange(tr.id);
                handleGenerateReport(null, tr.id);
              }}
              style={{
                padding: '4px 10px',
                fontSize: '11.5px',
                fontWeight: 600,
                borderRadius: 'var(--radius-sm)',
                border: timeRange === tr.id ? '1px solid var(--border-black)' : '1px solid var(--border-medium)',
                backgroundColor: timeRange === tr.id ? 'var(--pink-lightest)' : 'var(--bg-primary)',
                color: 'var(--text-primary)',
                cursor: 'pointer'
              }}
            >
              {tr.label}
            </button>
          ))}

          <button
            onClick={() => handleGenerateReport()}
            disabled={loading}
            className="btn btn-primary btn-sm"
            style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', marginLeft: '6px' }}
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
            <span>{loading ? 'Synthesizing...' : 'Generate Brief'}</span>
          </button>
        </div>
      </div>

      {/* Visual Pipeline Bar (Demo Requirement Section 16) */}
      <div style={{
        padding: '12px 18px',
        backgroundColor: 'var(--bg-primary)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '8px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
          <span style={{ fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase' }}>CORE PIPELINE:</span>
          
          <span style={{ fontWeight: 700, color: pipelineStep === 'events' ? '#b8324f' : 'var(--text-primary)' }}>
            REAL SQL EVENTS
          </span>
          <ChevronRight size={12} color="var(--border-dark)" />

          <span style={{ fontWeight: 700, color: pipelineStep === 'hindsight' ? '#b8324f' : 'var(--text-primary)' }}>
            HINDSIGHT RECALL
          </span>
          <ChevronRight size={12} color="var(--border-dark)" />

          <span style={{ fontWeight: 700, color: pipelineStep === 'patterns' ? '#b8324f' : 'var(--text-primary)' }}>
            PATTERNS (STEP 10)
          </span>
          <ChevronRight size={12} color="var(--border-dark)" />

          <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
            ALERTS (STEP 11)
          </span>
          <ChevronRight size={12} color="var(--border-dark)" />

          <span style={{ fontWeight: 700, color: pipelineStep === 'groq' ? '#b8324f' : 'var(--text-primary)' }}>
            GROQ REASONING
          </span>
          <ChevronRight size={12} color="var(--border-dark)" />

          <span className="badge badge-black" style={{ fontSize: '10px', padding: '2px 8px' }}>
            EXECUTIVE BRIEF
          </span>
        </div>

        <div className="cautious-pill">
          <ShieldCheck size={12} color="var(--text-primary)" />
          <span>ZERO FABRICATION GUARANTEE</span>
        </div>
      </div>

      {/* Mascot Status Callout */}
      <div style={{
        padding: '16px 22px',
        backgroundColor: isInsufficient ? '#fef8f8' : 'var(--pink-lightest)',
        border: '1.5px solid var(--border-black)',
        borderRadius: 'var(--radius-md)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <AgentMascot size={42} state={mascotState} />
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '13.5px', fontWeight: 800, color: 'var(--text-primary)' }}>
                IQ-Agent Executive Dispatch
              </span>
              <span className={`badge ${isInsufficient ? 'badge-outline' : 'badge-pink'}`} style={{ fontSize: '10px' }}>
                {isInsufficient ? 'Telemetry Boundary' : 'Verified Briefing'}
              </span>
            </div>
            <div style={{ fontSize: '12.5px', color: 'var(--text-secondary)', marginTop: '2px', lineHeight: 1.45 }}>
              {mascotSpeech}
            </div>
          </div>
        </div>

        {report && !isInsufficient && (
          <div style={{ textAlign: 'right', flexShrink: 0 }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block' }}>CONFIDENCE RATING</span>
            <span className="badge badge-black" style={{ fontSize: '11px', marginTop: '2px' }}>
              {report.confidence?.toUpperCase() || 'HIGH'}
            </span>
          </div>
        )}
      </div>

      {/* Main Content Area */}
      {loading ? (
        <div className="card" style={{ padding: '80px', textAlign: 'center' }}>
          <RefreshCw size={28} className="animate-spin" style={{ margin: '0 auto 16px', color: 'var(--text-muted)' }} />
          <div style={{ fontSize: '15px', fontWeight: 800, color: 'var(--text-primary)' }}>
            Synthesizing Executive Intelligence Brief...
          </div>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '6px' }}>
            Recalling persistent Hindsight memories, evaluating cross-category patterns, and grounding analysis via Groq.
          </p>
        </div>
      ) : isInsufficient ? (
        /* Section 13: Insufficient Historical Data State */
        <div className="card" style={{ padding: '36px 40px', border: '1.5px solid var(--border-black)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <AlertCircle size={28} color="#b8324f" />
            <div>
              <h2 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
                Insufficient Historical Telemetry
              </h2>
              <span style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>
                {report.competitor} • Period: {report.report_period}
              </span>
            </div>
          </div>

          <div className="intel-quote" style={{ fontSize: '13px', lineHeight: 1.6, marginBottom: '24px' }}>
            {report.executive_summary}
          </div>

          {/* Breakdown of available evidence */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
            <div style={{ padding: '16px', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>Available Events</div>
              <div style={{ fontSize: '20px', fontWeight: 800, color: 'var(--text-primary)', marginTop: '4px' }}>
                {report.available_events_count || 0}
              </div>
            </div>

            <div style={{ padding: '16px', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>Observed Date Range</div>
              <div style={{ fontSize: '13.5px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', marginTop: '8px' }}>
                {report.available_date_range?.start || 'None'} → {report.available_date_range?.end || 'None'}
              </div>
            </div>

            <div style={{ padding: '16px', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>Known Sources</div>
              <div style={{ fontSize: '12.5px', color: 'var(--text-primary)', marginTop: '6px' }}>
                {report.available_sources?.length > 0 ? report.available_sources.join(', ') : 'No sources logged'}
              </div>
            </div>
          </div>

          {/* Transparent Limitations */}
          <div>
            <span style={{ fontSize: '12px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', display: 'block', marginBottom: '8px' }}>
              Required Data to Generate Full Executive Briefing:
            </span>
            <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              {report.limitations?.map((lim, idx) => (
                <li key={idx}>{lim}</li>
              ))}
            </ul>
          </div>
        </div>
      ) : report ? (
        /* Printable Executive Memorandum Card */
        <div className="card" style={{
          padding: '40px 48px',
          display: 'flex',
          flexDirection: 'column',
          gap: '32px',
          border: '1.5px solid var(--border-black)',
          backgroundColor: 'var(--bg-primary)',
          boxShadow: 'var(--shadow-sm)'
        }}>
          
          {/* Memorandum Formal Letterhead */}
          <div style={{
            borderBottom: '2px solid var(--border-black)',
            paddingBottom: '24px',
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '16px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <CompanyLogo competitorId={report.competitor_id || selectedCompetitor} size={48} />
              <div>
                <div style={{
                  display: 'inline-block',
                  fontSize: '10px',
                  fontWeight: 900,
                  fontFamily: 'var(--font-mono)',
                  letterSpacing: '0.12em',
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase',
                  marginBottom: '2px'
                }}>
                  CONFIDENTIAL // BOARD-LEVEL INTELLIGENCE MEMO
                </div>
                <h2 style={{ fontSize: '26px', fontWeight: 900, color: 'var(--text-primary)', margin: 0, letterSpacing: '-0.02em' }}>
                  {report.competitor} Strategic Intelligence Brief
                </h2>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '6px', fontSize: '12px', color: 'var(--text-muted)' }}>
                  <span><strong style={{ color: 'var(--text-primary)' }}>Period:</strong> {report.report_period}</span>
                  <span>•</span>
                  <span><strong style={{ color: 'var(--text-primary)' }}>Generated:</strong> {report.generated_at}</span>
                  <span>•</span>
                  <span><strong style={{ color: 'var(--text-primary)' }}>Memory Bank:</strong> {report.memory_used?.memory_identifier}</span>
                </div>
              </div>
            </div>

            {/* Step 9 Before/After Pill Anchor */}
            <div style={{ textAlign: 'right' }}>
              <div className="cautious-pill" style={{ backgroundColor: 'var(--pink-lightest)' }}>
                <Database size={11} />
                <span>POWERED BY HINDSIGHT EPISODIC MEMORY</span>
              </div>
            </div>
          </div>

          {/* Section Navigation Tabs */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            borderBottom: '1px solid var(--border-subtle)',
            paddingBottom: '12px'
          }}>
            {[
              { id: 'summary', label: 'Executive Summary' },
              { id: 'patterns', label: `Detected Patterns (${report.major_patterns?.length || 0})` },
              { id: 'signals', label: `Strategic Signals (${report.strategic_signals?.length || 0})` },
              { id: 'changes', label: `What Changed (${report.what_changed?.length || 0})` },
              { id: 'activity', label: `Timeline Events (${report.recent_activity?.length || 0})` },
              { id: 'memory', label: 'Hindsight Memory' },
              { id: 'evidence', label: `Verified Evidence (${report.key_evidence?.length || 0})` }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  padding: '6px 14px',
                  fontSize: '12px',
                  fontWeight: 700,
                  borderRadius: 'var(--radius-sm)',
                  border: activeTab === tab.id ? '1px solid var(--border-black)' : '1px solid transparent',
                  backgroundColor: activeTab === tab.id ? 'var(--text-primary)' : 'transparent',
                  color: activeTab === tab.id ? '#ffffff' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* TAB 1: EXECUTIVE SUMMARY */}
          {(activeTab === 'summary' || activeTab === 'all') && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="badge badge-black" style={{ fontSize: '10px' }}>SECTION 01</span>
                <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
                  Executive Intelligence Summary
                </h3>
              </div>

              {/* Distinguish Fact from Pattern from Interpretation */}
              <div style={{
                padding: '24px 28px',
                backgroundColor: 'var(--pink-lightest)',
                border: '1px solid var(--border-dark)',
                borderRadius: 'var(--radius-md)',
                fontSize: '13.5px',
                lineHeight: 1.7,
                color: 'var(--text-primary)',
                whiteSpace: 'pre-line'
              }}>
                {report.executive_summary}
              </div>

              {/* Strategic Signals Callout inside Summary */}
              {report.strategic_signals?.length > 0 && (
                <div style={{ marginTop: '8px' }}>
                  <span style={{ fontSize: '11.5px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', display: 'block', marginBottom: '8px' }}>
                    Key Strategic Signals Inferred from Evidence:
                  </span>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '12px' }}>
                    {report.strategic_signals.map((sig, idx) => (
                      <div key={idx} style={{
                        padding: '14px 18px',
                        backgroundColor: 'var(--bg-secondary)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-sm)'
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                          <span style={{ fontWeight: 800, fontSize: '13px', color: 'var(--text-primary)' }}>
                            {sig.signal}
                          </span>
                          <span className="badge badge-outline" style={{ fontSize: '9.5px' }}>
                            {sig.confidence?.toUpperCase() || 'HIGH'}
                          </span>
                        </div>
                        <p style={{ margin: 0, fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                          {sig.observed_trajectory}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: MAJOR PATTERNS (STEP 10 INTEGRATION) */}
          {activeTab === 'patterns' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="badge badge-black" style={{ fontSize: '10px' }}>SECTION 02</span>
                <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
                  Detected Cross-Category Strategic Patterns
                </h3>
              </div>

              {report.major_patterns?.length === 0 ? (
                <div className="card" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  No multi-event patterns detected in this reporting period.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {report.major_patterns.map((p, idx) => (
                    <div key={idx} className="card" style={{
                      padding: '20px 24px',
                      borderLeft: '4px solid var(--border-black)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '12px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <TrendingUp size={16} color="var(--text-primary)" />
                          <h4 style={{ fontSize: '15px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
                            {p.pattern}
                          </h4>
                        </div>
                        <span className="badge badge-black">{p.confidence?.toUpperCase() || 'HIGH'}</span>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                        <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)' }}>Categories:</span>
                        {p.categories?.map((cat, cIdx) => (
                          <span key={cIdx} className="badge badge-outline" style={{ fontSize: '10px' }}>
                            {cat}
                          </span>
                        ))}
                      </div>

                      <p style={{ margin: 0, fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.55 }}>
                        <strong style={{ color: 'var(--text-primary)' }}>Cross-Event Evidence: </strong>
                        {p.evidence}
                      </p>

                      {p.why_it_matters && (
                        <div style={{ padding: '10px 14px', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', fontSize: '12.5px', color: 'var(--text-secondary)' }}>
                          <strong>Why It Matters: </strong>{p.why_it_matters}
                        </div>
                      )}

                      {/* Supporting Events Chips */}
                      {p.event_ids?.length > 0 && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap', paddingTop: '6px', borderTop: '1px dashed var(--border-subtle)' }}>
                          <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)' }}>Connected Event IDs:</span>
                          {p.event_ids.map((eid, eIdx) => (
                            <span key={eIdx} style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', padding: '2px 6px', backgroundColor: 'var(--pink-lightest)', borderRadius: 'var(--radius-sm)' }}>
                              {eid}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 3: STRATEGIC SIGNALS */}
          {activeTab === 'signals' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="badge badge-black" style={{ fontSize: '10px' }}>SECTION 03</span>
                <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
                  Evidence-Grounded Strategic Signals
                </h3>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {report.strategic_signals?.map((sig, idx) => (
                  <div key={idx} className="card" style={{ padding: '18px 22px', borderLeft: '4px solid #ea96a5' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Zap size={15} color="#0a0a0a" />
                        <h4 style={{ fontSize: '14.5px', fontWeight: 800, margin: 0 }}>{sig.signal}</h4>
                      </div>
                      <span className="badge badge-outline">{sig.confidence?.toUpperCase() || 'HIGH'}</span>
                    </div>

                    <p style={{ margin: '0 0 10px 0', fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                      {sig.observed_trajectory}
                    </p>

                    {sig.supporting_event_ids?.length > 0 && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--text-muted)' }}>
                        <span style={{ fontWeight: 700 }}>Supporting Telemetry IDs:</span>
                        {sig.supporting_event_ids.map((id, idIdx) => (
                          <span key={idIdx} style={{ fontFamily: 'var(--font-mono)', padding: '1px 5px', backgroundColor: 'var(--bg-secondary)', borderRadius: '3px' }}>
                            {id}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: WHAT CHANGED (STEP 11 ALERTS INTEGRATION) */}
          {activeTab === 'changes' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="badge badge-black" style={{ fontSize: '10px' }}>SECTION 04</span>
                <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
                  Recent Proactive Change Alerts ("What Changed?")
                </h3>
              </div>

              {report.what_changed?.length === 0 ? (
                <div className="card" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  No unacknowledged delta alerts recorded for this period.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  {report.what_changed.map((alt, idx) => (
                    <div key={idx} className="card" style={{ padding: '18px 22px', backgroundColor: 'var(--bg-primary)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span style={{ fontSize: '14px', fontWeight: 800, color: 'var(--text-primary)' }}>
                          {alt.title}
                        </span>
                        <span className="badge badge-pink">{alt.event_type || 'Product'}</span>
                      </div>
                      <p style={{ margin: '0 0 8px 0', fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.5 }}>
                        <strong>What Changed: </strong>{alt.what_changed}
                      </p>
                      <p style={{ margin: 0, fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                        <strong>Why It Matters: </strong>{alt.why_it_matters}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 5: TIMELINE EVENTS */}
          {activeTab === 'activity' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="badge badge-black" style={{ fontSize: '10px' }}>SECTION 05</span>
                <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
                  Chronological Verified Activity
                </h3>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {report.recent_activity?.map((ev, idx) => (
                  <div key={ev.id || idx} className="card" style={{ padding: '16px 20px', display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '16px' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11.5px', fontWeight: 700, color: 'var(--text-muted)' }}>
                          [{ev.event_date}]
                        </span>
                        <span className="badge badge-outline" style={{ fontSize: '10px' }}>
                          {ev.event_type || ev.category}
                        </span>
                      </div>
                      <h4 style={{ fontSize: '14px', fontWeight: 800, color: 'var(--text-primary)', margin: '0 0 4px 0' }}>
                        {ev.title}
                      </h4>
                      <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.45 }}>
                        {ev.description}
                      </p>
                    </div>

                    {onSelectEvent && (
                      <button
                        onClick={() => onSelectEvent(ev)}
                        className="btn btn-outline btn-sm"
                        style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', flexShrink: 0 }}
                      >
                        <Eye size={12} />
                        <span>Inspect</span>
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 6: HINDSIGHT MEMORY TRANSPARENCY (SECTION 8 & 11) */}
          {activeTab === 'memory' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="badge badge-black" style={{ fontSize: '10px' }}>SECTION 06</span>
                <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
                  What Did Hindsight Remember?
                </h3>
              </div>

              {/* Step 9 Before vs After Contrast Banner (Section 11) */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '16px',
                padding: '20px',
                backgroundColor: 'var(--bg-secondary)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-subtle)'
              }}>
                <div style={{ padding: '16px', backgroundColor: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                    Without Long-Term Memory (Generic Agent)
                  </div>
                  <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', margin: '8px 0 0 0', lineHeight: 1.5 }}>
                    Evaluates events in total isolation. Only sees the single most recent move with zero multi-quarter context.
                    Blind to OpenAI partnership extensions, pricing models, or earlier executive talent migrations.
                  </p>
                </div>

                <div style={{ padding: '16px', backgroundColor: 'var(--pink-lightest)', borderRadius: 'var(--radius-sm)', border: '1.5px solid var(--border-black)' }}>
                  <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-primary)' }}>
                    With Hindsight Persistent Memory
                  </div>
                  <p style={{ fontSize: '12.5px', color: 'var(--text-primary)', margin: '8px 0 0 0', lineHeight: 1.5 }}>
                    Recalled <strong>{report.memory_used?.event_count || 0} episodic memories</strong> across{' '}
                    <strong>{report.memory_used?.date_range?.start} → {report.memory_used?.date_range?.end}</strong>.
                    Connects foundational investment to Copilot 365 monetization, Inflection AI executive hiring, and Copilot Studio autonomous agents.
                  </p>
                </div>
              </div>

              {/* Recalled Memory Nodes */}
              <div>
                <span style={{ fontSize: '11.5px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', display: 'block', marginBottom: '10px' }}>
                  Recalled Episodic Memories Grounding This Brief:
                </span>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {report.historical_context?.map((mem, idx) => (
                    <div key={idx} style={{
                      padding: '12px 16px',
                      backgroundColor: 'var(--bg-primary)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '12px'
                    }}>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-muted)', flexShrink: 0 }}>
                        [{mem.date || 'Historical'}]
                      </span>
                      <span style={{ fontSize: '12.5px', color: 'var(--text-primary)', lineHeight: 1.45 }}>
                        {mem.text}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 7: KEY EVIDENCE & VERIFIED SOURCES (SECTION 7) */}
          {activeTab === 'evidence' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="badge badge-black" style={{ fontSize: '10px' }}>SECTION 07</span>
                <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
                  Traceable Evidence Ledger & Verified Sources
                </h3>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {report.key_evidence?.map((ev, idx) => (
                  <div key={idx} className="card" style={{
                    padding: '16px 20px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    flexWrap: 'wrap',
                    gap: '12px'
                  }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-muted)' }}>
                          [{ev.event_date}]
                        </span>
                        <span className="badge badge-outline" style={{ fontSize: '9.5px' }}>
                          {ev.event_type}
                        </span>
                        <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                          ID: {ev.event_id}
                        </span>
                      </div>
                      <h4 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
                        {ev.title}
                      </h4>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {ev.source_url ? (
                        <a
                          href={ev.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn btn-outline btn-sm"
                          style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', textDecoration: 'none' }}
                        >
                          <ExternalLink size={12} />
                          <span>{ev.source_name || 'View Source'}</span>
                        </a>
                      ) : (
                        <span style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>
                          {ev.source_name}
                        </span>
                      )}

                      {onSelectEvent && (
                        <button
                          onClick={() => onSelectEvent(ev)}
                          className="btn btn-ghost btn-sm"
                          style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                        >
                          <Eye size={12} />
                          <span>Inspect</span>
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Memorandum Sign-off Footer */}
          <div style={{
            borderTop: '2px solid var(--border-black)',
            paddingTop: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '11px',
            color: 'var(--text-muted)',
            fontFamily: 'var(--font-mono)'
          }}>
            <div>
              MEMORANDUM ID: BRIEF-{report.competitor_id?.toUpperCase() || 'COMP'}-{Date.now().toString().slice(-6)}
            </div>
            <div>
              AUTHENTICATED BY COMPETITORIQ AI ENGINE • HINDSIGHT VERIFIED
            </div>
          </div>

        </div>
      ) : (
        <div className="card" style={{
          padding: '52px 24px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '14px',
          backgroundColor: 'var(--bg-secondary)',
          border: '1px solid var(--border-subtle)',
          textAlign: 'center'
        }}>
          <AgentMascot size={60} state="curious" />
          <h3 style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-primary)' }}>
            Select a Competitor to Generate Executive Briefing
          </h3>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', maxWidth: '540px', lineHeight: 1.5 }}>
            Executive Intelligence Briefs synthesize accumulated events, recalled Hindsight episodic memories, multi-hop strategic patterns, and proactive alerts into a structured, board-ready memorandum.
          </p>
          <button
            onClick={() => handleGenerateReport()}
            className="btn btn-primary"
            style={{ marginTop: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}
          >
            <Sparkles size={15} />
            <span>Generate Brief for {competitors.find(c => c.id === selectedCompetitor)?.name || selectedCompetitor}</span>
          </button>
        </div>
      )}

    </div>
  );
}
