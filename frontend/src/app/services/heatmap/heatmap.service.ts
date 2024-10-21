import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Heatmap } from '../../models/point.model';
import { environment } from '../../../environments/environment';


@Injectable({
  providedIn: 'root'
})
export class HeatmapService {

  private url = `${environment.api}/heat_map`;

  private headers = new HttpHeaders({
    'Content-Type': 'application/json',
    // Add more headers if needed, like authorization
  });

  constructor(private httpClient: HttpClient) {}

  // Method to get interpolated points
  getInterpolatedPoints(
    date: string,
    indicator: string,
    method: string,
    params: any
  ): Observable<Heatmap> {
    // Create HttpParams object to hold the query parameters
    let payload = {
      datetime : date,
      indicator : indicator,
      interpolator : {
        method : method,
        params : params
      } 
    }
    
    let payload_encoded = JSON.stringify(payload)
    
    // Use get method with the constructed URL and query parameters
    return this.httpClient.get<Heatmap>(this.url+'/'+ payload_encoded, 
      {
        headers : this.headers
      }
    );
  }
}
