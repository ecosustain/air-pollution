import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';


@Component({
  selector: 'app-heatmap-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './heatmap-form.component.html',
  styleUrl: './heatmap-form.component.css'
})
export class HeatmapFormComponent implements OnInit {
  mapaDeCalorForm: FormGroup;
  timePeriodType: string = '';

  constructor(private fb: FormBuilder) {
    this.mapaDeCalorForm = this.fb.group({
      indicator: ['', Validators.required],  
      timePeriod: ['', Validators.required], 
      startYear: [''],    
      endYear: [''],     
      year: [''],        
      specificDate: this.fb.group({   
        day: [''],
        month: [''],
        year: ['']
      })
    });
  }

  ngOnInit(): void {}

  // Handle time period change
  onTimePeriodChange(event: Event) {
    const selectElement = event.target as HTMLSelectElement; // Cast to HTMLSelectElement
    const selectedValue = selectElement.value; // Now we can safely access .value
    this.timePeriodType = selectedValue;
  
    // Clear previous validators
    this.clearValidators();
  
    // Set validators based on the selected value
    if (selectedValue === 'Anual') {
      this.mapaDeCalorForm.get('startYear')?.setValidators([Validators.required]);
      this.mapaDeCalorForm.get('endYear')?.setValidators([Validators.required]);
    } else if (selectedValue === 'Mensal') {
      this.mapaDeCalorForm.get('year')?.setValidators([Validators.required]);
    } else if (selectedValue === 'Horária') {
      this.mapaDeCalorForm.get('specificDate.day')?.setValidators([Validators.required]);
      this.mapaDeCalorForm.get('specificDate.month')?.setValidators([Validators.required]);
      this.mapaDeCalorForm.get('specificDate.year')?.setValidators([Validators.required]);
    }
  
    // Update form validity
    this.mapaDeCalorForm.updateValueAndValidity();
  }

  // Helper function to clear validators from fields when switching time period
  clearValidators() {
    this.mapaDeCalorForm.get('startYear')?.clearValidators();
    this.mapaDeCalorForm.get('endYear')?.clearValidators();
    this.mapaDeCalorForm.get('year')?.clearValidators();
    this.mapaDeCalorForm.get('specificDate.day')?.clearValidators();
    this.mapaDeCalorForm.get('specificDate.month')?.clearValidators();
    this.mapaDeCalorForm.get('specificDate.year')?.clearValidators();
    
    this.mapaDeCalorForm.get('startYear')?.reset();
    this.mapaDeCalorForm.get('endYear')?.reset();
    this.mapaDeCalorForm.get('year')?.reset();
    this.mapaDeCalorForm.get('specificDate')?.reset();
  }

  // Form submission
  onSubmit() {
    if (this.mapaDeCalorForm.valid) {
      console.log('Form submitted:', this.mapaDeCalorForm.value);
    } else {
      console.log('Form is invalid');
    }
  }
}
