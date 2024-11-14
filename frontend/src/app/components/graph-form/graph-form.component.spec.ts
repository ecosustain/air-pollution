import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GraphFormComponent } from './graph-form.component';

describe('GraphFormComponent', () => {
  let component: GraphFormComponent;
  let fixture: ComponentFixture<GraphFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GraphFormComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GraphFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
