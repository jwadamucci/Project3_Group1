-- Drop existing tables if they exist
DROP TABLE IF EXISTS crop_yields;
CREATE TABLE crop_yields (
    Region VARCHAR(50),
    Crop VARCHAR(50),
    Year INT,
    Yield_hg_ha FLOAT,
    Yield_t_ha FLOAT,
    Rainfall_mm FLOAT,
    Avg_temp_c FLOAT,
    Pesticide_t FLOAT
);

-- View data in tables after population
SELECT * FROM crop_yields;
