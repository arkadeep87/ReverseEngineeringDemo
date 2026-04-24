const BasePremiumCalculationService = require('../../src/services/basePremiumCalculationService');

describe('BasePremiumCalculationService', () => {
  test('calculates base premium using approved rate-per-thousand factor', () => {
    const service = new BasePremiumCalculationService();
    const result = service.calculate({ coverageAmount: 10000 }, { basePremiumRatePerThousand: 4.25, version: 'BASELINE_V1' });
    expect(result.basePremium).toBe(42.5);
    expect(result.ratePerThousand).toBe(4.25);
  });
});
