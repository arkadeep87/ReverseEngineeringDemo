class PaymentFrequencySurchargeService {
  evaluate(request, pricingBaseline) {
    if (pricingBaseline.paymentFrequencySurchargeStatus === 'RETIRED' || pricingBaseline.paymentFrequencySurchargeStatus === 'INACTIVE') {
      return {
        surchargeAmount: 0,
        calculationBasis: 'RETIRED_OR_INACTIVE',
        rateOrFactorApplied: 0,
        sourceAttribution: 'PAYMENT_FREQUENCY_SURCHARGE_SERVICE',
        ruleVersion: pricingBaseline.version
      };
    }

    const percentage = Number(pricingBaseline.paymentFrequencySurcharges?.[request.paymentFrequency] || 0);
    return {
      surchargeAmount: 0,
      calculationBasis: 'CONFIGURED_RULE_AREA_PRESENT',
      rateOrFactorApplied: percentage,
      sourceAttribution: 'PAYMENT_FREQUENCY_SURCHARGE_SERVICE',
      ruleVersion: pricingBaseline.version
    };
  }
}

module.exports = PaymentFrequencySurchargeService;
