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
    const payload: any = {};
    payload.interval = formData.timePeriod;
    if (formData.specificDate?.year) {
      payload.year = formData.specificDate.year;
    }
    if (formData.month || formData.specificDate?.month) {
      payload.month = formData.month || formData.specificDate.month;
    }
    payload.indicators = formData.indicators;
    
    const encodedPayload = encodeURIComponent(JSON.stringify(payload));
    const fullUrl = `${this.apiUrl}/${encodedPayload}`;
    return this.http.get<any>(fullUrl);
  }
}
