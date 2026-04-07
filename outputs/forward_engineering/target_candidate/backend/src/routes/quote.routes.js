const express = require('express');
const controller = require('../controllers/quote.controller');

const router = express.Router();

router.post('/api/quotes/draft', controller.createDraftQuoteContext);
router.post('/api/quotes', controller.generateQuote);
router.get('/api/quotes/reference-data', controller.getReferenceData);
router.get('/api/quotes/:quoteId', controller.getQuoteById);
router.get('/api/quotes/:quoteId/breakdown', controller.getQuoteBreakdown);

module.exports = router;
