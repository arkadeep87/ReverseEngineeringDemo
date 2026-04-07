const repo = require('../storage/quote.repository');
const validation = require('./validation.service');
const consentService = require('./consent-compliance.service');
const eligibilityService = require('./eligibility-decision.service');
const pricingService = require('./pricing.service');
const underwritingService = require('./underwriting-handoff.service');
const auditService = require('./audit-trail.service');

async function createDraftQuoteContext(payload) {
  const context = await repo.createDraftQuoteContext(payload);
  await auditService.recordEvent({
    quoteContextId: context.quoteContextId,
    customerId: payload.customerId,
    country: payload.country,
    eventType: 'DRAFT_QUOTE_CREATED',
    eventOutcome: 'SUCCESS',
    reasonCode: null,
    reasonMessage: null,
    eventPayloadJson: payload
  });
  return context;
}

async function generateQuote(payload) {
  let context = payload.draftQuoteId
    ? await repo.getQuoteContextByDraftId(payload.draftQuoteId)
    : null;

  if (!context) {
    context = await repo.createDraftQuoteContext(payload);
  }

  const supportedCountryResult = await validation.validateSupportedCountry(payload.country);
  if (!supportedCountryResult.valid) {
    await auditService.recordRejectedAttempt(context, payload, supportedCountryResult.reasonCode, supportedCountryResult.reasonMessage, 'VALIDATION_FAILED');
    return rejectedResponse(supportedCountryResult.reasonMessage);
  }

  const referenceResult = await validation.validateReferenceData(payload);
  if (!referenceResult.valid) {
    await auditService.recordRejectedAttempt(context, payload, referenceResult.reasonCode, referenceResult.reasonMessage, 'VALIDATION_FAILED');
    return rejectedResponse(referenceResult.reasonMessage);
  }

  const coverageBoundsResult = await validation.validateCoverageBounds(payload);
  if (!coverageBoundsResult.valid) {
    await auditService.recordRejectedAttempt(context, payload, coverageBoundsResult.reasonCode, coverageBoundsResult.reasonMessage, 'VALIDATION_FAILED');
    return rejectedResponse(coverageBoundsResult.reasonMessage);
  }

  const consentResult = await consentService.evaluateAndPersist(context, payload);
  if (!consentResult.valid) {
    return rejectedResponse(consentResult.reasonMessage);
  }

  const eligibilityResult = await eligibilityService.evaluate(context, payload);
  await repo.saveEligibilityDecision(context.quoteContextId, payload, eligibilityResult);
  if (!eligibilityResult.eligible) {
    await auditService.recordRejectedAttempt(context, payload, eligibilityResult.reasonCode, eligibilityResult.reasonMessage, 'ELIGIBILITY_FAILED');
    return rejectedResponse(eligibilityResult.reasonMessage);
  }

  const pricingResult = await pricingService.calculate(payload);
  const quote = await repo.createQuote(context.quoteContextId, payload, pricingResult);
  await repo.saveFinancialBreakdown(quote.quoteId, pricingResult.breakdown);
  const underwriting = await underwritingService.createCase(quote.quoteId, payload.customerId, payload.country);
  await repo.linkUnderwritingCase(quote.quoteId, underwriting);
  await auditService.recordEvent({
    quoteContextId: context.quoteContextId,
    quoteId: quote.quoteId,
    customerId: payload.customerId,
    country: payload.country,
    eventType: 'QUOTE_GENERATED',
    eventOutcome: 'SUCCESS',
    reasonCode: null,
    reasonMessage: null,
    ruleSource: pricingResult.ruleSourceSummary,
    ruleVersion: pricingResult.ruleVersionSummary,
    eventPayloadJson: { pricingResult, underwriting }
  });

  return {
    quoteId: quote.quoteId,
    status: 'SUCCESS',
    rejectionReason: null,
    basePremium: pricingResult.basePremium,
    riskFactor: pricingResult.riskFactor,
    discountAmount: pricingResult.discountAmount,
    taxAmount: pricingResult.taxAmount,
    paymentFrequencySurchargeAmount: pricingResult.paymentFrequencySurchargeAmount,
    countryAdjustmentAmount: pricingResult.countryAdjustmentAmount,
    finalPremium: pricingResult.finalPremium,
    underwritingCaseId: underwriting.underwritingCaseId,
    underwritingStatus: underwriting.status,
    processingMessage: 'Quote generated successfully.',
    appliedRuleTrace: pricingResult.appliedRuleTrace
  };
}

function rejectedResponse(reasonMessage) {
  return {
    status: 'REJECTED',
    rejectionReason: reasonMessage,
    basePremium: null,
    riskFactor: null,
    discountAmount: null,
    taxAmount: null,
    paymentFrequencySurchargeAmount: null,
    countryAdjustmentAmount: null,
    finalPremium: null,
    underwritingCaseId: null,
    underwritingStatus: null,
    processingMessage: reasonMessage,
    appliedRuleTrace: []
  };
}

module.exports = {
  createDraftQuoteContext,
  generateQuote
};
