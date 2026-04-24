class SupportedCountryValidator {
  constructor() {
    this.supportedCountries = ['ES', 'DE', 'IT', 'PT', 'CH', 'GB'];
  }

  validate(countryCode) {
    if (!this.supportedCountries.includes(countryCode)) {
      const error = new Error('The selected country is outside the approved quote scope.');
      error.statusCode = 400;
      error.validationMessages = ['The selected country is outside the approved quote scope.'];
      error.rejectionReasonCode = 'UNSUPPORTED_COUNTRY';
      throw error;
    }
  }
}

module.exports = SupportedCountryValidator;
