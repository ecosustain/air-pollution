import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { indicators } from '../../models/indicators.models';
import { interpolatorMethods } from '../../models/interpolator-methods.models';

@Component({
  selector: 'app-heatmap-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
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

  constructor(private fb: FormBuilder) {
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
      const specificDateGroup = this.fb.group({});
      specificDateGroup.addControl('year', this.fb.control('', Validators.required));
      if(this.intervalType != 'monthly'){
        specificDateGroup.addControl('month', this.fb.control('', Validators.required));
        if (this.intervalType != 'daily') {
          specificDateGroup.addControl('day', this.fb.control('', Validators.required));
          if(this.intervalType != 'hourly') {
            specificDateGroup.addControl('hour', this.fb.control('', Validators.required));
          }
        }
      }
      this.mapaDeCalorForm.addControl('specificDate', specificDateGroup);
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
    ['firstYear', 'lastYear', 'specificDate'].forEach(control => {
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
  
  

  onSubmit() {
    if (this.mapaDeCalorForm.valid) {
      const formValue = JSON.parse(JSON.stringify(this.mapaDeCalorForm.value))
      console.log("Emmited form", this.mapaDeCalorForm.value)
      this.formSubmit.emit(formValue);
    } else {
      console.log('Form is invalid:', this.mapaDeCalorForm.value);
    }
  }
}
