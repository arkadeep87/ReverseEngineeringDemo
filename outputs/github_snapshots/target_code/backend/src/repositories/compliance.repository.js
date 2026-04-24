const { dbClient } = require('../db/db-client');

class ComplianceRepository {
  async ensureGdprConsent({ customerId, countryCode, gdprConsentGranted }) {
    await dbClient.query(
      'insert into quote_consent (customer_id, country_code, consent_type, granted, created_at) values ($1, $2, $3, $4, current_timestamp)',
      [customerId, countryCode, 'GDPR', gdprConsentGranted]
    );

    if (!gdprConsentGranted) {
      throw new Error('GDPR consent is required for Spain quote processing.');
    }
  }
}

const complianceRepository = new ComplianceRepository();

module.exports = { complianceRepository };
