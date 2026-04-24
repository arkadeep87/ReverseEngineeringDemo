class BasePremiumCalculationService {
  calculate(request, pricingBaseline) {
    const ratePerThousand = Number(pricingBaseline.basePremiumRatePerThousand);
    if (!ratePerThousand && ratePerThousand !== 0) {
      const error = new Error('Base premium configuration is missing for the active pricing baseline.');
      error.statusCode = 500;
      throw error;
    }

    const basePremium = Math.round((((Number(request.coverageAmount) / 1000) * ratePerThousand) + Number.EPSILON) * 100) / 100;
    return {
      basePremium,
      ratePerThousand,
      ruleVersion: pricingBaseline.version
    };
  }
}

module.exports = BasePremiumCalculationService;
