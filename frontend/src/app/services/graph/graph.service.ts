import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class GraphService {
  private apiUrl = 'http://127.0.0.1:5000/linegraph';

  constructor(private http: HttpClient) {}

  fetchGraphData(formData: any): Observable<any> {
    // Structure the payload as required by the endpoint
    const payload = {
      interval: formData.timePeriod,
      year: formData.specificDate?.year || null,
      month: formData.month || formData.specificDate?.month || null,
      indicators: formData.indicators
    };

    // Encode the payload for the URL
    const encodedPayload = encodeURIComponent(JSON.stringify(payload));
    const fullUrl = `${this.apiUrl}/${encodedPayload}`;
    
    return this.http.get<any>(fullUrl);
  }
}
