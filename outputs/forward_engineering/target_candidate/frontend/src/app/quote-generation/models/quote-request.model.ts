export interface QuoteRequest {
  customerId: string;
  age: number;
  policyType: 'HEALTH' | 'TRAVEL' | 'FAMILY' | 'CORPORATE';
  countryCode: 'ES';
  coverageAmount: number;
  customerSegment: 'STANDARD' | 'LOYALTY_GOLD' | 'EMPLOYEE';
  paymentFrequency: 'MONTHLY' | 'QUARTERLY' | 'ANNUAL';
  gdprConsentGranted: boolean;
}
