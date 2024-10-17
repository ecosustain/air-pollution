import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HeatmapFormComponent } from './heatmap-form.component';

describe('HeatmapFormComponent', () => {
  let component: HeatmapFormComponent;
  let fixture: ComponentFixture<HeatmapFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HeatmapFormComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HeatmapFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
