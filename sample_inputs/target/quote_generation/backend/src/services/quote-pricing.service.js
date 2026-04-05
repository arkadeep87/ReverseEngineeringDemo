const { pricingRepository } = require('../repositories/pricing.repository');
const { referenceDataRepository } = require('../repositories/reference-data.repository');

class QuotePricingService {
  async calculateQuote(request, strategy) {
    const basePremium = await referenceDataRepository.getBasePremium(request.policyType, request.coverageAmount);
    const riskFactor = await pricingRepository.calculateRiskFactor(request);
    const discountAmount = await pricingRepository.calculateDiscount(request, basePremium);
    const taxAmount = await pricingRepository.calculateCountryTax(request.countryCode, request.policyType, basePremium);

    const premiumAfterCoreRules = (basePremium * riskFactor) - discountAmount + taxAmount;
    const countryAdjustmentAmount = await pricingRepository.calculateSpainAdjustment(request, premiumAfterCoreRules, strategy);

    return {
      basePremium,
      riskFactor,
      discountAmount,
      taxAmount,
      countryAdjustmentAmount,
      finalPremium: premiumAfterCoreRules + countryAdjustmentAmount
    };
  }
}

const quotePricingService = new QuotePricingService();

module.exports = { quotePricingService };
