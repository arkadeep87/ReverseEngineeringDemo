class QuoteOrchestrationService {
  constructor({
    supportedCountryValidator,
    requestValidator,
    referenceDataValidationService,
    eligibilityAssessmentService,
    consentAndComplianceService,
    pricingBaselineGovernanceService,
    premiumCompositionService,
    quoteRepository,
    quoteChargePersistenceService,
    countryRuleResolver,
    underwritingCaseService,
    auditEventService,
    transactionManager
  }) {
    this.supportedCountryValidator = supportedCountryValidator;
    this.requestValidator = requestValidator;
    this.referenceDataValidationService = referenceDataValidationService;
    this.eligibilityAssessmentService = eligibilityAssessmentService;
    this.consentAndComplianceService = consentAndComplianceService;
    this.pricingBaselineGovernanceService = pricingBaselineGovernanceService;
    this.premiumCompositionService = premiumCompositionService;
    this.quoteRepository = quoteRepository;
    this.quoteChargePersistenceService = quoteChargePersistenceService;
    this.countryRuleResolver = countryRuleResolver;
    this.underwritingCaseService = underwritingCaseService;
    this.auditEventService = auditEventService;
    this.transactionManager = transactionManager;
  }

  async generateQuote(request) {
    this.requestValidator.validateRequiredFields(request);
    this.supportedCountryValidator.validate(request.countryCode);

    const referenceContext = await this.referenceDataValidationService.validate(request);
    const eligibility = await this.eligibilityAssessmentService.assess({ ...request, referenceContext });
    if (!eligibility.isEligible) {
      return {
        outcomeStatus: 'REJECTED',
        validationMessages: [eligibility.message],
        rejectionReasonCode: eligibility.reasonCode,
        correlationId: request.correlationId
      };
    }

    const consentDecision = await this.consentAndComplianceService.handleConsent(request);
    if (!consentDecision.quoteCompletionAllowed) {
      return {
        outcomeStatus: 'REJECTED',
        validationMessages: [consentDecision.message],
        rejectionReasonCode: consentDecision.reasonCode,
        auditMessage: consentDecision.auditMessage,
        correlationId: request.correlationId
      };
    }

    const pricingBaseline = await this.pricingBaselineGovernanceService.resolve(request);
    const countryRules = await this.countryRuleResolver.resolve(request.countryCode);
    const pricingResult = await this.premiumCompositionService.compose({
      request,
      pricingBaseline,
      countryRules
    });

    return this.transactionManager.runInTransaction(async (db) => {
      const quoteRecord = await this.quoteRepository.createQuoteHeader(db, {
        customerId: request.customerId,
        countryCode: request.countryCode,
        policyType: request.policyType,
        coverageAmount: request.coverageAmount,
        customerSegment: request.customerSegment,
        paymentFrequency: request.paymentFrequency,
        consentStatus: request.consentStatus,
        eligibilityOutcome: 'ELIGIBLE',
        pricingBaselineVersion: pricingBaseline.version,
        basePremium: pricingResult.basePremium,
        riskLoadingAmount: pricingResult.riskLoadingAmount,
        riskFactorApplied: pricingResult.riskFactorApplied,
        discountAmount: pricingResult.discountAmount,
        taxAmount: pricingResult.taxAmount,
        taxRateApplied: pricingResult.taxRateApplied,
        countryAdjustmentAmount: pricingResult.countryAdjustmentAmount,
        countryAdjustmentSource: pricingResult.countryAdjustmentSource,
        finalPremium: pricingResult.finalPremium,
        processingStatus: 'PERSISTED_PENDING_DEPENDENCIES',
        quoteOutcomeStatus: 'SUCCESS',
        correlationId: request.correlationId
      });

      await this.quoteRepository.createQuoteContext(db, {
        quoteId: quoteRecord.quoteId,
        age: request.age,
        countryCode: request.countryCode,
        policyType: request.policyType,
        customerSegment: request.customerSegment,
        paymentFrequency: request.paymentFrequency,
        coverageAmount: request.coverageAmount,
        policyDefinitionId: referenceContext.policyDefinitionId,
        paymentFrequencyDefinitionId: referenceContext.paymentFrequencyDefinitionId,
        eligibilityRuleVersion: eligibility.ruleVersion,
        pricingRuleVersion: pricingBaseline.version,
        taxRuleVersion: pricingResult.taxRuleVersion,
        countryAdjustmentAmount: pricingResult.countryAdjustmentAmount,
        countryAdjustmentSource: pricingResult.countryAdjustmentSource,
        countryAdjustmentRuleVersion: pricingResult.countryAdjustmentRuleVersion,
        requestPayloadHash: referenceContext.requestPayloadHash,
        decisionSnapshotJson: JSON.stringify({ eligibility, consentDecision, pricingResult })
      });

      await this.quoteChargePersistenceService.persistCharges(db, quoteRecord.quoteId, pricingResult.chargeLines);

      const underwriting = await this.underwritingCaseService.createCase(db, {
        quoteId: quoteRecord.quoteId,
        customerId: request.customerId,
        countryCode: request.countryCode,
        workflowStatus: pricingResult.underwritingStatus,
        workflowStatusReason: 'QUOTE_COMPLETION',
        routingRuleVersion: pricingResult.routingRuleVersion
      });

      await this.quoteRepository.linkUnderwritingCase(db, quoteRecord.quoteId, underwriting.underwritingCaseId);

      await this.auditEventService.recordSuccess(db, {
        quoteId: quoteRecord.quoteId,
        customerId: request.customerId,
        correlationId: request.correlationId,
        businessMessage: 'Quote generated successfully.'
      });

      await this.quoteRepository.updateProcessingStatus(db, quoteRecord.quoteId, 'COMPLETED');

      return {
        outcomeStatus: 'SUCCESS',
        quoteId: quoteRecord.quoteId,
        countryCode: request.countryCode,
        policyType: request.policyType,
        coverageAmount: request.coverageAmount,
        basePremium: pricingResult.basePremium,
        riskLoadingAmount: pricingResult.riskLoadingAmount,
        riskFactorApplied: pricingResult.riskFactorApplied,
        discountAmount: pricingResult.discountAmount,
        taxAmount: pricingResult.taxAmount,
        taxRateApplied: pricingResult.taxRateApplied,
        countryAdjustmentAmount: pricingResult.countryAdjustmentAmount,
        countryAdjustmentSource: pricingResult.countryAdjustmentSource,
        finalPremium: pricingResult.finalPremium,
        paymentFrequency: request.paymentFrequency,
        underwritingCaseId: underwriting.underwritingCaseId,
        underwritingStatus: pricingResult.underwritingStatus,
        auditMessage: 'Quote generated successfully.',
        validationMessages: [],
        correlationId: request.correlationId
      };
    }, async (error, db) => {
      if (error && error.partialQuoteId) {
        await this.quoteRepository.updateProcessingStatus(db, error.partialQuoteId, 'RECOVERABLE_FAILURE');
        await this.auditEventService.recordFailure(db, {
          quoteId: error.partialQuoteId,
          customerId: request.customerId,
          correlationId: request.correlationId,
          businessMessage: 'Quote processing entered recovery state.'
        });
      }
    });
  }
}

module.exports = QuoteOrchestrationService;
