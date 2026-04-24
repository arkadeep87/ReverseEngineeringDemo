class PremiumCompositionService {
  constructor({
    basePremiumCalculationService,
    riskLoadingService,
    discountCalculationService,
    taxCalculationService,
    countryAdjustmentResolutionService,
    paymentFrequencySurchargeService
  }) {
    this.basePremiumCalculationService = basePremiumCalculationService;
    this.riskLoadingService = riskLoadingService;
    this.discountCalculationService = discountCalculationService;
    this.taxCalculationService = taxCalculationService;
    this.countryAdjustmentResolutionService = countryAdjustmentResolutionService;
    this.paymentFrequencySurchargeService = paymentFrequencySurchargeService;
  }

  async compose({ request, pricingBaseline, countryRules }) {
    const base = await this.basePremiumCalculationService.calculate(request, pricingBaseline);
    const risk = await this.riskLoadingService.calculate(request, pricingBaseline, base.basePremium);
    const discount = await this.discountCalculationService.calculate(request, pricingBaseline, {
      basePremium: base.basePremium,
      riskLoadingAmount: risk.riskLoadingAmount
    });
    const tax = await this.taxCalculationService.calculate(request, pricingBaseline, {
      basePremium: base.basePremium,
      riskLoadingAmount: risk.riskLoadingAmount,
      discountAmount: discount.discountAmount
    }, countryRules);
    const countryAdjustment = await this.countryAdjustmentResolutionService.resolve(request, pricingBaseline, {
      basePremium: base.basePremium,
      riskLoadingAmount: risk.riskLoadingAmount,
      discountAmount: discount.discountAmount,
      taxAmount: tax.taxAmount
    }, countryRules);
    const surcharge = await this.paymentFrequencySurchargeService.evaluate(request, pricingBaseline);

    const finalPremium = this.roundCurrency(
      base.basePremium + risk.riskLoadingAmount - discount.discountAmount + tax.taxAmount + countryAdjustment.countryAdjustmentAmount + surcharge.surchargeAmount
    );

    const chargeLines = [
      {
        chargeType: 'BASE_PREMIUM',
        chargeSequence: 1,
        chargeAmount: base.basePremium,
        calculationBasis: 'RATE_PER_THOUSAND',
        rateOrFactorApplied: base.ratePerThousand,
        sourceAttribution: 'BASE_PREMIUM_CALCULATION_SERVICE',
        ruleVersion: base.ruleVersion,
        taxRateIfApplicable: null,
        isMaterialComponent: true
      },
      {
        chargeType: 'DISCOUNT',
        chargeSequence: 3,
        chargeAmount: discount.discountAmount,
        calculationBasis: discount.calculationBasis,
        rateOrFactorApplied: discount.discountRate,
        sourceAttribution: 'DISCOUNT_CALCULATION_SERVICE',
        ruleVersion: discount.ruleVersion,
        taxRateIfApplicable: null,
        isMaterialComponent: true
      },
      {
        chargeType: 'TAX',
        chargeSequence: 4,
        chargeAmount: tax.taxAmount,
        calculationBasis: tax.taxBasis,
        rateOrFactorApplied: tax.taxRateApplied,
        sourceAttribution: tax.sourceAttribution,
        ruleVersion: tax.ruleVersion,
        taxRateIfApplicable: tax.taxRateApplied,
        isMaterialComponent: true
      },
      {
        chargeType: 'COUNTRY_ADJUSTMENT',
        chargeSequence: 5,
        chargeAmount: countryAdjustment.countryAdjustmentAmount,
        calculationBasis: countryAdjustment.calculationBasis,
        rateOrFactorApplied: countryAdjustment.rateOrFactorApplied,
        sourceAttribution: countryAdjustment.countryAdjustmentSource,
        ruleVersion: countryAdjustment.ruleVersion,
        taxRateIfApplicable: null,
        isMaterialComponent: true
      }
    ];

    if (surcharge.surchargeAmount !== 0) {
      chargeLines.push({
        chargeType: 'SURCHARGE',
        chargeSequence: 6,
        chargeAmount: surcharge.surchargeAmount,
        calculationBasis: surcharge.calculationBasis,
        rateOrFactorApplied: surcharge.rateOrFactorApplied,
        sourceAttribution: surcharge.sourceAttribution,
        ruleVersion: surcharge.ruleVersion,
        taxRateIfApplicable: null,
        isMaterialComponent: true
      });
    }

    return {
      basePremium: base.basePremium,
      riskLoadingAmount: risk.riskLoadingAmount,
      riskFactorApplied: risk.riskFactorApplied,
      discountAmount: discount.discountAmount,
      taxAmount: tax.taxAmount,
      taxRateApplied: tax.taxRateApplied,
      taxRuleVersion: tax.ruleVersion,
      countryAdjustmentAmount: countryAdjustment.countryAdjustmentAmount,
      countryAdjustmentSource: countryAdjustment.countryAdjustmentSource,
      countryAdjustmentRuleVersion: countryAdjustment.ruleVersion,
      underwritingStatus: countryRules.underwritingStatus,
      routingRuleVersion: countryRules.routingRuleVersion,
      finalPremium,
      chargeLines
    };
  }

  roundCurrency(value) {
    return Math.round((Number(value) + Number.EPSILON) * 100) / 100;
  }
}

module.exports = PremiumCompositionService;
