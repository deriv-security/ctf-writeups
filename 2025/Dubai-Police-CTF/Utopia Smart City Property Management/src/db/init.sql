USE smartcity;

DROP TABLE IF EXISTS users;

CREATE TABLE
    users (
        idx INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(128) NOT NULL,
        password VARCHAR(128) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

DROP TABLE IF EXISTS properties;

CREATE TABLE
    properties (
        idx INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(96) NOT NULL,
        description TEXT NOT NULL,
        address VARCHAR(255) NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        property_type ENUM ('apartment', 'house', 'condo', 'studio') DEFAULT 'apartment',
        bedrooms INT DEFAULT 1,
        bathrooms INT DEFAULT 1,
        area_sqft INT DEFAULT 500,
        amenities TEXT,
        contact_info VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );

INSERT INTO
    users (username, password)
VALUES
    ('admin', 'admin_password'),
    ('guest', 'guest'),
    ('resident', 'resident123'),
    ('visitor', 'visitor456');

INSERT INTO
    properties (
        title,
        description,
        address,
        price,
        property_type,
        bedrooms,
        bathrooms,
        area_sqft,
        amenities,
        contact_info
    )
VALUES
    (
        'Skyline Tower Apartment',
        'Modern apartment with smart home features and panoramic city view. Located in the heart of UTOPIA''s innovation district with easy access to public transport and tech companies.',
        '123 Innovation Boulevard, UTOPIA District 1',
        2500.00,
        'apartment',
        2,
        2,
        1200,
        '["smart_thermostat", "high_speed_internet", "gym", "rooftop_garden", "concierge"]',
        'contact@skylinetower.utopia'
    ),
    (
        'Green Valley House',
        'Eco-friendly house with solar panels, smart energy management, and private garden. Perfect for families who value sustainability and modern living.',
        '456 Sustainability Street, UTOPIA District 2',
        3200.00,
        'house',
        3,
        2,
        1800,
        '["solar_panels", "garden", "electric_car_charging", "smart_security", "energy_efficient"]',
        'info@greenvalley.utopia'
    ),
    (
        'Tech Hub Studio',
        'Compact studio perfect for digital nomads and tech professionals. Located in the tech quarter with co-working spaces and innovation labs nearby.',
        '789 Innovation Avenue, UTOPIA Tech Quarter',
        1800.00,
        'studio',
        1,
        1,
        600,
        '["high_speed_internet", "co_working_space", "smart_lighting", "24_7_security"]',
        'hello@techhub.utopia'
    ),
    (
        'Luxury Penthouse',
        'Premium penthouse with panoramic city views and smart home automation. Features private elevator and access to exclusive amenities.',
        '321 Elite Heights, UTOPIA Central',
        5500.00,
        'condo',
        4,
        3,
        2500,
        '["panoramic_views", "private_elevator", "smart_home_system", "concierge", "spa"]',
        'luxury@eliteheights.utopia'
    ),
    (
        'Smart Family Home',
        'Family-friendly home with integrated IoT systems, automated climate control, and secure smart locks. Located in a quiet residential area.',
        '654 Family Lane, UTOPIA Residential Zone',
        2800.00,
        'house',
        3,
        2,
        1600,
        '["smart_locks", "automated_climate", "security_system", "playground_nearby"]',
        'family@smarthomes.utopia'
    ),
    (
        'Urban Loft',
        'Industrial-style loft with exposed brick, smart lighting, and high-speed connectivity. Perfect for creative professionals and artists.',
        '987 Creative District, UTOPIA Arts Quarter',
        2200.00,
        'apartment',
        2,
        1,
        1000,
        '["exposed_brick", "smart_lighting", "artist_studio", "high_ceilings"]',
        'loft@urbanliving.utopia'
    );

DROP TABLE IF EXISTS flag;

CREATE TABLE
    flag (flag TEXT);
