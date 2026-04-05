const { quoteRepository } = require('../repositories/quote.repository');
const { auditRepository } = require('../repositories/audit.repository');

class QuotePersistenceService {
  async persistQuote(request, pricing, strategy) {
    const quoteId = await quoteRepository.insertQuoteHeader(request, pricing);

    await quoteRepository.upsertQuoteContext(quoteId, request, pricing);
    await quoteRepository.insertQuoteCharge(quoteId, 'BASE_PREMIUM', pricing.basePremium);
    await quoteRepository.insertQuoteCharge(quoteId, 'SPAIN_ADJUSTMENT', pricing.countryAdjustmentAmount);
    await quoteRepository.insertUnderwritingCase(quoteId, request.customerId, request.countryCode);

    const auditMessage = strategy.buildAuditMessage(request, pricing);
    await auditRepository.logQuoteEvent(quoteId, 'QUOTE_GENERATED', auditMessage);

    return { quoteId, auditMessage };
  }
}

const quotePersistenceService = new QuotePersistenceService();

module.exports = { quotePersistenceService };
