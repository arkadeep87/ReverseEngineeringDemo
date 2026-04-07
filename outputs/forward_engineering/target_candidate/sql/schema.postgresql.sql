create table customer_profile (
    customer_id text primary key,
    full_name text not null,
    segment_code text not null,
    country_code text not null
);

create table product_catalog (
    policy_type text primary key,
    base_rate numeric(9,4) not null,
    minimum_cover numeric(12,2) not null,
    maximum_cover numeric(12,2) not null
);

create table payment_plan (
    payment_frequency text primary key,
    surcharge_pct numeric(9,4) not null
);

create table quote_consent (
    quote_consent_id bigserial primary key,
    customer_id text not null,
    country_code text not null,
    consent_type text not null,
    granted boolean not null,
    created_at timestamp not null default current_timestamp
);

create table quotes (
    quote_id uuid primary key,
    customer_id text not null,
    policy_type text not null,
    country_code text not null,
    base_premium numeric(12,2) not null,
    coverage_amount numeric(12,2) not null,
    customer_segment text not null,
    payment_frequency text not null,
    risk_factor numeric(10,4) not null,
    discount_amount numeric(12,2) not null,
    tax_amount numeric(12,2) not null,
    final_premium numeric(12,2) not null,
    gdpr_consent_granted boolean not null,
    created_at timestamp not null default current_timestamp
);

create table quote_context (
    quote_id uuid primary key,
    customer_age integer not null,
    country_code text not null,
    policy_type text not null,
    customer_segment text not null,
    payment_frequency text not null,
    coverage_amount numeric(12,2) not null,
    final_premium numeric(12,2) not null,
    country_adjustment_amount numeric(12,2) not null,
    last_updated timestamp not null default current_timestamp
);

create table quote_charge (
    quote_charge_id bigserial primary key,
    quote_id uuid not null,
    charge_code text not null,
    amount numeric(12,2) not null,
    created_at timestamp not null default current_timestamp
);

create table underwriting_case (
    underwriting_case_id bigserial primary key,
    quote_id uuid not null,
    customer_id text not null,
    country_code text not null,
    case_status text not null,
    created_at timestamp not null default current_timestamp
);

create table audit_log (
    audit_log_id bigserial primary key,
    quote_id uuid not null,
    event_type text not null,
    event_message text not null,
    created_at timestamp not null default current_timestamp
);
