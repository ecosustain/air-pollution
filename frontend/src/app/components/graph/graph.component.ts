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

  ngOnChanges() {
    if (this.formData)
      this.fetchChartData(this.formData);
  }

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

  private removePreviousChart(data: any) {
    if (this.chart)
      this.chart.destroy();
    if (data.line_graph.length == 0) {
      this.chart = undefined;
      return false;
    }
    return true
  }

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

  private defineChartData(labels: any, datasets: any) {
    const chartData: ChartData<'line'> = {
      labels: labels,
      datasets: datasets
    };
    return chartData;
  }

  private getXAxisLabel(timeField: string) {
    const labels = new Map<string, string>([
      ["year", "Ano"],
      ["day", "Dia"],
      ["hour", "Hora"],
      ["month", "Mês"]
    ]);
    return labels.get(timeField);
  }

  private generateColor(index: number): string {
    const hue = (index * 137) % 360;
    return `hsl(${hue}, 70%, 50%)`;
  }
}
