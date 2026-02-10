-- Optimization SQL
-- 1. Add columns for pre-calculated coordinates
ALTER TABLE parcels ADD COLUMN IF NOT EXISTS center_lat FLOAT;
ALTER TABLE parcels ADD COLUMN IF NOT EXISTS center_lng FLOAT;

-- 2. Populate the coordinates (one-time cost)
UPDATE parcels 
SET 
    center_lat = ST_Y(ST_Centroid(ST_Transform(geometry, 4326))),
    center_lng = ST_X(ST_Centroid(ST_Transform(geometry, 4326)))
WHERE center_lat IS NULL;

-- 3. Create Indexes for fast filtering and sorting
CREATE INDEX IF NOT EXISTS idx_parcels_viability ON parcels (viability_score DESC);
CREATE INDEX IF NOT EXISTS idx_parcels_town ON parcels ("TOWN_ID");
CREATE INDEX IF NOT EXISTS idx_parcels_geom ON parcels USING GIST (geometry);
