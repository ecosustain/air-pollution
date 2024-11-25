import { Component, Input, OnInit, OnChanges, SimpleChanges, Output, EventEmitter } from '@angular/core';
import * as L from 'leaflet';
import { Heatmaps } from '../../models/point.model';
import { indicators } from '../../models/indicators.models';
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
  imports: [FormsModule, CommonModule],
})
export class HeatmapComponent implements OnInit, OnChanges {
  @Input() formData: any; // Input from parent component containing heatmap configuration.
  @Output() isLoading = new EventEmitter<boolean>();

  heatmaps: Heatmaps = {};
  timeInterval: string = '';

  loadingState: boolean = false; 

  private map: L.Map | null = null;
  private legendControl: L.Control | null = null;

  minHeatmapIndex: number = 1;
  maxHeatmapIndex: number = 1;
  currentHeatmapIndex: number = 1;

  readonly monthNames = [
    'jan', 'fev', 'mar', 'abr', 'mai', 'jun',
    'jul', 'ago', 'set', 'out', 'nov', 'dez',
  ];

  constructor(private http: HttpClient, private heatmapService: HeatmapService) {
    this.isLoading.emit(false);
  }

  ngOnInit(): void {
    this.initializeMap();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (this.formData) {
      this.fetchHeatmapData(this.formData);
    }
  }

  /**
   * Fetches heatmap data based on formData.
  */
  private fetchHeatmapData(formData: any): void {
    if(this.loadingState){
     console.log("Application is running on loading mode. Can't fetch heatmap data now.") 
    }
    else{
      this.loadingState = true;
      this.isLoading.emit(true); // Start loading
      this.heatmapService.getInterpolatedHeatmap(formData).subscribe({
        next: (data) => {
          console.log('Received heatmap data:', data);
          this.heatmaps = data;
          this.timeInterval = formData.interval;
          this.updateSlider(data);
          this.updateMap(data, formData, this.currentHeatmapIndex);
          this.loadingState = false;
          this.isLoading.emit(false); // Stop loading
        },
        error: (err) => {
          console.error('Error fetching heatmap data:', err);
          this.isLoading.emit(false); // Stop loading in case of error
        },
      });
    }
  }

  /**
   * Updates slider bounds based on the heatmap data.
  */
  private updateSlider(data: Heatmaps): void {
    const heatmapIndices = Object.keys(data).map((key) => parseInt(key, 10));
    if (heatmapIndices.length > 0) {
      this.minHeatmapIndex = Math.min(...heatmapIndices);
      this.maxHeatmapIndex = Math.max(...heatmapIndices);
      this.currentHeatmapIndex = this.minHeatmapIndex;
    }
  }

  /**
   * Handles changes in heatmap index from the slider.
  */
  onHeatmapIndexChange(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.currentHeatmapIndex = parseInt(target.value, 10);

    const qualityIntervals = this.getIndicatorQualityIntervals(this.formData.indicator);
    const qualityColors = this.getIndicatorQualityColors(this.formData.indicator);
    this.addRectangles(this.currentHeatmapIndex, this.heatmaps, qualityIntervals, qualityColors);
  }

  /**
   * Updates the heatmap and legend.
  */
  private updateMap(data: Heatmaps, formData: any, heatmapIndex: number): void {
    const qualityIntervals = this.getIndicatorQualityIntervals(formData.indicator);
    const qualityColors = this.getIndicatorQualityColors(formData.indicator);
    const measureUnit = this.getIndicatorMeasureUnit(formData.indicator);

    this.addRectangles(heatmapIndex, data, qualityIntervals, qualityColors);
    this.addLegend(qualityIntervals, qualityColors, measureUnit, formData.indicator);
  }

  /**
   * Retrieves quality intervals for the given indicator.
  */
  private getIndicatorQualityIntervals(indicatorName: string): number[] {
    return indicators.find((indicator) => indicator.name === indicatorName)?.qualityIntervals || [];
  }

