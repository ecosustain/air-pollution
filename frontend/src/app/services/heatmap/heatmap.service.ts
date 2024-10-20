import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Point } from '../../models/point.model';

@Injectable({
  providedIn: 'root'
})
export class HeatmapService {

  private url = environment.api

  constructor(private httpClient: HttpClient) { }

  getInterpolatedPoints(){
    return this.httpClient.get<Point[]>(this.url + '/heat_map')
  }
}
