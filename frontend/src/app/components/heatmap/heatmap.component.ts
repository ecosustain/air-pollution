import { Component, Input, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import * as L from 'leaflet';
import shp from 'shpjs';
import { Heatmaps, HeatmapResponse, Point } from '../../models/point.model'; // Assuming you have this model
import { indicators} from '../../models/indicators.models'; // Assuming you have this model
import { HttpClient } from '@angular/common/http';
import { spGeoJson } from '../../models/spGeoJson.const';

@Component({
  selector: 'app-heatmap',
  standalone: true,
  templateUrl: './heatmap.component.html',
  styleUrls: ['./heatmap.component.css']
})
export class HeatmapComponent implements OnInit, OnChanges {
  @Input() heatmaps: Heatmaps = {};
  @Input() indicator: string = ''; 
  
  private map: any;
  private interval: number[] | undefined = [];
  private measureUnit : string | undefined = "";

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.initializeMap();
    console.log('Initial Heatmap Intervals:', this.heatmaps); // Log initial points
    //this.addRectangles(); // Call addRectangles if you want to draw rectangles on init
  }

  ngOnChanges(changes: SimpleChanges): void {
    if(changes['indicator']){
        console.log('Updated indicator response:', changes['indicator'].currentValue); // Log updated indicator
        this.updateIntervals(this.indicator);
        this.updateUnitMeasure(this.indicator);
        this.addLegend(this.indicator); 
      }
    if (changes['heatmaps']) {
      console.log('Updated heatmaps response:', changes['heatmaps'].currentValue); // Log updated points
      this.addRectangles(this.heatmaps); // Update rectangles when points change
    }
  }

  private initializeMap(): void {
    this.map = L.map('map').setView([-23.5489, -46.6388], 13);

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

    // Add legend after map is initialized
    this.addLegend(this.indicator);
  }

  private updateIntervals(indicatorName : string){
    const selectedIndicator = indicators.find(indicator => indicator.name === indicatorName);
    this.interval = selectedIndicator?.interval
  }
  private updateUnitMeasure(indicatorName : string){
    const selectedIndicator = indicators.find(indicator => indicator.name === indicatorName);
    this.measureUnit = selectedIndicator?.measureUnit
  }

  // Add rectangles to the map based on points array
  private addRectangles(heatmaps : Heatmaps): void {
    if (!this.map) return;

    this.map.eachLayer((layer: any) => {
      if (layer instanceof L.Rectangle) {
        this.map.removeLayer(layer);
      }
    });

    const borders_coordinates = {
      "min_lat": -24.00736242788278,
      "max_lat": -23.35831688708724,
      "min_long": -46.83459631388834,
      "max_long": -46.36359807038185,
    };

    const number_of_lat_points = 60;

    const lat_distance = borders_coordinates.max_lat - borders_coordinates.min_lat;
    const long_distance = borders_coordinates.max_long - borders_coordinates.min_long;

    const aspect_ratio = lat_distance / long_distance

    const number_of_long_points = number_of_lat_points / aspect_ratio

    const latStepSize = (borders_coordinates.max_lat - borders_coordinates.min_lat) / number_of_lat_points;
    const longStepSize = (borders_coordinates.max_long - borders_coordinates.min_long) / number_of_long_points;

    console.log("The heatmaps is now: ", this.heatmaps)

    heatmaps["1"].forEach(point => {
      L.rectangle([[point.lat - (latStepSize / 2), point.long - (latStepSize / 2)],
                    [point.lat + (longStepSize / 2), point.long + (longStepSize / 2)]], {
        color: 'transparent', // Can change color as needed
        fillColor: this.chooseColor(point.value),
        fillOpacity: 0.4,
        weight: 1
      }).addTo(this.map);
    });
  }

  // Choose color based on measure
  private chooseColor(measure: number): string {
    const intervals = this.interval as number[];
    const colors = ['green', 'yellow', 'pink', 'red', 'purple'];

    for (let i = 1; i < intervals.length; i++) {
        if (measure <= intervals[i]) {
            return colors[i-1];
        }
    }
    
    // If the measure is above the last interval, return the last color
    return colors[colors.length - 1];
  }

  // Add a legend control to the map
  private addLegend(indicator : string): void {
    const legend = new (L.Control.extend({
      options: { position: 'bottomright' },
      
      onAdd: (map: any) => {
        const div = L.DomUtil.create('div', 'info legend');
        const intervals = this.interval as number[]; 
        const colors = ['green', 'yellow', 'pink', 'red', 'purple'];
        const unitMeasure = this.measureUnit;

        // Loop through intervals and generate a label with a color square and unit for each range
        for (let i = 0; i < intervals.length; i++) {
          div.innerHTML +=
            '<i style="background:' + colors[i] + '; width: 18px; height: 18px; display: inline-block;"></i> ' +
            intervals[i] + (intervals[i + 1] ? '&ndash;' + intervals[i + 1] : '+') +' '+ unitMeasure +'<br>';
        }
        return div;
      }
    }))();
  
    legend.addTo(this.map);
  }
}
