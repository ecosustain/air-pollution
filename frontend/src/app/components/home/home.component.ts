import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HeatmapFormComponent } from "../heatmap-form/heatmap-form.component";
import { HeatmapComponent } from "../heatmap/heatmap.component";
import { GraphFormComponent } from '../graph-form/graph-form.component';
import { GraphComponent } from "../graph/graph.component";
import { Heatmaps, Point } from '../../models/point.model';
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
    GraphFormComponent,
    GraphComponent,
    DatePipe],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit{
  formChoice : FormGroup;
  chosenForm : string = "Mapa de Calor";

  heatmapPoints : Point[] = [];
  heatmaps : Heatmaps = {};
  indicator : string = '';
  errorMessage : string = '';

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

  formatHour(year: number, month: number, day: number, hour: number): string {
    const date = new Date(year, month - 1, day, hour); // month is 0-indexed in Date object
    return this.datePipe.transform(date, 'yyyy-MM-dd HH:mm:ss') || '';
  }

  formatDay(year: number, month: number, day: number): string {
    const date = new Date(year, month - 1, day); // month is 0-indexed in Date object
    return this.datePipe.transform(date, 'yyyy-MM-dd') || '';
  }

  formatMonth(year: number, month: number){
    const date = new Date(year, month - 1); // month is 0-indexed in Date object
    return this.datePipe.transform(date, 'yyyy-MM-dd') || '';
  }

  handleFormSubmit(formValues: any) {
    let payload = formValues

    if(formValues.interval === "instant") {
      payload.hour = this.formatHour(
        formValues.specificDate.year,
        formValues.specificDate.month, 
        formValues.specificDate.day, 
        formValues.specificDate.hour);
      delete payload["specificDate"];
    } else if (formValues.interval === "hourly"){
      payload.day = this.formatDay(
        formValues.specificDate.year,
        formValues.specificDate.month, 
        formValues.specificDate.day) 
        delete payload["specificDate"];
    } else if (formValues.interval === "daily"){
      payload.month = this.formatMonth(
        formValues.specificDate.year,
        formValues.specificDate.month
      );
      delete payload["specificDate"];
    } else if (formValues.interval === "monthly"){
      payload.year = formValues.specificDate.year;
      delete payload["specificDate"];
    } else if (formValues.interval === "yearly"){
      payload.first_year = formValues.firstYear;
      payload.last_year = formValues.lastYear;
    }

    this.heatmapService.getInterpolatedHeatmap(payload)
      .subscribe({
        next: (heatmapResponse) => {
          console.log('Query did okay');
          this.heatmaps = heatmapResponse.heatmaps;
          this.indicator = payload.indicator;
        },
        error: (err) => {
          this.errorMessage = 'Failed to retrieve points';
          console.error(err);
        }
      });
  }
}
