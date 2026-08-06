const express = require('express');
const router = express.Router();
const { enrichCompanyHandler, getResultsHandler } = require('../controllers/companyController');

// POST /enrich
router.post('/enrich', enrichCompanyHandler);

// GET /results
router.get('/results', getResultsHandler);

module.exports = router;
