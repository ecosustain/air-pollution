import { Component, AfterViewInit } from '@angular/core';
import { Chart, ChartConfiguration, ChartData, registerables } from 'chart.js';

Chart.register(...registerables);

@Component({
  selector: 'app-graph',
  standalone: true,
  imports: [],
  templateUrl: './graph.component.html',
  styleUrl: './graph.component.css'
})
export class GraphComponent implements AfterViewInit {
  chart: Chart | undefined;
  sampleData = {
    labels: [
      'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho',
      'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ],
    points: [3, 5, 2, 8, 6, 1, 9, 15, 0, 2, 5, 2]
  };

  ngAfterViewInit() {
    this.createChart();
  }

  createChart() {
    const data: ChartData<'line'> = {
      labels: this.sampleData.labels,
      datasets: [{
        label: 'Concentração MP2.5',
        data: this.sampleData.points,
        borderColor: 'rgb(75, 192, 192)',
        fill: false,
        tension: 0.1
      }]
    };
    

    const config: ChartConfiguration<'line'> = {
      type: 'line',
      data: data,
      options: {
        scales: {
          x: {
            type: 'category',
            title: { display: true, text: 'Meses' }
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
}
