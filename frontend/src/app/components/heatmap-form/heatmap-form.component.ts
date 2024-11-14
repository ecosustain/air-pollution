import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

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

    if (this.intervalType === 'yearly') {
      this.mapaDeCalorForm.addControl('startYear', this.fb.control('', Validators.required));
      this.mapaDeCalorForm.addControl('endYear', this.fb.control('', Validators.required));
    } else if (this.intervalType === 'monthly') {
      this.mapaDeCalorForm.addControl('year', this.fb.control('', Validators.required));
    } else if (this.intervalType === 'daily' || this.intervalType === 'hourly') {
      this.mapaDeCalorForm.addControl('specificDate', this.fb.group({
        day: ['', Validators.required],
        month: ['', Validators.required],
        year: ['', Validators.required],
        hour: this.intervalType === 'hourly' ? this.fb.control('', Validators.required) : this.fb.control('')
      }));
    }
    this.mapaDeCalorForm.updateValueAndValidity();
  }

  onMethodChange(event: Event) {
    this.methodType = (event.target as HTMLSelectElement).value;
    const params = this.mapaDeCalorForm.get('interpolator')?.get('params') as FormGroup;
    this.clearParamsDynamicControls();

    if (this.methodType === 'KNN') {
      params.addControl('k', this.fb.control('', Validators.required));
    } else if (this.methodType === 'Krigin') {
      params.addControl('method', this.fb.control('', Validators.required));
      params.addControl('variogram_model', this.fb.control('', Validators.required));
      params.addControl('n_lags', this.fb.control('', Validators.required));
      params.addControl('weight', this.fb.control(false, Validators.required));
    }
    params.updateValueAndValidity();
  }

  clearTimeDynamicControls() {
    ['startYear', 'endYear', 'year', 'specificDate'].forEach(control => {
      this.mapaDeCalorForm.removeControl(control);
    });
  }

  clearParamsDynamicControls() {
    const params = this.mapaDeCalorForm.get('interpolator.params') as FormGroup;
    ['k', 'method', 'variogram_model', 'n_lags', 'weight'].forEach(control => {
      if (params.get(control)) {
        params.removeControl(control);
      }
    });
    params.reset();
    params.clearValidators();
  }
  

  onSubmit() {
    if (this.mapaDeCalorForm.valid) {
      const formValue = this.mapaDeCalorForm.value;
      console.log(formValue)
      this.formSubmit.emit(formValue);
    } else {
      console.log('Form is invalid:', this.mapaDeCalorForm.value);
    }
  }
}
