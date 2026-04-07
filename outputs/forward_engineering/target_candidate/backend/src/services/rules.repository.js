const db = require('./db');

async function getSupportedCountries() {
  const result = await db.query('select country_code from reference_country where supported_indicator = true and now() between effective_from and coalesce(effective_to, now()) order by country_code');
  return result.rows.map(r => r.country_code);
}

async function getTaxRule(country, policyType) {
  const result = await db.query(
    `select tax_rate, rule_source, rule_version
     from tax_rule
     where country_code = $1 and (policy_type = $2 or policy_type is null)
       and now() between effective_from and coalesce(effective_to, now())
     order by priority asc, case when policy_type = $2 then 0 else 1 end asc
     limit 1`,
    [country, policyType]
  );
  return result.rows[0];
}

async function getCountryAdjustmentRules(country, policyType, paymentFrequency) {
  const result = await db.query(
    `select adjustment_type, percentage_rate, fixed_amount, rule_source, rule_version
     from country_adjustment_rule
     where country_code = $1
       and (policy_type = $2 or policy_type is null)
       and (payment_frequency = $3 or payment_frequency is null)
       and now() between effective_from and coalesce(effective_to, now())
     order by priority asc`,
    [country, policyType, paymentFrequency]
  );
  return result.rows;
}

async function getPaymentFrequencyRule(paymentFrequency) {
  const result = await db.query(
    `select surcharge_percent, rule_version, 'REFERENCE_PAYMENT_FREQUENCY' as rule_source,
            case when surcharge_percent is not null then true else false end as enabled
     from reference_payment_frequency
     where payment_frequency_code = $1
       and now() between effective_from and coalesce(effective_to, now())`,
    [paymentFrequency]
  );
  return result.rows[0];
}

async function getRiskModel() {
  return { riskFactor: 1.00, ruleSource: 'CONFIG', ruleVersion: 'RISK_MODEL_V1' };
}

async function getConsentRequirement(country) {
  const result = await db.query(
    `select true as required_indicator
     from reference_country
     where country_code = $1 and supported_indicator = true
     limit 1`,
    [country]
  );
  return result.rows[0] || { requiredIndicator: true };
}

async function getConsentRequirements(country) {
  if (!country) {
    const result = await db.query(`select country_code, true as required_indicator from reference_country where supported_indicator = true`);
    const map = {};
    for (const row of result.rows) {
      map[row.country_code] = { requiredIndicator: row.required_indicator };
    }
    return map;
  }
  const single = await getConsentRequirement(country);
  return { [country]: { requiredIndicator: single.required_indicator ?? single.requiredIndicator } };
}

async function getCountryDefaults(country) {
  if (!country) {
    const result = await db.query('select country_code, default_policy_type from reference_country where supported_indicator = true');
    const map = {};
    result.rows.forEach(r => map[r.country_code] = { defaultPolicyType: r.default_policy_type });
    return map;
  }
  const result = await db.query('select country_code, default_policy_type from reference_country where country_code = $1', [country]);
  const row = result.rows[0];
  return row ? { [row.country_code]: { defaultPolicyType: row.default_policy_type } } : {};
}

async function getUnderwritingStatusMapping(country) {
  const result = await db.query(
    `select target_status, mapping_version
     from underwriting_status_mapping
     where country_code = $1
       and now() between effective_from and coalesce(effective_to, now())
     order by mapping_version desc
     limit 1`,
    [country]
  );
  return result.rows[0];
}

module.exports = {
  getSupportedCountries,
  getTaxRule,
  getCountryAdjustmentRules,
  getPaymentFrequencyRule,
  getRiskModel,
  getConsentRequirement,
  getConsentRequirements,
  getCountryDefaults,
  getUnderwritingStatusMapping
};
