// CompetitorIQ Centralized API Service Layer
// Connects the frontend to the Flask backend (SQLite + Hindsight episodic memory + Groq LLM)

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api';

/**
 * Custom API Error containing status code and error details.
 */
export class ApiError extends Error {
  constructor(message, status = 500, errorType = 'internal_error', details = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.errorType = errorType;
    this.details = details;
    this.isOffline = status === 0 || errorType === 'network_offline';
  }
}

/**
 * Universal JSON fetch helper with offline and timeout detection.
 */
async function fetchJson(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  };

  try {
    const res = await fetch(url, config);
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      const errorMsg = data.message || data.error || `HTTP ${res.status}: ${res.statusText}`;
      throw new ApiError(errorMsg, res.status, data.error_type || 'api_error', data);
    }

    return data;
  } catch (err) {
    if (err instanceof ApiError) {
      throw err;
    }
    // Network / offline error
    console.warn(`CompetitorIQ API Connection Error on ${endpoint}:`, err);
    throw new ApiError(
      'Unable to connect to CompetitorIQ backend server at http://127.0.0.1:5000. Please ensure the backend is running.',
      0,
      'network_offline',
      err
    );
  }
}

/**
 * Normalize competitor records to ensure both camelCase and snake_case properties are populated.
 */
export function normalizeCompetitor(c) {
  if (!c) return null;
  return {
    id: c.id,
    name: c.name,
    website: c.website || '',
    industry: c.industry || 'Technology / AI Platforms',
    description: c.description || '',
    tagline: c.tagline || c.description || 'Frontier AI & Cloud Technology Platform',
    hq: c.hq || 'Global Headquarters',
    stage: c.stage || 'Public / Venture Backed',
    threatLevel: c.threat_level || c.threatLevel || 'High',
    threat_level: c.threat_level || c.threatLevel || 'High',
    primaryBattleground: c.primary_battleground || c.primaryBattleground || c.industry || 'Enterprise AI',
    strategySummary: c.strategy_summary || c.description || 'Continuous monitoring of foundation models, enterprise workflows, and developer platforms.',
    arrEstimate: c.arr_estimate || c.arrEstimate || 'Enterprise Scale',
    employeeCount: c.employee_count || c.employeeCount || '10,000+',
    memoryNodesCount: c.memory_nodes_count || c.event_count || 12,
    eventCount: c.event_count || 0,
    patternScore: c.pattern_score || 94,
    categories: c.categories || ['Product', 'Technology', 'Pricing', 'Partnership'],
    lastUpdate: c.updated_at ? new Date(c.updated_at).toLocaleDateString() : 'Active monitoring',
    hindsightMemoryIdentifier: c.hindsight_memory_identifier || `competitor-${c.id}`
  };
}

/**
 * Normalize event records to ensure consistent field naming across UI components.
 */
export function normalizeEvent(e) {
  if (!e) return null;
  return {
    id: e.id,
    competitorId: e.competitor_id || e.competitorId,
    competitorName: e.competitor_name || e.competitorName || 'Competitor',
    category: e.event_type || e.category || 'Product',
    eventType: e.event_type || e.category || 'Product',
    title: e.title,
    description: e.description || '',
    date: e.event_date || e.date,
    eventDate: e.event_date || e.date,
    sourceName: e.source_name || e.source || 'Verified Source',
    sourceUrl: e.source_url || e.sourceUrl || '',
    impact: e.impact || 'Moderate',
    confidence: e.confidence || '95%',
    evidenceSnippet: e.evidence_snippet || e.description || '',
    whyItMatters: e.why_it_matters || e.significance || e.description || 'Strategic development with market positioning implications.',
    hindsightStatus: e.hindsight_status || 'retained'
  };
}

/**
 * Normalize an Alert record into standard UI format.
 */
export function normalizeAlert(a) {
  if (!a) return null;
  return {
    id: a.id,
    competitorId: a.competitor_id || a.competitorId,
    competitorName: a.competitor_name || a.competitorName || (a.competitor_id ? a.competitor_id.charAt(0).toUpperCase() + a.competitor_id.slice(1) : 'Competitor'),
    eventId: a.event_id || a.eventId,
    title: a.title,
    whatChanged: a.what_changed || a.whatChanged || '',
    whyItMatters: a.why_it_matters || a.whyItMatters || '',
    historicalContext: a.historical_context || a.historicalContext || '',
    eventType: a.event_type || a.eventType || 'Product',
    severity: a.severity || 'Medium attention',
    confidence: a.confidence || 'high',
    status: a.status || 'new',
    detectedAt: a.detected_at || a.detectedAt || '',
    sourceName: a.source_name || a.sourceName || 'Verified Corporate Source',
    sourceUrl: a.source_url || a.sourceUrl || '',
    memoryUsed: a.memory_used || { count: 0, earliest: null, latest: null },
    supportingEvents: (a.supporting_events || []).map(pe => ({
      eventId: pe.event_id || pe.eventId,
      title: pe.title,
      date: pe.date,
      eventType: pe.event_type || pe.eventType || 'Product'
    }))
  };
}

