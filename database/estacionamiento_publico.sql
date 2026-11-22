-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: estacionamiento_publico
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `clientes`
--

DROP TABLE IF EXISTS `clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clientes` (
  `cliente_id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) DEFAULT NULL,
  `telefono` varchar(10) DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `rfc` varchar(13) DEFAULT NULL,
  `tipo_cliente_id` int(11) DEFAULT NULL,
  `registrado_por` int(11) DEFAULT NULL,
  `fecha_registro` datetime DEFAULT NULL,
  `activo` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`cliente_id`),
  UNIQUE KEY `rfc` (`rfc`),
  KEY `tipo_cliente_id` (`tipo_cliente_id`),
  KEY `registrado_por` (`registrado_por`),
  CONSTRAINT `clientes_ibfk_1` FOREIGN KEY (`tipo_cliente_id`) REFERENCES `tipos_cliente` (`tipo_cliente_id`),
  CONSTRAINT `clientes_ibfk_2` FOREIGN KEY (`registrado_por`) REFERENCES `usuarios` (`usuario_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clientes`
--

LOCK TABLES `clientes` WRITE;
/*!40000 ALTER TABLE `clientes` DISABLE KEYS */;
/*!40000 ALTER TABLE `clientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cobros`
--

DROP TABLE IF EXISTS `cobros`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cobros` (
  `cobro_id` int(11) NOT NULL AUTO_INCREMENT,
  `servicio_id` int(11) DEFAULT NULL,
  `horas_cobradas` int(11) DEFAULT NULL,
  `monto_total` decimal(10,2) DEFAULT NULL,
  `fecha_hora_cobro` datetime DEFAULT NULL,
  `metodo_pago_id` int(11) DEFAULT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`cobro_id`),
  UNIQUE KEY `servicio_id` (`servicio_id`),
  KEY `metodo_pago_id` (`metodo_pago_id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `cobros_ibfk_1` FOREIGN KEY (`servicio_id`) REFERENCES `servicios` (`servicio_id`),
  CONSTRAINT `cobros_ibfk_2` FOREIGN KEY (`metodo_pago_id`) REFERENCES `metodos_pago` (`metodo_pago_id`),
  CONSTRAINT `cobros_ibfk_3` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`usuario_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cobros`
--

LOCK TABLES `cobros` WRITE;
/*!40000 ALTER TABLE `cobros` DISABLE KEYS */;
INSERT INTO `cobros` VALUES (1,1,1,30.00,'2026-11-22 14:39:39',1,1),(2,3,1,30.00,'2026-11-22 14:57:49',1,1),(3,5,1,30.00,'2026-11-22 15:11:45',1,1),(4,4,1,40.00,'2026-11-22 15:36:46',1,1);
/*!40000 ALTER TABLE `cobros` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cobros_detalle`
--

DROP TABLE IF EXISTS `cobros_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cobros_detalle` (
  `cobro_detalle_id` int(11) NOT NULL AUTO_INCREMENT,
  `cobro_id` int(11) DEFAULT NULL,
  `tarifa_id` int(11) DEFAULT NULL,
  `horas` int(11) DEFAULT NULL,
  `precio_hora_aplicado` decimal(10,2) DEFAULT NULL,
  `subtotal` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`cobro_detalle_id`),
  KEY `cobro_id` (`cobro_id`),
  KEY `tarifa_id` (`tarifa_id`),
  CONSTRAINT `cobros_detalle_ibfk_1` FOREIGN KEY (`cobro_id`) REFERENCES `cobros` (`cobro_id`),
  CONSTRAINT `cobros_detalle_ibfk_2` FOREIGN KEY (`tarifa_id`) REFERENCES `tarifas` (`tarifa_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cobros_detalle`
--

LOCK TABLES `cobros_detalle` WRITE;
/*!40000 ALTER TABLE `cobros_detalle` DISABLE KEYS */;
INSERT INTO `cobros_detalle` VALUES (2,2,1,1,30.00,30.00),(3,3,1,1,30.00,30.00),(4,4,1,1,40.00,40.00);
/*!40000 ALTER TABLE `cobros_detalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `descuentos_pension`
--

DROP TABLE IF EXISTS `descuentos_pension`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `descuentos_pension` (
  `descuento_id` int(11) NOT NULL AUTO_INCREMENT,
  `anios_minimos` int(11) DEFAULT NULL,
  `porcentaje` decimal(5,2) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`descuento_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `descuentos_pension`
--

LOCK TABLES `descuentos_pension` WRITE;
/*!40000 ALTER TABLE `descuentos_pension` DISABLE KEYS */;
/*!40000 ALTER TABLE `descuentos_pension` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `estados_pension`
--

DROP TABLE IF EXISTS `estados_pension`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `estados_pension` (
  `estado_pension_id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`estado_pension_id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `estados_pension`
--

LOCK TABLES `estados_pension` WRITE;
/*!40000 ALTER TABLE `estados_pension` DISABLE KEYS */;
INSERT INTO `estados_pension` VALUES (1,'activa'),(2,'vencida');
/*!40000 ALTER TABLE `estados_pension` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `metodos_pago`
--

DROP TABLE IF EXISTS `metodos_pago`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `metodos_pago` (
  `metodo_pago_id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`metodo_pago_id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `metodos_pago`
--

LOCK TABLES `metodos_pago` WRITE;
/*!40000 ALTER TABLE `metodos_pago` DISABLE KEYS */;
INSERT INTO `metodos_pago` VALUES (1,'efectivo'),(2,'tarjeta');
/*!40000 ALTER TABLE `metodos_pago` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pagos_pension`
--

DROP TABLE IF EXISTS `pagos_pension`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pagos_pension` (
  `pago_pension_id` int(11) NOT NULL AUTO_INCREMENT,
  `pension_id` int(11) DEFAULT NULL,
  `periodo_inicio` date DEFAULT NULL,
  `periodo_fin` date DEFAULT NULL,
  `monto_base` decimal(10,2) DEFAULT NULL,
  `descuento_id` int(11) DEFAULT NULL,
  `monto_pagado` decimal(10,2) DEFAULT NULL,
  `fecha_pago` datetime DEFAULT NULL,
  `metodo_pago_id` int(11) DEFAULT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`pago_pension_id`),
  KEY `pension_id` (`pension_id`),
  KEY `descuento_id` (`descuento_id`),
  KEY `metodo_pago_id` (`metodo_pago_id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `pagos_pension_ibfk_1` FOREIGN KEY (`pension_id`) REFERENCES `pensiones` (`pension_id`),
  CONSTRAINT `pagos_pension_ibfk_2` FOREIGN KEY (`descuento_id`) REFERENCES `descuentos_pension` (`descuento_id`),
  CONSTRAINT `pagos_pension_ibfk_3` FOREIGN KEY (`metodo_pago_id`) REFERENCES `metodos_pago` (`metodo_pago_id`),
  CONSTRAINT `pagos_pension_ibfk_4` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`usuario_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pagos_pension`
--

LOCK TABLES `pagos_pension` WRITE;
/*!40000 ALTER TABLE `pagos_pension` DISABLE KEYS */;
/*!40000 ALTER TABLE `pagos_pension` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pensiones`
--

DROP TABLE IF EXISTS `pensiones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pensiones` (
  `pension_id` int(11) NOT NULL AUTO_INCREMENT,
  `cliente_id` int(11) DEFAULT NULL,
  `vehiculo_id` int(11) DEFAULT NULL,
  `tarifa_id` int(11) DEFAULT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `estado_pension_id` int(11) DEFAULT NULL,
  `usuario_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`pension_id`),
  KEY `cliente_id` (`cliente_id`),
  KEY `vehiculo_id` (`vehiculo_id`),
  KEY `tarifa_id` (`tarifa_id`),
  KEY `estado_pension_id` (`estado_pension_id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `pensiones_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`cliente_id`),
  CONSTRAINT `pensiones_ibfk_2` FOREIGN KEY (`vehiculo_id`) REFERENCES `vehiculos` (`vehiculo_id`),
  CONSTRAINT `pensiones_ibfk_3` FOREIGN KEY (`tarifa_id`) REFERENCES `tarifas` (`tarifa_id`),
  CONSTRAINT `pensiones_ibfk_4` FOREIGN KEY (`estado_pension_id`) REFERENCES `estados_pension` (`estado_pension_id`),
  CONSTRAINT `pensiones_ibfk_5` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`usuario_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pensiones`
--

LOCK TABLES `pensiones` WRITE;
/*!40000 ALTER TABLE `pensiones` DISABLE KEYS */;
/*!40000 ALTER TABLE `pensiones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `perfiles`
--

DROP TABLE IF EXISTS `perfiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `perfiles` (
  `perfil_id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`perfil_id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `perfiles`
--

LOCK TABLES `perfiles` WRITE;
/*!40000 ALTER TABLE `perfiles` DISABLE KEYS */;
INSERT INTO `perfiles` VALUES (1,'admin'),(2,'cobrador');
/*!40000 ALTER TABLE `perfiles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `servicios`
--

DROP TABLE IF EXISTS `servicios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `servicios` (
  `servicio_id` int(11) NOT NULL AUTO_INCREMENT,
  `vehiculo_id` int(11) DEFAULT NULL,
  `tipo_servicio_id` int(11) DEFAULT NULL,
  `pension_id` int(11) DEFAULT NULL,
  `fecha_hora_entrada` datetime DEFAULT NULL,
  `fecha_hora_salida` datetime DEFAULT NULL,
  `usuario_entrada_id` int(11) DEFAULT NULL,
  `usuario_salida_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`servicio_id`),
  KEY `vehiculo_id` (`vehiculo_id`),
  KEY `tipo_servicio_id` (`tipo_servicio_id`),
  KEY `pension_id` (`pension_id`),
  KEY `usuario_entrada_id` (`usuario_entrada_id`),
  KEY `usuario_salida_id` (`usuario_salida_id`),
  CONSTRAINT `servicios_ibfk_1` FOREIGN KEY (`vehiculo_id`) REFERENCES `vehiculos` (`vehiculo_id`),
  CONSTRAINT `servicios_ibfk_2` FOREIGN KEY (`tipo_servicio_id`) REFERENCES `tipos_servicio` (`tipo_servicio_id`),
  CONSTRAINT `servicios_ibfk_3` FOREIGN KEY (`pension_id`) REFERENCES `pensiones` (`pension_id`),
  CONSTRAINT `servicios_ibfk_4` FOREIGN KEY (`usuario_entrada_id`) REFERENCES `usuarios` (`usuario_id`),
  CONSTRAINT `servicios_ibfk_5` FOREIGN KEY (`usuario_salida_id`) REFERENCES `usuarios` (`usuario_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servicios`
--

LOCK TABLES `servicios` WRITE;
/*!40000 ALTER TABLE `servicios` DISABLE KEYS */;
INSERT INTO `servicios` VALUES (1,1,1,NULL,'2026-11-22 14:19:01','2026-11-22 14:39:39',1,1),(2,2,1,NULL,'2026-11-22 14:30:53',NULL,1,NULL),(3,3,1,NULL,'2026-11-22 14:57:36','2026-11-22 14:57:49',1,1),(4,4,1,NULL,'2026-11-22 15:11:13','2026-11-22 15:36:46',1,1),(5,5,1,NULL,'2026-11-22 15:11:17','2026-11-22 15:11:45',1,1);
/*!40000 ALTER TABLE `servicios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tarifas`
--

DROP TABLE IF EXISTS `tarifas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tarifas` (
  `tarifa_id` int(11) NOT NULL AUTO_INCREMENT,
  `tipo_servicio_id` int(11) DEFAULT NULL,
  `tipo_cliente_id` int(11) DEFAULT NULL,
  `hora_desde` int(11) DEFAULT NULL,
  `hora_hasta` int(11) DEFAULT NULL,
  `precio` decimal(10,2) DEFAULT NULL,
  `unidad` varchar(5) DEFAULT NULL,
  `activa` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`tarifa_id`),
  KEY `tipo_servicio_id` (`tipo_servicio_id`),
  KEY `tipo_cliente_id` (`tipo_cliente_id`),
  CONSTRAINT `tarifas_ibfk_1` FOREIGN KEY (`tipo_servicio_id`) REFERENCES `tipos_servicio` (`tipo_servicio_id`),
  CONSTRAINT `tarifas_ibfk_2` FOREIGN KEY (`tipo_cliente_id`) REFERENCES `tipos_cliente` (`tipo_cliente_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tarifas`
--

LOCK TABLES `tarifas` WRITE;
/*!40000 ALTER TABLE `tarifas` DISABLE KEYS */;
INSERT INTO `tarifas` VALUES (1,1,1,1,5,40.00,'hora',1),(2,1,1,6,NULL,25.00,'hora',1),(3,1,2,1,5,26.00,'hora',1),(4,1,2,6,NULL,22.00,'hora',1);
/*!40000 ALTER TABLE `tarifas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipos_cliente`
--

DROP TABLE IF EXISTS `tipos_cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tipos_cliente` (
  `tipo_cliente_id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`tipo_cliente_id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipos_cliente`
--

LOCK TABLES `tipos_cliente` WRITE;
/*!40000 ALTER TABLE `tipos_cliente` DISABLE KEYS */;
INSERT INTO `tipos_cliente` VALUES (2,'frecuente'),(1,'paso');
/*!40000 ALTER TABLE `tipos_cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipos_servicio`
--

DROP TABLE IF EXISTS `tipos_servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tipos_servicio` (
  `tipo_servicio_id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`tipo_servicio_id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipos_servicio`
--

LOCK TABLES `tipos_servicio` WRITE;
/*!40000 ALTER TABLE `tipos_servicio` DISABLE KEYS */;
INSERT INTO `tipos_servicio` VALUES (1,'caj?n'),(2,'pensi?n');
/*!40000 ALTER TABLE `tipos_servicio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `usuarios` (
  `usuario_id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `username` varchar(30) DEFAULT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `perfil_id` int(11) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`usuario_id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `username` (`username`),
  KEY `perfil_id` (`perfil_id`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`perfil_id`) REFERENCES `perfiles` (`perfil_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'Juan Luis Lepe','juan@test.com','admin','12345',1,1);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vehiculos`
--

DROP TABLE IF EXISTS `vehiculos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vehiculos` (
  `vehiculo_id` int(11) NOT NULL AUTO_INCREMENT,
  `matricula` varchar(7) DEFAULT NULL,
  `marca` varchar(30) DEFAULT NULL,
  `modelo` varchar(30) DEFAULT NULL,
  `color` varchar(20) DEFAULT NULL,
  `cliente_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`vehiculo_id`),
  UNIQUE KEY `matricula` (`matricula`),
  KEY `cliente_id` (`cliente_id`),
  CONSTRAINT `vehiculos_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`cliente_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vehiculos`
--

LOCK TABLES `vehiculos` WRITE;
/*!40000 ALTER TABLE `vehiculos` DISABLE KEYS */;
INSERT INTO `vehiculos` VALUES (1,'JLLAJ6','Por definir','Por definir','Por definir',NULL),(2,'JAJA23','Por definir','Por definir','Por definir',NULL),(3,'JSOJDAN','Por definir','Por definir','Por definir',NULL),(4,'JSWQHDB','Por definir','Por definir','Por definir',NULL),(5,'LKDQWNB','Por definir','Por definir','Por definir',NULL);
/*!40000 ALTER TABLE `vehiculos` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-22 15:40:49
