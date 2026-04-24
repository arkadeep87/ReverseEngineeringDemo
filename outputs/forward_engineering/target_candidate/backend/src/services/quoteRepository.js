class QuoteRepository {
  constructor({ pool }) {
    this.pool = pool;
  }

  async createQuoteHeader(db, input) {
    const client = db || this.pool;
    const result = await client.query(
      `insert into quote_header (
        customer_id, country_code, policy_type, coverage_amount, customer_segment, payment_frequency,
        consent_status, eligibility_outcome, pricing_baseline_version, base_premium, risk_loading_amount,
        risk_factor_applied, discount_amount, tax_amount, tax_rate_applied, country_adjustment_amount,
        country_adjustment_source, final_premium, processing_status, quote_outcome_status, correlation_id
      ) values (
        $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21
      ) returning quote_id`,
      [
        input.customerId,
        input.countryCode,
        input.policyType,
        input.coverageAmount,
        input.customerSegment,
        input.paymentFrequency,
        input.consentStatus,
        input.eligibilityOutcome,
        input.pricingBaselineVersion,
        input.basePremium,
        input.riskLoadingAmount,
        input.riskFactorApplied,
        input.discountAmount,
        input.taxAmount,
        input.taxRateApplied,
        input.countryAdjustmentAmount,
        input.countryAdjustmentSource,
        input.finalPremium,
        input.processingStatus,
        input.quoteOutcomeStatus,
        input.correlationId
      ]
    );
    return { quoteId: result.rows[0].quote_id };
  }

  async createQuoteContext(db, input) {
    return db.query(
      `insert into quote_context (
        quote_id, age, country_code, policy_type, customer_segment, payment_frequency, coverage_amount,
        policy_definition_id, payment_frequency_definition_id, eligibility_rule_version, pricing_rule_version,
        tax_rule_version, country_adjustment_amount, country_adjustment_source, country_adjustment_rule_version,
        request_payload_hash, decision_snapshot_json
      ) values ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17)`,
      [
        input.quoteId,
        input.age,
        input.countryCode,
        input.policyType,
        input.customerSegment,
        input.paymentFrequency,
        input.coverageAmount,
        input.policyDefinitionId,
        input.paymentFrequencyDefinitionId,
        input.eligibilityRuleVersion,
        input.pricingRuleVersion,
        input.taxRuleVersion,
        input.countryAdjustmentAmount,
        input.countryAdjustmentSource,
        input.countryAdjustmentRuleVersion,
        input.requestPayloadHash,
        input.decisionSnapshotJson
      ]
    );
  }

  async insertQuoteCharge(db, input) {
    return db.query(
      `insert into quote_charge (
        quote_id, charge_type, charge_sequence, charge_amount, charge_currency, calculation_basis,
        rate_or_factor_applied, source_attribution, rule_version, tax_rate_if_applicable, is_material_component
      ) values ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)`,
      [
        input.quoteId,
        input.chargeType,
        input.chargeSequence,
        input.chargeAmount,
        input.chargeCurrency,
        input.calculationBasis,
        input.rateOrFactorApplied,
        input.sourceAttribution,
        input.ruleVersion,
        input.taxRateIfApplicable,
        input.isMaterialComponent
      ]
    );
  }

  async createUnderwritingCase(db, input) {
    const result = await db.query(
      `insert into underwriting_case (
        quote_id, customer_id, country_code, workflow_status, workflow_status_reason, routing_rule_version, case_status
      ) values ($1,$2,$3,$4,$5,$6,$7) returning underwriting_case_id`,
      [
        input.quoteId,
        input.customerId,
        input.countryCode,
        input.workflowStatus,
        input.workflowStatusReason,
        input.routingRuleVersion,
        'OPEN'
      ]
    );
    return { underwritingCaseId: result.rows[0].underwriting_case_id };
  }

  async linkUnderwritingCase(db, quoteId, underwritingCaseId) {
    return db.query('update quote_header set underwriting_case_id = $1 where quote_id = $2', [underwritingCaseId, quoteId]);
  }

  async insertAuditEvent(db, input) {
    const client = db || this.pool;
    return client.query(
      `insert into audit_event (
        quote_id, customer_id, event_type, event_category, business_message, event_payload_json, processing_state, correlation_id
      ) values ($1,$2,$3,$4,$5,$6,$7,$8)`,
      [
        input.quoteId,
        input.customerId,
        input.eventType,
        input.eventCategory,
        input.businessMessage,
        input.eventPayloadJson,
        input.processingState,
        input.correlationId
      ]
    );
  }

  async updateProcessingStatus(db, quoteId, processingStatus) {
    return db.query('update quote_header set processing_status = $1, updated_at = now() where quote_id = $2', [processingStatus, quoteId]);
  }
}

module.exports = QuoteRepository;
