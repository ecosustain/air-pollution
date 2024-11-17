import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { HeatmapResponse, Heatmaps } from '../../models/point.model';
import { environment } from '../../../environments/environment';


@Injectable({
  providedIn: 'root'
})
export class HeatmapService {

  private url = `${environment.api}/heatmap`;

  private headers = new HttpHeaders({
    'Content-Type': 'application/json',
  });

  constructor(private httpClient: HttpClient) {}

  // Method to get interpolated points
  getInterpolatedHeatmap(
    payload : object
  ): Observable<Heatmaps> {
    
    let payload_encoded = JSON.stringify(payload)
    
    // Use get method with the constructed URL and query parameters
    return this.httpClient.get<Heatmaps>(this.url+'/'+ payload_encoded, 
      {
        headers : this.headers
      }
    );
  }
}
