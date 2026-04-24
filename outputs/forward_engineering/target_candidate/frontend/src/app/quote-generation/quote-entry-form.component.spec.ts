import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { of, throwError } from 'rxjs';
import { QuoteEntryFormComponent } from './quote-entry-form.component';
import { QuoteApiService } from './quote-api.service';

class QuoteApiServiceStub {
  getReferenceData = jasmine.createSpy('getReferenceData').and.returnValue(of({
    supportedCountries: ['ES', 'DE', 'IT', 'PT', 'CH', 'GB'],
    enabledCountries: ['ES', 'DE', 'IT', 'PT', 'CH', 'GB'],
    activePolicyDefinitions: [{ policyDefinitionId: 'p1', policyType: 'HEALTH' }],
    paymentFrequencies: [{ paymentFrequencyDefinitionId: 'pf1', frequencyCode: 'ANNUAL' }],
    coverageBounds: [{ policyType: 'HEALTH', minimumCoverageAmount: 1000, maximumCoverageAmount: 100000 }],
    consentNoticeMetadata: { noticeText: 'Privacy notice', noticeVersion: 'v1' },
    effectiveDate: '2026-04-24'
  }));
  generateQuote = jasmine.createSpy('generateQuote');
}

describe('QuoteEntryFormComponent', () => {
  let component: QuoteEntryFormComponent;
  let fixture: ComponentFixture<QuoteEntryFormComponent>;
  let quoteApi: QuoteApiServiceStub;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [QuoteEntryFormComponent],
      imports: [ReactiveFormsModule],
      providers: [{ provide: QuoteApiService, useClass: QuoteApiServiceStub }]
    }).compileComponents();

    fixture = TestBed.createComponent(QuoteEntryFormComponent);
    component = fixture.componentInstance;
    quoteApi = TestBed.inject(QuoteApiService) as unknown as QuoteApiServiceStub;
    fixture.detectChanges();
  });

  it('loads approved reference data on init', () => {
    expect(quoteApi.getReferenceData).toHaveBeenCalled();
    expect(component.enabledCountries).toEqual(['ES', 'DE', 'IT', 'PT', 'CH', 'GB']);
  });

  it('marks required fields invalid before submission', () => {
    component.submit();
    expect(component.form.invalid).toBeTrue();
    expect(component.apiMessages).toContain('Please correct the highlighted fields before requesting a quote.');
  });

  it('reloads reference data when country changes', () => {
    component.form.patchValue({ countryCode: 'DE' });
    component.onCountryChange();
    expect(quoteApi.getReferenceData).toHaveBeenCalled();
  });

  it('submits consent denied requests to support auditable denied-consent journeys', () => {
    quoteApi.generateQuote.and.returnValue(of({
      outcomeStatus: 'REJECTED',
      validationMessages: ['Consent denied for quote completion.'],
      auditMessage: 'Denied-consent attempt recorded.'
    }));

    component.form.patchValue({
      customerId: 'C1',
      age: '35',
      countryCode: 'ES',
      policyType: 'HEALTH',
      coverageAmount: '10000',
      customerSegment: 'STANDARD',
      paymentFrequency: 'ANNUAL',
      consentStatus: 'DENIED',
      channel: 'DIGITAL'
    });

    component.submit();

    expect(quoteApi.generateQuote).toHaveBeenCalled();
    expect(component.apiMessages).toContain('Consent denied for quote completion.');
    expect(component.apiMessages).toContain('Denied-consent attempt recorded.');
  });

  it('renders successful quote result summary', () => {
    quoteApi.generateQuote.and.returnValue(of({
      outcomeStatus: 'SUCCESS',
      quoteId: 'Q123',
      finalPremium: 150.55,
      countryAdjustmentAmount: 10.25,
      underwritingStatus: 'EU_COMPLIANCE',
      basePremium: 100,
      riskLoadingAmount: 8,
      discountAmount: 4,
      taxAmount: 12.3,
      auditMessage: 'Quote generated successfully.'
    }));

    component.form.patchValue({
      customerId: 'C1',
      age: '35',
      countryCode: 'DE',
      policyType: 'HEALTH',
      coverageAmount: '10000',
      customerSegment: 'STANDARD',
      paymentFrequency: 'ANNUAL',
      consentStatus: 'GRANTED',
      channel: 'DIGITAL'
    });

    component.submit();

    expect(component.submissionResult?.outcomeStatus).toBe('SUCCESS');
    expect(component.submissionResult?.quoteId).toBe('Q123');
    expect(component.apiMessages).toContain('Quote generated successfully.');
  });

  it('shows server-side business-readable validation failures', () => {
    quoteApi.generateQuote.and.returnValue(throwError(() => ({
      error: {
        validationMessages: ['Requested cover is outside the permitted product range.'],
        auditMessage: 'Quote validation failed.'
      }
    })));

    component.form.patchValue({
      customerId: 'C1',
      age: '35',
      countryCode: 'IT',
      policyType: 'HEALTH',
      coverageAmount: '9999999',
      customerSegment: 'STANDARD',
      paymentFrequency: 'ANNUAL',
      consentStatus: 'GRANTED',
      channel: 'DIGITAL'
    });

    component.submit();

    expect(component.apiMessages).toContain('Requested cover is outside the permitted product range.');
    expect(component.apiMessages).toContain('Quote validation failed.');
  });
});
