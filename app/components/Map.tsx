'use client';

import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || '';

interface MapProps {
  filters: {
    minAcreage: number;
    gridViable: boolean;
    lowWetland: boolean;
  };
}

const Map = ({ filters }: MapProps) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [lng] = useState(-72.52);
  const [lat] = useState(42.37);
  const [zoom] = useState(12);

  useEffect(() => {
    if (map.current) return;
    if (!mapContainer.current) return;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: [lng, lat],
      zoom: zoom
    });

    map.current.on('load', async () => {
      if (!map.current) return;

      // Add source
      map.current.addSource('parcels', {
        type: 'geojson',
        data: '/api/parcels'
      });

      // Add layer
      map.current.addLayer({
        id: 'parcels-fill',
        type: 'fill',
        source: 'parcels',
        paint: {
          'fill-color': [
            'case',
            ['==', ['get', 'status', ['get', 'grid']], 'VIABLE'], '#fbbf24', // yellow-400
            '#4b5563' // gray-600 fallback
          ],
          'fill-opacity': 0.6,
          'fill-outline-color': '#ffffff'
        }
      });

      // Add hover effect
      map.current.on('mouseenter', 'parcels-fill', () => {
        if (map.current) map.current.getCanvas().style.cursor = 'pointer';
      });

      map.current.on('mouseleave', 'parcels-fill', () => {
        if (map.current) map.current.getCanvas().style.cursor = 'default';
      });
    });

    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  // Update filters
  useEffect(() => {
    if (!map.current || !map.current.isStyleLoaded()) return;

    const filterArray: any[] = ['all'];

    if (filters.gridViable) {
      filterArray.push(['==', ['get', 'status', ['get', 'grid']], 'VIABLE']);
    }

    if (filters.lowWetland) {
      filterArray.push(['<', ['get', 'wetlands_overlap_pct', ['get', 'enviro']], 0.2]);
    }

    // Min acreage check (LOT_SIZE in MassGIS is often acres)
    filterArray.push(['>=', ['get', 'lot_size'], filters.minAcreage]);

    map.current.setFilter('parcels-fill', filterArray.length > 1 ? filterArray : null);
  }, [filters]);

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainer} className="w-full h-full" />
    </div>
  );
};

export default Map;
