import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class QuoteApiService {
  constructor(private http: HttpClient) {}

  createDraftQuote(payload: any): Observable<any> {
    return this.http.post('/api/quotes/draft', payload);
  }

  generateQuote(payload: any): Observable<any> {
    return this.http.post('/api/quotes', payload);
  }

  getQuoteById(quoteId: string): Observable<any> {
    return this.http.get(`/api/quotes/${quoteId}`);
  }

  getBreakdown(quoteId: string): Observable<any> {
    return this.http.get(`/api/quotes/${quoteId}/breakdown`);
  }

  getReferenceData(country?: string): Observable<any> {
    let params = new HttpParams();
    if (country) {
      params = params.set('country', country);
    }
    return this.http.get('/api/quotes/reference-data', { params });
  }
}
