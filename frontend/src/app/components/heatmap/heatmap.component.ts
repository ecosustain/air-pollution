import { Component, Input, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import * as L from 'leaflet';
import { Point } from '../../models/point.model'; // Assuming you have this model

@Component({
  selector: 'app-heatmap',
  standalone: true,
  templateUrl: './heatmap.component.html',
  styleUrls: ['./heatmap.component.css']
})
export class HeatmapComponent implements OnInit, OnChanges {
  @Input() points: Point[] = []; // Receiving points array from the parent

  private map: any;

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
    // L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    //   attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    // }).addTo(this.map);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 20,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    }).addTo(this.map);
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

    const rectangleSize = 0.4/20; // Define the size of the rectangles (latitude/longitude range)

    console.log("The points is now: ", this.points)

    this.points.forEach(point => {
      L.rectangle([[point.lat - (rectangleSize / 2), point.long - (rectangleSize / 2)],
                    [point.lat + (rectangleSize / 2), point.long + (rectangleSize / 2)]], {
        color: 'red', // Can change color as needed
        fillColor: 'red',
        fillOpacity: 0.1,
        weight: 1 // Border thickness
      }).addTo(this.map);
    });
  }

  // Calculate opacity based on value (customize range as per your value scale)
  private calculateOpacity(max: number, min: number, value: number): number {
    return Math.min(Math.max(value / max, 0.1), 1); // Ensure opacity is between 0.1 and 1
  }
}
