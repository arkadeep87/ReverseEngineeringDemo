class PricingBaselineGovernanceService {
  constructor({ pricingBaselineRepository }) {
    this.pricingBaselineRepository = pricingBaselineRepository;
  }

  async resolve(request) {
    const baseline = await this.pricingBaselineRepository.getApprovedBaseline(request.countryCode, request.policyType, request.requestTimestamp);
    if (!baseline) {
      const error = new Error('No approved pricing baseline is active for the requested quote scenario.');
      error.statusCode = 400;
      error.validationMessages = ['No approved pricing baseline is active for the requested quote scenario.'];
      error.rejectionReasonCode = 'PRICING_BASELINE_UNAVAILABLE';
      throw error;
    }
    return baseline;
  }
}

module.exports = PricingBaselineGovernanceService;
