const ReferenceDataValidationService = require('../../src/services/referenceDataValidationService');

describe('ReferenceDataValidationService', () => {
  const hashService = { hash: jest.fn(() => 'hash-1') };

  test('rejects missing or inactive policy definition', async () => {
    const service = new ReferenceDataValidationService({
      referenceDataRepository: {
        getActivePolicyDefinition: jest.fn().mockResolvedValue(null),
        getActivePaymentFrequencyDefinition: jest.fn()
      },
      hashService
    });

    await expect(service.validate({ countryCode: 'DE', policyType: 'HEALTH', paymentFrequency: 'ANNUAL', coverageAmount: 5000, requestTimestamp: '2026-04-24' }))
      .rejects.toThrow('The selected policy definition is missing or inactive.');
  });

  test('rejects missing or inactive payment frequency definition', async () => {
    const service = new ReferenceDataValidationService({
      referenceDataRepository: {
        getActivePolicyDefinition: jest.fn().mockResolvedValue({ policyDefinitionId: 'p1', minimumCoverageAmount: 1000, maximumCoverageAmount: 10000 }),
        getActivePaymentFrequencyDefinition: jest.fn().mockResolvedValue(null)
      },
      hashService
    });

    await expect(service.validate({ countryCode: 'DE', policyType: 'HEALTH', paymentFrequency: 'ANNUAL', coverageAmount: 5000, requestTimestamp: '2026-04-24' }))
      .rejects.toThrow('The selected payment frequency definition is missing or inactive.');
  });

  test('rejects coverage outside approved product range', async () => {
    const service = new ReferenceDataValidationService({
      referenceDataRepository: {
        getActivePolicyDefinition: jest.fn().mockResolvedValue({ policyDefinitionId: 'p1', minimumCoverageAmount: 1000, maximumCoverageAmount: 10000 }),
        getActivePaymentFrequencyDefinition: jest.fn().mockResolvedValue({ paymentFrequencyDefinitionId: 'pf1' })
      },
      hashService
    });

    await expect(service.validate({ countryCode: 'DE', policyType: 'HEALTH', paymentFrequency: 'ANNUAL', coverageAmount: 20000, requestTimestamp: '2026-04-24' }))
      .rejects.toThrow('Requested cover is outside the permitted product range.');
  });
});
