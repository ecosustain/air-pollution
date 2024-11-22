import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule, DatePipe } from '@angular/common';
import { indicators } from '../../models/indicators.models';
import { interpolatorMethods } from '../../models/interpolator-methods.models';


@Component({
  selector: 'app-heatmap-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, DatePipe],
  templateUrl: './heatmap-form.component.html',
  styleUrls: ['./heatmap-form.component.css']
})
export class HeatmapFormComponent implements OnInit {
  mapaDeCalorForm: FormGroup;
  intervalType: string = '';
  methodType: string = '';
  indicators = indicators
  interpolatorMethods = interpolatorMethods

  @Output() formSubmit = new EventEmitter<any>();

  constructor(
    private fb: FormBuilder,
    private datePipe: DatePipe
  ) {
    this.mapaDeCalorForm = this.fb.group({
      indicator: ['', Validators.required],
      interpolator : this.fb.group({
        method: ['', Validators.required],
        params: this.fb.group({})
      }),
      interval: ['', Validators.required],
    });
  }

  ngOnInit(): void {}

  onIntervalChange(event: Event) {
    const selectedValue = (event.target as HTMLSelectElement).value;
    this.intervalType = selectedValue;
    this.clearTimeDynamicControls();

    if(this.intervalType === 'yearly') {
      this.mapaDeCalorForm.addControl('firstYear', this.fb.control('', Validators.required));
      this.mapaDeCalorForm.addControl('lastYear', this.fb.control('', Validators.required));
    } else {
      this.mapaDeCalorForm.addControl('year', this.fb.control('', Validators.required));
      if(this.intervalType != 'monthly'){
        this.mapaDeCalorForm.addControl('month', this.fb.control('', Validators.required));
        if (this.intervalType != 'daily') {
          this.mapaDeCalorForm.addControl('day', this.fb.control('', Validators.required));
          if(this.intervalType != 'hourly') {
            this.mapaDeCalorForm.addControl('hour', this.fb.control('', Validators.required));
          }
        }
      }
    }

    this.mapaDeCalorForm.updateValueAndValidity();
  }

  onMethodChange(event: Event) {
    this.methodType = (event.target as HTMLSelectElement).value;
    const params = this.mapaDeCalorForm.get('interpolator')?.get('params') as FormGroup;
    
    this.clearParamsDynamicControls();
  
    const selectedMethod = this.interpolatorMethods.find(method => method.name === this.methodType);
  
    if (selectedMethod) {
      selectedMethod.params.forEach(param => {
        const control = this.fb.control(param.type === 'checkbox' ? false : '', Validators.required);
        params.addControl(param.name, control);
      });
    }

    params.updateValueAndValidity();
  }
  

  get selectedMethodParams() {
    const selectedMethod = this.interpolatorMethods.find(method => method.name === this.methodType);
    return selectedMethod ? selectedMethod.params : [];
  }

  clearTimeDynamicControls() {
    ['firstYear', 'lastYear', 'year', 'month', 'day', 'hour'].forEach(control => {
      this.mapaDeCalorForm.removeControl(control);
    });
  }

  clearParamsDynamicControls() {
    const params = this.mapaDeCalorForm.get('interpolator.params') as FormGroup;
  
    Object.keys(params.controls).forEach(control => {
      params.removeControl(control);
    });
    
    params.reset();
    params.clearValidators();
  }
  
  formatDatePart(
    format: string,
    year: number, 
    month?: number, 
    day?: number, 
    hour?: number, 
  ): string {
    const date = new Date(
      year, 
      (month || 1) - 1, 
      day || 1, 
      hour || 0
    );
    return this.datePipe.transform(date, format) || '';
  }
  
  formatDate(heatmapForm: any): any {
    const newFormValue = { ...heatmapForm };
  
    switch (newFormValue.interval) {
      case 'instant':
        newFormValue.hour = this.formatDatePart(
          'yyyy-MM-dd HH:mm:ss',          
          newFormValue.year, 
          newFormValue.month, 
          newFormValue.day, 
          newFormValue.hour
        );
        this.removeKeys(newFormValue, ['year', 'month', 'day']);
        break;
  
      case 'hourly':
        newFormValue.day = this.formatDatePart(
          'yyyy-MM-dd',
          newFormValue.year, 
          newFormValue.month, 
          newFormValue.day, 
          undefined
        );
        this.removeKeys(newFormValue, ['year', 'month']);
        break;
  
      case 'daily':
        newFormValue.month = this.formatDatePart(
          'yyyy-MM',
          newFormValue.year, 
          newFormValue.month, 
          undefined, 
          undefined
        );
        this.removeKeys(newFormValue, ['year']);
        break;
  
      case 'monthly':
        newFormValue.year = newFormValue.year.toString();
        break;
  
      case 'yearly':
        newFormValue.first_year = newFormValue.firstYear.toString();
        newFormValue.last_year = newFormValue.lastYear.toString();
        this.removeKeys(newFormValue, ['firstYear', 'lastYear']);
        break;
  
      default:
        console.error('Unknown interval:', newFormValue.interval);
        break;
    }
  
    return newFormValue;
  }
  
  private removeKeys(object: any, keys: string[]): void {
    keys.forEach((key) => delete object[key]);
  }
   

  onSubmit() {
    if (this.mapaDeCalorForm.valid) {
      const formValue = this.mapaDeCalorForm.value;
      const newFormValue = this.formatDate(formValue);
      console.log("Completed form", this.mapaDeCalorForm.value);
      console.log("Emmited form", newFormValue);
      this.formSubmit.emit(newFormValue);
    } else {
      console.log('Form is invalid:', this.mapaDeCalorForm.value);
    }
  }
}
