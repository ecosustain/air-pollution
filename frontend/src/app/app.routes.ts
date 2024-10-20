import { Routes } from '@angular/router';
import { HeatmapFormComponent } from './heatmap-form/heatmap-form.component';
import { HeatmapComponent } from './heatmap/heatmap.component';
import { HomeComponent } from './home/home.component';
export const routes: Routes = [
    { path: 'heatmap-form', component: HeatmapFormComponent },
    { path: 'heatmap', component : HeatmapComponent },
    { path: 'home', component : HomeComponent }
];
