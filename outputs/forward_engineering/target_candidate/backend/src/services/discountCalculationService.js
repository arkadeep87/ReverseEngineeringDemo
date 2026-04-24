class DiscountCalculationService {
  calculate(request, pricingBaseline, amounts) {
    const mode = pricingBaseline.discountModelType;
    if (mode === 'FLAT_PERCENT') {
      const rate = Number(pricingBaseline.discountRate);
      const basisAmount = amounts.basePremium + amounts.riskLoadingAmount;
      const discountAmount = Math.round(((basisAmount * rate) + Number.EPSILON) * 100) / 100;
      return {
        discountAmount,
        discountRate: rate,
        calculationBasis: 'BASE_PLUS_RISK',
        ruleVersion: pricingBaseline.version
      };
    }

    if (mode === 'NONE') {
      return {
        discountAmount: 0,
        discountRate: 0,
        calculationBasis: 'NONE',
        ruleVersion: pricingBaseline.version
      };
    }

    const error = new Error('Discount rule configuration is incomplete or unsupported for the active baseline.');
    error.statusCode = 500;
    throw error;
  }
}

module.exports = DiscountCalculationService;
