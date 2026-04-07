const quoteService = require('../services/quote-orchestration.service');
const quoteQueryService = require('../services/quote-query.service');

async function createDraftQuoteContext(req, res, next) {
  try {
    const result = await quoteService.createDraftQuoteContext(req.body);
    res.status(201).json(result);
  } catch (err) {
    next(err);
  }
}

async function generateQuote(req, res, next) {
  try {
    const result = await quoteService.generateQuote(req.body);
    if (result.status === 'REJECTED') {
      return res.status(422).json(result);
    }
    res.status(201).json(result);
  } catch (err) {
    next(err);
  }
}

async function getReferenceData(req, res, next) {
  try {
    const result = await quoteQueryService.getReferenceData(req.query.country);
    res.json(result);
  } catch (err) {
    next(err);
  }
}

async function getQuoteById(req, res, next) {
  try {
    const result = await quoteQueryService.getQuoteById(req.params.quoteId);
    res.json(result);
  } catch (err) {
    next(err);
  }
}

async function getQuoteBreakdown(req, res, next) {
  try {
    const result = await quoteQueryService.getQuoteBreakdown(req.params.quoteId);
    res.json(result);
  } catch (err) {
    next(err);
  }
}

module.exports = {
  createDraftQuoteContext,
  generateQuote,
  getReferenceData,
  getQuoteById,
  getQuoteBreakdown
};
