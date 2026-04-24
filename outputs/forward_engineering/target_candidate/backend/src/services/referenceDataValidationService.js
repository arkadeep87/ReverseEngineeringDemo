class ReferenceDataValidationService {
  constructor({ referenceDataRepository, hashService }) {
    this.referenceDataRepository = referenceDataRepository;
    this.hashService = hashService;
  }

  async validate(request) {
    const policyDefinition = await this.referenceDataRepository.getActivePolicyDefinition(request.countryCode, request.policyType, request.requestTimestamp);
    if (!policyDefinition) {
      const error = new Error('The selected policy definition is missing or inactive.');
      error.statusCode = 400;
      error.validationMessages = ['The selected policy definition is missing or inactive.'];
      error.rejectionReasonCode = 'INVALID_POLICY_DEFINITION';
      throw error;
    }

    const paymentFrequencyDefinition = await this.referenceDataRepository.getActivePaymentFrequencyDefinition(request.paymentFrequency, request.requestTimestamp);
    if (!paymentFrequencyDefinition) {
      const error = new Error('The selected payment frequency definition is missing or inactive.');
      error.statusCode = 400;
      error.validationMessages = ['The selected payment frequency definition is missing or inactive.'];
      error.rejectionReasonCode = 'INVALID_PAYMENT_FREQUENCY';
      throw error;
    }

    if (request.coverageAmount < Number(policyDefinition.minimumCoverageAmount) || request.coverageAmount > Number(policyDefinition.maximumCoverageAmount)) {
      const error = new Error('Requested cover is outside the permitted product range.');
      error.statusCode = 400;
      error.validationMessages = ['Requested cover is outside the permitted product range.'];
      error.rejectionReasonCode = 'COVERAGE_OUT_OF_RANGE';
      throw error;
    }

    return {
      policyDefinitionId: policyDefinition.policyDefinitionId,
      paymentFrequencyDefinitionId: paymentFrequencyDefinition.paymentFrequencyDefinitionId,
      requestPayloadHash: this.hashService.hash(request),
      policyDefinition,
      paymentFrequencyDefinition
    };
  }
}

module.exports = ReferenceDataValidationService;
