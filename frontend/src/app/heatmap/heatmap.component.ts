import { Component } from '@angular/core';
import { HeatmapFormComponent } from "../heatmap-form/heatmap-form.component";

@Component({
  selector: 'app-heatmap',
  standalone: true,
  imports: [HeatmapFormComponent],
  templateUrl: './heatmap.component.html',
  styleUrl: './heatmap.component.css'
})
export class HeatmapComponent {

}
