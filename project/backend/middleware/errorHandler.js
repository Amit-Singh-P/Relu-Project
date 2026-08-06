// Centralized error-handling middleware. Must be registered last in app.js.
// eslint-disable-next-line no-unused-vars
const errorHandler = (err, req, res, next) => {
  console.error('Error:', err.message);

  const statusCode = err.statusCode || 500;
  res.status(statusCode).json({
    error: err.message || 'Internal server error.'
  });
};

module.exports = errorHandler;
