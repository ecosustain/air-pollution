import { Component, OnInit, Output, EventEmitter, Input} from '@angular/core';
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
  indicators = [
    'MP2.5', 'MP10', 'O3', "BEN", "CO", "DV", "DVG", "ERT", "NO", 
    "NO2", "NOX", "PRESS", "RADG", "RADUV", "SO2", "TEMP", "TOL",
    "UR", "VV"
  ];
  timePeriodType: string = '';
  @Output() formSubmit = new EventEmitter<any>();
  @Input() isLoading : boolean = false;

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
    if(this.isLoading){
      console.log("Application is loading: can't submit graph form now.");
    }
    else{
      this.graphForm.markAllAsTouched();
      if (this.graphForm.valid) {
        const formData: any = {
          timePeriod: this.translateTimePeriod(this.graphForm.value.timePeriod.toLowerCase()),
          indicators: this.graphForm.value.indicators,
          specificDate: {
            year: this.graphForm.value.specificDate.year || null,
            month: this.graphForm.value.specificDate.month || null
          },
          month: this.graphForm.value.month || null
        };
    
        if (formData.timePeriod === 'monthly' || formData.timePeriod === 'hourly')
          formData.specificDate = null;
        if (formData.timePeriod === 'daily')
          formData.month = null;
    
        console.log('Form submitted:', formData);
        this.formSubmit.emit(formData);
      } else {
        console.log('Form is invalid');
      }
    }
  }

  private translateTimePeriod(originalTimePeriod: string) {
    const translations = new Map<string, string>([
      ["anual", "yearly"],
      ["mensal", "monthly"],
      ["mensaltotal", "monthly"],
      ["diária", "daily"],
      ["horária", "hourly"]
    ]);
    return translations.get(originalTimePeriod);
  }
}
