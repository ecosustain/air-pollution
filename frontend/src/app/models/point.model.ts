export interface Point {
    lat: number;
    long: number;
    value: number;
}

export interface Heatmaps {
    [key: string]: Point[];
}

export interface HeatmapResponse {
    heatmaps: Heatmaps;
}
