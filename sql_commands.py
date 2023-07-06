commands = {
    'CreateExchangeTable':'''
        CREATE TABLE IF NOT EXISTS Exchange (
            id SERIAL PRIMARY KEY, 
            abbreviation VARCHAR(32) NOT NULL, 
            name VARCHAR(255) NOT NULL, 
            website_url VARCHAR(255) NULL, 
            city VARCHAR(255) NULL, 
            country VARCHAR(255) NULL, 
            currency VARCHAR(64) NULL, 
            time_zone_offset TIME NULL, 
            created_datetime TIMESTAMP NOT NULL, 
            last_updated_datetime TIMESTAMP NOT NULL
        );
    ''',
    'CreateDataVendorTable':'''
        CREATE TABLE IF NOT EXISTS DataVendor (
            id SERIAL PRIMARY KEY, 
            name VARCHAR(255) NOT NULL,
            website_url VARCHAR(255) NULL,  
            support_email VARCHAR(255) NULL,  
            created_datetime TIMESTAMP NOT NULL, 
            last_updated_datetime TIMESTAMP NOT NULL
        );
    ''',
    'CreateSymbolTable':'''
        CREATE TABLE IF NOT EXISTS Symbol (
            id SERIAL PRIMARY KEY, 
            exchange_id INT NULL,
            ticker VARCHAR(64) NOT NULL,
            instrument VARCHAR(64) NOT NULL,
            name VARCHAR(255) NULL,
            sector VARCHAR(255) NULL,  
            currency VARCHAR(64) NULL,
            linked_table VARCHAR(32) NOT NULL UNIQUE, 
            created_datetime TIMESTAMP NOT NULL, 
            last_updated_datetime TIMESTAMP NOT NULL, 
            CONSTRAINT index_exchange_id
                FOREIGN KEY(exchange_id)
                    REFERENCES Exchange(id) 
        );
    ''',
}