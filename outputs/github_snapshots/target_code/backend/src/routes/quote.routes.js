const express = require('express');
const { generateSpainQuote } = require('../controllers/quote.controller');

const quoteRouter = express.Router();

quoteRouter.post('/generate', generateSpainQuote);

module.exports = { quoteRouter };
