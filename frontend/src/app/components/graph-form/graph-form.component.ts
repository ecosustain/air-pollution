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

  translateTimePeriod(originalTimePeriod: string) {
    const translations = new Map<string, string>([
      ["anual", "yearly"],
      ["mensal", "monthly"],
      ["mensal 2", "monthly"],
      ["diária", "daily"],
      ["horária", "hourly"]
    ]);
    return translations.get(originalTimePeriod);
  }

  onSubmit() {
    this.graphForm.markAllAsTouched();
    if (this.graphForm.valid) {
      // Structure formData with timePeriod and specificDate, as well as additional fields based on interval
      const formData: any = {
        timePeriod: this.translateTimePeriod(this.graphForm.value.timePeriod.toLowerCase()),
        indicators: this.graphForm.value.indicators,
        specificDate: {
          year: this.graphForm.value.specificDate.year || null,
          month: this.graphForm.value.specificDate.month || null
        },
        month: this.graphForm.value.month || null
      };
  
      // Adjust specificDate and month based on interval
      if (formData.timePeriod === 'monthly' || formData.timePeriod === 'hourly') {
        formData.specificDate = null;  // Clear specificDate for monthly/hourly intervals
      } 
      if (formData.timePeriod === 'daily') {
        formData.month = null;  // Only specificDate should be populated for daily
      } 
  
      console.log('Form submitted:', formData); // Log the structured form data
  
      this.formSubmit.emit(formData);  // Emit the form data to the parent component (GraphComponent)
    } else {
      console.log('Form is invalid');
    }
  }  
}
