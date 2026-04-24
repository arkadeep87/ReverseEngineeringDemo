class CountryAdjustmentResolutionService {
  resolve(request, pricingBaseline, amounts, countryRules) {
    const corePremium = amounts.basePremium + amounts.riskLoadingAmount - amounts.discountAmount + amounts.taxAmount;
    let countryAdjustmentAmount = 0;
    let calculationBasis = 'COUNTRY_RULE';
    let rateOrFactorApplied = null;

    switch (request.countryCode) {
      case 'DE': {
        const percentage = 0.032;
        countryAdjustmentAmount += this.round(corePremium * percentage);
        rateOrFactorApplied = percentage;
        if (request.policyType === 'HEALTH') {
          countryAdjustmentAmount += this.round(corePremium * 0.014);
        }
        break;
      }
      case 'IT': {
        countryAdjustmentAmount += 22;
        rateOrFactorApplied = 22;
        if (request.policyType === 'FAMILY') {
          countryAdjustmentAmount -= 12;
        }
        break;
      }
      case 'PT': {
        const percentage = 0.012;
        countryAdjustmentAmount += this.round(corePremium * percentage);
        rateOrFactorApplied = percentage;
        if (request.paymentFrequency === 'ANNUAL') {
          countryAdjustmentAmount -= 7.5;
        }
        break;
      }
      case 'CH': {
        const percentage = 0.021;
        countryAdjustmentAmount += this.round(corePremium * percentage);
        rateOrFactorApplied = percentage;
        if (request.policyType === 'CORPORATE') {
          countryAdjustmentAmount += 35;
        }
        break;
      }
      case 'GB': {
        const percentage = 0.12;
        countryAdjustmentAmount += this.round(corePremium * percentage);
        rateOrFactorApplied = percentage;
        if (request.policyType === 'TRAVEL') {
          countryAdjustmentAmount += 6;
        }
        break;
      }
      case 'ES':
      default: {
        countryAdjustmentAmount += Number(countryRules.adjustmentValue || 0);
        rateOrFactorApplied = Number(countryRules.adjustmentValue || 0);
      }
    }

    return {
      countryAdjustmentAmount: this.round(countryAdjustmentAmount),
      countryAdjustmentSource: countryRules.adjustmentSource || 'PRIMARY',
      calculationBasis,
      rateOrFactorApplied,
      ruleVersion: countryRules.adjustmentRuleVersion
    };
  }

  round(value) {
    return Math.round((Number(value) + Number.EPSILON) * 100) / 100;
  }
}

module.exports = CountryAdjustmentResolutionService;
