import { useState } from 'react';
import { enrichCompany } from '../services/api';
import ProfileCard from './ProfileCard';

const EnrichSection = () => {
  const [websiteName, setWebsiteName] = useState('');
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);

    if (!websiteName.trim() || !url.trim()) {
      setError('Please enter both a website name and a URL.');
      return;
    }

    setLoading(true);
    try {
      const data = await enrichCompany(websiteName.trim(), url.trim());
      setResult(data);
    } catch (err) {
      const message =
        err.response?.data?.error || err.message || 'Something went wrong while enriching this company.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="section">
      <div className="section-label">
        <span className="index">1</span> Enrich a Company
      </div>
      <div className="panel">
        <form className="form-grid" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="websiteName">Website Name</label>
            <input
              id="websiteName"
              type="text"
              placeholder="e.g. Acme Corp"
              value={websiteName}
              onChange={(e) => setWebsiteName(e.target.value)}
              disabled={loading}
            />
          </div>
          <div className="field">
            <label htmlFor="url">Company URL</label>
            <input
              id="url"
              type="text"
              placeholder="https://acme.com"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={loading}
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Enriching…' : 'Enrich'}
          </button>
        </form>

        {loading && (
          <div className="status-line">
            <span className="spinner" />
            Contacting AI provider and building the company profile…
          </div>
        )}

        {!loading && error && <div className="status-line error">⚠ {error}</div>}

        {!loading && result && (
          <ProfileCard
            websiteName={result.websiteName}
            url={result.url}
            profile={result.enrichedProfile}
            timestamp={result.createdAt}
          />
        )}
      </div>
    </section>
  );
};

export default EnrichSection;
