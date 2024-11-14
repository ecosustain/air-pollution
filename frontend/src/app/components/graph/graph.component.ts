// graph.component.ts
import { Component, AfterViewInit, Input } from '@angular/core';
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
export class GraphComponent implements AfterViewInit {
  @Input() formData: any;
  chart: Chart | undefined;

  constructor(private graphService: GraphService) {}

  ngAfterViewInit() {
    if (this.formData) {
      this.fetchChartData(this.formData);
    }
  }

  ngOnChanges() {
    if (this.formData) {
      this.fetchChartData(this.formData);
    }
  }

  fetchChartData(formData: any) {
    this.graphService.fetchGraphData(formData).subscribe((data: any) => {
      console.log('Received data:', data);
      this.updateChart(data);
    });
  }

  updateChart(data: any) {
    if (this.chart) {
      this.chart.destroy();
    }
    if (data.line_graph.length == 0) {
      this.chart = undefined;
      return;
    }

    const timeField = Object.keys(data.line_graph[0][Object.keys(data.line_graph[0])[0]][0]).find(
      key => key === 'year' || key === 'day' || key === 'hour'
    );
    
    if (!timeField) {
      console.error('No valid time field found in the data.');
      return;
    }

    const allTimePoints = new Set<number>();
    data.line_graph.forEach((pollutantObj: any) => {
      const pollutantKey = Object.keys(pollutantObj)[0];
      pollutantObj[pollutantKey].forEach((point: any) => {
        allTimePoints.add(point[timeField]);
      });
    });
    const labels = Array.from(allTimePoints).sort((a, b) => a - b);

    const datasets = data.line_graph.map((pollutantObj: any, index: number) => {
      const pollutantKey = Object.keys(pollutantObj)[0];
      const points = pollutantObj[pollutantKey];
      const timeToValueMap = new Map<number, number>();
      points.forEach((point: any) => {
        timeToValueMap.set(point[timeField], point.average_value);
      });
      const data = labels.map((label) => timeToValueMap.get(label) || null);
      return {
        label: pollutantKey,
        data: data,
        borderColor: this.generateColor(index),
        fill: false,
        tension: 0.1,
      };
    });

    const chartData: ChartData<'line'> = {
      labels: labels,
      datasets: datasets
    };

    const config: ChartConfiguration<'line'> = {
      type: 'line',
      data: chartData,
      options: {
        scales: {
          x: {
            type: 'category',
            title: { display: true, text: this.getXAxisLabel(timeField) }
          },
          y: {
            type: 'linear',
            title: { display: true, text: 'Concentração' }
          }
        }
      }
    };
    this.chart = new Chart('lineChartCanvas', config);
  }

  private getXAxisLabel(timeField: string) {
    const labels = new Map<string, string>([
      ["year", "Ano"],
      ["day", "Dia"],
      ["hour", "Hora"]
    ]);
    return labels.get(timeField);
  }

  private generateColor(index: number): string {
    const hue = (index * 137) % 360;
    return `hsl(${hue}, 70%, 50%)`;
  }
}
