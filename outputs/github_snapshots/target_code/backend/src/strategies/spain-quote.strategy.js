class SpainQuoteStrategy {
  calculateAdjustment(request, premiumAfterCoreRules) {
    const consortiumLevy = premiumAfterCoreRules * 0.018;
    const travelAssistReserve = request.policyType === 'TRAVEL' ? 9.5 : 0;
    return Number((consortiumLevy + travelAssistReserve).toFixed(2));
  }

  buildAuditMessage(request, pricing) {
    return `Spain quote generated for ${request.customerId} with final premium ${pricing.finalPremium.toFixed(2)}.`;
  }
}

const spainQuoteStrategy = new SpainQuoteStrategy();

module.exports = { spainQuoteStrategy };
