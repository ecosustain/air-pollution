import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HeatmapFormComponent } from "../heatmap-form/heatmap-form.component";
import { HeatmapComponent } from "../heatmap/heatmap.component";
import { GraphFormComponent } from '../graph-form/graph-form.component';
import { GraphComponent } from "../graph/graph.component";
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
  
  formData: any;
  heatmapFormData : any;
  
  
  errorMessage : string = '';

  constructor (
    private fb : FormBuilder) 
    {
    this.formChoice = this.fb.group({
      formKind : ["Mapa de Calor", Validators.required]
    });
  }

  ngOnInit(): void {
    
  }

  onChoiceChange (event : Event) {
    const selectElement = event.target as HTMLSelectElement;
    const selectedValue = selectElement.value;
    this.chosenForm = selectedValue;
  }

  handleHeatmapFormSubmit(formData: any) {
    this.heatmapFormData = formData;
    console.log('Heatmap form submitted and data passed to heatmap:', formData);
  }

  handleGraphFormSubmit(formData: any): void {
    this.formData = formData;
    console.log('Graph form submitted and data passed to graph:', formData);
  }


}
