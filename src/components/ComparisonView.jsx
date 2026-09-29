import React, { useState, useEffect } from 'react';
import {
  Scale,
  ShieldCheck,
  ArrowRight,
  ExternalLink,
  Check,
  Copy,
  BarChart3,
  Sparkles,
  Database,
  Layers,
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import { COMPETITORS } from '../data/mockData';
import { competitorApi } from '../services/api';
import CompanyLogo from './CompanyLogo';
import CategoryIcon from './CategoryIcon';
import AgentMascot from './AgentMascot';

export default function ComparisonView({ onSelectCompetitor, onSelectView }) {
  const [competitorsList, setCompetitorsList] = useState([]);
  const [selectedCompetitors, setSelectedCompetitors] = useState([]);
  const [comparisonQuestion, setComparisonQuestion] = useState('');
  const [comparisonResult, setComparisonResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch real competitors on mount
  useEffect(() => {
    competitorApi.getCompetitors()
      .then(data => {
        if (data && data.length > 0) {
          setCompetitorsList(data);
        }
      })
      .catch(err => console.warn('Could not load competitors in ComparisonView:', err));
  }, []);

  const toggleCompetitor = (compName) => {
    setSelectedCompetitors(prev => {
      if (prev.includes(compName)) {
        return prev.filter(c => c !== compName);
      } else {
        if (prev.length >= 5) return prev; // Max 5 for visual comparison
        return [...prev, compName];
      }
    });
  };

  const handleRunComparison = async () => {
    if (selectedCompetitors.length < 2 || !comparisonQuestion.trim()) return;
    setIsLoading(true);
    setError(null);

    try {
      const data = await competitorApi.compareCompetitors({
        competitors: selectedCompetitors,
        question: comparisonQuestion
      });
      setComparisonResult(data);
    } catch (err) {
      console.error('Comparison error:', err);
      setError(err.message || 'Unable to execute comparative reasoning across memory banks.');
    } finally {
      setIsLoading(false);
    }
  };

  const activeCompetitors = competitorsList.length > 0 ? competitorsList : COMPETITORS;

  return (
    <div className="content-body" style={{ display: 'flex', flexDirection: 'column', gap: '26px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: '22px', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            Multi-Competitor Strategic Comparison Matrix
          </h1>
          <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Comparative cross-sectional analysis across core operational dimensions, packaging strategies, and battleground vulnerabilities.
          </p>
        </div>

        <div className="cautious-pill">
          <Scale size={13} color="var(--text-primary)" />
          <span>SIDE-BY-SIDE INTELLIGENCE AUDIT</span>
        </div>
      </div>

      {/* Dynamic Multi-Competitor Selector & Inquiry Bar */}
      <div className="card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '18px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 800, color: 'var(--text-primary)' }}>
              Select Competitors to Compare (Select 2 to 5):
            </div>
            <div style={{ fontSize: '11.5px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Each selected rival recalls its isolated Hindsight memory bank before Groq cross-analyzes differences.
            </div>
          </div>
          <span className="badge badge-black">
            {selectedCompetitors.length} Rivals Selected
          </span>
        </div>

        {/* Competitor Selector Pills */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {activeCompetitors.map(comp => {
            const isSelected = selectedCompetitors.includes(comp.name);
            return (
              <button
                key={comp.id || comp.name}
                type="button"
                onClick={() => toggleCompetitor(comp.name)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 12px',
                  fontSize: '12px',
                  fontWeight: 600,
                  borderRadius: 'var(--radius-sm)',
                  border: isSelected ? '1.5px solid var(--text-primary)' : '1px solid var(--border-medium)',
                  backgroundColor: isSelected ? 'var(--text-primary)' : 'var(--bg-secondary)',
                  color: isSelected ? 'var(--text-inverse)' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
              >
                <CompanyLogo competitorId={comp.id} size={14} />
                <span>{comp.name}</span>
                {isSelected && <Check size={12} />}
              </button>
            );
          })}
        </div>

        {/* Comparison Question Bar */}
        <div style={{ display: 'flex', gap: '10px', marginTop: '6px' }}>
          <input
            type="text"
            placeholder="Comparison question: e.g. How do their AI strategies differ?"
            value={comparisonQuestion}
            onChange={(e) => setComparisonQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !isLoading && handleRunComparison()}
            className="input-minimal"
            style={{ fontSize: '13.5px', padding: '10px 14px' }}
          />

          <button
            onClick={handleRunComparison}
            disabled={isLoading || selectedCompetitors.length < 2 || !comparisonQuestion.trim()}
            className="btn btn-primary"
            style={{ minWidth: '180px', padding: '10px 18px', gap: '8px' }}
          >
            <Sparkles size={15} />
            <span>{isLoading ? 'Synthesizing...' : 'Compare Memory Banks'}</span>
          </button>
        </div>

        {/* Preset Question Queries */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 700 }}>Inquiry Presets:</span>
          {[
            'How do their AI strategies differ?',
            'What are the commercial pricing divergences?',
            'Which rival is advancing fastest in enterprise autonomous agents?'
          ].map((preset, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setComparisonQuestion(preset);
              }}
              style={{
                fontSize: '11px',
                padding: '3px 8px',
                backgroundColor: 'var(--bg-secondary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                cursor: 'pointer',
                color: 'var(--text-secondary)'
              }}
            >
              {preset}
            </button>
          ))}
        </div>
      </div>

      {/* Error Banner */}
      {error && (
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
            <strong>Comparison Error:</strong> {error}
          </div>
          <button
            onClick={handleRunComparison}
            className="btn btn-sm btn-outline"
            style={{ borderColor: '#FEB2B2', color: '#C53030' }}
          >
            Retry
          </button>
        </div>
      )}

      {/* Loading Stepper */}
      {isLoading && (
        <div className="card" style={{ padding: '36px', textAlign: 'center', backgroundColor: 'var(--pink-lightest)', borderColor: 'var(--pink-border)' }}>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '14px' }}>
            <AgentMascot size={54} state="thinking" className="mascot-floating" />
          </div>
          <div style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '6px' }}>
            Recalling & Isolating Memory Banks for {selectedCompetitors.join(' vs ')}
          </div>
          <div style={{ fontSize: '13px', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
            Groq LLM is synthesizing company insights, shared patterns, and strategic divergences...
          </div>
        </div>
      )}

      {/* Initial Empty State: "Nothing selected yet" / "Choose competitors to begin" */}
      {!isLoading && !comparisonResult && (
        <div
          className="card"
          style={{
            padding: '36px 28px',
            textAlign: 'center',
            backgroundColor: 'var(--bg-secondary)',
            borderColor: 'var(--border-subtle)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '12px'
          }}
        >
          <AgentMascot size={52} state="curious" />
          <h3 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)', marginTop: '4px' }}>
            {selectedCompetitors.length < 2
              ? 'Choose at least 2 competitors to begin comparison'
              : 'Ready to compare memory banks'}
          </h3>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', maxWidth: '520px', lineHeight: 1.5 }}>
            {selectedCompetitors.length < 2
              ? 'Select 2 to 5 rival companies above and enter a comparison question. CompetitorIQ will pull from isolated Hindsight memory banks and cross-analyze strategic differences.'
              : `You have selected ${selectedCompetitors.join(', ')}. Enter an inquiry or click an inquiry preset above, then click 'Compare Memory Banks' to begin.`}
          </p>
        </div>
      )}

      {/* Real Comparison Result Display */}
      {!isLoading && comparisonResult && (
        <div className="card" style={{ padding: '28px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Header */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            paddingBottom: '16px',
            borderBottom: '1px solid var(--border-subtle)',
            flexWrap: 'wrap',
            gap: '12px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <AgentMascot size={40} state="explaining" />
              <div>
                <span style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 800 }}>
                  Multi-Competitor Synthesis
                </span>
                <div style={{ fontSize: '17px', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>
                  "{comparisonResult.question || comparisonQuestion}"
                </div>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="badge badge-black">
                {comparisonResult.competitors?.length || selectedCompetitors.length} RIVALS COMPARED
              </span>
              <span className="badge badge-pink">
                MODEL: {comparisonResult.model_used || 'openai/gpt-oss-120b'}
              </span>
            </div>
          </div>

          {/* 1. Comparison Executive Summary */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
              <span className="badge badge-black" style={{ fontSize: '10px' }}>SECTION 1</span>
              <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                EXECUTIVE COMPARISON SYNTHESIS
              </div>
            </div>
            <div style={{
              padding: '18px 22px',
              backgroundColor: 'var(--pink-lightest)',
              border: '1.5px solid var(--pink-border)',
              borderRadius: 'var(--radius-md)',
              fontSize: '14.5px',
              lineHeight: 1.6,
              color: 'var(--text-primary)'
            }}>
              {comparisonResult.comparison || 'Comparative analysis complete.'}
            </div>
          </div>

          {/* 2. Company Insights Grid */}
          {comparisonResult.company_insights && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
                <span className="badge badge-black" style={{ fontSize: '10px' }}>SECTION 2</span>
                <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                  COMPANY-SPECIFIC INTELLIGENCE INSIGHTS
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: `repeat(auto-fit, minmax(280px, 1fr))`, gap: '14px' }}>
                {Object.entries(comparisonResult.company_insights).map(([compName, insightText]) => (
                  <div
                    key={compName}
                    className="card"
                    style={{
                      padding: '18px',
                      borderLeft: '4px solid var(--text-primary)',
                      backgroundColor: 'var(--bg-secondary)'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                      <CompanyLogo competitorId={compName.toLowerCase().replace(/[^a-z0-9]+/g, '-')} size={20} />
                      <div style={{ fontSize: '14px', fontWeight: 800, color: 'var(--text-primary)' }}>
                        {compName}
                      </div>
                    </div>
                    <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                      {typeof insightText === 'string' ? insightText : JSON.stringify(insightText)}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 3. Shared Patterns & Differences Columns */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            {/* Shared Patterns */}
            <div className="card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
                <span className="badge badge-black" style={{ fontSize: '10px' }}>PATTERNS</span>
                <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                  Shared Patterns & Convergences
                </div>
              </div>
              {(!comparisonResult.shared_patterns || comparisonResult.shared_patterns.length === 0) ? (
                <div style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>
                  No shared behavioral patterns observed across these entities in memory.
                </div>
              ) : (
                <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.6 }}>
                  {comparisonResult.shared_patterns.map((pat, idx) => (
                    <li key={idx} style={{ marginBottom: '6px' }}>{pat}</li>
                  ))}
                </ul>
              )}
            </div>

            {/* Strategic Differences */}
            <div className="card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
                <span className="badge badge-pink" style={{ fontSize: '10px' }}>DIFFERENCES</span>
                <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                  Strategic Divergences
                </div>
              </div>
              {(!comparisonResult.differences || comparisonResult.differences.length === 0) ? (
                <div style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>
                  No sharp strategic divergences identified in current memory context.
                </div>
              ) : (
                <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.6 }}>
                  {comparisonResult.differences.map((diff, idx) => (
                    <li key={idx} style={{ marginBottom: '6px' }}>{diff}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* 4. Memory Transparency per Competitor */}
          <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
              <Database size={14} color="var(--text-primary)" />
              <span style={{ fontSize: '12px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-primary)' }}>
                Hindsight Memory Transparency per Competitor Bank
              </span>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
              {comparisonResult.memory_used && Object.entries(comparisonResult.memory_used).map(([compName, memInfo]) => (
                <div
                  key={compName}
                  style={{
                    padding: '8px 14px',
                    backgroundColor: 'var(--bg-secondary)',
                    border: '1px solid var(--border-medium)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '11.5px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  <CompanyLogo competitorId={compName.toLowerCase().replace(/[^a-z0-9]+/g, '-')} size={14} />
                  <span style={{ fontWeight: 800 }}>{compName}:</span>
                  <span style={{ color: 'var(--text-secondary)' }}>
                    {memInfo?.count || (Array.isArray(memInfo) ? memInfo.length : 0)} recalled nodes
                  </span>
                  {memInfo?.date_range && (
                    <span style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                      ({memInfo.date_range.earliest || 'Past'} → {memInfo.date_range.latest || 'Present'})
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>

        </div>
      )}

      {/* Competitor Overview Cards Row */}
      <div>
        <div style={{ fontSize: '12px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '12px' }}>
          Registered Competitors for Comparative Analysis ({activeCompetitors.length})
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          {activeCompetitors.map(comp => (
            <div
              key={comp.id || comp.name}
              className="card"
              style={{
                padding: '18px',
                cursor: 'pointer',
                border: selectedCompetitors.includes(comp.name) ? '1.5px solid var(--text-primary)' : '1px solid var(--border-subtle)',
                backgroundColor: selectedCompetitors.includes(comp.name) ? 'var(--pink-lightest)' : 'var(--bg-primary)'
              }}
              onClick={() => onSelectCompetitor(comp.id)}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <CompanyLogo competitorId={comp.id} size={28} />
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <span className="badge badge-black">{comp.stage || 'Tracked'}</span>
                  <span className="badge badge-pink">{comp.threatLevel || 'Active'}</span>
                </div>
              </div>
              <div style={{ fontSize: '17px', fontWeight: 800, color: 'var(--text-primary)' }}>
                {comp.name}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                {comp.arrEstimate || 'Enterprise Scale'} • {comp.employeeCount || 'Monitored'}
              </div>
              <div style={{ fontSize: '11.5px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '10px' }}>
                View Dossier →
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
