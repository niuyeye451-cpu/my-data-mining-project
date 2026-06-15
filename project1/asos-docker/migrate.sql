-- 迁移已有 asos_dresses 表，新增字段
-- 每条 ALTER 独立执行，已存在的列会报错但不影响后续（用 || true 忽略）
USE asos_db;

ALTER TABLE asos_dresses ADD COLUMN breadcrumb VARCHAR(255) DEFAULT '' AFTER status;
ALTER TABLE asos_dresses ADD COLUMN material TEXT AFTER breadcrumb;
ALTER TABLE asos_dresses ADD COLUMN size_options VARCHAR(255) DEFAULT '' AFTER material;
ALTER TABLE asos_dresses ADD COLUMN care_info TEXT AFTER size_options;
ALTER TABLE asos_dresses ADD COLUMN gender TINYINT DEFAULT 0 AFTER care_info;
ALTER TABLE asos_dresses ADD COLUMN images_dir VARCHAR(100) DEFAULT '' AFTER gender;
ALTER TABLE asos_dresses ADD COLUMN crawled_at VARCHAR(30) DEFAULT '' AFTER images_dir;
