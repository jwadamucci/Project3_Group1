DROP TABLE IF EXISTS crop_yields;

CREATE TABLE crop_yields (
    region TEXT,
    crop TEXT,
    year INTEGER,
    yield_hg_ha REAL,
    yield_t_ha REAL,
    rainfall_mm REAL,
    avg_temp_c REAL,
    pesticide_t REAL
);

SELECT * FROM crop_yields; 