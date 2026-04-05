CREATE PROCEDURE sp_save_quote_header
    @customer_id      VARCHAR(30),
    @country_code     VARCHAR(2),
    @policy_type      VARCHAR(20),
    @coverage_amount  NUMERIC(12,2),
    @base_premium     NUMERIC(12,2),
    @final_premium    NUMERIC(12,2)
AS
BEGIN
    DECLARE @quote_id INT
    SELECT @quote_id = ABS(CHECKSUM(@customer_id, @country_code, @policy_type, GETDATE()))

    INSERT INTO quote_header (
        quote_id, customer_id, country_code, policy_type,
        coverage_amount, base_premium, final_premium, created_at
    )
    VALUES (
        @quote_id, @customer_id, @country_code, @policy_type,
        @coverage_amount, @base_premium, @final_premium, GETDATE()
    )

    IF NOT EXISTS (SELECT 1 FROM quote_context WHERE quote_id = @quote_id)
    BEGIN
        INSERT INTO quote_context (
            quote_id, customer_age, country_code, policy_type,
            customer_segment, payment_frequency, coverage_amount,
            base_premium, final_premium, discount_amount, tax_amount,
            risk_factor, consent_granted, last_updated
        )
        VALUES (
            @quote_id, 0, @country_code, @policy_type,
            'STANDARD', 'ANNUAL', @coverage_amount,
            @base_premium, @final_premium, 0, 0,
            1.0000, 'N', GETDATE()
        )
    END

    SELECT @quote_id AS quote_id
END
go

CREATE PROCEDURE sp_save_quote_line_item
    @quote_id       INT,
    @charge_code    VARCHAR(40),
    @amount         NUMERIC(12,2),
    @source_table   VARCHAR(40)
AS
BEGIN
    DECLARE @line_no INT
    SELECT @line_no = ISNULL(MAX(line_no), 0) + 1
      FROM quote_line_item
     WHERE quote_id = @quote_id

    INSERT INTO quote_line_item (quote_id, line_no, charge_code, amount, source_table)
    VALUES (@quote_id, @line_no, @charge_code, @amount, @source_table)
END
go

CREATE PROCEDURE sp_apply_country_adjustments
    @country_code     VARCHAR(2),
    @policy_type      VARCHAR(20),
    @payment_frequency VARCHAR(10),
    @premium_amount   NUMERIC(12,2),
    @adjustment_amount NUMERIC(12,2) OUTPUT
AS
BEGIN
    SELECT @adjustment_amount = 0

    IF @country_code = 'DE'
    BEGIN
        SELECT @adjustment_amount = ROUND(@premium_amount * 0.032, 2)
        IF @policy_type = 'HEALTH'
            SELECT @adjustment_amount = @adjustment_amount + ROUND(@premium_amount * 0.014, 2)
    END
    ELSE IF @country_code = 'IT'
    BEGIN
        SELECT @adjustment_amount = 22
        IF @policy_type = 'FAMILY'
            SELECT @adjustment_amount = @adjustment_amount - 12
    END
    ELSE IF @country_code = 'ES'
    BEGIN
        SELECT @adjustment_amount = ROUND(@premium_amount * 0.018, 2)
        IF @policy_type = 'TRAVEL'
            SELECT @adjustment_amount = @adjustment_amount + 9.50
    END
    ELSE IF @country_code = 'PT'
    BEGIN
        SELECT @adjustment_amount = ROUND(@premium_amount * 0.012, 2)
        IF @payment_frequency = 'ANNUAL'
            SELECT @adjustment_amount = @adjustment_amount - 7.50
    END
    ELSE IF @country_code = 'CH'
    BEGIN
        SELECT @adjustment_amount = ROUND(@premium_amount * 0.021, 2)
        IF @policy_type = 'CORPORATE'
            SELECT @adjustment_amount = @adjustment_amount + 35
    END
    ELSE IF @country_code = 'GB'
    BEGIN
        SELECT @adjustment_amount = ROUND(@premium_amount * 0.12, 2)
        IF @policy_type = 'TRAVEL'
            SELECT @adjustment_amount = @adjustment_amount + 6
    END
END
go

CREATE PROCEDURE sp_save_underwriting_case
    @quote_id      INT,
    @customer_id   VARCHAR(30),
    @country_code  VARCHAR(2)
AS
BEGIN
    DECLARE @case_status VARCHAR(20)
    SELECT @case_status = 'PENDING_REVIEW'

    IF @country_code IN ('DE', 'IT', 'ES', 'PT')
        SELECT @case_status = 'EU_COMPLIANCE'

    IF @country_code = 'CH'
        SELECT @case_status = 'CANTON_CHECK'

    IF @country_code = 'GB'
        SELECT @case_status = 'IPT_REVIEW'

    INSERT INTO underwriting_case (
        underwriting_case_id, quote_id, customer_id,
        country_code, case_status, created_at
    )
    VALUES (
        ABS(CHECKSUM(@quote_id, @customer_id, GETDATE())),
        @quote_id,
        @customer_id,
        @country_code,
        @case_status,
        GETDATE()
    )
END
go
