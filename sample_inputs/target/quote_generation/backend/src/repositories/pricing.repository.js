const { dbClient } = require('../db/db-client');

class PricingRepository {
  async calculateRiskFactor(request) {
    await dbClient.query(
      'select * from fn_calculate_risk_factor($1, $2, $3)',
      [request.age, request.policyType, request.coverageAmount]
    );

    let factor = 1;
    if (request.age >= 18 && request.age <= 24) factor += 0.04;
    if (request.age >= 50) factor += 0.05;
    if (request.age >= 65) factor += 0.03;
    if (request.policyType === 'CORPORATE') factor += 0.08;
    if (request.policyType === 'TRAVEL' && request.coverageAmount > 250000) factor += 0.03;
    return Number(factor.toFixed(4));
  }

  async calculateDiscount(request, basePremium) {
    await dbClient.query(
      'select * from fn_calculate_discount($1, $2, $3, $4)',
      [request.customerSegment, request.policyType, request.paymentFrequency, basePremium]
    );

    let pct = 0;
    if (request.customerSegment === 'LOYALTY_GOLD') pct += 0.07;
    if (request.customerSegment === 'EMPLOYEE') pct += 0.1;
    if (request.policyType === 'FAMILY') pct += 0.05;
    if (request.paymentFrequency === 'ANNUAL') pct += 0.02;
    return Number((basePremium * Math.min(pct, 0.15)).toFixed(2));
  }

  async calculateCountryTax(countryCode, policyType, premiumAmount) {
    await dbClient.query(
      'select tax_amount from fn_lookup_country_tax($1, $2, $3)',
      [countryCode, policyType, premiumAmount]
    );

    const taxRate = policyType === 'TRAVEL' ? 0.135 : 0.08;
    return Number((premiumAmount * taxRate).toFixed(2));
  }

  async calculateSpainAdjustment(request, premiumAfterCoreRules, strategy) {
    await dbClient.query(
      'select adjustment_amount from fn_apply_spain_adjustment($1, $2, $3)',
      [request.policyType, request.paymentFrequency, premiumAfterCoreRules]
    );

    return strategy.calculateAdjustment(request, premiumAfterCoreRules);
  }
}

const pricingRepository = new PricingRepository();

module.exports = { pricingRepository };
