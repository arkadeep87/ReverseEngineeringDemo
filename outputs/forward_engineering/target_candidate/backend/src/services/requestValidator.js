class RequestValidator {
  validateRequiredFields(request) {
    const requiredFields = [
      'customerId',
      'age',
      'countryCode',
      'policyType',
      'coverageAmount',
      'customerSegment',
      'paymentFrequency',
      'consentStatus',
      'channel',
      'requestTimestamp',
      'correlationId'
    ];

    const missing = requiredFields.filter((field) => request[field] === undefined || request[field] === null || request[field] === '');
    if (missing.length > 0) {
      const error = new Error('Missing required quote request fields.');
      error.statusCode = 400;
      error.validationMessages = [`Missing required fields: ${missing.join(', ')}`];
      error.rejectionReasonCode = 'MISSING_REQUIRED_FIELDS';
      throw error;
    }
  }
}

module.exports = RequestValidator;
