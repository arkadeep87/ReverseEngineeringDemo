const repo = require('../storage/quote.repository');

async function recordEvent(event) {
  await repo.saveAuditEvent(event);
}

async function recordRejectedAttempt(context, payload, reasonCode, reasonMessage, eventType) {
  await repo.saveAuditEvent({
    quoteContextId: context.quoteContextId,
    quoteId: null,
    customerId: payload.customerId,
    country: payload.country,
    eventType,
    eventOutcome: 'REJECTED',
    reasonCode,
    reasonMessage,
    ruleSource: null,
    ruleVersion: null,
    eventPayloadJson: payload
  });
}

module.exports = {
  recordEvent,
  recordRejectedAttempt
};
