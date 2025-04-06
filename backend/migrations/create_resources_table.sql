CREATE TABLE IF NOT EXISTS resources (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    quantity FLOAT,
    unit VARCHAR(50),
    status VARCHAR(50) NOT NULL,
    location VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_resources_organization_id ON resources(organization_id);
CREATE INDEX IF NOT EXISTS idx_resources_resource_type ON resources(resource_type);
CREATE INDEX IF NOT EXISTS idx_resources_status ON resources(status);
