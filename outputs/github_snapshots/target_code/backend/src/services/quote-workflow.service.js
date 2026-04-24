const { quoteValidationService } = require('./quote-validation.service');
const { quotePricingService } = require('./quote-pricing.service');
const { quotePersistenceService } = require('./quote-persistence.service');
const { spainQuoteStrategy } = require('../strategies/spain-quote.strategy');

class QuoteWorkflowService {
  async generateQuote(request) {
    await quoteValidationService.validateRequest(request);

    const pricing = await quotePricingService.calculateQuote(request, spainQuoteStrategy);
    const persistence = await quotePersistenceService.persistQuote(request, pricing, spainQuoteStrategy);

    return {
      quoteId: persistence.quoteId,
      pricing,
      auditMessage: persistence.auditMessage
    };
  }
}

const quoteWorkflowService = new QuoteWorkflowService();

module.exports = { quoteWorkflowService };
