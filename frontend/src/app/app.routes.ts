import { Routes } from '@angular/router';
import { HeatmapFormComponent } from './components/heatmap-form/heatmap-form.component';
import { HeatmapComponent } from './components/heatmap/heatmap.component';
import { HomeComponent } from './components/home/home.component';
import { GraphComponent } from './components/graph/graph.component';
import { GraphFormComponent } from './components/graph-form/graph-form.component';
export const routes: Routes = [
    { path: 'heatmap-form', component: HeatmapFormComponent },
    { path: 'heatmap', component : HeatmapComponent },
    { path: 'home', component : HomeComponent },
    { path: 'linegraph-form', component: GraphFormComponent},
    { path: 'linegraph', component: GraphComponent}
];
