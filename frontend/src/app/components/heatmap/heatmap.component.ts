import { Component, Input, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import * as L from 'leaflet';
import shp from 'shpjs';
import { Point } from '../../models/point.model'; // Assuming you have this model
import { HttpClient } from '@angular/common/http';
import { spGeoJson } from '../../models/spGeoJson.const';

@Component({
  selector: 'app-heatmap',
  standalone: true,
  templateUrl: './heatmap.component.html',
  styleUrls: ['./heatmap.component.css']
})
export class HeatmapComponent implements OnInit, OnChanges {
  @Input() points: Point[] = []; // Receiving points array from the parent

  private map: any;

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.initializeMap();
    console.log('Initial points:', this.points); // Log initial points
    //this.addRectangles(); // Call addRectangles if you want to draw rectangles on init
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['points']) {
      console.log('Updated points:', changes['points'].currentValue); // Log updated points
      this.addRectangles(); // Update rectangles when points change
    }
  }

  // Initialize the Leaflet map
  private initializeMap(): void {
    this.map = L.map('map').setView([-23.5489, -46.6388], 13);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 20,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    }).addTo(this.map);

    L.geoJSON(spGeoJson, {
      style: {
        color: 'black', // Line color for LineString or Polygon outlines
        weight: 1,
        fillOpacity: 0.1, // Fill opacity for Polygons
      }
    }).addTo(this.map);

    // Add legend after map is initialized
    this.addLegend();
  }

  // Add rectangles to the map based on points array
  private addRectangles(): void {
    if (!this.map) return;

    // Clear existing rectangles before adding new ones
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

    console.log("The points is now: ", this.points)

    this.points.forEach(point => {
      L.rectangle([[point.lat - (latStepSize / 2), point.long - (latStepSize / 2)],
                    [point.lat + (longStepSize / 2), point.long + (longStepSize / 2)]], {
        color: 'transparent', // Can change color as needed
        fillColor: this.chooseColor(point.value),
        fillOpacity: 0.4,
        weight: 1 // Border thickness
      }).addTo(this.map);
    });
  }

  // Choose color based on measure
  private chooseColor(measure: number): string {
    if (measure < 25) {
      return 'green';
    } else if (measure < 50) {
      return 'yellow';
    } else if (measure < 75) {
      return 'pink';
    } else if (measure < 125) {
      return 'red';
    } else {
      return 'purple';
    }
  }

  // Add a legend control to the map
  private addLegend(): void {
    const legend = new (L.Control.extend({
      options: { position: 'bottomright' },
      
      onAdd: (map: any) => {
        const div = L.DomUtil.create('div', 'info legend');
        const intervals = [0, 25, 50, 75, 125]; // Intervals based on chooseColor function
        const colors = ['green', 'yellow', 'pink', 'red', 'purple'];
  
        // Loop through intervals and generate a label with a color square and unit for each range
        for (let i = 0; i < intervals.length; i++) {
          div.innerHTML +=
            '<i style="background:' + colors[i] + '; width: 18px; height: 18px; display: inline-block;"></i> ' +
            intervals[i] + (intervals[i + 1] ? '&ndash;' + intervals[i + 1] : '+') + ' µg/m³<br>';
        }
        return div;
      }
    }))();
  
    legend.addTo(this.map);
  }
  
    

  // Calculate opacity based on value (customize range as per your value scale)
  private calculateOpacity(max: number, min: number, value: number): number {
    return Math.min(Math.max(value / max, 0.1), 1); // Ensure opacity is between 0.1 and 1
  }
}
