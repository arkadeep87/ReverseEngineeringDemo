const { dbClient } = require('../db/db-client');

class AuditRepository {
  async logQuoteEvent(quoteId, eventType, eventMessage) {
    await dbClient.query(
      'insert into audit_log (quote_id, event_type, event_message, created_at) values ($1, $2, $3, current_timestamp)',
      [quoteId, eventType, eventMessage]
    );
  }
}

const auditRepository = new AuditRepository();

module.exports = { auditRepository };
