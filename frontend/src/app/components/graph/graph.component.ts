import { Component, EventEmitter, Input, OnChanges, Output } from '@angular/core';
import { Chart, ChartConfiguration, ChartData, registerables } from 'chart.js';
import { GraphService } from '../../services/graph/graph.service';
import { CommonModule } from '@angular/common';

Chart.register(...registerables);

@Component({
  selector: 'app-graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.css'],
  standalone: true,
  imports: [CommonModule]
})
export class GraphComponent implements OnChanges {
  @Input() formData: any;
  @Output() isLoading = new EventEmitter<boolean>();

  loadingState: boolean = false; 

  chart: Chart | undefined;

  constructor(private graphService: GraphService) {}

  /**
   * Detects changes in the input data and triggers the process
   * to fetch and update the chart if new form data is provided.
   */
  ngOnChanges() {
    if (this.formData)
      this.fetchChartData(this.formData);
  }

  /**
   * Fetches chart data from the backend service based on the provided form data.
   * 
   * @param {any} formData - The input form data containing parameters for the backend API call.
   */
  fetchChartData(formData: any) {
    if(this.loadingState){
      console.log("Application is running on loading mode. Can't fetch graph data now.") 
    }
    else{
      this.loadingState = true;
      this.isLoading.emit(true); // Start loading
      this.graphService.fetchGraphData(formData).subscribe({
        next : (data) => {
          console.log('Received data:', data);
          this.updateChart(data);
          this.loadingState = false;
          this.isLoading.emit(false); // Stop loading
        },
        error : (err) => {
          console.error('Error fetching graph data:', err);
          this.loadingState = false;
          this.isLoading.emit(false);
        } 
      });
    }
  }

  /**
   * Updates the chart with new data by processing the response and rendering a new chart.
   * 
   * @param {any} data - The data received from the backend for rendering the chart.
   */
  updateChart(data: any) {
    if (!this.removePreviousChart(data))
      return;
    const timeLabel = this.findTimeLabel(data);
    if (!timeLabel) {
      this.chart = undefined;
      return;
    }
    const labels = this.getSortedTimePoints(data, timeLabel);
    const datasets = this.getDatasets(data, timeLabel, labels)
    const chartData = this.defineChartData(labels, datasets);
    const config = this.defineChartConfiguration(chartData, timeLabel);
    this.chart = new Chart('lineChartCanvas', config);
  }

  /**
   * Removes the previous chart instance, if it exists, to prepare for rendering a new one.
   * 
   * @param {any} data - The data to check for valid chart rendering.
   * @returns {boolean} `true` if a new chart can be created; otherwise, `false`.
   */
  private removePreviousChart(data: any) {
    if (this.chart)
      this.chart.destroy();
    if (data.line_graph.length == 0) {
      this.chart = undefined;
      return false;
    }
    return true
  }

  /**
   * Identifies the appropriate time label (e.g., 'year', 'day') from the data structure.
   * 
   * @param {any} data - The data received from the backend.
   * @returns {string | null} The identified time label, or `null` if none is found.
   */
  private findTimeLabel(data: any) {
    for (const indicatorData of data.line_graph) {
      const indicatorKey = Object.keys(indicatorData)[0];
      const points = indicatorData[indicatorKey];
      
      if (Array.isArray(points) && points.length > 0) {
        const timeLabel = Object.keys(points[0]).find(
          key => key === 'year' || key === 'day' || key === 'hour' || key === 'month'
        );
        if (timeLabel)
          return timeLabel;
      }
    }
    return null;
  }

  /**
   * Retrieves and sorts all unique time points from the backend data.
   * 
   * @param {any} data - The data received from the backend.
   * @param {string} timeLabel - The key representing the time field (e.g., 'year').
   * @returns {number[]} A sorted array of unique time points.
   */
  private getSortedTimePoints(data: any, timeLabel: string) {
    const allTimePoints = new Set<number>();
    data.line_graph.forEach((indicatorObj: any) => {
      const indicatorKey = Object.keys(indicatorObj)[0];
      indicatorObj[indicatorKey].forEach((point: any) => {
        allTimePoints.add(point[timeLabel]);
      });
    });
    const sortedTimePoints = Array.from(allTimePoints).sort((a, b) => a - b);
    return sortedTimePoints;
  }

  /**
   * Generates datasets for the chart using the provided backend data and time labels.
   * 
   * @param {any} data - The backend data containing points for each indicator.
   * @param {string} timeLabel - The key representing the time field (e.g., 'year').
   * @param {any[]} labels - The sorted time labels to align data points.
   * @returns {any[]} An array of datasets formatted for the chart library.
   */
  private getDatasets(data: any, timeLabel: string, labels: any) {
    const datasets = data.line_graph.map((indicatorObj: any, index: number) => {
      const indicatorKey = Object.keys(indicatorObj)[0];
      const points = indicatorObj[indicatorKey];
      const timeToValueMap = new Map<number, number>();
      points.forEach((point: any) => {
        timeToValueMap.set(point[timeLabel], point.average_value);
      });
      const data = labels.map((label: any) => timeToValueMap.get(label) || null);
      return {
        label: indicatorKey,
        data: data,
        borderColor: this.generateColor(index),
        fill: false,
        tension: 0.1,
      };
    });
    return datasets;
  }

  /**
   * Defines the chart configuration object for rendering.
   * 
   * @param {any} chartData - The processed chart data containing labels and datasets.
   * @param {string} timeLabel - The key representing the time field (e.g., 'year').
   * @returns {ChartConfiguration<'line'>} The chart configuration for the library.
   */
  private defineChartConfiguration(chartData: any, timeLabel: string) {
    const config: ChartConfiguration<'line'> = {
      type: 'line',
      data: chartData,
      options: {
        scales: {
          x: {
            type: 'category',
            title: { display: true, text: this.getXAxisLabel(timeLabel) }
          },
          y: {
            type: 'linear',
            title: { display: true, text: 'Valor' }
          }
        }
      }
    };
    return config
  }

  /**
   * Defines the data structure for the chart.
   * 
   * @param {any[]} labels - The chart labels representing time points.
   * @param {any[]} datasets - The datasets containing data points for each indicator.
   * @returns {ChartData<'line'>} The formatted chart data.
   */
  private defineChartData(labels: any, datasets: any) {
    const chartData: ChartData<'line'> = {
      labels: labels,
      datasets: datasets
    };
    return chartData;
  }

  /**
   * Returns the display label for the X-axis based on the time field.
   * 
   * @param {string} timeField - The key representing the time field (e.g., 'year').
   * @returns {string | undefined} The localized X-axis label.
   */
  private getXAxisLabel(timeField: string) {
    const labels = new Map<string, string>([
      ["year", "Ano"],
      ["day", "Dia"],
      ["hour", "Hora"],
      ["month", "Mês"]
    ]);
    return labels.get(timeField);
  }

  /**
   * Generates a unique color for a dataset based on its index.
   * 
   * @param {number} index - The index of the dataset.
   * @returns {string} A color in HSL format.
   */
  private generateColor(index: number): string {
    const hue = (index * 137) % 360;
    return `hsl(${hue}, 70%, 50%)`;
  }
}
