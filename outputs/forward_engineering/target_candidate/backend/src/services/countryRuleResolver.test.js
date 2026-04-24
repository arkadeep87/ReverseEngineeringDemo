const CountryRuleResolver = require('../../src/services/countryRuleResolver');

describe('CountryRuleResolver', () => {
  const resolver = new CountryRuleResolver({
    spainRoutingConfigRepository: {
      getApprovedRouting: jest.fn().mockResolvedValue({ workflowStatus: 'SPAIN_STANDARD_REVIEW', routingRuleVersion: 'ES_ROUTE_V1' })
    }
  });

  test('returns Germany tax and underwriting rules', async () => {
    const result = await resolver.resolve('DE', 'HEALTH');
    expect(result.taxRate).toBe(0.21);
    expect(result.underwritingStatus).toBe('EU_COMPLIANCE');
  });

  test('returns Italy tax and underwriting rules', async () => {
    const result = await resolver.resolve('IT', 'FAMILY');
    expect(result.taxRate).toBe(0.11);
    expect(result.underwritingStatus).toBe('EU_COMPLIANCE');
  });

  test('returns Portugal tax and underwriting rules', async () => {
    const result = await resolver.resolve('PT', 'FAMILY');
    expect(result.taxRate).toBe(0.095);
    expect(result.underwritingStatus).toBe('EU_COMPLIANCE');
  });

  test('returns Switzerland tax and underwriting rules', async () => {
    const result = await resolver.resolve('CH', 'CORPORATE');
    expect(result.taxRate).toBe(0.065);
    expect(result.underwritingStatus).toBe('CANTON_CHECK');
  });

  test('returns United Kingdom tax and underwriting rules', async () => {
    const result = await resolver.resolve('GB', 'TRAVEL');
    expect(result.taxRate).toBe(0.12);
    expect(result.underwritingStatus).toBe('IPT_REVIEW');
  });

  test('returns approved Spain routing configuration', async () => {
    const result = await resolver.resolve('ES', 'HEALTH');
    expect(result.underwritingStatus).toBe('SPAIN_STANDARD_REVIEW');
  });
});
