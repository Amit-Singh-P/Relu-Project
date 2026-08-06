// Human-readable labels for known enrichment fields. Any field not listed
// here still renders automatically using a title-cased version of its key,
// so the card never breaks if the AI schema gains or loses a field.
const FIELD_LABELS = {
  companyName: 'Company Name',
  website: 'Website',
  industry: 'Industry',
  foundedYear: 'Founded',
  headquarters: 'Headquarters',
  employeeCount: 'Employees',
  companyType: 'Company Type',
  contactEmail: 'Contact Email',
  phone: 'Phone'
};

const HIDDEN_KEYS = ['companyName', 'description', 'products', 'socialLinks'];

const toLabel = (key) =>
  FIELD_LABELS[key] ||
  key
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, (c) => c.toUpperCase())
    .trim();

const renderValue = (value) => {
  if (value === null || value === undefined || value === '') {
    return <span className="ledger-value empty">Not available</span>;
  }
  if (Array.isArray(value)) {
    if (value.length === 0) return <span className="ledger-value empty">Not available</span>;
    return (
      <div className="chip-row">
        {value.map((item, idx) => (
          <span className="chip" key={idx}>
            {String(item)}
          </span>
        ))}
      </div>
    );
  }
  if (typeof value === 'object') {
    const entries = Object.entries(value).filter(([, v]) => v);
    if (entries.length === 0) return <span className="ledger-value empty">Not available</span>;
    return (
      <div className="chip-row">
        {entries.map(([k, v]) => (
          <span className="chip" key={k}>
            {toLabel(k)}: {String(v)}
          </span>
        ))}
      </div>
    );
  }
  return <span className="ledger-value">{String(value)}</span>;
};

/**
 * Renders any enriched company profile object safely. Does not assume any
 * field is present — every value falls back to "Not available".
 */
const ProfileCard = ({ websiteName, url, profile, timestamp }) => {
  const safeProfile = profile && typeof profile === 'object' ? profile : {};
  const knownKeys = Object.keys(FIELD_LABELS).filter((k) => k in safeProfile);
  const extraKeys = Object.keys(safeProfile).filter(
    (k) => !HIDDEN_KEYS.includes(k) && !FIELD_LABELS[k]
  );
  const ledgerKeys = [...knownKeys, ...extraKeys];

  return (
    <div className="dossier">
      <div className="dossier-header">
        <h3>{safeProfile.companyName || websiteName || 'Unknown Company'}</h3>
        {timestamp && <span className="tag">{new Date(timestamp).toLocaleString()}</span>}
      </div>

      {safeProfile.description && <div className="dossier-desc">{safeProfile.description}</div>}

      <div className="ledger">
        <div className="ledger-row">
          <div className="ledger-key">Submitted URL</div>
          <span className="ledger-value">{url || 'Not available'}</span>
        </div>
        {ledgerKeys.map((key) => (
          <div className="ledger-row" key={key}>
            <div className="ledger-key">{toLabel(key)}</div>
            {renderValue(safeProfile[key])}
          </div>
        ))}
        {safeProfile.products && (
          <div className="ledger-row">
            <div className="ledger-key">Products</div>
            {renderValue(safeProfile.products)}
          </div>
        )}
        {safeProfile.socialLinks && (
          <div className="ledger-row">
            <div className="ledger-key">Social Links</div>
            {renderValue(safeProfile.socialLinks)}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfileCard;