  /**
   * Retrieves quality colors for the given indicator.
  */
  private getIndicatorQualityColors(indicatorName: string): string[] {
    return indicators.find((indicator) => indicator.name === indicatorName)?.qualityColors || [];
  }

  /**
   * Retrieves the measure unit for the given indicator.
  */
  private getIndicatorMeasureUnit(indicatorName: string): string {
    return indicators.find((indicator) => indicator.name === indicatorName)?.measureUnit || '';
  }

  /**
   * Initializes the Leaflet map.
  */
  private initializeMap(): void {
    this.map = L.map('map').setView([-23.5489, -46.6388], 10);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 20,
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    }).addTo(this.map);

    L.geoJSON(spGeoJson, {
      style: { color: 'black', weight: 1, fillOpacity: 0.1 },
    }).addTo(this.map);
  }

  /**
   * Adds rectangles to the map representing heatmap data.
  */
  private addRectangles(index: number, heatmaps: Heatmaps, qualityIntervals: number[], qualityColors: string[]): void {
    if (!this.map || !heatmaps[index]) return;

    this.map.eachLayer((layer) => {
      if (layer instanceof L.Rectangle) this.map?.removeLayer(layer);
    });

    const bounds = {
      min_lat: -24.00736242788278,
      max_lat: -23.35831688708724,
      min_long: -46.83459631388834,
      max_long: -46.36359807038185,
    };

    const latPoints = 60;
    const latStep = (bounds.max_lat - bounds.min_lat) / latPoints;
    const longStep = (bounds.max_long - bounds.min_long) / (latPoints / ((bounds.max_lat - bounds.min_lat) / (bounds.max_long - bounds.min_long)));

    heatmaps[index].forEach((point) => {
      L.rectangle(
        [
          [point.lat - latStep / 2, point.long - longStep / 2],
          [point.lat + latStep / 2, point.long + longStep / 2],
        ],
        {
          color: 'transparent',
          fillColor: this.chooseColor(point.value, qualityIntervals, qualityColors),
          fillOpacity: 0.4,
          weight: 1,
        }
      ).addTo(this.map!);
    });
  }

  /**
   * Determines rectangle color based on value and intervals.
  */
  private chooseColor(value: number, qualityIntervals: number[], qualityColors: string[]): string {
    for (let i = 0; i < qualityIntervals.length; i++) {
      if (value <= qualityIntervals[i]) return qualityColors[i];
    }
    return qualityColors[qualityColors.length - 1];
  }

  /**
   * Adds a legend to the map.
  */
  private addLegend(qualityIntervals: number[], qualityIntervalsColors: string[], measureUnit: string, indicatorName: string): void {
    if (!this.map) return;
    if (this.legendControl) this.map.removeControl(this.legendControl);
  
    this.legendControl = new (L.Control.extend({
      options: { position: 'bottomright' },
      onAdd: () => {
        const div = L.DomUtil.create('div', 'info legend');
  
        // Add the indicator name at the top of the legend
        div.innerHTML = `<h4 style="margin-top: 5px; 
                                    margin-bottom: 5px;
                        ">${indicatorName}</h4>`;
  
        // Add the color intervals and labels
        let label : string = '';
        qualityIntervals.forEach((val, i) => {
          if(!qualityIntervals[i-1]){
            label = `≤ ${val}`;
          }
          else{
            label = `> ${qualityIntervals[i - 1]} – ${val}`;
          }
          div.innerHTML += `<i style="background:${qualityIntervalsColors[i]}"></i> ${label} ${measureUnit}<br>`;
        });
        
        let val = qualityIntervals[qualityIntervals.length - 1];
        label = ` > ${val}`;
        div.innerHTML += `<i style="background:${qualityIntervalsColors[qualityIntervalsColors.length - 1]}"></i> ${label} ${measureUnit}<br>`;
        return div;
      },
    }))();
  
    this.legendControl.addTo(this.map);
  }
  
}
