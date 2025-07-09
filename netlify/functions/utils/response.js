/**
 * Creates a standard response object for API endpoints
 * @param {number} statusCode - HTTP status code
 * @param {object} body - Response body
 * @returns {object} - Netlify function response object
 */
const createResponse = (statusCode, body) => {
  return {
    statusCode,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*', // Allow CORS from any origin
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    },
    body: JSON.stringify(body)
  };
};

/**
 * Handles errors in a consistent way
 * @param {Error} error - Error object
 * @returns {object} - Netlify function response object
 */
const handleError = (error) => {
  console.error('Function error:', error);
  
  return createResponse(500, {
    success: false,
    message: 'Server error',
    error: error.message
  });
};

module.exports = {
  createResponse,
  handleError
};
