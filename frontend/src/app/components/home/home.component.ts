import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HeatmapFormComponent } from "../heatmap-form/heatmap-form.component";
import { HeatmapComponent } from "../heatmap/heatmap.component";
import { GraphComponent } from "../graph/graph.component";
import { Point } from '../../models/point.model';
import { HeatmapService } from '../../services/heatmap/heatmap.service';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule, 
    ReactiveFormsModule, 
    HeatmapFormComponent, 
    HeatmapComponent, 
    GraphComponent,
    DatePipe],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit{
  formChoice : FormGroup;
  chosenForm : string = "Mapa de Calor";

  heatmapPoints : Point[] = [];
  errorMessage : string = ''

  constructor (
    private fb : FormBuilder, 
    private heatmapService: HeatmapService,
    private datePipe: DatePipe) 
    {
    this.formChoice = this.fb.group({
      formKind : ["Mapa de Calor", Validators.required]
    })
  }

  ngOnInit(): void {
    
  }

  onChoiceChange (event : Event) {
    const selectElement = event.target as HTMLSelectElement; // Cast to HTMLSelectElement
    const selectedValue = selectElement.value; // Now we can safely access .value
    this.chosenForm = selectedValue;
  }

  formatDate(day: number, month: number, year: number, hour: number): string {
    const date = new Date(year, month - 1, day, hour); // month is 0-indexed in Date object
    return this.datePipe.transform(date, 'yyyy-MM-dd HH:mm:ss') || '';
  }

  handleFormSubmit(formValues: any) {
    const date = this.formatDate(
                            formValues.specificDate.day, 
                            formValues.specificDate.month, 
                            formValues.specificDate.year,
                            formValues.specificDate.hour);
    
    const indicator = formValues.indicator;
    const method = formValues.method;
    const param = formValues.param;

    this.heatmapService.getInterpolatedPoints(date, indicator, method, param)
      .subscribe({
        next: (points) => {
          console.log('Requisição deu certo')
          this.heatmapPoints = points.heat_map;
        },
        error: (err) => {
          this.errorMessage = 'Failed to retrieve points';
          console.error(err);
        }
      });
  }
}
