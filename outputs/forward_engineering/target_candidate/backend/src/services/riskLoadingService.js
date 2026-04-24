class RiskLoadingService {
  calculate(request, pricingBaseline, basePremium) {
    const mode = pricingBaseline.riskModelType;
    if (mode === 'FLAT') {
      const factor = Number(pricingBaseline.riskFlatFactor);
      const riskLoadingAmount = Math.round(((basePremium * (factor - 1)) + Number.EPSILON) * 100) / 100;
      return {
        riskFactorApplied: factor,
        riskLoadingAmount,
        ruleVersion: pricingBaseline.version
      };
    }

    if (mode === 'NONE') {
      return {
        riskFactorApplied: 1,
        riskLoadingAmount: 0,
        ruleVersion: pricingBaseline.version
      };
    }

    const error = new Error('Risk model configuration is incomplete or unsupported for the active baseline.');
    error.statusCode = 500;
    throw error;
  }
}

module.exports = RiskLoadingService;
