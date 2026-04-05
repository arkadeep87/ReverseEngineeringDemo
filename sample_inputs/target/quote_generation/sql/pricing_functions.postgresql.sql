create or replace function fn_calculate_risk_factor(
    p_age integer,
    p_policy_type text,
    p_coverage_amount numeric
)
returns table (risk_factor numeric)
language sql
as $$
    select
        1.0000
        + case when p_age between 18 and 24 then 0.0400 else 0 end
        + case when p_age >= 50 then 0.0500 else 0 end
        + case when p_age >= 65 then 0.0300 else 0 end
        + case when p_policy_type = 'CORPORATE' then 0.0800 else 0 end
        + case when p_policy_type = 'TRAVEL' and p_coverage_amount > 250000 then 0.0300 else 0 end;
$$;

create or replace function fn_calculate_discount(
    p_customer_segment text,
    p_policy_type text,
    p_payment_frequency text,
    p_base_premium numeric
)
returns table (discount_amount numeric)
language sql
as $$
    select round(
        p_base_premium * least(
            (case when p_customer_segment = 'LOYALTY_GOLD' then 0.07 else 0 end)
          + (case when p_customer_segment = 'EMPLOYEE' then 0.10 else 0 end)
          + (case when p_policy_type = 'FAMILY' then 0.05 else 0 end)
          + (case when p_payment_frequency = 'ANNUAL' then 0.02 else 0 end),
            0.15
        ),
        2
    );
$$;

create or replace function fn_lookup_country_tax(
    p_country_code text,
    p_policy_type text,
    p_premium_amount numeric
)
returns table (tax_amount numeric)
language sql
as $$
    select round(
        p_premium_amount *
        case
            when p_country_code = 'ES' and p_policy_type = 'TRAVEL' then 0.135
            when p_country_code = 'ES' then 0.080
            else 0
        end,
        2
    );
$$;

create or replace function fn_apply_spain_adjustment(
    p_policy_type text,
    p_payment_frequency text,
    p_premium_amount numeric
)
returns table (adjustment_amount numeric)
language sql
as $$
    select round(
        (p_premium_amount * 0.018)
        + case when p_policy_type = 'TRAVEL' then 9.50 else 0 end,
        2
    );
$$;
