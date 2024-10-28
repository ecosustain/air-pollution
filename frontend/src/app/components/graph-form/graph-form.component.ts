import { Component, OnInit, Output, EventEmitter} from '@angular/core';
import { FormBuilder, FormGroup, FormArray, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-graph-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './graph-form.component.html',
  styleUrl: './graph-form.component.css'
})
export class GraphFormComponent implements OnInit {
  graphForm: FormGroup;
  pollutants = ['MP2.5', 'MP2.10', 'O3'];
  timePeriodType: string = '';
  @Output() formSubmit = new EventEmitter<any>();

  constructor(private fb: FormBuilder) {
    this.graphForm = this.fb.group({
      indicators: this.fb.array([], Validators.required),
      timePeriod: ['', Validators.required], 
      month: [''],        
      specificDate: this.fb.group({   
        month: [''],
        year: ['']
      }),
    });
  }

  get indicatorsArray() {
    return this.graphForm.get('indicators') as FormArray;
  }

  onCheckboxChange(event: any) {
    const indicatorsArray = this.indicatorsArray;
    if (event.target.checked) {
      indicatorsArray.push(this.fb.control(event.target.value));
    } else {
      const index = indicatorsArray.controls.findIndex(
        x => x.value === event.target.value
      );
      if (index > -1) {
        indicatorsArray.removeAt(index);
      }
    }
  }

  ngOnInit(): void {}

  onTimePeriodChange(event: Event) {
    const selectElement = event.target as HTMLSelectElement;
    const selectedValue = selectElement.value;
    this.timePeriodType = selectedValue;
    this.clearValidators();
  
    if ((this.timePeriodType === 'Mensal') || (this.timePeriodType === 'Horária')) {
      this.graphForm.get('month')?.setValidators([Validators.required]);
    } else if (this.timePeriodType === 'Diária') {
      this.graphForm.get('specificDate.month')?.setValidators([Validators.required]);
      this.graphForm.get('specificDate.year')?.setValidators([Validators.required]);
    }

    this.graphForm.updateValueAndValidity();
  }

  clearValidators() {
    this.graphForm.get('month')?.clearValidators();
    this.graphForm.get('specificDate.month')?.clearValidators();
    this.graphForm.get('specificDate.year')?.clearValidators();

    this.graphForm.get('month')?.reset();
    this.graphForm.get('specificDate')?.reset();
  }

  onSubmit() {
    this.graphForm.markAllAsTouched(); 
    if (this.graphForm.valid) {
      console.log('Form submitted:', this.graphForm.value);
      this.formSubmit.emit(this.graphForm.value);
    } else {
      console.log('Form is invalid');
    }
  }

}
