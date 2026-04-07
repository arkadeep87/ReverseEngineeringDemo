const repo = require('../storage/quote.repository');
const rulesRepo = require('../storage/rules.repository');

async function createCase(quoteId, customerId, country) {
  const mapping = await rulesRepo.getUnderwritingStatusMapping(country);
  return repo.createUnderwritingCase({
    quoteId,
    customerId,
    country,
    status: mapping.targetStatus,
    statusMappingSource: mapping.mappingVersion
  });
}

module.exports = {
  createCase
};
