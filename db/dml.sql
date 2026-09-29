-- =============================================================
-- DML - Datos iniciales
-- Ejecutar después de ddl.sql
-- =============================================================

SET NAMES utf8mb4;

USE sport_reserve;

-- -------------------------------------------------------------
-- Deportes precargados
-- -------------------------------------------------------------
INSERT INTO deportes (id, nombre) VALUES
(1, 'Fútbol'),
(2, 'Básquet'),
(3, 'Tenis'),
(4, 'Pádel'),
(5, 'Vóley');

-- -------------------------------------------------------------
-- Canchas iniciales
-- -------------------------------------------------------------
INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa) VALUES
('Cancha 1 - Fútbol 5', 1, 1000000, FALSE, TRUE),
('Cancha 2 - Fútbol 5 techada', 1, 1200000, TRUE, TRUE),
('Cancha 3 - Básquet', 2, 800000, FALSE, TRUE),
('Cancha 4 - Tenis', 3, 600000, FALSE, TRUE);

-- -------------------------------------------------------------
-- Socios de prueba
-- -------------------------------------------------------------
INSERT INTO socios (nombre, email, activo) VALUES
('Juan Pérez', 'juan.perez@example.com', TRUE),
('María García', 'maria.garcia@example.com', TRUE),
('Carlos López', 'carlos.lopez@example.com', FALSE);
