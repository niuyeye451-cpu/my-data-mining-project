CREATE DATABASE IF NOT EXISTS asos_local CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE asos_local;

CREATE TABLE IF NOT EXISTS asos_dresses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_code VARCHAR(50) UNIQUE,
    url TEXT,
    title VARCHAR(255),
    price VARCHAR(50),
    brand VARCHAR(100),
    colour VARCHAR(50),
    description TEXT,
    image_url TEXT,
    status TINYINT DEFAULT 0 COMMENT '0=待抓取, 1=成功, 2=失败',
    material TEXT COMMENT '材质/面料信息',
    size_options VARCHAR(255) DEFAULT '' COMMENT '可选尺码列表',
    care_info TEXT COMMENT '洗护说明',
    gender TINYINT DEFAULT 0 COMMENT '0=Women, 1=Men',
    images_dir TEXT COMMENT '商品图片 URL 列表 (JSON 数组)',
    crawled_at VARCHAR(30) DEFAULT '' COMMENT '详情抓取时间戳',
    scrape_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
