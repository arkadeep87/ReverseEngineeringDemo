class AuditEventService {
  constructor({ quoteRepository }) {
    this.quoteRepository = quoteRepository;
  }

  async recordSuccess(dbOrInput, maybeInput) {
    const hasDb = maybeInput !== undefined;
    const db = hasDb ? dbOrInput : null;
    const input = hasDb ? maybeInput : dbOrInput;
    return this.quoteRepository.insertAuditEvent(db, {
      quoteId: input.quoteId,
      customerId: input.customerId,
      eventType: 'QUOTE_SUCCESS',
      eventCategory: 'BUSINESS',
      businessMessage: input.businessMessage,
      eventPayloadJson: JSON.stringify({ correlationId: input.correlationId }),
      processingState: 'COMPLETED',
      correlationId: input.correlationId
    });
  }

  async recordDeniedConsentEvent(input) {
    return this.quoteRepository.insertAuditEvent(null, {
      quoteId: input.quoteId,
      customerId: input.customerId,
      eventType: 'CONSENT_DENIED',
      eventCategory: 'COMPLIANCE',
      businessMessage: input.businessMessage,
      eventPayloadJson: JSON.stringify({ correlationId: input.correlationId }),
      processingState: 'COMPLETED',
      correlationId: input.correlationId
    });
  }

  async recordFailure(db, input) {
    return this.quoteRepository.insertAuditEvent(db, {
      quoteId: input.quoteId,
      customerId: input.customerId,
      eventType: 'QUOTE_RECOVERY_REQUIRED',
      eventCategory: 'OPERATIONAL',
      businessMessage: input.businessMessage,
      eventPayloadJson: JSON.stringify({ correlationId: input.correlationId }),
      processingState: 'RECOVERABLE_FAILURE',
      correlationId: input.correlationId
    });
  }
}

module.exports = AuditEventService;
