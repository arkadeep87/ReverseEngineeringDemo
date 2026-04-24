insert into payment_frequency_definition (payment_frequency_definition_id, frequency_code, active_flag, effective_from, surcharge_percentage)
values
  (gen_random_uuid(), 'MONTHLY', true, now(), 0),
  (gen_random_uuid(), 'QUARTERLY', true, now(), 0),
  (gen_random_uuid(), 'ANNUAL', true, now(), 0)
on conflict (frequency_code) do nothing;

insert into country_pricing_rule (country_pricing_rule_id, country_code, policy_type, rule_area, adjustment_type, adjustment_value, fallback_value, precedence_mode, active_flag, effective_from, approval_reference, rule_version)
values
  (gen_random_uuid(), 'DE', null, 'COUNTRY_ADJUSTMENT', 'PERCENT', 0.032, null, 'PRIMARY_ONLY', true, now(), 'APPROVED_DE_ADJ', 'DE_ADJ_V1'),
  (gen_random_uuid(), 'DE', 'HEALTH', 'COUNTRY_ADJUSTMENT_ADDITIVE', 'PERCENT', 0.014, null, 'PRIMARY_ONLY', true, now(), 'APPROVED_DE_HEALTH_ADJ', 'DE_ADJ_HEALTH_V1'),
  (gen_random_uuid(), 'IT', null, 'COUNTRY_ADJUSTMENT', 'FIXED', 22, null, 'PRIMARY_ONLY', true, now(), 'APPROVED_IT_ADJ', 'IT_ADJ_V1'),
  (gen_random_uuid(), 'IT', 'FAMILY', 'COUNTRY_ADJUSTMENT_REDUCTION', 'FIXED', -12, null, 'PRIMARY_ONLY', true, now(), 'APPROVED_IT_FAMILY_ADJ', 'IT_ADJ_FAMILY_V1'),
  (gen_random_uuid(), 'PT', null, 'COUNTRY_ADJUSTMENT', 'PERCENT', 0.012, null, 'PRIMARY_ONLY', true, now(), 'APPROVED_PT_ADJ', 'PT_ADJ_V1'),
  (gen_random_uuid(), 'PT', null, 'COUNTRY_ADJUSTMENT_ANNUAL_REDUCTION', 'FIXED', -7.50, null, 'PRIMARY_ONLY', true, now(), 'APPROVED_PT_ANNUAL_ADJ', 'PT_ADJ_ANNUAL_V1'),
  (gen_random_uuid(), 'CH', null, 'COUNTRY_ADJUSTMENT', 'PERCENT', 0.021, null, 'PRIMARY_ONLY', true, now(), 'APPROVED_CH_ADJ', 'CH_ADJ_V1'),
  (gen_random_uuid(), 'CH', 'CORPORATE', 'COUNTRY_ADJUSTMENT_SURCHARGE', 'FIXED', 35, null, 'PRIMARY_ONLY', true, now(), 'APPROVED_CH_CORP_ADJ', 'CH_ADJ_CORP_V1'),
  (gen_random_uuid(), 'GB', null, 'COUNTRY_ADJUSTMENT', 'PERCENT', 0.12, null, 'PRIMARY_ONLY', true, now(), 'APPROVED_GB_ADJ', 'GB_ADJ_V1'),
  (gen_random_uuid(), 'GB', 'TRAVEL', 'COUNTRY_ADJUSTMENT_SURCHARGE', 'FIXED', 6, null, 'PRIMARY_ONLY', true, now(), 'APPROVED_GB_TRAVEL_ADJ', 'GB_ADJ_TRAVEL_V1')
on conflict do nothing;

insert into country_tax_rule (country_tax_rule_id, country_code, policy_type, tax_rate, tax_basis, active_flag, effective_from, approval_reference, rule_version)
values
  (gen_random_uuid(), 'DE', null, 0.19, 'BASE_PLUS_RISK_MINUS_DISCOUNT', true, now(), 'APPROVED_DE_TAX', 'DE_TAX_V1'),
  (gen_random_uuid(), 'DE', 'HEALTH', 0.21, 'BASE_PLUS_RISK_MINUS_DISCOUNT', true, now(), 'APPROVED_DE_HEALTH_TAX', 'DE_TAX_HEALTH_V1'),
  (gen_random_uuid(), 'IT', null, 0.09, 'BASE_PLUS_RISK_MINUS_DISCOUNT', true, now(), 'APPROVED_IT_TAX', 'IT_TAX_V1'),
  (gen_random_uuid(), 'IT', 'FAMILY', 0.11, 'BASE_PLUS_RISK_MINUS_DISCOUNT', true, now(), 'APPROVED_IT_FAMILY_TAX', 'IT_TAX_FAMILY_V1'),
  (gen_random_uuid(), 'PT', null, 0.075, 'BASE_PLUS_RISK_MINUS_DISCOUNT', true, now(), 'APPROVED_PT_TAX', 'PT_TAX_V1'),
  (gen_random_uuid(), 'PT', 'FAMILY', 0.095, 'BASE_PLUS_RISK_MINUS_DISCOUNT', true, now(), 'APPROVED_PT_FAMILY_TAX', 'PT_TAX_FAMILY_V1'),
  (gen_random_uuid(), 'CH', null, 0.05, 'BASE_PLUS_RISK_MINUS_DISCOUNT', true, now(), 'APPROVED_CH_TAX', 'CH_TAX_V1'),
  (gen_random_uuid(), 'CH', 'CORPORATE', 0.065, 'BASE_PLUS_RISK_MINUS_DISCOUNT', true, now(), 'APPROVED_CH_CORP_TAX', 'CH_TAX_CORP_V1'),
  (gen_random_uuid(), 'GB', null, 0.06, 'BASE_PLUS_RISK_MINUS_DISCOUNT', true, now(), 'APPROVED_GB_TAX', 'GB_TAX_V1'),
  (gen_random_uuid(), 'GB', 'TRAVEL', 0.12, 'BASE_PLUS_RISK_MINUS_DISCOUNT', true, now(), 'APPROVED_GB_TRAVEL_TAX', 'GB_TAX_TRAVEL_V1')
on conflict do nothing;
