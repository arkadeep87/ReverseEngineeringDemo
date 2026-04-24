const crypto = require('crypto');
const { dbClient } = require('../db/db-client');

class QuoteRepository {
  async insertQuoteHeader(request, pricing) {
    const quoteId = crypto.randomUUID();

    await dbClient.query(
      'insert into quotes (quote_id, customer_id, policy_type, country_code, base_premium, coverage_amount, customer_segment, payment_frequency, risk_factor, discount_amount, tax_amount, final_premium, gdpr_consent_granted, created_at) values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, current_timestamp)',
      [
        quoteId,
        request.customerId,
        request.policyType,
        request.countryCode,
        pricing.basePremium,
        request.coverageAmount,
        request.customerSegment,
        request.paymentFrequency,
        pricing.riskFactor,
        pricing.discountAmount,
        pricing.taxAmount,
        pricing.finalPremium,
        request.gdprConsentGranted
      ]
    );

    return quoteId;
  }

  async upsertQuoteContext(quoteId, request, pricing) {
    await dbClient.query(
      'insert into quote_context (quote_id, customer_age, country_code, policy_type, customer_segment, payment_frequency, coverage_amount, final_premium, country_adjustment_amount, last_updated) values ($1, $2, $3, $4, $5, $6, $7, $8, $9, current_timestamp) on conflict (quote_id) do update set final_premium = excluded.final_premium, country_adjustment_amount = excluded.country_adjustment_amount, last_updated = current_timestamp',
      [
        quoteId,
        request.age,
        request.countryCode,
        request.policyType,
        request.customerSegment,
        request.paymentFrequency,
        request.coverageAmount,
        pricing.finalPremium,
        pricing.countryAdjustmentAmount
      ]
    );
  }

  async insertQuoteCharge(quoteId, chargeCode, amount) {
    await dbClient.query(
      'insert into quote_charge (quote_id, charge_code, amount, created_at) values ($1, $2, $3, current_timestamp)',
      [quoteId, chargeCode, amount]
    );
  }

  async insertUnderwritingCase(quoteId, customerId, countryCode) {
    await dbClient.query(
      'insert into underwriting_case (quote_id, customer_id, country_code, case_status, created_at) values ($1, $2, $3, $4, current_timestamp)',
      [quoteId, customerId, countryCode, 'SPAIN_STANDARD_REVIEW']
    );
  }
}

const quoteRepository = new QuoteRepository();

module.exports = { quoteRepository };
