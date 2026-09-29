-- =============================================================
-- DDL - Estructura de la base de datos
-- Compatible con MySQL 8+
-- =============================================================

SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS sport_reserve
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE sport_reserve;

-- -------------------------------------------------------------
-- Tabla: deportes
-- Deportes precargados del club
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS deportes (
    id     INT          NOT NULL,
    nombre VARCHAR(50)  NOT NULL,

    PRIMARY KEY (id)
);

-- -------------------------------------------------------------
-- Tabla: canchas
-- Canchas disponibles para reservar
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS canchas (
    id          INT          NOT NULL AUTO_INCREMENT,
    nombre      VARCHAR(100) NOT NULL,
    id_deporte  INT          NOT NULL,
    precio_hora INT          NOT NULL,
    techada     BOOLEAN      NOT NULL DEFAULT FALSE,
    activa      BOOLEAN      NOT NULL DEFAULT TRUE,

    PRIMARY KEY (id),
    FOREIGN KEY (id_deporte) REFERENCES deportes(id)
);

-- -------------------------------------------------------------
-- Tabla: socios
-- Socios del club
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS socios (
    id     INT          NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    email  VARCHAR(255) NOT NULL,
    activo BOOLEAN      NOT NULL DEFAULT TRUE,

    PRIMARY KEY (id),
    UNIQUE KEY uq_socios_email (email)
);

-- -------------------------------------------------------------
-- Tabla: reservas
-- Reservas de canchas
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reservas (
    id                INT          NOT NULL AUTO_INCREMENT,
    id_socio          INT          NOT NULL,
    id_cancha         INT          NOT NULL,
    fecha_hora_inicio DATETIME(6)  NOT NULL,
    fecha_hora_fin    DATETIME(6)  NOT NULL,
    estado            VARCHAR(20)  NOT NULL DEFAULT 'confirmada',
    precio_hora       INT          NOT NULL,
    precio_total      INT          NOT NULL,

    PRIMARY KEY (id),
    FOREIGN KEY (id_socio)  REFERENCES socios(id),
    FOREIGN KEY (id_cancha) REFERENCES canchas(id)
);

-- -------------------------------------------------------------
-- Tabla: bloqueos
-- Bloqueos de mantenimiento (extensión opcional)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bloqueos (
    id          INT          NOT NULL AUTO_INCREMENT,
    id_cancha   INT          NOT NULL,
    fecha       DATE         NOT NULL,
    hora_inicio TIME         NOT NULL,
    hora_fin    TIME         NOT NULL,
    motivo      VARCHAR(255) NOT NULL,

    PRIMARY KEY (id),
    FOREIGN KEY (id_cancha) REFERENCES canchas(id)
);
