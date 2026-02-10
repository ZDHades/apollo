import { NextResponse } from 'next/server';
import pool from '@/lib/db';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get('id');

  // OPTION A: Fetch details for a specific parcel
  if (id && id !== 'undefined' && id !== 'null') {
    try {
      console.log(`Fetching details for parcel ID: ${id}`);
      const query = `
        SELECT 
          "OBJECTID"::text as id,
          "SITE_ADDR" as address,
          "LOT_SIZE" as lot_size,
          viability_score as score,
          viability_rank as rank,
          enviro_status as enviro,
          grid_status as grid,
          zoning_status as zoning,
          physical_status as physical,
          legal_social_status as legal,
          infrastructure_status as infra,
          center_lat as lat,
          center_lng as lng
        FROM parcels
        WHERE "OBJECTID" = $1::bigint;
      `;
      const result = await pool.query(query, [id]);
      
      if (result.rows.length === 0) {
        console.warn(`Parcel ID ${id} not found in database.`);
        return NextResponse.json({ error: 'Parcel not found' }, { status: 404 });
      }
      
      const parcel = result.rows[0];
      parcel.satellite_url = `https://www.google.com/maps/@${parcel.lat},${parcel.lng},400m/data=!3m1!1e3`;
      
      return NextResponse.json(parcel);
    } catch (error) {
      console.error('API Error (Detail):', error);
      return NextResponse.json({ error: 'Failed to fetch details' }, { status: 500 });
    }
  }

  // OPTION B: Fetch summary list for Map/List View
  try {
    const query = `
      SELECT 
        "OBJECTID"::text as id,
        "SITE_ADDR" as address,
        "LOT_SIZE" as lot_size,
        viability_score as score,
        viability_rank as rank,
        center_lat,
        center_lng,
        ST_AsGeoJSON(ST_SimplifyPreserveTopology(geometry, 0.00001))::json as geometry
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
        id: row.id, // Using string ID for consistency
        geometry: row.geometry,
        properties: {
          id: row.id,
          address: row.address,
          lot_size: row.lot_size,
          score: row.score,
          rank: row.rank,
          lat: row.center_lat,
          lng: row.center_lng
        },
      })),
    };

    return NextResponse.json(geojson);
  } catch (error) {
    console.error('API Error (Summary):', error);
    return NextResponse.json({ error: 'Failed to fetch parcels' }, { status: 500 });
  }
}
