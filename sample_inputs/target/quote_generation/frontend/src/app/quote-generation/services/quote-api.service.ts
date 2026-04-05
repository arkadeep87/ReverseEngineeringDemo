import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { QuoteRequest } from '../models/quote-request.model';
import { QuoteResponse } from '../models/quote-response.model';

@Injectable({ providedIn: 'root' })
export class QuoteApiService {
  private readonly baseUrl = '/api/v1/quotes';

  constructor(private readonly http: HttpClient) {}

  generateQuote(payload: QuoteRequest): Observable<QuoteResponse> {
    return this.http.post<QuoteResponse>(`${this.baseUrl}/generate`, payload);
  }
}
