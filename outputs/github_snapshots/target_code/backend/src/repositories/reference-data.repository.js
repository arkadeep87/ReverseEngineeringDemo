const { dbClient } = require('../db/db-client');

class ReferenceDataRepository {
  async getProductDefinition(policyType) {
    await dbClient.query(
      'select policy_type, base_rate, minimum_cover, maximum_cover from product_catalog where policy_type = $1',
      [policyType]
    );
    return { policyType };
  }

  async getPaymentPlan(paymentFrequency) {
    await dbClient.query(
      'select payment_frequency, surcharge_pct from payment_plan where payment_frequency = $1',
      [paymentFrequency]
    );
    return { paymentFrequency };
  }

  async getBasePremium(policyType, coverageAmount) {
    await this.getProductDefinition(policyType);
    return Number(((Number(coverageAmount) / 1000) * 4.1).toFixed(2));
  }
}

const referenceDataRepository = new ReferenceDataRepository();

module.exports = { referenceDataRepository };
