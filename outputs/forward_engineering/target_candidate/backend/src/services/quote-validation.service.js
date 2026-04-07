const { customerRepository } = require('../repositories/customer.repository');
const { referenceDataRepository } = require('../repositories/reference-data.repository');
const { complianceRepository } = require('../repositories/compliance.repository');

class QuoteValidationService {
  async validateRequest(request) {
    if (request.countryCode !== 'ES') {
      throw new Error('Target quote generation currently supports Spain only.');
    }

    const customer = await customerRepository.findCustomerById(request.customerId);
    const product = await referenceDataRepository.getProductDefinition(request.policyType);
    const paymentPlan = await referenceDataRepository.getPaymentPlan(request.paymentFrequency);

    if (!customer || !product || !paymentPlan) {
      throw new Error('Quote reference data is incomplete.');
    }

    if (Number(request.age) < 18) {
      throw new Error('Customer must be at least 18 years old.');
    }

    await complianceRepository.ensureGdprConsent({
      customerId: request.customerId,
      countryCode: request.countryCode,
      gdprConsentGranted: request.gdprConsentGranted
    });
  }
}

const quoteValidationService = new QuoteValidationService();

module.exports = { quoteValidationService };
