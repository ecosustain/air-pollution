import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HeatmapFormComponent } from "../heatmap-form/heatmap-form.component";
import { HeatmapComponent } from "../heatmap/heatmap.component";
import { GraphComponent } from "../graph/graph.component";
import { Point } from '../../models/point.model';
import { HeatmapService } from '../../services/heatmap/heatmap.service';


@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, HeatmapFormComponent, HeatmapComponent, GraphComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit{
  formChoice : FormGroup;
  chosenForm : string = "Mapa de Calor";

  heatmapPoints : Point[] = [];
  errorMessage : string = ''

  constructor (private fb : FormBuilder, private heatmapService: HeatmapService) {
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

  handleFormSubmit(formValues: any) {
    const { date, indicator, method, params } = formValues;

    this.heatmapService.getInterpolatedPoints(date, indicator, method, params)
      .subscribe({
        next: (points) => {
          this.heatmapPoints = points;
        },
        error: (err) => {
          this.errorMessage = 'Failed to retrieve points';
          console.error(err);
        }
      });
  }
}
