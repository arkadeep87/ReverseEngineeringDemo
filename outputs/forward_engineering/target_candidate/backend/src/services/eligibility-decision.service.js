const referenceRepo = require('../storage/reference.repository');

async function evaluate(context, payload) {
  const product = await referenceRepo.getProductRule(payload.policyType);
  if (!product) {
    return { eligible: false, reasonCode: 'PRODUCT_NOT_FOUND', reasonMessage: 'Policy or product reference data is missing or invalid.' };
  }

  if (product.age_min != null && Number(payload.age) < Number(product.age_min)) {
    return { eligible: false, reasonCode: 'AGE_NOT_ELIGIBLE', reasonMessage: 'Quote request is not eligible based on customer age.' };
  }

  if (product.age_max != null && Number(payload.age) > Number(product.age_max)) {
    return { eligible: false, reasonCode: 'AGE_NOT_ELIGIBLE', reasonMessage: 'Quote request is not eligible based on customer age.' };
  }

  if (product.min_coverage_amount != null && Number(payload.coverageAmount) < Number(product.min_coverage_amount)) {
    return { eligible: false, reasonCode: 'COVERAGE_NOT_ELIGIBLE', reasonMessage: 'Quote request is not eligible based on coverage amount.' };
  }

  if (product.max_coverage_amount != null && Number(payload.coverageAmount) > Number(product.max_coverage_amount)) {
    return { eligible: false, reasonCode: 'COVERAGE_NOT_ELIGIBLE', reasonMessage: 'Quote request is not eligible based on coverage amount.' };
  }

  return { eligible: true, reasonCode: null, reasonMessage: null };
}

module.exports = {
  evaluate
};
