import { NextResponse } from 'next/server';
import pool from '@/lib/db';

export async function GET() {
  try {
    const query = `
      SELECT 
        "OBJECTID",
        "SITE_ADDR",
        "LOT_SIZE",
        viability_score,
        viability_rank,
        enviro_status,
        grid_status,
        zoning_status,
        physical_status,
        legal_social_status,
        infrastructure_status,
        ST_AsGeoJSON(geometry)::json as geometry
      FROM parcels
      WHERE geometry IS NOT NULL
      ORDER BY viability_score DESC
      LIMIT 5000;
    `;

    const result = await pool.query(query);

    const geojson = {
      type: 'FeatureCollection',
      features: result.rows.map((row) => ({
        type: 'Feature',
        id: row.OBJECTID,
        geometry: row.geometry,
        properties: {
          id: row.OBJECTID,
          address: row.SITE_ADDR,
          lot_size: row.LOT_SIZE,
          score: row.viability_score,
          rank: row.viability_rank,
          enviro: row.enviro_status,
          grid: row.grid_status,
          zoning: row.zoning_status,
          physical: row.physical_status,
          legal: row.legal_social_status,
          infra: row.infrastructure_status,
        },
      })),
    };

    return NextResponse.json(geojson);
  } catch (error) {
    console.error('Database error:', error);
    return NextResponse.json({ error: 'Failed to fetch parcels' }, { status: 500 });
  }
}
