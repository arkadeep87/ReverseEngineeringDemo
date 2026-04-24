class EligibilityAssessmentService {
  constructor({ eligibilityRuleRepository }) {
    this.eligibilityRuleRepository = eligibilityRuleRepository;
  }

  async assess(request) {
    const rule = await this.eligibilityRuleRepository.getRule(request.countryCode, request.policyType, request.requestTimestamp);

    if (rule && rule.minimumAge !== null && request.age < Number(rule.minimumAge)) {
      return {
        isEligible: false,
        reasonCode: 'AGE_NOT_ELIGIBLE',
        message: 'The customer does not meet the minimum age eligibility requirement.',
        ruleVersion: rule.ruleVersion
      };
    }

    if (rule && Array.isArray(rule.disallowedSegments) && rule.disallowedSegments.includes(request.customerSegment)) {
      return {
        isEligible: false,
        reasonCode: 'SEGMENT_NOT_ELIGIBLE',
        message: 'The selected customer segment is not eligible for this quote.',
        ruleVersion: rule.ruleVersion
      };
    }

    return {
      isEligible: true,
      reasonCode: null,
      message: 'Eligible',
      ruleVersion: rule ? rule.ruleVersion : 'DEFAULT'
    };
  }
}

module.exports = EligibilityAssessmentService;
