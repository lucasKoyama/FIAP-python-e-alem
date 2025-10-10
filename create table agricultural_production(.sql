CREATE TABLE agricultural_production (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_name VARCHAR2(100) NOT NULL,
    quantity NUMBER(10,2) NOT NULL,
    sale_price NUMBER(10,2) DEFAULT 0,
    cost_price NUMBER(10,2) DEFAULT 0,
    planting_date DATE,
    harvest_date DATE,
    production_status VARCHAR2(20) DEFAULT 'PLANTED',
    created_at DATE DEFAULT SYSDATE,
    updated_at DATE DEFAULT SYSDATE,
    
    CONSTRAINT chk_quantity_positive CHECK (quantity > 0),
    CONSTRAINT chk_prices_non_negative CHECK (sale_price >= 0 AND cost_price >= 0),
    CONSTRAINT chk_production_status CHECK (production_status IN ('PLANTED', 'HARVESTED', 'SOLD'))
);