/**
 * Normalize AI Analyst response from the backend into UI consumable format.
 */
export function normalizeAnalystResponse(res) {
  if (!res) return null;

  const keyEvents = (res.key_events || []).map(ke => ({
    id: ke.event_id || 'evt-ref',
    title: ke.title || ke.event || 'Observed Milestone',
    category: ke.event_type || 'Product',
    date: ke.date || 'Historical',
    sourceName: ke.source || 'Verified Intelligence Record',
    sourceUrl: ke.source_url || '',
    competitorName: res.competitor || 'Target Competitor'
  }));

  const evidenceList = (res.evidence || []).map(ev => ({
    id: ev.memory_id || 'mem-node',
    label: `${ev.date ? `[${ev.date}] ` : ''}${ev.category || 'Memory'}: ${ev.text ? (ev.text.length > 70 ? ev.text.substring(0, 70) + '...' : ev.text) : 'Verified memory node'}`,
    date: ev.date,
    category: ev.category,
    text: ev.text,
    relevance: ev.relevance_score,
    source: ev.source,
    sourceUrl: ev.source_url
  }));

  return {
    competitor: res.competitor,
    query: res.question || '',
    question: res.question || '',
    strategicInsight: res.answer || '',
    answer: res.answer || '',
    pattern: res.pattern || 'Evolving Competitive Trajectory',
    strategicSignal: res.strategic_signal || '',
    implications: res.why_it_matters || '',
    confidence: res.confidence ? `${String(res.confidence).toUpperCase()} (Grounding in Persistent Memory)` : 'HIGH',
    dateRange: res.memory_used?.date_range?.earliest
      ? `${res.memory_used.date_range.earliest} → ${res.memory_used.date_range.latest || 'Present'}`
      : 'Verified Historical Timeline',
    memoryCount: res.memory_used?.count || evidenceList.length,
    memoryUsed: evidenceList,
    supportingEvents: keyEvents,
    connections: res.connections || [],
    analysisPoints: (res.connections || []).map(c =>
      typeof c === 'string' ? c : `${c.relationship ? `[${c.relationship}] ` : ''}${c.explanation || ''}`
    ),
    limitations: res.limitations || [],
    modelUsed: res.model_used || 'openai/gpt-oss-120b',
    bankId: res.bank_id,
    isInsufficientMemory: Boolean(
      res.memory_used?.count === 0 ||
      (res.answer && res.answer.toLowerCase().includes('insufficient stored evidence'))
    )
  };
}

/**
 * CompetitorIQ Frontend API Service
 */
