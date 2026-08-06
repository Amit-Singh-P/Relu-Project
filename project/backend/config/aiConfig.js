/**
 * Defines the exact JSON schema the AI must return for company enrichment.
 * This schema is shared across all AI provider implementations so that the
 * saved profile structure never changes regardless of which provider is used.
 */
const ENRICHMENT_JSON_SCHEMA = {
  type: 'object',
  properties: {
    companyName: { type: ['string', 'null'] },
    website: { type: ['string', 'null'] },
    industry: { type: ['string', 'null'] },
    description: { type: ['string', 'null'] },
    foundedYear: { type: ['string', 'number', 'null'] },
    headquarters: { type: ['string', 'null'] },
    employeeCount: { type: ['string', 'null'] },
    companyType: { type: ['string', 'null'] },
    products: {
      type: ['array', 'null'],
      items: { type: 'string' }
    },
    socialLinks: {
      type: ['object', 'null'],
      properties: {
        linkedin: { type: ['string', 'null'] },
        twitter: { type: ['string', 'null'] },
        facebook: { type: ['string', 'null'] }
      }
    },
    contactEmail: { type: ['string', 'null'] },
    phone: { type: ['string', 'null'] }
  },
  required: [
    'companyName',
    'website',
    'industry',
    'description',
    'foundedYear',
    'headquarters',
    'employeeCount',
    'companyType',
    'products',
    'socialLinks',
    'contactEmail',
    'phone'
  ]
};

// Default keys so downstream code (frontend rendering, DB defaults) always
// has every field present, even if the AI omits one.
const EMPTY_ENRICHMENT_PROFILE = {
  companyName: null,
  website: null,
  industry: null,
  description: null,
  foundedYear: null,
  headquarters: null,
  employeeCount: null,
  companyType: null,
  products: null,
  socialLinks: {
    linkedin: null,
    twitter: null,
    facebook: null
  },
  contactEmail: null,
  phone: null
};

module.exports = {
  ENRICHMENT_JSON_SCHEMA,
  EMPTY_ENRICHMENT_PROFILE
};
