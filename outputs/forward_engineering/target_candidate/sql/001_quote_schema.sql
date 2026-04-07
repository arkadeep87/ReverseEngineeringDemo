create extension if not exists pgcrypto;

create table if not exists quote_context (
  quote_context_id uuid primary key default gen_random_uuid(),
  draft_quote_id uuid not null unique default gen_random_uuid(),
  customer_id varchar(100) not null,
  age integer not null,
  country varchar(2) not null,
  policy_type varchar(50) not null,
  coverage_amount numeric(18,2) not null,
  payment_frequency varchar(20) not null,
  customer_segment varchar(50) not null,
  consent_indicator boolean not null,
  defaulted_values_json jsonb,
  validation_state varchar(50),
  calculation_context_json jsonb,
  processing_stage varchar(50),
  final_premium numeric(18,2),
  created_timestamp timestamptz not null default now(),
  updated_timestamp timestamptz not null default now()
);

create table if not exists quote (
  quote_id uuid primary key default gen_random_uuid(),
  draft_quote_id uuid not null,
  quote_context_id uuid not null references quote_context(quote_context_id),
  customer_id varchar(100) not null,
  country varchar(2) not null,
  policy_type varchar(50) not null,
  coverage_amount numeric(18,2) not null,
  payment_frequency varchar(20) not null,
  customer_segment varchar(50) not null,
  consent_indicator boolean not null,
  eligibility_status varchar(20),
  eligibility_reason varchar(500),
  base_premium numeric(18,2),
  risk_factor numeric(18,6),
  discount_amount numeric(18,2),
  tax_amount numeric(18,2),
  payment_frequency_surcharge_amount numeric(18,2),
  country_adjustment_amount numeric(18,2),
  final_premium numeric(18,2),
  pricing_rule_version_set jsonb,
  tax_rule_version varchar(100),
  country_adjustment_rule_version varchar(100),
  underwriting_case_id uuid,
  status varchar(20) not null,
  created_timestamp timestamptz not null default now(),
  updated_timestamp timestamptz not null default now()
);

create table if not exists quote_financial_breakdown (
  breakdown_id uuid primary key default gen_random_uuid(),
  quote_id uuid not null references quote(quote_id),
  component_type varchar(50) not null,
  component_code varchar(100) not null,
  calculation_sequence integer not null,
  calculation_basis_amount numeric(18,2),
  rate_or_factor numeric(18,6),
  fixed_amount numeric(18,2),
  signed_amount numeric(18,2) not null,
  currency_code varchar(3) not null,
  rule_source varchar(100),
  rule_version varchar(100),
  created_timestamp timestamptz not null default now()
);

create table if not exists consent_record (
  consent_record_id uuid primary key default gen_random_uuid(),
  customer_id varchar(100) not null,
  quote_context_id uuid references quote_context(quote_context_id),
  quote_id uuid references quote(quote_id),
  country varchar(2) not null,
  consent_type varchar(50) not null,
  required_indicator boolean not null,
  provided_indicator boolean not null,
  outcome varchar(20) not null,
  rejection_reason varchar(500),
  captured_timestamp timestamptz not null default now()
);

create table if not exists eligibility_decision (
  eligibility_decision_id uuid primary key default gen_random_uuid(),
  quote_context_id uuid not null references quote_context(quote_context_id),
  quote_id uuid references quote(quote_id),
  customer_id varchar(100) not null,
  country varchar(2) not null,
  policy_type varchar(50) not null,
  coverage_amount numeric(18,2) not null,
  age integer not null,
  outcome varchar(20) not null,
  reject_reason_code varchar(100),
  reject_reason_message varchar(500),
  evaluated_timestamp timestamptz not null default now()
);

create table if not exists underwriting_case (
  underwriting_case_id uuid primary key default gen_random_uuid(),
  quote_id uuid not null references quote(quote_id),
  customer_id varchar(100) not null,
  country varchar(2) not null,
  status varchar(50) not null,
  status_mapping_source varchar(100),
  created_timestamp timestamptz not null default now()
);

create table if not exists reference_country (
  country_code varchar(2) primary key,
  country_name varchar(100) not null,
  supported_indicator boolean not null,
  default_policy_type varchar(50),
  effective_from timestamptz not null,
  effective_to timestamptz
);

create table if not exists reference_product_rule (
  product_rule_id uuid primary key default gen_random_uuid(),
  policy_type varchar(50) not null,
  min_coverage_amount numeric(18,2),
  max_coverage_amount numeric(18,2),
  age_min integer,
  age_max integer,
  effective_from timestamptz not null,
  effective_to timestamptz,
  rule_version varchar(100) not null
);

create table if not exists reference_payment_frequency (
  payment_frequency_code varchar(20) primary key,
  description varchar(100) not null,
  surcharge_percent numeric(18,6),
  effective_from timestamptz not null,
  effective_to timestamptz,
  rule_version varchar(100) not null
);

create table if not exists tax_rule (
  tax_rule_id uuid primary key default gen_random_uuid(),
  country_code varchar(2) not null references reference_country(country_code),
  policy_type varchar(50),
  tax_rate numeric(18,6) not null,
  calculation_basis varchar(100) not null,
  priority integer not null,
  rule_source varchar(100) not null,
  fallback_allowed boolean not null,
  effective_from timestamptz not null,
  effective_to timestamptz,
  rule_version varchar(100) not null
);

create table if not exists country_adjustment_rule (
  country_adjustment_rule_id uuid primary key default gen_random_uuid(),
  country_code varchar(2) not null references reference_country(country_code),
  policy_type varchar(50),
  payment_frequency varchar(20),
  adjustment_type varchar(20) not null,
  percentage_rate numeric(18,6),
  fixed_amount numeric(18,2),
  sequence_stage varchar(50) not null,
  priority integer not null,
  rule_source varchar(100) not null,
  fallback_allowed boolean not null,
  effective_from timestamptz not null,
  effective_to timestamptz,
  rule_version varchar(100) not null
);

create table if not exists underwriting_status_mapping (
  mapping_id uuid primary key default gen_random_uuid(),
  country_code varchar(2) not null references reference_country(country_code),
  legacy_status varchar(50) not null,
  target_status varchar(50) not null,
  operational_meaning varchar(200),
  effective_from timestamptz not null,
  effective_to timestamptz,
  mapping_version varchar(100) not null
);

create table if not exists audit_event (
  audit_event_id uuid primary key default gen_random_uuid(),
  quote_context_id uuid references quote_context(quote_context_id),
  quote_id uuid references quote(quote_id),
  customer_id varchar(100) not null,
  country varchar(2) not null,
  event_type varchar(100) not null,
  event_outcome varchar(50) not null,
  reason_code varchar(100),
  reason_message varchar(500),
  rule_source varchar(200),
  rule_version varchar(100),
  event_payload_json jsonb,
  created_timestamp timestamptz not null default now()
);
