import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { QuoteApiService } from '../services/quote-api.service';

@Component({
  selector: 'app-quote-entry',
  templateUrl: './quote-entry.component.html'
})
export class QuoteEntryComponent implements OnInit {
  quoteForm!: FormGroup;
  supportedCountries: string[] = [];
  policyTypes: string[] = [];
  paymentFrequencies: string[] = [];
  countryDefaults: any = {};
  coverageBounds: any = {};
  consentRequirements: any = {};
  validationMessages: string[] = [];
  result: any = null;
  loading = false;
  draftQuoteId: string | null = null;

  constructor(private fb: FormBuilder, private quoteApi: QuoteApiService) {}

  ngOnInit(): void {
    this.quoteForm = this.fb.group({
      customerId: ['', Validators.required],
      age: [null, [Validators.required]],
      country: ['', Validators.required],
      policyType: ['', Validators.required],
      coverageAmount: [null, [Validators.required]],
      paymentFrequency: ['', Validators.required],
      customerSegment: ['', Validators.required],
      consentIndicator: [false, Validators.required]
    });

    this.loadReferenceData();

    this.quoteForm.get('country')?.valueChanges.subscribe((country) => {
      if (!country) {
        return;
      }
      this.loadReferenceData(country);
      this.applyCountryDefaults(country);
    });
  }

  loadReferenceData(country?: string): void {
    this.quoteApi.getReferenceData(country).subscribe((data) => {
      this.supportedCountries = data.supportedCountries || [];
      this.policyTypes = data.policyTypes || [];
      this.paymentFrequencies = data.paymentFrequencies || [];
      this.countryDefaults = data.countryDefaults || {};
      this.coverageBounds = data.coverageBounds || {};
      this.consentRequirements = data.consentRequirements || {};
    });
  }

  applyCountryDefaults(country: string): void {
    const defaults = this.countryDefaults?.[country];
    if (defaults?.defaultPolicyType && !this.quoteForm.get('policyType')?.value) {
      this.quoteForm.patchValue({ policyType: defaults.defaultPolicyType });
    }
  }

  validateForm(): boolean {
    this.validationMessages = [];
    if (this.quoteForm.invalid) {
      this.validationMessages.push('Please provide all mandatory quote input fields.');
    }

    const country = this.quoteForm.get('country')?.value;
    if (country && this.supportedCountries.length && !this.supportedCountries.includes(country)) {
      this.validationMessages.push('Selected country is not supported for quote processing.');
    }

    const policyType = this.quoteForm.get('policyType')?.value;
    const coverageAmount = this.quoteForm.get('coverageAmount')?.value;
    const bound = this.coverageBounds?.[policyType];
    if (bound && coverageAmount != null) {
      if ((bound.minCoverageAmount != null && coverageAmount < bound.minCoverageAmount) ||
          (bound.maxCoverageAmount != null && coverageAmount > bound.maxCoverageAmount)) {
        this.validationMessages.push('Coverage amount is outside the permitted product range.');
      }
    }

    const consentRequired = this.consentRequirements?.[country]?.requiredIndicator === true;
    const consentGiven = this.quoteForm.get('consentIndicator')?.value === true;
    if (consentRequired && !consentGiven) {
      this.validationMessages.push('Required consent is missing for the selected country.');
    }

    return this.validationMessages.length === 0;
  }

  createDraftAndGenerate(): void {
    this.result = null;
    if (!this.validateForm()) {
      return;
    }

    this.loading = true;
    const payload = this.quoteForm.getRawValue();

    this.quoteApi.createDraftQuote(payload).subscribe({
      next: (draft) => {
        this.draftQuoteId = draft.draftQuoteId;
        const request = { ...payload, draftQuoteId: draft.draftQuoteId };
        this.quoteApi.generateQuote(request).subscribe({
          next: (response) => {
            this.result = response;
            this.validationMessages = response.rejectionReason ? [response.rejectionReason] : [];
            this.loading = false;
          },
          error: (err) => {
            this.validationMessages = [err?.error?.rejectionReason || 'Quote generation failed.'];
            this.loading = false;
          }
        });
      },
      error: (err) => {
        this.validationMessages = err?.error?.validationMessages || ['Draft quote creation failed.'];
        this.loading = false;
      }
    });
  }
}
