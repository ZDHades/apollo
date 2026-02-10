import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://apollo:solar_password@localhost:5432/apollo',
});

export default pool;