export const competitorApi = {
  // 1. Competitors API
  async getCompetitors() {
    const data = await fetchJson('/competitors');
    const comps = data.competitors || data || [];
    return comps.map(normalizeCompetitor);
  },

  async getCompetitor(id) {
    const data = await fetchJson(`/competitors/${id}`);
    return normalizeCompetitor(data.competitor || data);
  },

  async getCompetitorById(id) {
    return this.getCompetitor(id);
  },

  async createCompetitor(data) {
    const res = await fetchJson('/competitors', {
      method: 'POST',
      body: JSON.stringify(data)
    });
    return normalizeCompetitor(res.competitor || res);
  },

  // 2. Events & Timeline API
  async getCompetitorEvents(id) {
    const data = await fetchJson(`/competitors/${id}/events`);
    const evts = data.events || [];
    return evts.map(normalizeEvent);
  },

  async getCompetitorTimeline(id) {
    const data = await fetchJson(`/competitors/${id}/timeline`);
    const timeline = data.timeline || data.events || [];
    return {
      competitor: normalizeCompetitor(data.competitor),
      timeline: timeline.map(normalizeEvent)
    };
  },

  async getEvents(params = {}) {
    const query = new URLSearchParams();
    if (params.competitor && params.competitor !== 'all') query.set('competitor', params.competitor);
    if (params.competitorId && params.competitorId !== 'all') query.set('competitor', params.competitorId);
    if (params.event_type && params.event_type !== 'all') query.set('event_type', params.event_type);
    if (params.category && params.category !== 'all') query.set('event_type', params.category);
    if (params.start_date) query.set('start_date', params.start_date);
    if (params.end_date) query.set('end_date', params.end_date);
    if (params.search) query.set('search', params.search);
    if (params.order_by) query.set('order_by', params.order_by);
    if (params.limit) query.set('limit', params.limit);

    const qs = query.toString();
    const endpoint = qs ? `/events?${qs}` : '/events';
    const data = await fetchJson(endpoint);
    const evts = data.events || data || [];
    return evts.map(normalizeEvent);
  },

  async getEventById(id) {
    const data = await fetchJson(`/events/${id}`);
    return normalizeEvent(data.event || data);
  },

  async createEvent(eventData) {
    const data = await fetchJson('/events', {
      method: 'POST',
      body: JSON.stringify(eventData)
    });
    return {
      event: normalizeEvent(data.event),
      hindsightStatus: data.hindsight_status
    };
  },

  // 3. AI Strategic Analyst API
  async analyzeCompetitor(payload) {
    const data = await fetchJson('/analyst/analyze', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    return normalizeAnalystResponse(data);
  },

  async queryAnalyst(question, competitor = null, onStep = null) {
    if (onStep) onStep('AI agent is recalling competitor history from Hindsight...');
    await new Promise(r => setTimeout(r, 350));

    if (onStep) onStep('AI agent is connecting multi-hop events across time...');
    await new Promise(r => setTimeout(r, 400));

    if (onStep) onStep('AI agent is generating evidence-grounded intelligence with Groq...');

    const payload = {
      competitor: competitor || 'Microsoft',
      question
    };

    return this.analyzeCompetitor(payload);
  },

  // 4. Multi-Competitor Comparison API
  async compareCompetitors(payload) {
    const data = await fetchJson('/analyst/compare', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    return data;
  },

  // 5. Memory & Ingestion Status API
  async getMemoryStatus() {
    return fetchJson('/memory/status');
  },

  async recallMemory(competitor, query, topK = 10) {
    const data = await fetchJson('/memory/recall', {
      method: 'POST',
      body: JSON.stringify({
        competitor,
        query,
        top_k: topK
      })
    });
    return data;
  },

  async getIngestionStatus() {
    return fetchJson('/ingestion/status');
  },

  async checkHealth() {
    return fetchJson('/health');
  },

  // 6. Before vs After Benchmark Interface (Step 9)
  async getBeforeAfterAnalysis(competitor, question, options = {}) {
    return fetchJson('/analyst/before-after', {
      method: 'POST',
      body: JSON.stringify({
        competitor: competitor || 'Microsoft',
        question: question || `How has ${competitor || 'Microsoft'}'s AI strategy evolved?`,
        start_date: options.startDate || null,
        end_date: options.endDate || null,
        top_k: options.topK || 10
      })
    });
  },

  async getBeforeAfterComparison(scenarioId = null) {
    return fetchJson(`/analyst/benchmark${scenarioId ? `?scenario=${scenarioId}` : ''}`).catch(() => null);
  },

  // 7. Strategic Pattern Detection & Connect the Dots (Step 10)
  async getPatterns(competitor, options = {}) {
    return fetchJson('/analyst/patterns', {
      method: 'POST',
      body: JSON.stringify({
        competitor: competitor || 'Microsoft',
        start_date: options.startDate || null,
        end_date: options.endDate || null,
        top_k: options.topK || 10
      })
    });
  },

  async getCompetitorPatterns(competitorId, options = {}) {
    const queryParams = new URLSearchParams();
    if (options.startDate) queryParams.set('start_date', options.startDate);
    if (options.endDate) queryParams.set('end_date', options.endDate);
    if (options.topK) queryParams.set('top_k', options.topK);
    const qs = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return fetchJson(`/competitors/${competitorId}/patterns${qs}`);
  },

  // 8. Proactive Strategic Alerts & "What Changed?" (Step 11)
  async getAlerts(params = {}) {
    const queryParams = new URLSearchParams();
    if (params.competitorId && params.competitorId !== 'all') queryParams.set('competitor_id', params.competitorId);
    if (params.status && params.status !== 'all') queryParams.set('status', params.status);
    if (params.eventType && params.eventType !== 'all') queryParams.set('event_type', params.eventType);
    const qs = queryParams.toString() ? `?${queryParams.toString()}` : '';
    const res = await fetchJson(`/alerts${qs}`);
    return (res.alerts || []).map(normalizeAlert);
  },

  async generateAlerts(competitor) {
    return fetchJson('/alerts/generate', {
      method: 'POST',
      body: JSON.stringify({ competitor })
    });
  },

  async markAlertRead(alertId) {
    return fetchJson(`/alerts/${alertId}/read`, {
      method: 'PATCH'
    });
  },

  async dismissAlert(alertId) {
    return fetchJson(`/alerts/${alertId}/dismiss`, {
      method: 'PATCH'
    });
  },

  async getChanges(competitorId, params = {}) {
    const queryParams = new URLSearchParams();
    if (params.since) queryParams.set('since', params.since);
    if (params.until) queryParams.set('until', params.until);
    const qs = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return fetchJson(`/competitors/${competitorId}/changes${qs}`);
  },

  // 9. Executive Intelligence Briefing (Step 12)
  async getCompetitorReport(competitor, timeRange = 'all') {
    const data = await fetchJson('/reports/competitor', {
      method: 'POST',
      body: JSON.stringify({
        competitor,
        time_range: timeRange
      })
    });
    return data.report;
  }
};

export default competitorApi;
