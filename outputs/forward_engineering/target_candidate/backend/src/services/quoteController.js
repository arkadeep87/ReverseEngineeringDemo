class QuoteController {
  constructor({ quoteOrchestrationService, quoteQueryService, referenceDataService, reconciliationService }) {
    this.quoteOrchestrationService = quoteOrchestrationService;
    this.quoteQueryService = quoteQueryService;
    this.referenceDataService = referenceDataService;
    this.reconciliationService = reconciliationService;
  }

  async generateQuote(req, res) {
    try {
      const result = await this.quoteOrchestrationService.generateQuote(req.body);
      const statusCode = result.outcomeStatus === 'SUCCESS' ? 200 : 400;
      return res.status(statusCode).json(result);
    } catch (error) {
      return res.status(error.statusCode || 500).json({
        outcomeStatus: 'ERROR',
        auditMessage: error.message || 'The quote could not be processed.',
        validationMessages: error.validationMessages || [],
        rejectionReasonCode: error.rejectionReasonCode,
        correlationId: req.body?.correlationId || req.query?.correlationId
      });
    }
  }

  async getQuoteDetail(req, res) {
    const result = await this.quoteQueryService.getQuoteDetail(req.params.quoteId, req.query.correlationId);
    return res.status(200).json(result);
  }

  async getReferenceData(req, res) {
    const result = await this.referenceDataService.getReferenceData({
      countryCode: req.query.countryCode,
      asOfDate: req.query.asOfDate,
      correlationId: req.query.correlationId
    });
    return res.status(200).json(result);
  }

  async getReconciliation(req, res) {
    const result = await this.reconciliationService.getReconciliation(req.query);
    return res.status(200).json(result);
  }
}

module.exports = QuoteController;
