SELECT 
    (zoning_status->>'use_type') as use_type,
    (grid_status->>'status') as grid_status,
    (enviro_status->>'status') as enviro_status,
    count(*) 
FROM parcels 
GROUP BY use_type, grid_status, enviro_status;
