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
    const labels = data.line_graph[0][Object.keys(data.line_graph[0])[0]]
      .slice()
      .sort((a: any, b: any) => a.year - b.year)
      .map((point: any) => point.year);

    const datasets = data.line_graph.map((pollutantObj: any) => {
      const pollutantKey = Object.keys(pollutantObj)[0];
      const points = pollutantObj[pollutantKey]
        .slice()
        .sort((a: any, b: any) => a.year - b.year);

      return {
        label: pollutantKey, // Use the pollutant key as the label
        data: points.map((point: any) => point.average_value), // Extract the average values for the data
        borderColor: 'rgb(75, 192, 192)', // Customize the color as needed
        fill: false, // Don't fill the area under the line
        tension: 0.1 // Set the line tension (smoothing)
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
            title: { display: true, text: 'Ano' }
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
