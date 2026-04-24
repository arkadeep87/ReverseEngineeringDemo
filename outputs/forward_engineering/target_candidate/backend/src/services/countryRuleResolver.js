class CountryRuleResolver {
  constructor({ spainRoutingConfigRepository }) {
    this.spainRoutingConfigRepository = spainRoutingConfigRepository;
  }

  async resolve(countryCode, policyType) {
    if (countryCode === 'DE') {
      return {
        taxRate: policyType === 'HEALTH' ? 0.21 : 0.19,
        taxRuleVersion: 'DE_TAX_V1',
        taxSource: 'COUNTRY_TAX_RULE',
        adjustmentSource: 'PRIMARY',
        adjustmentRuleVersion: 'DE_ADJ_V1',
        underwritingStatus: 'EU_COMPLIANCE',
        routingRuleVersion: 'DE_ROUTE_V1'
      };
    }
    if (countryCode === 'IT') {
      return {
        taxRate: policyType === 'FAMILY' ? 0.11 : 0.09,
        taxRuleVersion: 'IT_TAX_V1',
        taxSource: 'COUNTRY_TAX_RULE',
        adjustmentSource: 'PRIMARY',
        adjustmentRuleVersion: 'IT_ADJ_V1',
        underwritingStatus: 'EU_COMPLIANCE',
        routingRuleVersion: 'IT_ROUTE_V1'
      };
    }
    if (countryCode === 'PT') {
      return {
        taxRate: policyType === 'FAMILY' ? 0.095 : 0.075,
        taxRuleVersion: 'PT_TAX_V1',
        taxSource: 'COUNTRY_TAX_RULE',
        adjustmentSource: 'PRIMARY',
        adjustmentRuleVersion: 'PT_ADJ_V1',
        underwritingStatus: 'EU_COMPLIANCE',
        routingRuleVersion: 'PT_ROUTE_V1'
      };
    }
    if (countryCode === 'CH') {
      return {
        taxRate: policyType === 'CORPORATE' ? 0.065 : 0.05,
        taxRuleVersion: 'CH_TAX_V1',
        taxSource: 'COUNTRY_TAX_RULE',
        adjustmentSource: 'PRIMARY',
        adjustmentRuleVersion: 'CH_ADJ_V1',
        underwritingStatus: 'CANTON_CHECK',
        routingRuleVersion: 'CH_ROUTE_V1'
      };
    }
    if (countryCode === 'GB') {
      return {
        taxRate: policyType === 'TRAVEL' ? 0.12 : 0.06,
        taxRuleVersion: 'GB_TAX_V1',
        taxSource: 'COUNTRY_TAX_RULE',
        adjustmentSource: 'PRIMARY',
        adjustmentRuleVersion: 'GB_ADJ_V1',
        underwritingStatus: 'IPT_REVIEW',
        routingRuleVersion: 'GB_ROUTE_V1'
      };
    }

    const spainRoute = await this.spainRoutingConfigRepository.getApprovedRouting();
    return {
      taxRate: 0,
      taxRuleVersion: 'ES_TAX_BASELINE',
      taxSource: 'COUNTRY_TAX_RULE',
      adjustmentSource: 'PRIMARY',
      adjustmentRuleVersion: 'ES_ADJ_BASELINE',
      adjustmentValue: 0,
      underwritingStatus: spainRoute.workflowStatus,
      routingRuleVersion: spainRoute.routingRuleVersion
    };
  }
}

module.exports = CountryRuleResolver;
