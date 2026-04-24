create extension if not exists pgcrypto;

create table if not exists quote_header (
  quote_id uuid primary key default gen_random_uuid(),
  customer_id varchar(100) not null,
  country_code varchar(2) not null,
  policy_type varchar(50) not null,
  coverage_amount numeric(18,2) not null,
  customer_segment varchar(50) not null,
  payment_frequency varchar(20) not null,
  consent_status varchar(20) not null,
  eligibility_outcome varchar(30) not null,
  pricing_baseline_version varchar(100) not null,
  base_premium numeric(18,2) not null,
  risk_loading_amount numeric(18,2) not null,
  risk_factor_applied numeric(18,6),
  discount_amount numeric(18,2) not null,
  tax_amount numeric(18,2) not null,
  tax_rate_applied numeric(18,6),
  country_adjustment_amount numeric(18,2) not null,
  country_adjustment_source varchar(100),
  final_premium numeric(18,2) not null,
  underwriting_case_id uuid,
  processing_status varchar(40) not null,
  quote_outcome_status varchar(30) not null,
  correlation_id varchar(100) not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists quote_context (
  quote_context_id uuid primary key default gen_random_uuid(),
  quote_id uuid not null references quote_header(quote_id) on delete cascade,
  age integer not null,
  country_code varchar(2) not null,
  policy_type varchar(50) not null,
  customer_segment varchar(50) not null,
  payment_frequency varchar(20) not null,
  coverage_amount numeric(18,2) not null,
  policy_definition_id uuid not null,
  payment_frequency_definition_id uuid not null,
  eligibility_rule_version varchar(100),
  pricing_rule_version varchar(100),
  tax_rule_version varchar(100),
  country_adjustment_amount numeric(18,2),
  country_adjustment_source varchar(100),
  country_adjustment_rule_version varchar(100),
  request_payload_hash varchar(128) not null,
  decision_snapshot_json jsonb not null,
  created_at timestamptz not null default now()
);

create table if not exists quote_charge (
  quote_charge_id uuid primary key default gen_random_uuid(),
  quote_id uuid not null references quote_header(quote_id) on delete cascade,
  charge_type varchar(50) not null,
  charge_sequence integer not null,
  charge_amount numeric(18,2) not null,
  charge_currency varchar(3) not null,
  calculation_basis varchar(100),
  rate_or_factor_applied numeric(18,6),
  source_attribution varchar(100) not null,
  rule_version varchar(100),
  tax_rate_if_applicable numeric(18,6),
  is_material_component boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists consent_event (
  consent_event_id uuid primary key default gen_random_uuid(),
  customer_id varchar(100) not null,
  quote_id uuid references quote_header(quote_id) on delete set null,
  country_code varchar(2) not null,
  consent_status varchar(20) not null,
  consent_notice_version varchar(100) not null,
  business_outcome varchar(50) not null,
  captured_at timestamptz not null,
  captured_by_channel varchar(50) not null,
  correlation_id varchar(100) not null,
  retention_classification varchar(100) not null
);

create table if not exists underwriting_case (
  underwriting_case_id uuid primary key default gen_random_uuid(),
  quote_id uuid not null unique references quote_header(quote_id) on delete cascade,
  customer_id varchar(100) not null,
  country_code varchar(2) not null,
  workflow_status varchar(50) not null,
  workflow_status_reason varchar(100),
  routing_rule_version varchar(100),
  case_status varchar(30) not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists audit_event (
  audit_event_id uuid primary key default gen_random_uuid(),
  quote_id uuid references quote_header(quote_id) on delete cascade,
  customer_id varchar(100) not null,
  event_type varchar(50) not null,
  event_category varchar(50) not null,
  business_message text not null,
  event_payload_json jsonb,
  processing_state varchar(40) not null,
  correlation_id varchar(100) not null,
  created_at timestamptz not null default now()
);

create table if not exists policy_definition (
  policy_definition_id uuid primary key default gen_random_uuid(),
  country_code varchar(2) not null,
  policy_type varchar(50) not null,
  active_flag boolean not null,
  effective_from timestamptz not null,
  effective_to timestamptz,
  minimum_coverage_amount numeric(18,2) not null,
  maximum_coverage_amount numeric(18,2) not null,
  eligibility_constraints_json jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists payment_frequency_definition (
  payment_frequency_definition_id uuid primary key default gen_random_uuid(),
  frequency_code varchar(20) not null unique,
  active_flag boolean not null,
  effective_from timestamptz not null,
  effective_to timestamptz,
  surcharge_percentage numeric(18,6),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists country_pricing_rule (
  country_pricing_rule_id uuid primary key default gen_random_uuid(),
  country_code varchar(2) not null,
  policy_type varchar(50),
  rule_area varchar(50) not null,
  adjustment_type varchar(30),
  adjustment_value numeric(18,6),
  fallback_value numeric(18,6),
  precedence_mode varchar(30),
  active_flag boolean not null,
  effective_from timestamptz not null,
  effective_to timestamptz,
  approval_reference varchar(100),
  rule_version varchar(100) not null
);

create table if not exists country_tax_rule (
  country_tax_rule_id uuid primary key default gen_random_uuid(),
  country_code varchar(2) not null,
  policy_type varchar(50),
  tax_rate numeric(18,6) not null,
  tax_basis varchar(100) not null,
  active_flag boolean not null,
  effective_from timestamptz not null,
  effective_to timestamptz,
  approval_reference varchar(100),
  rule_version varchar(100) not null
);

create table if not exists migration_reconciliation_extract (
  extract_id uuid primary key default gen_random_uuid(),
  generated_at timestamptz not null default now(),
  from_datetime timestamptz not null,
  to_datetime timestamptz not null,
  country_code varchar(2),
  extract_status varchar(30) not null,
  storage_location text,
  generated_by varchar(100) not null
);

create index if not exists idx_quote_header_country_created on quote_header(country_code, created_at);
create index if not exists idx_quote_header_processing_status on quote_header(processing_status);
create index if not exists idx_quote_charge_quote_id on quote_charge(quote_id);
create index if not exists idx_audit_event_quote_id on audit_event(quote_id);
create index if not exists idx_consent_event_customer on consent_event(customer_id, captured_at);
create index if not exists idx_policy_definition_lookup on policy_definition(country_code, policy_type, active_flag, effective_from);
create index if not exists idx_payment_frequency_definition_lookup on payment_frequency_definition(frequency_code, active_flag, effective_from);
create index if not exists idx_country_pricing_rule_lookup on country_pricing_rule(country_code, rule_area, active_flag, effective_from);
create index if not exists idx_country_tax_rule_lookup on country_tax_rule(country_code, policy_type, active_flag, effective_from);
