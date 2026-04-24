import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { QuoteApiService } from './quote-api.service';

describe('QuoteApiService', () => {
  let service: QuoteApiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule]
    });
    service = TestBed.inject(QuoteApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('posts quote generation request to approved endpoint', () => {
    service.generateQuote({
      customerId: 'C1',
      age: 40,
      countryCode: 'GB',
      policyType: 'TRAVEL',
      coverageAmount: 5000,
      customerSegment: 'STANDARD',
      paymentFrequency: 'ANNUAL',
      consentStatus: 'GRANTED',
      channel: 'DIGITAL',
      requestTimestamp: '2026-04-24T00:00:00Z',
      correlationId: 'corr-1'
    }).subscribe();

    const req = httpMock.expectOne('/api/v1/quotes');
    expect(req.request.method).toBe('POST');
    expect(req.request.body.countryCode).toBe('GB');
    req.flush({ outcomeStatus: 'SUCCESS' });
  });

  it('retrieves quote reference data from approved endpoint', () => {
    service.getReferenceData('DE', '2026-04-24', 'corr-1').subscribe();

    const req = httpMock.expectOne(r => r.url === '/api/v1/quotes/reference-data' && r.params.get('countryCode') === 'DE');
    expect(req.request.method).toBe('GET');
    req.flush({
      supportedCountries: ['ES', 'DE', 'IT', 'PT', 'CH', 'GB'],
      enabledCountries: ['DE'],
      activePolicyDefinitions: [],
      paymentFrequencies: [],
      coverageBounds: [],
      consentNoticeMetadata: { noticeText: 'Notice', noticeVersion: 'v1' },
      effectiveDate: '2026-04-24'
    });
  });
});
