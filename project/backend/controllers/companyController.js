const Company = require('../models/Company');
const { enrichCompany } = require('./aiService');

/**
 * Simple URL validator using the built-in URL constructor.
 */
const isValidUrl = (value) => {
  try {
    const parsed = new URL(value);
    return parsed.protocol === 'http:' || parsed.protocol === 'https:';
  } catch (err) {
    return false;
  }
};

// POST /enrich
const enrichCompanyHandler = async (req, res, next) => {
  try {
    const { websiteName, url } = req.body;

    if (!websiteName || typeof websiteName !== 'string' || !websiteName.trim()) {
      return res.status(400).json({ error: 'websiteName is required and must be a non-empty string.' });
    }

    if (!url || typeof url !== 'string' || !url.trim()) {
      return res.status(400).json({ error: 'url is required and must be a non-empty string.' });
    }

    if (!isValidUrl(url.trim())) {
      return res.status(400).json({ error: 'url must be a valid http/https website URL.' });
    }

    const enrichedProfile = await enrichCompany(websiteName.trim(), url.trim());

    const company = new Company({
      websiteName: websiteName.trim(),
      url: url.trim(),
      enrichedProfile
    });

    const savedCompany = await company.save();

    return res.status(201).json(savedCompany);
  } catch (error) {
    return next(error);
  }
};

// GET /results
const getResultsHandler = async (req, res, next) => {
  try {
    const companies = await Company.find().sort({ createdAt: -1 });
    return res.status(200).json(companies);
  } catch (error) {
    return next(error);
  }
};

module.exports = { enrichCompanyHandler, getResultsHandler };
