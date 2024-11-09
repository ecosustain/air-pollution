import { Component, OnInit, Output, EventEmitter} from '@angular/core';
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
  @Output() formSubmit = new EventEmitter<any>();

  constructor(private fb: FormBuilder) {
    this.mapaDeCalorForm = this.fb.group({
      indicator: ['', Validators.required],
      method:['', Validators.required],
      param:['', Validators.required], 
      timePeriod: ['', Validators.required], 
      startYear: [''],    
      endYear: [''],     
      year: [''],        
      specificDate: this.fb.group({   
        day: [''],
        month: [''],
        year: [''],
        hour : ['']
      }),
    });
  }

  ngOnInit(): void {}

  onTimePeriodChange(event: Event) {
    const selectElement = event.target as HTMLSelectElement;
    const selectedValue = selectElement.value;
    this.timePeriodType = selectedValue;
    this.clearValidators();
  
    if (this.timePeriodType === 'Anual') {
      this.mapaDeCalorForm.get('startYear')?.setValidators([Validators.required]);
      this.mapaDeCalorForm.get('endYear')?.setValidators([Validators.required]);
    } else if (this.timePeriodType === 'Mensal') {
      this.mapaDeCalorForm.get('year')?.setValidators([Validators.required]);
    } else if (this.timePeriodType === 'Diária' || this.timePeriodType === 'Horária' ) {
      this.mapaDeCalorForm.get('specificDate.day')?.setValidators([Validators.required]);
      this.mapaDeCalorForm.get('specificDate.month')?.setValidators([Validators.required]);
      this.mapaDeCalorForm.get('specificDate.year')?.setValidators([Validators.required]);
      this.mapaDeCalorForm.get('specificDate.hour')?.setValidators([Validators.required]);
    }
    this.mapaDeCalorForm.updateValueAndValidity();
  }

  clearValidators() {
    this.mapaDeCalorForm.get('startYear')?.clearValidators();
    this.mapaDeCalorForm.get('endYear')?.clearValidators();
    this.mapaDeCalorForm.get('year')?.clearValidators();
    this.mapaDeCalorForm.get('specificDate.day')?.clearValidators();
    this.mapaDeCalorForm.get('specificDate.month')?.clearValidators();
    this.mapaDeCalorForm.get('specificDate.year')?.clearValidators();
    this.mapaDeCalorForm.get('specificDate.hour')?.clearValidators();

    this.mapaDeCalorForm.get('startYear')?.reset();
    this.mapaDeCalorForm.get('endYear')?.reset();
    this.mapaDeCalorForm.get('year')?.reset();
    this.mapaDeCalorForm.get('specificDate')?.reset();
  }

  onSubmit() {
    if (this.mapaDeCalorForm.valid) {
      console.log('Form submitted:', this.mapaDeCalorForm.value);
      this.formSubmit.emit(this.mapaDeCalorForm.value);
    } else {
      console.log('Form is invalid');
    }
  }
}
