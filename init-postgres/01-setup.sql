
-- users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- admin user
INSERT INTO users (id, email, username, first_name, last_name, hashed_password, role) VALUES
(1, '581515@stud.hvl.no', 'Yosafe', 'Yosafe', 'Fesaha Oqbamecail', '$2b$12$JT2J7Lvx4fHipNyEtDuW8.iu7IGOg/0n/um9eCGCQD.njLCRjawLq', 'admin');