import { Component, OnInit, Output, EventEmitter, Input } from '@angular/core';
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
  indicators = indicators;
  interpolatorMethods = interpolatorMethods;
  selectedMethodParams: any[] = [];

  @Output() formSubmit = new EventEmitter<any>();
  @Input() isLoading : boolean = false;

  constructor(private fb: FormBuilder, private datePipe: DatePipe) {
    this.mapaDeCalorForm = this.createForm();
  }

  ngOnInit(): void {}

  /**
   * Initializes the base form group structure
  */
  private createForm(): FormGroup {
    return this.fb.group({
      indicator: ['', Validators.required],
      interpolator: this.fb.group({
        method: ['', Validators.required],
        params: this.fb.group({})
      }),
      interval: ['', Validators.required]
    });
  }
  /**
   * Handles interval type changes and dynamically updates form controls
  */
  onIntervalChange(event: Event): void {
    const selectedValue = (event.target as HTMLSelectElement).value;
    this.intervalType = selectedValue;

    this.resetDynamicControls(['firstYear', 'lastYear', 'year', 'month', 'day', 'hour']);

    const controlsToAdd = this.getControlsForInterval(this.intervalType);
    controlsToAdd.forEach(({ name, validator }) =>
      this.mapaDeCalorForm.addControl(name, this.fb.control('', validator))
    );

    this.mapaDeCalorForm.updateValueAndValidity();
  }


  /**
   * Handles method changes and dynamically updates parameters
  */
  onMethodChange(event: Event): void {
    this.methodType = (event.target as HTMLSelectElement).value;
    const params = this.mapaDeCalorForm.get('interpolator.params') as FormGroup;

    this.resetDynamicControls(Object.keys(params.controls), params);

    const selectedMethod = this.interpolatorMethods.find(method => method.name === this.methodType);
    if (selectedMethod) {
      this.selectedMethodParams = selectedMethod.params;
      selectedMethod.params.forEach(param =>
        params.addControl(
          param.name,
          this.fb.control(param.type === 'checkbox' ? false : '', Validators.required)
        )
      );
    } else {
      this.selectedMethodParams = [];
    }

    params.updateValueAndValidity();
  }
  
  /**
   * Resets dynamic controls based on the specified keys
  */
  private resetDynamicControls(keys: string[], group: FormGroup = this.mapaDeCalorForm): void {
    keys.forEach(key => group.removeControl(key));
  }

  /**
   * Returns controls based on the selected interval type
  */
  private getControlsForInterval(intervalType: string): { name: string; validator: any }[] {
    const controls: Record<string, { name: string; validator: any }[]> = {
      yearly: [
        { name: 'firstYear', validator: Validators.required },
        { name: 'lastYear', validator: Validators.required }
      ],
      monthly: [{ name: 'year', validator: Validators.required }],
      daily: [
        { name: 'year', validator: Validators.required },
        { name: 'month', validator: Validators.required }
      ],
      hourly: [
        { name: 'year', validator: Validators.required },
        { name: 'month', validator: Validators.required },
        { name: 'day', validator: Validators.required }
      ],
      instant: [
        { name: 'year', validator: Validators.required },
        { name: 'month', validator: Validators.required },
        { name: 'day', validator: Validators.required },
        { name: 'hour', validator: Validators.required }
      ]
    };

    return controls[intervalType] || [];
  }

  /**
   * Formats a date based on the specified parts and format
  */
  formatDatePart(format: string, year: number, month?: number, day?: number, hour?: number): string {
    const date = new Date(year, (month || 1) - 1, day || 1, hour || 0);
    return this.datePipe.transform(date, format) || '';
  }

  /**
   * Formats the form date fields based on interval type
  */
  formatDate(formValue: any): any {
    const newFormValue = { ...formValue };

    /**
     * Define formatting strategies for each interval type
    */
    const formattingStrategies: Record<string, () => void> = {
      instant: () => {
        newFormValue.hour = this.formatDatePart(
          'yyyy-MM-dd HH:mm:ss',
          newFormValue.year,
          newFormValue.month,
          newFormValue.day,
          newFormValue.hour
        );
        this.removeKeys(newFormValue, ['year', 'month', 'day']);
      },
      hourly: () => {
        newFormValue.day = this.formatDatePart(
          'yyyy-MM-dd',
          newFormValue.year,
          newFormValue.month,
          newFormValue.day
        );
        this.removeKeys(newFormValue, ['year', 'month']);
      },
      daily: () => {
        newFormValue.month = this.formatDatePart(
          'yyyy-MM',
          newFormValue.year,
          newFormValue.month
        );
        this.removeKeys(newFormValue, ['year']);
      },
      monthly: () => {
        newFormValue.year = newFormValue.year.toString();
      },
      yearly: () => {
        newFormValue.first_year = newFormValue.firstYear.toString();
        newFormValue.last_year = newFormValue.lastYear.toString();
        this.removeKeys(newFormValue, ['firstYear', 'lastYear']);
      }
    };

    formattingStrategies[newFormValue.interval]?.();

    return newFormValue;
  }

  /**
    * Utility to remove specified keys from an object
  */
  private removeKeys(object: any, keys: string[]): void {
    keys.forEach(key => delete object[key]);
  }
  
  /**
    * Handles form submission
  */
  onSubmit(): void {
    if(this.isLoading){
      console.log("Application is loading: can't submit heatmap form now.");
    }
    else{
      if (this.mapaDeCalorForm.valid) {
        const formValue = this.mapaDeCalorForm.value;
        const formattedValue = this.formatDate(formValue);
        console.log('Completed form', formValue);
        console.log('Emitted form', formattedValue);
        this.formSubmit.emit(formattedValue);
      } else {
        console.error('Form is invalid:', this.mapaDeCalorForm.value);
      }
    }
  }
}
