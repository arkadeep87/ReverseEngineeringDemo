const PremiumCompositionService = require('../../src/services/premiumCompositionService');

describe('PremiumCompositionService', () => {
  test('assembles pricing in approved component sequence and returns material charge lines', async () => {
    const service = new PremiumCompositionService({
      basePremiumCalculationService: { calculate: jest.fn().mockResolvedValue({ basePremium: 100, ratePerThousand: 4.25, ruleVersion: 'V1' }) },
      riskLoadingService: { calculate: jest.fn().mockResolvedValue({ riskLoadingAmount: 8, riskFactorApplied: 1.08, ruleVersion: 'V1' }) },
      discountCalculationService: { calculate: jest.fn().mockResolvedValue({ discountAmount: 4, discountRate: 0.04, calculationBasis: 'BASE_PLUS_RISK', ruleVersion: 'V1' }) },
      taxCalculationService: { calculate: jest.fn().mockResolvedValue({ taxAmount: 9.36, taxRateApplied: 0.09, taxBasis: 'BASE_PLUS_RISK_MINUS_DISCOUNT', sourceAttribution: 'COUNTRY_TAX_RULE', ruleVersion: 'V1' }) },
      countryAdjustmentResolutionService: { resolve: jest.fn().mockResolvedValue({ countryAdjustmentAmount: 5, countryAdjustmentSource: 'PRIMARY', calculationBasis: 'COUNTRY_RULE', rateOrFactorApplied: 0.05, ruleVersion: 'V1' }) },
      paymentFrequencySurchargeService: { evaluate: jest.fn().mockResolvedValue({ surchargeAmount: 0, calculationBasis: 'RETIRED_OR_INACTIVE', rateOrFactorApplied: 0, sourceAttribution: 'PAYMENT_FREQUENCY_SURCHARGE_SERVICE', ruleVersion: 'V1' }) }
    });

    const result = await service.compose({
      request: { countryCode: 'ES' },
      pricingBaseline: { version: 'V1' },
      countryRules: { underwritingStatus: 'SPAIN_STANDARD_REVIEW', routingRuleVersion: 'ES_ROUTE_V1' }
    });

    expect(result.finalPremium).toBe(118.36);
    expect(result.chargeLines.map(c => c.chargeType)).toEqual(['BASE_PREMIUM', 'DISCOUNT', 'TAX', 'COUNTRY_ADJUSTMENT']);
  });
});
