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
  });

  constructor(private httpClient: HttpClient) {}

  getInterpolatedPoints(
    date: string,
    indicator: string,
    method: string,
    params: any
  ): Observable<Heatmap> {
    let payload = {
      datetime : date,
      indicator : indicator,
      interpolator : {
        method : method,
        params : params
      } 
    }
    
    let payload_encoded = JSON.stringify(payload)
    
    return this.httpClient.get<Heatmap>(this.url+'/'+ payload_encoded, 
      {
        headers : this.headers
      }
    );
  }
}
