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
  onParcelSelect: (id: string) => void;
}

const Map = ({ filters, onParcelSelect }: MapProps) => {
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
      zoom: zoom,
      fadeDuration: 0
    });

    map.current.on('load', async () => {
      if (!map.current) return;

      map.current.addSource('parcels', {
        type: 'geojson',
        data: '/api/parcels'
      });

      map.current.addLayer({
        id: 'parcels-fill',
        type: 'fill',
        source: 'parcels',
        paint: {
          'fill-color': [
            'interpolate',
            ['linear'],
            ['get', 'score'],
            0, '#ef4444',
            0.5, '#f59e0b',
            0.8, '#10b981'
          ],
          'fill-opacity': [
            'case',
            ['boolean', ['feature-state', 'hover'], false],
            0.9,
            0.6
          ]
        }
      });

      map.current.addLayer({
        id: 'parcels-outline',
        type: 'line',
        source: 'parcels',
        paint: {
          'line-color': '#ffffff',
          'line-width': 0.5,
          'line-opacity': 0.2
        }
      });

      map.current.addLayer({
        id: 'parcels-highlight',
        type: 'line',
        source: 'parcels',
        paint: {
          'line-color': '#ffffff',
          'line-width': 3
        },
        filter: ['==', ['get', 'id'], '']
      });

      map.current.on('click', 'parcels-fill', (e) => {
        if (e.features && e.features.length > 0) {
          const feature = e.features[0];
          const id = feature.properties?.id || feature.id;
          
          if (id) {
            onParcelSelect(String(id));
            if (map.current) {
              map.current.setFilter('parcels-highlight', ['==', ['get', 'id'], String(id)]);
            }
          }
        }
      });

      let hoveredStateId: any = null;
      map.current.on('mousemove', 'parcels-fill', (e) => {
        if (e.features && e.features.length > 0) {
          if (hoveredStateId !== null && map.current) {
            map.current.setFeatureState({ source: 'parcels', id: hoveredStateId }, { hover: false });
          }
          hoveredStateId = e.features[0].id;
          if (hoveredStateId !== null && map.current) {
            map.current.setFeatureState({ source: 'parcels', id: hoveredStateId }, { hover: true });
          }
        }
      });

      map.current.on('mouseleave', 'parcels-fill', () => {
        if (hoveredStateId !== null && map.current) {
          map.current.setFeatureState({ source: 'parcels', id: hoveredStateId }, { hover: false });
        }
        hoveredStateId = null;
      });
    });

    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  useEffect(() => {
    if (!map.current || !map.current.isStyleLoaded()) return;
    map.current.setFilter('parcels-fill', ['>=', ['get', 'lot_size'], filters.minAcreage]);
  }, [filters.minAcreage]);

  return (
    <div className="relative w-full h-full bg-zinc-900">
      <div ref={mapContainer} className="w-full h-full" />
    </div>
  );
};

export default Map;
