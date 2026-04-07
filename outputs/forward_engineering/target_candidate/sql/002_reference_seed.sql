insert into reference_country (country_code, country_name, supported_indicator, default_policy_type, effective_from, effective_to) values
('DE', 'Germany', true, null, now(), null),
('IT', 'Italy', true, null, now(), null),
('ES', 'Spain', true, null, now(), null),
('PT', 'Portugal', true, null, now(), null),
('CH', 'Switzerland', true, null, now(), null),
('GB', 'United Kingdom', true, null, now(), null)
on conflict (country_code) do nothing;

insert into reference_payment_frequency (payment_frequency_code, description, surcharge_percent, effective_from, effective_to, rule_version) values
('MONTHLY', 'Monthly', 0.015000, now(), null, 'PAYMENT_FREQUENCY_V1'),
('QUARTERLY', 'Quarterly', 0.008000, now(), null, 'PAYMENT_FREQUENCY_V1'),
('ANNUAL', 'Annual', 0.000000, now(), null, 'PAYMENT_FREQUENCY_V1')
on conflict (payment_frequency_code) do nothing;

insert into tax_rule (country_code, policy_type, tax_rate, calculation_basis, priority, rule_source, fallback_allowed, effective_from, effective_to, rule_version) values
('DE', 'HEALTH', 0.210000, 'PREMIUM_AFTER_CORE_RULES', 1, 'TAX_CATALOG', false, now(), null, 'DE_TAX_V1'),
('DE', null, 0.190000, 'PREMIUM_AFTER_CORE_RULES', 2, 'TAX_CATALOG', false, now(), null, 'DE_TAX_V1'),
('IT', 'FAMILY', 0.110000, 'PREMIUM_AFTER_CORE_RULES', 1, 'TAX_CATALOG', false, now(), null, 'IT_TAX_V1'),
('IT', null, 0.090000, 'PREMIUM_AFTER_CORE_RULES', 2, 'TAX_CATALOG', false, now(), null, 'IT_TAX_V1'),
('ES', 'TRAVEL', 0.135000, 'PREMIUM_AFTER_CORE_RULES', 1, 'TAX_CATALOG', false, now(), null, 'ES_TAX_V1'),
('ES', null, 0.080000, 'PREMIUM_AFTER_CORE_RULES', 2, 'TAX_CATALOG', false, now(), null, 'ES_TAX_V1'),
('PT', 'FAMILY', 0.095000, 'PREMIUM_AFTER_CORE_RULES', 1, 'TAX_CATALOG', false, now(), null, 'PT_TAX_V1'),
('PT', null, 0.075000, 'PREMIUM_AFTER_CORE_RULES', 2, 'TAX_CATALOG', false, now(), null, 'PT_TAX_V1'),
('CH', 'CORPORATE', 0.065000, 'PREMIUM_AFTER_CORE_RULES', 1, 'TAX_CATALOG', false, now(), null, 'CH_TAX_V1'),
('CH', null, 0.050000, 'PREMIUM_AFTER_CORE_RULES', 2, 'TAX_CATALOG', false, now(), null, 'CH_TAX_V1'),
('GB', 'TRAVEL', 0.120000, 'PREMIUM_AFTER_CORE_RULES', 1, 'TAX_CATALOG', false, now(), null, 'GB_TAX_V1'),
('GB', null, 0.060000, 'PREMIUM_AFTER_CORE_RULES', 2, 'TAX_CATALOG', false, now(), null, 'GB_TAX_V1');

insert into country_adjustment_rule (country_code, policy_type, payment_frequency, adjustment_type, percentage_rate, fixed_amount, sequence_stage, priority, rule_source, fallback_allowed, effective_from, effective_to, rule_version) values
('DE', null, null, 'PERCENTAGE', 0.032000, null, 'AFTER_CORE_RULES', 1, 'COUNTRY_ADJUSTMENT_CATALOG', false, now(), null, 'DE_ADJ_V1'),
('DE', 'HEALTH', null, 'PERCENTAGE', 0.014000, null, 'AFTER_CORE_RULES', 2, 'COUNTRY_ADJUSTMENT_CATALOG', false, now(), null, 'DE_ADJ_V1'),
('IT', null, null, 'FIXED', null, 22.00, 'AFTER_CORE_RULES', 1, 'COUNTRY_ADJUSTMENT_CATALOG', false, now(), null, 'IT_ADJ_V1'),
('IT', 'FAMILY', null, 'FIXED', null, -12.00, 'AFTER_CORE_RULES', 2, 'COUNTRY_ADJUSTMENT_CATALOG', false, now(), null, 'IT_ADJ_V1'),
('ES', null, null, 'PERCENTAGE', 0.018000, null, 'AFTER_CORE_RULES', 1, 'COUNTRY_ADJUSTMENT_CATALOG', false, now(), null, 'ES_ADJ_V1'),
('ES', 'TRAVEL', null, 'FIXED', null, 9.50, 'AFTER_CORE_RULES', 2, 'COUNTRY_ADJUSTMENT_CATALOG', false, now(), null, 'ES_ADJ_V1'),
('PT', null, null, 'PERCENTAGE', 0.012000, null, 'AFTER_CORE_RULES', 1, 'COUNTRY_ADJUSTMENT_CATALOG', false, now(), null, 'PT_ADJ_V1'),
('PT', null, 'ANNUAL', 'FIXED', null, -7.50, 'AFTER_CORE_RULES', 2, 'COUNTRY_ADJUSTMENT_CATALOG', false, now(), null, 'PT_ADJ_V1'),
('CH', null, null, 'PERCENTAGE', 0.021000, null, 'AFTER_CORE_RULES', 1, 'COUNTRY_ADJUSTMENT_CATALOG', false, now(), null, 'CH_ADJ_V1'),
('CH', 'CORPORATE', null, 'FIXED', null, 35.00, 'AFTER_CORE_RULES', 2, 'COUNTRY_ADJUSTMENT_CATALOG', false, now(), null, 'CH_ADJ_V1'),
('GB', null, null, 'PERCENTAGE', 0.120000, null, 'AFTER_CORE_RULES', 1, 'COUNTRY_ADJUSTMENT_CATALOG', false, now(), null, 'GB_ADJ_V1'),
('GB', 'TRAVEL', null, 'FIXED', null, 6.00, 'AFTER_CORE_RULES', 2, 'COUNTRY_ADJUSTMENT_CATALOG', false, now(), null, 'GB_ADJ_V1');

insert into underwriting_status_mapping (country_code, legacy_status, target_status, operational_meaning, effective_from, effective_to, mapping_version) values
('DE', 'EU_COMPLIANCE', 'EU_COMPLIANCE', 'Germany underwriting compliance review', now(), null, 'UW_MAP_V1'),
('IT', 'EU_COMPLIANCE', 'EU_COMPLIANCE', 'Italy underwriting compliance review', now(), null, 'UW_MAP_V1'),
('ES', 'EU_COMPLIANCE', 'SPAIN_STANDARD_REVIEW', 'Spain approved operational equivalent', now(), null, 'UW_MAP_V1'),
('PT', 'EU_COMPLIANCE', 'EU_COMPLIANCE', 'Portugal underwriting compliance review', now(), null, 'UW_MAP_V1'),
('CH', 'CANTON_CHECK', 'CANTON_CHECK', 'Switzerland canton review', now(), null, 'UW_MAP_V1'),
('GB', 'IPT_REVIEW', 'IPT_REVIEW', 'United Kingdom IPT review', now(), null, 'UW_MAP_V1');
