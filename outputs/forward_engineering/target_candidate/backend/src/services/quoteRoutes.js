const express = require('express');

module.exports = function createQuoteRoutes(controller) {
  const router = express.Router();

  router.post('/api/v1/quotes', controller.generateQuote.bind(controller));
  router.get('/api/v1/quotes/:quoteId', controller.getQuoteDetail.bind(controller));
  router.get('/api/v1/quotes/reference-data', controller.getReferenceData.bind(controller));
  router.get('/api/v1/quotes/reconciliation', controller.getReconciliation.bind(controller));

  return router;
};
