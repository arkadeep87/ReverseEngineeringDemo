const ConsentAndComplianceService = require('../../src/services/consentAndComplianceService');

describe('ConsentAndComplianceService', () => {
  test('records granted consent and allows quote completion', async () => {
    const consentRepository = { recordConsent: jest.fn().mockResolvedValue(undefined) };
    const auditEventService = { recordDeniedConsentEvent: jest.fn() };
    const consentRuleRepository = { getRule: jest.fn().mockResolvedValue({ consentMandatory: true, noticeVersion: 'v1' }) };
    const service = new ConsentAndComplianceService({ consentRepository, consentRuleRepository, auditEventService });

    const result = await service.handleConsent({
      customerId: 'C1',
      countryCode: 'ES',
      consentStatus: 'GRANTED',
      requestTimestamp: '2026-04-24T00:00:00Z',
      channel: 'DIGITAL',
      correlationId: 'corr-1'
    });

    expect(consentRepository.recordConsent).toHaveBeenCalled();
    expect(result.quoteCompletionAllowed).toBe(true);
  });

  test('records denied-consent audit and blocks completion where consent is mandatory', async () => {
    const consentRepository = { recordConsent: jest.fn().mockResolvedValue(undefined) };
    const auditEventService = { recordDeniedConsentEvent: jest.fn().mockResolvedValue(undefined) };
    const consentRuleRepository = { getRule: jest.fn().mockResolvedValue({ consentMandatory: true, noticeVersion: 'v1' }) };
    const service = new ConsentAndComplianceService({ consentRepository, consentRuleRepository, auditEventService });

    const result = await service.handleConsent({
      customerId: 'C1',
      countryCode: 'DE',
      consentStatus: 'DENIED',
      requestTimestamp: '2026-04-24T00:00:00Z',
      channel: 'DIGITAL',
      correlationId: 'corr-1'
    });

    expect(auditEventService.recordDeniedConsentEvent).toHaveBeenCalled();
    expect(consentRepository.recordConsent).toHaveBeenCalled();
    expect(result.quoteCompletionAllowed).toBe(false);
    expect(result.reasonCode).toBe('CONSENT_REQUIRED');
  });
});
