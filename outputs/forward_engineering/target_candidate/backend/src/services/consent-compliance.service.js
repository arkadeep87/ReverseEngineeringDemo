const repo = require('../storage/quote.repository');
const rulesRepo = require('../storage/rules.repository');
const auditService = require('./audit-trail.service');

async function evaluateAndPersist(context, payload) {
  const consentRule = await rulesRepo.getConsentRequirement(payload.country);
  const required = !!consentRule.requiredIndicator;
  const provided = !!payload.consentIndicator;

  if (required && !provided) {
    await repo.saveConsentRecord({
      customerId: payload.customerId,
      quoteContextId: context.quoteContextId,
      quoteId: null,
      country: payload.country,
      consentType: 'GDPR',
      requiredIndicator: true,
      providedIndicator: false,
      outcome: 'REJECTED',
      rejectionReason: 'Required consent is missing for the selected country.'
    });

    await auditService.recordRejectedAttempt(
      context,
      payload,
      'CONSENT_REQUIRED',
      'Required consent is missing for the selected country.',
      'CONSENT_FAILED'
    );

    return { valid: false, reasonMessage: 'Required consent is missing for the selected country.' };
  }

  await repo.saveConsentRecord({
    customerId: payload.customerId,
    quoteContextId: context.quoteContextId,
    quoteId: null,
    country: payload.country,
    consentType: 'GDPR',
    requiredIndicator: required,
    providedIndicator: provided,
    outcome: 'GRANTED',
    rejectionReason: null
  });

  return { valid: true };
}

module.exports = {
  evaluateAndPersist
};
