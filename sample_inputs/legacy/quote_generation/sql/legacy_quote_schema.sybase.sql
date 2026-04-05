CREATE TABLE customer_profile (
    customer_id                  VARCHAR(30)   NOT NULL,
    full_name                    VARCHAR(120)  NOT NULL,
    segment_code                 VARCHAR(20)   NOT NULL,
    country_code                 VARCHAR(2)    NOT NULL,
    preferred_payment_frequency  VARCHAR(10)   NOT NULL,
    open_underwriting_case       BIT           NOT NULL DEFAULT 0
)
go

CREATE TABLE policy_catalog (
    policy_type      VARCHAR(20)   NOT NULL,
    base_rate        NUMERIC(9,4)  NOT NULL,
    minimum_cover    NUMERIC(12,2) NOT NULL,
    maximum_cover    NUMERIC(12,2) NOT NULL,
    active_flag      CHAR(1)       NOT NULL
)
go

CREATE TABLE payment_schedule (
    schedule_code    VARCHAR(10)   NOT NULL,
    collection_days  INT           NOT NULL,
    surcharge_pct    NUMERIC(9,4)  NOT NULL,
    active_flag      CHAR(1)       NOT NULL
)
go

CREATE TABLE quote_header (
    quote_id          INT            NOT NULL,
    customer_id       VARCHAR(30)    NOT NULL,
    country_code      VARCHAR(2)     NOT NULL,
    policy_type       VARCHAR(20)    NOT NULL,
    coverage_amount   NUMERIC(12,2)  NOT NULL,
    base_premium      NUMERIC(12,2)  NOT NULL,
    final_premium     NUMERIC(12,2)  NOT NULL,
    created_at        DATETIME       NOT NULL
)
go

CREATE TABLE quote_line_item (
    quote_id       INT            NOT NULL,
    line_no        INT            NOT NULL,
    charge_code    VARCHAR(40)    NOT NULL,
    amount         NUMERIC(12,2)  NOT NULL,
    source_table   VARCHAR(40)    NOT NULL
)
go

CREATE TABLE underwriting_case (
    underwriting_case_id  INT          NOT NULL,
    quote_id              INT          NOT NULL,
    customer_id           VARCHAR(30)  NOT NULL,
    country_code          VARCHAR(2)   NOT NULL,
    case_status           VARCHAR(20)  NOT NULL,
    created_at            DATETIME     NOT NULL
)
go

CREATE TABLE audit_event (
    audit_event_id   INT            IDENTITY,
    quote_id         INT            NOT NULL,
    event_type       VARCHAR(40)    NOT NULL,
    event_message    VARCHAR(255)   NOT NULL,
    created_at       DATETIME       NOT NULL
)
go

INSERT INTO policy_catalog VALUES ('HEALTH', 4.2500, 10000, 750000, 'Y')
INSERT INTO policy_catalog VALUES ('TRAVEL', 3.6000, 5000, 1000000, 'Y')
INSERT INTO policy_catalog VALUES ('FAMILY', 4.9000, 15000, 900000, 'Y')
INSERT INTO policy_catalog VALUES ('CORPORATE', 6.3000, 50000, 2500000, 'Y')
go

INSERT INTO payment_schedule VALUES ('MONTHLY', 30, 0.0150, 'Y')
INSERT INTO payment_schedule VALUES ('QUARTERLY', 90, 0.0080, 'Y')
INSERT INTO payment_schedule VALUES ('ANNUAL', 365, 0.0000, 'Y')
go
