class QuoteChargePersistenceService {
  constructor({ quoteRepository }) {
    this.quoteRepository = quoteRepository;
  }

  async persistCharges(db, quoteId, chargeLines) {
    const mandatoryChargeTypes = ['BASE_PREMIUM', 'TAX', 'COUNTRY_ADJUSTMENT'];
    for (const chargeType of mandatoryChargeTypes) {
      if (!chargeLines.find((line) => line.chargeType === chargeType)) {
        const error = new Error(`Mandatory charge line missing: ${chargeType}`);
        error.statusCode = 500;
        throw error;
      }
    }

    for (const line of chargeLines) {
      await this.quoteRepository.insertQuoteCharge(db, {
        quoteId,
        chargeType: line.chargeType,
        chargeSequence: line.chargeSequence,
        chargeAmount: line.chargeAmount,
        chargeCurrency: 'EUR',
        calculationBasis: line.calculationBasis,
        rateOrFactorApplied: line.rateOrFactorApplied,
        sourceAttribution: line.sourceAttribution,
        ruleVersion: line.ruleVersion,
        taxRateIfApplicable: line.taxRateIfApplicable,
        isMaterialComponent: line.isMaterialComponent
      });
    }
  }
}

module.exports = QuoteChargePersistenceService;
