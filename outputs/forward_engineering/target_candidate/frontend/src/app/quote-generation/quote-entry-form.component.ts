import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { QuoteApiService, GenerateQuoteRequest, GenerateQuoteResponse, QuoteReferenceDataResponse } from './quote-api.service';

@Component({
  selector: 'app-quote-entry-form',
  templateUrl: './quote-entry-form.component.html'
})
export class QuoteEntryFormComponent implements OnInit {
  form: FormGroup;
  referenceData: QuoteReferenceDataResponse | null = null;
  submissionResult: GenerateQuoteResponse | null = null;
  loading = false;
  loadingReferenceData = false;
  apiMessages: string[] = [];
  correlationId = '';

  constructor(private fb: FormBuilder, private quoteApi: QuoteApiService) {
    this.form = this.fb.group({
      customerId: ['', [Validators.required]],
      age: ['', [Validators.required, Validators.pattern(/^[0-9]+$/)]],
      countryCode: ['', [Validators.required]],
      policyType: ['', [Validators.required]],
      coverageAmount: ['', [Validators.required, Validators.pattern(/^\d+(\.\d+)?$/)]],
      customerSegment: ['', [Validators.required]],
      paymentFrequency: ['', [Validators.required]],
      consentStatus: ['', [Validators.required]],
      channel: ['DIGITAL', [Validators.required]]
    });
  }

  ngOnInit(): void {
    this.correlationId = this.createCorrelationId();
    this.loadReferenceData();
  }

  loadReferenceData(countryCode?: string): void {
    this.loadingReferenceData = true;
    this.quoteApi.getReferenceData(countryCode, new Date().toISOString(), this.correlationId).subscribe({
      next: (data) => {
        this.referenceData = data;
        this.loadingReferenceData = false;
      },
      error: (error) => {
        this.loadingReferenceData = false;
        this.apiMessages = this.extractMessages(error?.error?.validationMessages, 'Unable to load quote reference data.');
      }
    });
  }

  onCountryChange(): void {
    const countryCode = this.form.get('countryCode')?.value;
    this.submissionResult = null;
    this.apiMessages = [];
    if (countryCode) {
      this.loadReferenceData(countryCode);
    }
  }

  submit(): void {
    this.submissionResult = null;
    this.apiMessages = [];

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.apiMessages = ['Please correct the highlighted fields before requesting a quote.'];
      return;
    }

    const request: GenerateQuoteRequest = {
      customerId: this.form.value.customerId,
      age: Number(this.form.value.age),
      countryCode: this.form.value.countryCode,
      policyType: this.form.value.policyType,
      coverageAmount: Number(this.form.value.coverageAmount),
      customerSegment: this.form.value.customerSegment,
      paymentFrequency: this.form.value.paymentFrequency,
      consentStatus: this.form.value.consentStatus,
      channel: this.form.value.channel,
      requestTimestamp: new Date().toISOString(),
      correlationId: this.correlationId
    };

    this.loading = true;
    this.quoteApi.generateQuote(request).subscribe({
      next: (response) => {
        this.loading = false;
        this.submissionResult = response;
        this.apiMessages = this.extractMessages(response.validationMessages, response.auditMessage);
      },
      error: (error) => {
        this.loading = false;
        this.submissionResult = null;
        const payload = error?.error;
        this.apiMessages = this.extractMessages(payload?.validationMessages, payload?.auditMessage || 'The quote could not be processed.');
      }
    });
  }

  get enabledCountries(): string[] {
    return this.referenceData?.enabledCountries || [];
  }

  get activePolicyDefinitions(): Array<{ policyType: string; policyDefinitionId: string }> {
    return this.referenceData?.activePolicyDefinitions || [];
  }

  get paymentFrequencies(): Array<{ frequencyCode: string }> {
    return this.referenceData?.paymentFrequencies || [];
  }

  get consentNotice(): string {
    return this.referenceData?.consentNoticeMetadata?.noticeText || '';
  }

  hasFieldError(fieldName: string): boolean {
    const field = this.form.get(fieldName);
    return !!field && field.invalid && (field.touched || field.dirty);
  }

  fieldErrorMessage(fieldName: string): string {
    const field = this.form.get(fieldName);
    if (!field || !field.errors) {
      return '';
    }
    if (field.errors['required']) {
      return 'This field is required.';
    }
    if (fieldName === 'age' && field.errors['pattern']) {
      return 'Age must be a valid number.';
    }
    if (fieldName === 'coverageAmount' && field.errors['pattern']) {
      return 'Coverage amount must be a valid positive number.';
    }
    return 'Invalid value.';
  }

  private extractMessages(validationMessages?: string[], auditMessage?: string): string[] {
    const messages: string[] = [];
    if (validationMessages && validationMessages.length > 0) {
      messages.push(...validationMessages);
    }
    if (auditMessage) {
      messages.push(auditMessage);
    }
    return Array.from(new Set(messages.filter(Boolean)));
  }

  private createCorrelationId(): string {
    return 'corr-' + Math.random().toString(36).slice(2) + '-' + Date.now();
  }
}
