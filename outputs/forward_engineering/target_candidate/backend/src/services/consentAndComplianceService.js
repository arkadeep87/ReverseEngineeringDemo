class ConsentAndComplianceService {
  constructor({ consentRepository, consentRuleRepository, auditEventService }) {
    this.consentRepository = consentRepository;
    this.consentRuleRepository = consentRuleRepository;
    this.auditEventService = auditEventService;
  }

  async handleConsent(request) {
    const consentRule = await this.consentRuleRepository.getRule(request.countryCode, request.channel, request.requestTimestamp);
    const consentMandatory = consentRule ? !!consentRule.consentMandatory : true;

    if (request.consentStatus === 'GRANTED') {
      await this.consentRepository.recordConsent({
        customerId: request.customerId,
        quoteId: null,
        countryCode: request.countryCode,
        consentStatus: 'GRANTED',
        consentNoticeVersion: consentRule?.noticeVersion || 'CURRENT',
        businessOutcome: 'CONSENT_RECORDED',
        capturedAt: request.requestTimestamp,
        capturedByChannel: request.channel,
        correlationId: request.correlationId,
        retentionClassification: 'GDPR_QUOTE_CONSENT'
      });
      return {
        quoteCompletionAllowed: true,
        reasonCode: null,
        message: 'Consent granted.',
        auditMessage: 'Consent recorded.'
      };
    }

    await this.auditEventService.recordDeniedConsentEvent({
      quoteId: null,
      customerId: request.customerId,
      correlationId: request.correlationId,
      businessMessage: 'Denied-consent attempt recorded.'
    });

    await this.consentRepository.recordConsent({
      customerId: request.customerId,
      quoteId: null,
      countryCode: request.countryCode,
      consentStatus: 'DENIED',
      consentNoticeVersion: consentRule?.noticeVersion || 'CURRENT',
      businessOutcome: consentMandatory ? 'QUOTE_BLOCKED' : 'QUOTE_ALLOWED',
      capturedAt: request.requestTimestamp,
      capturedByChannel: request.channel,
      correlationId: request.correlationId,
      retentionClassification: 'GDPR_QUOTE_CONSENT'
    });

    if (consentMandatory) {
      return {
        quoteCompletionAllowed: false,
        reasonCode: 'CONSENT_REQUIRED',
        message: 'Consent denied for quote completion.',
        auditMessage: 'Denied-consent attempt recorded.'
      };
    }

    return {
      quoteCompletionAllowed: true,
      reasonCode: null,
      message: 'Consent denied but quote completion is permitted by rule.',
      auditMessage: 'Denied-consent attempt recorded.'
    };
  }
}

module.exports = ConsentAndComplianceService;
