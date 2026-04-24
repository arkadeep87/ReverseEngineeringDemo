import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface GenerateQuoteRequest {
  customerId: string;
  age: number;
  countryCode: string;
  policyType: string;
  coverageAmount: number;
  customerSegment: string;
  paymentFrequency: string;
  consentStatus: string;
  channel: string;
  requestTimestamp: string;
  correlationId: string;
}

export interface GenerateQuoteResponse {
  outcomeStatus: string;
  quoteId?: string;
  countryCode?: string;
  policyType?: string;
  coverageAmount?: number;
  basePremium?: number;
  riskLoadingAmount?: number;
  riskFactorApplied?: number;
  discountAmount?: number;
  taxAmount?: number;
  taxRateApplied?: number;
  countryAdjustmentAmount?: number;
  countryAdjustmentSource?: string;
  finalPremium?: number;
  paymentFrequency?: string;
  underwritingCaseId?: string;
  underwritingStatus?: string;
  auditMessage?: string;
  validationMessages?: string[];
  rejectionReasonCode?: string;
  correlationId?: string;
}

export interface QuoteReferenceDataResponse {
  supportedCountries: string[];
  enabledCountries: string[];
  activePolicyDefinitions: Array<{ policyDefinitionId: string; policyType: string }>;
  paymentFrequencies: Array<{ paymentFrequencyDefinitionId: string; frequencyCode: string }>;
  coverageBounds: Array<{ policyType: string; minimumCoverageAmount: number; maximumCoverageAmount: number }>;
  consentNoticeMetadata: { noticeText: string; noticeVersion: string };
  effectiveDate: string;
}

@Injectable({ providedIn: 'root' })
export class QuoteApiService {
  constructor(private http: HttpClient) {}

  generateQuote(request: GenerateQuoteRequest): Observable<GenerateQuoteResponse> {
    return this.http.post<GenerateQuoteResponse>('/api/v1/quotes', request);
  }

  getReferenceData(countryCode: string | undefined, asOfDate: string, correlationId: string): Observable<QuoteReferenceDataResponse> {
    let params = new HttpParams().set('asOfDate', asOfDate).set('correlationId', correlationId);
    if (countryCode) {
      params = params.set('countryCode', countryCode);
    }
    return this.http.get<QuoteReferenceDataResponse>('/api/v1/quotes/reference-data', { params });
  }
}
