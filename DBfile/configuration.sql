-- MySQL dump 10.13  Distrib 5.1.73, for redhat-linux-gnu (x86_64)
--
-- Host: localhost    Database: configuration
-- ------------------------------------------------------
-- Server version	5.1.73

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `zc_client`
--

DROP TABLE IF EXISTS `zc_client`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `zc_client` (
  `id` int(5) NOT NULL AUTO_INCREMENT,
  `name` char(50) NOT NULL,
  `type` char(10) NOT NULL,
  `serverip` char(20) NOT NULL,
  `serverport` char(5) NOT NULL,
  `keypath` char(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `zc_client`
--

LOCK TABLES `zc_client` WRITE;
/*!40000 ALTER TABLE `zc_client` DISABLE KEYS */;
INSERT INTO `zc_client` VALUES (1,'cn.','NS','173.26.101.233','53','/var/namedFaker/cn.key'),(2,'ru.','NS','173.26.101.236','53','/var/namedFaker/ru.key');
/*!40000 ALTER TABLE `zc_client` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `zc_server`
--

DROP TABLE IF EXISTS `zc_server`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `zc_server` (
  `id` int(5) NOT NULL AUTO_INCREMENT,
  `name` char(50) NOT NULL,
  `ttl` char(10) NOT NULL,
  `class` char(10) NOT NULL,
  `type` char(10) NOT NULL,
  `rdata` char(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `zc_server`
--

LOCK TABLES `zc_server` WRITE;
/*!40000 ALTER TABLE `zc_server` DISABLE KEYS */;
INSERT INTO `zc_server` VALUES (1,'cn.','172800','IN','NS','a.dns.cn.'),(2,'cn.','172800','IN','NS','b.dns.cn.'),(3,'cn.','172800','IN','NS','c.dns.cn.'),(4,'cn.','172800','IN','NS','d.dns.cn.'),(5,'cn.','172800','IN','NS','e.dns.cn.'),(6,'cn.','172800','IN','NS','ns.cernet.net.'),(7,'a.dns.cn.','172800','IN','A','203.119.25.1'),(8,'b.dns.cn.','172800','IN','A','203.119.26.1'),(9,'c.dns.cn.','172800','IN','A','203.119.27.1'),(10,'d.dns.cn.','172800','IN','A','203.119.28.1'),(11,'e.dns.cn.','172800','IN','A','203.119.29.1'),(12,'ns.cernet.net.','172800','IN','A','202.112.0.44');
/*!40000 ALTER TABLE `zc_server` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-09-21  2:22:16
