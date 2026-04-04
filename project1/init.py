CREATE DATABASE IF NOT EXISTS asos_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE asos_db;

CREATE TABLE IF NOT EXISTS asos_dresses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_code VARCHAR(50) UNIQUE,
    url TEXT,
    title VARCHAR(255),
    price VARCHAR(50),
    brand VARCHAR(100),
    colour VARCHAR(50),
    description TEXT,
    status TINYINT DEFAULT 0, -- 状态：0-待抓取，1-已完成，2-抓取失败
    scrape_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);