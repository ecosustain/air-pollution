import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class GraphService {
  private apiUrl = `${environment.api}/linegraph`;

  constructor(private http: HttpClient) {}

  /**
   * Fetches graph data from the backend API based on the provided form data.
   * 
   * The method constructs a payload from the user-provided form data, including
   * the time period, specific year and month (if available), and a list of indicators.
   * This payload is then encoded and sent as part of a GET request to the API.
   *
   * @param {any} formData - The form data collected from the user. 
   *                         Contains the following properties:
   *                         - `timePeriod` (string): The type of interval (e.g., "yearly").
   *                         - `specificDate` (optional): An object with properties:
   *                           - `year` (number): The specific year for filtering (if applicable).
   *                           - `month` (number): The specific month for filtering (if applicable).
   *                         - `month` (optional): A general month filter.
   *                         - `indicators` (string[]): A list of pollutant indicators.
   * @returns {Observable<any>} An observable that emits the data returned from the backend API.
   */
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
