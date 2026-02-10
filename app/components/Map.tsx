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
  onParcelSelect: (parcel: any) => void;
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
      zoom: zoom
    });

    map.current.on('load', async () => {
      if (!map.current) return;

      map.current.addSource('parcels', {
        type: 'geojson',
        data: '/api/parcels',
        promoteId: 'id'
      });

      // Layer 1: Viability Heatmap
      map.current.addLayer({
        id: 'parcels-fill',
        type: 'fill',
        source: 'parcels',
        paint: {
          'fill-color': [
            'interpolate',
            ['linear'],
            ['get', 'score'],
            0, '#ef4444',   // Red (Poor)
            0.5, '#f59e0b', // Amber (Fair)
            0.8, '#10b981'  // Green (Excellent)
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
          'line-opacity': 0.3
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
          const props = { ...feature.properties };
          
          ['enviro', 'grid', 'zoning', 'physical', 'legal', 'infra'].forEach(key => {
            if (typeof props[key] === 'string') {
              try { props[key] = JSON.parse(props[key]); } catch(e) {}
            }
          });

          onParcelSelect(props);
          if (map.current) {
            map.current.setFilter('parcels-highlight', ['==', ['get', 'id'], props.id]);
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
          if (map.current) {
            map.current.setFeatureState({ source: 'parcels', id: hoveredStateId }, { hover: true });
            map.current.getCanvas().style.cursor = 'pointer';
          }
        }
      });

      map.current.on('mouseleave', 'parcels-fill', () => {
        if (hoveredStateId !== null && map.current) {
          map.current.setFeatureState({ source: 'parcels', id: hoveredStateId }, { hover: false });
        }
        hoveredStateId = null;
        if (map.current) map.current.getCanvas().style.cursor = 'default';
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

    const filterArray: any[] = ['all'];
    filterArray.push(['>=', ['get', 'lot_size'], filters.minAcreage]);

    if (filters.gridViable) {
      // Since Mapbox flattens JSON props in get, we might need a better way 
      // or filter on server. For now, let's keep it simple.
    }

    map.current.setFilter('parcels-fill', filterArray.length > 1 ? filterArray : null);
  }, [filters]);

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainer} className="w-full h-full" />
    </div>
  );
};

export default Map;
