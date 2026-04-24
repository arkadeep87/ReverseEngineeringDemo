class TaxCalculationService {
  calculate(request, pricingBaseline, amounts, countryRules) {
    const taxRateApplied = Number(countryRules.taxRate);
    const taxableBasis = amounts.basePremium + amounts.riskLoadingAmount - amounts.discountAmount;
    const taxAmount = Math.round(((taxableBasis * taxRateApplied) + Number.EPSILON) * 100) / 100;

    return {
      taxAmount,
      taxRateApplied,
      taxBasis: 'BASE_PLUS_RISK_MINUS_DISCOUNT',
      sourceAttribution: countryRules.taxSource || 'COUNTRY_TAX_RULE',
      ruleVersion: countryRules.taxRuleVersion
    };
  }
}

module.exports = TaxCalculationService;
