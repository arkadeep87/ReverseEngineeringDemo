const QuoteOrchestrationService = require('../../src/services/quoteOrchestrationService');

describe('QuoteOrchestrationService', () => {
  test('returns rejection when eligibility fails before pricing and persistence', async () => {
    const service = new QuoteOrchestrationService({
      supportedCountryValidator: { validate: jest.fn() },
      requestValidator: { validateRequiredFields: jest.fn() },
      referenceDataValidationService: { validate: jest.fn().mockResolvedValue({}) },
      eligibilityAssessmentService: { assess: jest.fn().mockResolvedValue({ isEligible: false, message: 'The customer does not meet the minimum age eligibility requirement.', reasonCode: 'AGE_NOT_ELIGIBLE', ruleVersion: 'ELIG_V1' }) },
      consentAndComplianceService: { handleConsent: jest.fn() },
      pricingBaselineGovernanceService: { resolve: jest.fn() },
      premiumCompositionService: { compose: jest.fn() },
      quoteRepository: {},
      quoteChargePersistenceService: {},
      countryRuleResolver: { resolve: jest.fn() },
      underwritingCaseService: {},
      auditEventService: {},
      transactionManager: { runInTransaction: jest.fn() }
    });

    const result = await service.generateQuote({ countryCode: 'ES', correlationId: 'corr-1' });
    expect(result.outcomeStatus).toBe('REJECTED');
    expect(result.rejectionReasonCode).toBe('AGE_NOT_ELIGIBLE');
  });

  test('returns rejection when denied consent blocks quote completion', async () => {
    const service = new QuoteOrchestrationService({
      supportedCountryValidator: { validate: jest.fn() },
      requestValidator: { validateRequiredFields: jest.fn() },
      referenceDataValidationService: { validate: jest.fn().mockResolvedValue({}) },
      eligibilityAssessmentService: { assess: jest.fn().mockResolvedValue({ isEligible: true, ruleVersion: 'ELIG_V1' }) },
      consentAndComplianceService: { handleConsent: jest.fn().mockResolvedValue({ quoteCompletionAllowed: false, message: 'Consent denied for quote completion.', reasonCode: 'CONSENT_REQUIRED', auditMessage: 'Denied-consent attempt recorded.' }) },
      pricingBaselineGovernanceService: { resolve: jest.fn() },
      premiumCompositionService: { compose: jest.fn() },
      quoteRepository: {},
      quoteChargePersistenceService: {},
      countryRuleResolver: { resolve: jest.fn() },
      underwritingCaseService: {},
      auditEventService: {},
      transactionManager: { runInTransaction: jest.fn() }
    });

    const result = await service.generateQuote({ countryCode: 'DE', correlationId: 'corr-1' });
    expect(result.outcomeStatus).toBe('REJECTED');
    expect(result.rejectionReasonCode).toBe('CONSENT_REQUIRED');
    expect(result.auditMessage).toBe('Denied-consent attempt recorded.');
  });

  test('completes successful quote transaction and returns approved response fields', async () => {
    const db = { query: jest.fn() };
    const transactionManager = { runInTransaction: jest.fn(async (work) => work(db)) };
    const quoteRepository = {
      createQuoteHeader: jest.fn().mockResolvedValue({ quoteId: 'Q1' }),
      createQuoteContext: jest.fn().mockResolvedValue(undefined),
      linkUnderwritingCase: jest.fn().mockResolvedValue(undefined),
      updateProcessingStatus: jest.fn().mockResolvedValue(undefined)
    };

    const service = new QuoteOrchestrationService({
      supportedCountryValidator: { validate: jest.fn() },
      requestValidator: { validateRequiredFields: jest.fn() },
      referenceDataValidationService: { validate: jest.fn().mockResolvedValue({ policyDefinitionId: 'P1', paymentFrequencyDefinitionId: 'PF1', requestPayloadHash: 'hash' }) },
      eligibilityAssessmentService: { assess: jest.fn().mockResolvedValue({ isEligible: true, ruleVersion: 'ELIG_V1' }) },
      consentAndComplianceService: { handleConsent: jest.fn().mockResolvedValue({ quoteCompletionAllowed: true }) },
      pricingBaselineGovernanceService: { resolve: jest.fn().mockResolvedValue({ version: 'BASELINE_V1' }) },
      premiumCompositionService: {
        compose: jest.fn().mockResolvedValue({
          basePremium: 100,
          riskLoadingAmount: 8,
          riskFactorApplied: 1.08,
          discountAmount: 4,
          taxAmount: 9,
          taxRateApplied: 0.09,
          taxRuleVersion: 'TAX_V1',
          countryAdjustmentAmount: 5,
          countryAdjustmentSource: 'PRIMARY',
          countryAdjustmentRuleVersion: 'ADJ_V1',
          underwritingStatus: 'EU_COMPLIANCE',
          routingRuleVersion: 'ROUTE_V1',
          finalPremium: 118,
          chargeLines: [{ chargeType: 'BASE_PREMIUM' }, { chargeType: 'TAX' }, { chargeType: 'COUNTRY_ADJUSTMENT' }]
        })
      },
      quoteRepository,
      quoteChargePersistenceService: { persistCharges: jest.fn().mockResolvedValue(undefined) },
      countryRuleResolver: { resolve: jest.fn().mockResolvedValue({ underwritingStatus: 'EU_COMPLIANCE' }) },
      underwritingCaseService: { createCase: jest.fn().mockResolvedValue({ underwritingCaseId: 'UW1' }) },
      auditEventService: { recordSuccess: jest.fn().mockResolvedValue(undefined) },
      transactionManager
    });

    const result = await service.generateQuote({
      customerId: 'C1',
      countryCode: 'DE',
      policyType: 'HEALTH',
      coverageAmount: 10000,
      customerSegment: 'STANDARD',
      paymentFrequency: 'ANNUAL',
      consentStatus: 'GRANTED',
      age: 40,
      correlationId: 'corr-1'
    });

    expect(result.outcomeStatus).toBe('SUCCESS');
    expect(result.quoteId).toBe('Q1');
    expect(result.underwritingStatus).toBe('EU_COMPLIANCE');
    expect(quoteRepository.updateProcessingStatus).toHaveBeenCalledWith(db, 'Q1', 'COMPLETED');
  });
});
