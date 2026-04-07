const repo = require('../storage/quote.repository');
const rulesRepo = require('../storage/rules.repository');
const referenceRepo = require('../storage/reference.repository');

async function getReferenceData(country) {
  const supportedCountries = await rulesRepo.getSupportedCountries();
  const policyTypes = await referenceRepo.getPolicyTypes(country);
  const paymentFrequencies = await referenceRepo.getPaymentFrequencies(country);
  const countryDefaults = await rulesRepo.getCountryDefaults(country);
  const coverageBounds = await referenceRepo.getCoverageBounds();
  const consentRequirements = await rulesRepo.getConsentRequirements(country);
  return {
    supportedCountries,
    policyTypes,
    paymentFrequencies,
    countryDefaults,
    coverageBounds,
    consentRequirements
  };
}

async function getQuoteById(quoteId) {
  return repo.getQuoteById(quoteId);
}

async function getQuoteBreakdown(quoteId) {
  return repo.getQuoteBreakdown(quoteId);
}

module.exports = {
  getReferenceData,
  getQuoteById,
  getQuoteBreakdown
};
