const rulesRepo = require('../storage/rules.repository');
const referenceRepo = require('../storage/reference.repository');

async function validateSupportedCountry(country) {
  const supported = await rulesRepo.getSupportedCountries();
  if (!supported.includes(country)) {
    return { valid: false, reasonCode: 'UNSUPPORTED_COUNTRY', reasonMessage: 'Selected country is not supported for quote processing.' };
  }
  return { valid: true };
}

async function validateReferenceData(payload) {
  const customer = await referenceRepo.getCustomer(payload.customerId);
  if (!customer) {
    return { valid: false, reasonCode: 'CUSTOMER_NOT_FOUND', reasonMessage: 'Customer reference data is missing or invalid.' };
  }

  const product = await referenceRepo.getProductRule(payload.policyType);
  if (!product) {
    return { valid: false, reasonCode: 'PRODUCT_NOT_FOUND', reasonMessage: 'Policy or product reference data is missing or invalid.' };
  }

  const paymentFrequency = await referenceRepo.getPaymentFrequency(payload.paymentFrequency);
  if (!paymentFrequency) {
    return { valid: false, reasonCode: 'PAYMENT_FREQUENCY_NOT_FOUND', reasonMessage: 'Payment frequency reference data is missing or invalid.' };
  }

  return { valid: true };
}

async function validateCoverageBounds(payload) {
  const product = await referenceRepo.getProductRule(payload.policyType);
  if (!product) {
    return { valid: false, reasonCode: 'PRODUCT_NOT_FOUND', reasonMessage: 'Policy or product reference data is missing or invalid.' };
  }

  if (product.min_coverage_amount != null && Number(payload.coverageAmount) < Number(product.min_coverage_amount)) {
    return { valid: false, reasonCode: 'COVERAGE_OUT_OF_RANGE', reasonMessage: 'Coverage amount is outside the permitted product range.' };
  }

  if (product.max_coverage_amount != null && Number(payload.coverageAmount) > Number(product.max_coverage_amount)) {
    return { valid: false, reasonCode: 'COVERAGE_OUT_OF_RANGE', reasonMessage: 'Coverage amount is outside the permitted product range.' };
  }

  return { valid: true };
}

module.exports = {
  validateSupportedCountry,
  validateReferenceData,
  validateCoverageBounds
};
