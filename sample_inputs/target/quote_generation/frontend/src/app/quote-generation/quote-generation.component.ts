import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { QuoteApiService } from './services/quote-api.service';
import { QuoteResponse } from './models/quote-response.model';

@Component({
  selector: 'app-quote-generation',
  templateUrl: './quote-generation.component.html'
})
export class QuoteGenerationComponent {
  result?: QuoteResponse;

  readonly form = this.fb.nonNullable.group({
    customerId: ['', Validators.required],
    age: [30, [Validators.required, Validators.min(18)]],
    policyType: ['HEALTH', Validators.required],
    countryCode: [{ value: 'ES', disabled: true }, Validators.required],
    coverageAmount: [50000, [Validators.required, Validators.min(1)]],
    customerSegment: ['STANDARD', Validators.required],
    paymentFrequency: ['ANNUAL', Validators.required],
    gdprConsentGranted: [false, Validators.requiredTrue]
  });

  constructor(
    private readonly fb: FormBuilder,
    private readonly quoteApi: QuoteApiService
  ) {}

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.quoteApi.generateQuote({
      ...this.form.getRawValue(),
      countryCode: 'ES'
    }).subscribe((result) => {
      this.result = result;
    });
  }
}
