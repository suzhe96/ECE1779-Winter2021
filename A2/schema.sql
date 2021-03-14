-- -----------------------------------------------------
-- REF: ECE1779 Database_lecture estore.sql
-- -----------------------------------------------------

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `ECE1779_A2_DB` ;
CREATE SCHEMA IF NOT EXISTS `ECE1779_A2_DB` DEFAULT CHARACTER SET utf8 ;
USE `ECE1779_A2_DB` ;

-- -----------------------------------------------------
-- Table `users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ECE1779_A2_DB`.`users`;
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(255) NOT NULL,
    `email` VARCHAR(255) NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `is_admin` BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (`id`)
)ENGINE=InnoDB;


DROP TABLE IF EXISTS `images`;
CREATE TABLE images (
    `id` INT NOT NULL AUTO_INCREMENT,
    `category` INT NOT NULL,
    `user_id` INT NOT NULL,
    `image_key` VARCHAR(255) NOT NULL,
    `image_url` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION
)ENGINE=InnoDB;

DROP TABLE IF EXISTS `autoscale`;
CREATE TABLE autoscale (
    `id` INT NOT NULL AUTO_INCREMENT,
    `scale` char(10) NOT NULL,
    `cpu_grow_threshold` INT NOT NULL,
    `cpu_shrink_threshold` INT NOT NULL,
    `cpu_grow_ratio`    INT NOT NULL,
    `cpu_shrink_ratio`  INT NOT NULL,
    PRIMARY KEY (id)
) ENGINE = InnoDB;
SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- -----------------------------------------------------
-- Data for table `ECE1779_A2_DB`.`users`
-- -----------------------------------------------------
