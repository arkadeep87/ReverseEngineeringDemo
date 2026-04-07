const rulesRepo = require('../storage/rules.repository');

function round2(value) {
  return Math.round((Number(value) + Number.EPSILON) * 100) / 100;
}

async function calculate(payload) {
  const basePremium = round2((Number(payload.coverageAmount) / 1000) * 4.25);

  const riskModel = await rulesRepo.getRiskModel(payload);
  const riskFactor = Number(riskModel.riskFactor);
  const riskAmount = round2(basePremium * (riskFactor - 1));

  const discountAmount = round2(basePremium * 0.04);

  const surchargeRule = await rulesRepo.getPaymentFrequencyRule(payload.paymentFrequency);
  const paymentFrequencySurchargeAmount = surchargeRule.enabled
    ? round2((basePremium + riskAmount - discountAmount) * Number(surchargeRule.surchargePercent))
    : 0;

  const premiumAfterCoreRules = round2(basePremium + riskAmount - discountAmount + paymentFrequencySurchargeAmount);

  const taxRule = await rulesRepo.getTaxRule(payload.country, payload.policyType);
  const taxAmount = round2(premiumAfterCoreRules * Number(taxRule.taxRate));

  const countryAdjustment = await resolveCountryAdjustment(payload, premiumAfterCoreRules);
  const finalPremium = round2(premiumAfterCoreRules + taxAmount + countryAdjustment.amount);

  return {
    basePremium,
    riskFactor,
    discountAmount,
    taxAmount,
    paymentFrequencySurchargeAmount,
    countryAdjustmentAmount: countryAdjustment.amount,
    finalPremium,
    ruleSourceSummary: {
      taxRuleSource: taxRule.ruleSource,
      countryAdjustmentRuleSource: countryAdjustment.ruleSource,
      surchargeRuleSource: surchargeRule.ruleSource,
      riskRuleSource: riskModel.ruleSource
    },
    ruleVersionSummary: {
      taxRuleVersion: taxRule.ruleVersion,
      countryAdjustmentRuleVersion: countryAdjustment.ruleVersion,
      surchargeRuleVersion: surchargeRule.ruleVersion,
      riskRuleVersion: riskModel.ruleVersion,
      basePremiumFormulaVersion: 'BASE_PREMIUM_V1_4_25',
      discountRuleVersion: 'DISCOUNT_V1_4_PERCENT'
    },
    appliedRuleTrace: [
      { component: 'BASE_PREMIUM', ruleVersion: 'BASE_PREMIUM_V1_4_25', amount: basePremium },
      { component: 'RISK', ruleVersion: riskModel.ruleVersion, factor: riskFactor, amount: riskAmount },
      { component: 'DISCOUNT', ruleVersion: 'DISCOUNT_V1_4_PERCENT', amount: discountAmount },
      { component: 'SURCHARGE', ruleVersion: surchargeRule.ruleVersion, amount: paymentFrequencySurchargeAmount },
      { component: 'TAX', ruleVersion: taxRule.ruleVersion, amount: taxAmount },
      { component: 'COUNTRY_ADJUSTMENT', ruleVersion: countryAdjustment.ruleVersion, amount: countryAdjustment.amount }
    ],
    breakdown: [
      { componentType: 'BASE_PREMIUM', componentCode: 'BASE_PREMIUM', calculationSequence: 1, calculationBasisAmount: Number(payload.coverageAmount), rateOrFactor: 4.25, fixedAmount: null, signedAmount: basePremium, currencyCode: 'EUR', ruleSource: 'CONFIG', ruleVersion: 'BASE_PREMIUM_V1_4_25' },
      { componentType: 'RISK', componentCode: 'RISK_FACTOR', calculationSequence: 2, calculationBasisAmount: basePremium, rateOrFactor: riskFactor, fixedAmount: null, signedAmount: riskAmount, currencyCode: 'EUR', ruleSource: riskModel.ruleSource, ruleVersion: riskModel.ruleVersion },
      { componentType: 'DISCOUNT', componentCode: 'STANDARD_DISCOUNT', calculationSequence: 3, calculationBasisAmount: basePremium, rateOrFactor: 0.04, fixedAmount: null, signedAmount: -discountAmount, currencyCode: 'EUR', ruleSource: 'CONFIG', ruleVersion: 'DISCOUNT_V1_4_PERCENT' },
      { componentType: 'SURCHARGE', componentCode: 'PAYMENT_FREQUENCY_SURCHARGE', calculationSequence: 4, calculationBasisAmount: premiumAfterCoreRules, rateOrFactor: surchargeRule.surchargePercent, fixedAmount: null, signedAmount: paymentFrequencySurchargeAmount, currencyCode: 'EUR', ruleSource: surchargeRule.ruleSource, ruleVersion: surchargeRule.ruleVersion },
      { componentType: 'TAX', componentCode: 'COUNTRY_TAX', calculationSequence: 5, calculationBasisAmount: premiumAfterCoreRules, rateOrFactor: taxRule.taxRate, fixedAmount: null, signedAmount: taxAmount, currencyCode: 'EUR', ruleSource: taxRule.ruleSource, ruleVersion: taxRule.ruleVersion },
      { componentType: 'COUNTRY_ADJUSTMENT', componentCode: 'COUNTRY_ADJUSTMENT', calculationSequence: 6, calculationBasisAmount: premiumAfterCoreRules, rateOrFactor: countryAdjustment.rateOrFactor, fixedAmount: countryAdjustment.fixedAmount, signedAmount: countryAdjustment.amount, currencyCode: 'EUR', ruleSource: countryAdjustment.ruleSource, ruleVersion: countryAdjustment.ruleVersion }
    ]
  };
}

async function resolveCountryAdjustment(payload, premiumAfterCoreRules) {
  const rules = await rulesRepo.getCountryAdjustmentRules(payload.country, payload.policyType, payload.paymentFrequency);
  let total = 0;
  let appliedRate = null;
  let fixedAmount = 0;
  let ruleSource = null;
  let ruleVersion = null;

  for (const rule of rules) {
    let value = 0;
    if (rule.adjustmentType === 'PERCENTAGE') {
      value = round2(premiumAfterCoreRules * Number(rule.percentageRate));
      appliedRate = Number(rule.percentageRate);
    }
    if (rule.adjustmentType === 'FIXED') {
      value = round2(Number(rule.fixedAmount));
      fixedAmount = round2(fixedAmount + Number(rule.fixedAmount));
    }
    total = round2(total + value);
    ruleSource = rule.ruleSource;
    ruleVersion = rule.ruleVersion;
  }

  return {
    amount: total,
    rateOrFactor: appliedRate,
    fixedAmount,
    ruleSource,
    ruleVersion
  };
}

module.exports = {
  calculate
};
