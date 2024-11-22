import { Component, Input, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import * as L from 'leaflet';
import { Heatmaps} from '../../models/point.model';
import { indicators} from '../../models/indicators.models'; 
import { HttpClient } from '@angular/common/http';
import { spGeoJson } from '../../models/spGeoJson.const';
import { FormsModule } from '@angular/forms'; 
import { CommonModule } from '@angular/common';
import { HeatmapService } from '../../services/heatmap/heatmap.service';


@Component({
  selector: 'app-heatmap',
  standalone: true,
  templateUrl: './heatmap.component.html',
  styleUrls: ['./heatmap.component.css'],
  imports: [FormsModule, CommonModule]
})
export class HeatmapComponent implements OnInit, OnChanges {
  @Input() formData : any; 

  heatmaps : Heatmaps;
  timeInterval : string = '';

  private map: any;
  private legendControl: L.Control | null = null;

  minHeatmapIndex: number;
  maxHeatmapIndex: number;
  currentHeatmapIndex: number;


  month_names =  ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];


  constructor(private http: HttpClient, private heatmapService : HeatmapService) { 
    this.heatmaps = {};
    this.minHeatmapIndex = 1;
    this.maxHeatmapIndex = 1;
    this.currentHeatmapIndex = 1;
  }

  ngOnInit(): void {
    this.initializeMap();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if(this.formData){
      this.getHeatmapData(this.formData);
    }
  }
  
  getHeatmapData(formData : any) {
    this.heatmapService.getInterpolatedHeatmap(formData)
      .subscribe({
        next: (data) => {
          console.log('Received data:', data);
          this.heatmaps = data;
          this.timeInterval = formData.interval;
          this.updateSlider(data);
          this.updateMap(data, formData, this.currentHeatmapIndex);
        },
        error: (err) => {
          console.error(err);
        }
      });
  }

  updateSlider(data : any) {
    const heatmapsKeys = Object.keys(data).map(key => parseInt(key, 10));
      if (heatmapsKeys.length > 0) {
        this.minHeatmapIndex = Math.min(...heatmapsKeys);
        this.maxHeatmapIndex = Math.max(...heatmapsKeys);
        this.currentHeatmapIndex = this.minHeatmapIndex; 
      }
  }

  onHeatmapIndexChange(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.currentHeatmapIndex = parseInt(target.value, 10);
    const indicatorQualityIntervals = this.getIndicatorQualityIntervals(this.formData.indicator);
    this.addRectangles(this.currentHeatmapIndex, this.heatmaps, indicatorQualityIntervals);
  }

  updateMap(data : any, formData : any, heatmapIndex : number){
    const indicatorQualityIntervals = this.getIndicatorQualityIntervals(formData.indicator);
    const indicatorMeasureUnit = this.getIndicatorMeasureUnit(formData.indicator);

    this.addRectangles(heatmapIndex, data, indicatorQualityIntervals);
    this.addLegend(indicatorQualityIntervals, indicatorMeasureUnit);
  }

  getIndicatorQualityIntervals(indicatorName : string){
    const selectedIndicator = indicators.find(indicator => indicator.name === indicatorName);
    if(selectedIndicator){
    return selectedIndicator.interval;
    } else {
      return [];
    }
  }

  private getIndicatorMeasureUnit(indicatorName : string) : string {
    const selectedIndicator = indicators.find(indicator => indicator.name === indicatorName);
    if(selectedIndicator){
      return selectedIndicator.measureUnit;
    } else {
      return "";
    }
  }

  private initializeMap(): void {
    this.map = L.map('map').setView([-23.5489, -46.6388], 10);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 20,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    }).addTo(this.map);

    L.geoJSON(spGeoJson, {
      style: {
        color: 'black',
        weight: 1,
        fillOpacity: 0.1,
      }
    }).addTo(this.map);
  }


  private addRectangles(index: number, heatmaps : Heatmaps, getIndicatorQualityIntervals : number[]): void {
    if (!this.map || !heatmaps[index]) return;

    this.map.eachLayer((layer: any) => {
      if (layer instanceof L.Rectangle) this.map.removeLayer(layer);
    });

    const { min_lat, max_lat, min_long, max_long } = {
      min_lat: -24.00736242788278,
      max_lat: -23.35831688708724,
      min_long: -46.83459631388834,
      max_long: -46.36359807038185,
    };

    const latPoints = 60;
    const latStep = (max_lat - min_lat) / latPoints;
    const longStep = (max_long - min_long) / (latPoints / ((max_lat - min_lat) / (max_long - min_long)));

    heatmaps[index].forEach(point => {
      L.rectangle(
        [
          [point.lat - latStep / 2, point.long - longStep / 2],
          [point.lat + latStep / 2, point.long + longStep / 2]
        ],
        {
          color: 'transparent',
          fillColor: this.chooseColor(point.value, getIndicatorQualityIntervals),
          fillOpacity: 0.4,
          weight: 1,
        }
      ).addTo(this.map);
    });
  }

  private chooseColor(indicatorMeasure: number, indicatorQualityIntervals : number[]): string {
    const colors = ['green', 'yellow', 'pink', 'red', 'purple'];

    for (let i = 1; i < indicatorQualityIntervals.length; i++) {
        if (indicatorMeasure <= indicatorQualityIntervals[i]) {
            return colors[i-1];
        }
    }
    
    return colors[colors.length - 1];
  }

  private addLegend(indicatorQualityIntervals : number[], indicatorMeasureUnit : string): void {
    if (!this.map) return;
    if (this.legendControl) this.map.removeControl(this.legendControl);

    this.legendControl = new (L.Control.extend({
      options: { position: 'bottomright' },
      onAdd: () => {
        const div = L.DomUtil.create('div', 'info legend');
        indicatorQualityIntervals.forEach((val, i) => {
          const label = indicatorQualityIntervals[i + 1] ? `${val}–${indicatorQualityIntervals[i + 1]}` : `${val}+`;
          div.innerHTML += `<i style="background:${['green', 'yellow', 'pink', 'red', 'purple'][i]}"></i> ${label} ${indicatorMeasureUnit}<br>`;
        });
        return div;
      }
    }))();

    this.legendControl.addTo(this.map);
  }

}
