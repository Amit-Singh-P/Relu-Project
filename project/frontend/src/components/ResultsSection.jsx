import { useState } from 'react';
import { getAllResults } from '../services/api';

const truncate = (text, max = 140) => {
  if (!text) return '';
  return text.length > max ? `${text.slice(0, max).trim()}…` : text;
};

const ResultsSection = () => {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFetch = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getAllResults();
      setResults(Array.isArray(data) ? data : []);
    } catch (err) {
      const message = err.response?.data?.error || err.message || 'Failed to load results.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="section">
      <div className="section-label">
        <span className="index">2</span> All Enriched Companies
      </div>
      <div className="panel">
        <div className="results-toolbar">
          <button className="btn btn-outline" onClick={handleFetch} disabled={loading}>
            {loading ? 'Loading…' : 'Show All Results'}
          </button>
          {results && <span className="results-count">{results.length} record(s) found</span>}
        </div>

        {loading && (
          <div className="status-line">
            <span className="spinner" />
            Fetching stored company profiles…
          </div>
        )}

        {!loading && error && <div className="status-line error">⚠ {error}</div>}

        {!loading && results && results.length === 0 && (
          <div className="empty-state">No enriched companies yet. Run an enrichment above to get started.</div>
        )}

        {!loading && results && results.length > 0 && (
          <div className="results-grid">
            {results.map((item) => {
              const profile = item.enrichedProfile || {};
              return (
                <div className="result-card" key={item._id}>
                  <h4>{profile.companyName || item.websiteName || 'Unknown Company'}</h4>
                  <div className="url">{item.url}</div>
                  {profile.description && <div className="desc">{truncate(profile.description)}</div>}
                  <div className="meta-row">
                    {profile.industry && <span className="meta-pill">{profile.industry}</span>}
                    {profile.headquarters && <span className="meta-pill">{profile.headquarters}</span>}
                    {profile.employeeCount && <span className="meta-pill">{profile.employeeCount}</span>}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
};

export default ResultsSection;
