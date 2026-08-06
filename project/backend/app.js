const express = require('express');
const cors = require('cors');
const companyRoutes = require('./routes/companyRoutes');
const errorHandler = require('./middleware/errorHandler');

const app = express();

// Middleware
const allowedOrigins = (process.env.CLIENT_ORIGIN || '*')
  .split(',')
  .map((origin) => origin.trim());

app.use(
  cors({
    origin: allowedOrigins.includes('*') ? true : allowedOrigins
  })
);
app.use(express.json());

// Health check
app.get('/', (req, res) => {
  res.status(200).json({ status: 'Company Enrichment API is running.' });
});

// Routes
app.use('/', companyRoutes);

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Route not found.' });
});

// Centralized error handler (must be last)
app.use(errorHandler);

module.exports = app;
