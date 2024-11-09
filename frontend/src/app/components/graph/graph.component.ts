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

  getXAxisLabel(timeField: string) {
    const labels = new Map<string, string>([
      ["year", "Ano"],
      ["day", "Dia"],
      ["hour", "Hora"]
    ]);
    return labels.get(timeField);
  }

  updateChart(data: any) {
    const timeField = Object.keys(data.line_graph[0][Object.keys(data.line_graph[0])[0]][0]).find(
      key => key === 'year' || key === 'day' || key === 'hour'
    );
    
    if (!timeField) {
      console.error('No valid time field found in the data.');
      return;
    }
    
    // Extract labels by sorting the points based on the identified time field
    const labels = data.line_graph[0][Object.keys(data.line_graph[0])[0]]
      .slice()
      .sort((a: any, b: any) => a[timeField] - b[timeField])
      .map((point: any) => point[timeField]);
    
    // Generate datasets, sorting by the time field and extracting values in the sorted order
    const datasets = data.line_graph.map((pollutantObj: any) => {
      const pollutantKey = Object.keys(pollutantObj)[0]; // Get pollutant key (e.g., "MP2.5", "O3")
      const points = pollutantObj[pollutantKey]
        .slice()
        .sort((a: any, b: any) => a[timeField] - b[timeField]); // Sort by the dynamic time field
    
      return {
        label: pollutantKey, // Pollutant name as label
        data: points.map((point: any) => point.average_value), // Extract sorted average values
        borderColor: 'rgb(75, 192, 192)', // Customize color
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

    if (this.chart) {
      this.chart.destroy();
    }
    this.chart = new Chart('lineChartCanvas', config);
  }
}
