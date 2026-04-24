const CountryAdjustmentResolutionService = require('../../src/services/countryAdjustmentResolutionService');

describe('CountryAdjustmentResolutionService', () => {
  const service = new CountryAdjustmentResolutionService();
  const baseAmounts = { basePremium: 100, riskLoadingAmount: 8, discountAmount: 4, taxAmount: 9 };

  test('applies Germany 3.2% adjustment and 1.4% HEALTH additive adjustment', () => {
    const result = service.resolve({ countryCode: 'DE', policyType: 'HEALTH' }, {}, baseAmounts, { adjustmentSource: 'PRIMARY', adjustmentRuleVersion: 'DE_ADJ_V1' });
    expect(result.countryAdjustmentAmount).toBe(7.16);
  });

  test('applies Italy fixed adjustment 22 and FAMILY reduction 12', () => {
    const result = service.resolve({ countryCode: 'IT', policyType: 'FAMILY' }, {}, baseAmounts, { adjustmentSource: 'PRIMARY', adjustmentRuleVersion: 'IT_ADJ_V1' });
    expect(result.countryAdjustmentAmount).toBe(10);
  });

  test('applies Portugal 1.2% adjustment and ANNUAL reduction 7.50', () => {
    const result = service.resolve({ countryCode: 'PT', paymentFrequency: 'ANNUAL' }, {}, baseAmounts, { adjustmentSource: 'PRIMARY', adjustmentRuleVersion: 'PT_ADJ_V1' });
    expect(result.countryAdjustmentAmount).toBe(-6.14);
  });

  test('applies Switzerland 2.1% adjustment and CORPORATE surcharge 35', () => {
    const result = service.resolve({ countryCode: 'CH', policyType: 'CORPORATE' }, {}, baseAmounts, { adjustmentSource: 'PRIMARY', adjustmentRuleVersion: 'CH_ADJ_V1' });
    expect(result.countryAdjustmentAmount).toBe(37.37);
  });

  test('applies United Kingdom 12% adjustment and TRAVEL surcharge 6', () => {
    const result = service.resolve({ countryCode: 'GB', policyType: 'TRAVEL' }, {}, baseAmounts, { adjustmentSource: 'PRIMARY', adjustmentRuleVersion: 'GB_ADJ_V1' });
    expect(result.countryAdjustmentAmount).toBe(19.56);
  });
});
