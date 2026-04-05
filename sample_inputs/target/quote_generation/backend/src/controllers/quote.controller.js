const { quoteWorkflowService } = require('../services/quote-workflow.service');

const generateSpainQuote = async (req, res) => {
  const result = await quoteWorkflowService.generateQuote(req.body);
  res.status(200).json(result);
};

module.exports = { generateSpainQuote };
