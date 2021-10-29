CREATE DATABASE  IF NOT EXISTS `matches` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `matches`;
-- MySQL dump 10.13  Distrib 8.0.26, for Linux (x86_64)
--
-- Host: localhost    Database: matches
-- ------------------------------------------------------
-- Server version	8.0.26-0ubuntu0.20.04.3

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `matches_league`
--

DROP TABLE IF EXISTS `matches_league`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `matches_league` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(70) NOT NULL,
  `rating` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `matches_match`
--

DROP TABLE IF EXISTS `matches_match`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `matches_match` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `match_date` datetime(6) NOT NULL,
  `ticket_close_time` datetime(6) NOT NULL,
  `host_id` bigint NOT NULL,
  `share` int NOT NULL,
  `guest_id` bigint NOT NULL,
  `stadium` int NOT NULL,
  `season_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `matches_match_stadium_match_date_98351959_uniq` (`stadium`,`match_date`),
  KEY `matches_match_season_id_09c8c091_fk_matches_season_id` (`season_id`),
  KEY `matches_match_guest_id_1cb2c144` (`guest_id`),
  KEY `matches_match_host_id_85bf48cc` (`host_id`),
  CONSTRAINT `matches_match_guest_id_1cb2c144_fk_matches_team_id` FOREIGN KEY (`guest_id`) REFERENCES `matches_team` (`id`),
  CONSTRAINT `matches_match_host_id_85bf48cc_fk_matches_team_id` FOREIGN KEY (`host_id`) REFERENCES `matches_team` (`id`),
  CONSTRAINT `matches_match_season_id_09c8c091_fk_matches_season_id` FOREIGN KEY (`season_id`) REFERENCES `matches_season` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `matches_matchseats`
--

DROP TABLE IF EXISTS `matches_matchseats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `matches_matchseats` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `seat` bigint NOT NULL,
  `ticket_price` bigint NOT NULL,
  `match_id` bigint NOT NULL,
  `is_host` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `matches_matchseats_seat_match_id_7d065e47_uniq` (`seat`,`match_id`),
  KEY `matches_matchseats_match_id_18f94244_fk_matches_match_id` (`match_id`),
  CONSTRAINT `matches_matchseats_match_id_18f94244_fk_matches_match_id` FOREIGN KEY (`match_id`) REFERENCES `matches_match` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=120 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `matches_season`
--

DROP TABLE IF EXISTS `matches_season`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `matches_season` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `matches_team`
--

DROP TABLE IF EXISTS `matches_team`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `matches_team` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `province` varchar(50) NOT NULL,
  `city` varchar(50) NOT NULL,
  `league_id` bigint NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `matches_team_league_id_6f517ac3` (`league_id`),
  CONSTRAINT `matches_team_league_id_6f517ac3_fk_matches_league_id` FOREIGN KEY (`league_id`) REFERENCES `matches_league` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-10-29 17:12:42
