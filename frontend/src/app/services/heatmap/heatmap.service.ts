import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Point } from '../../models/point.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class HeatmapService {

  private url = `${environment.api}/heat_map`;

  constructor(private httpClient: HttpClient) {}

  // Method to get interpolated points
  getInterpolatedPoints(
    date: string,
    indicator: string,
    method: string,
    params: any
  ): Observable<Point[]> {
    const payload = {
      datetime: date,
      indicator: indicator,
      interpolator: {
        method: method,
        params: params
      }
    };

    return this.httpClient.post<Point[]>(this.url, payload);
  }
}
