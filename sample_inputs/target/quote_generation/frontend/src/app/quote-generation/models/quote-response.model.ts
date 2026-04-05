export interface QuoteResponse {
  quoteId: string;
  pricing: {
    basePremium: number;
    riskFactor: number;
    discountAmount: number;
    taxAmount: number;
    countryAdjustmentAmount: number;
    finalPremium: number;
  };
  auditMessage: string;
}
