DROP DATABASE IF EXISTS workoutware;
CREATE DATABASE workoutware;
USE workoutware;

--
-- Table structure for table `user_info`
--

DROP TABLE IF EXISTS `user_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_info` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `address` varchar(50) DEFAULT NULL,
  `town` varchar(50) DEFAULT NULL,
  `state` varchar(50) DEFAULT NULL,
  `country` varchar(50) DEFAULT NULL,
  `email` varchar(50) NOT NULL,
  `phone_number` varchar(50) DEFAULT NULL,
  `password_hash` varchar(100) NOT NULL,
  `date_of_birth` date DEFAULT NULL,
  `height` decimal(5,2) DEFAULT NULL,
  `date_registered` date DEFAULT NULL,
  `date_unregistered` date DEFAULT NULL,
  `registered` tinyint(1) DEFAULT NULL,
  `fitness_goal` varchar(50) DEFAULT NULL,
  `user_type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `phone_number` (`phone_number`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `exercise`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exercise` (
  `exercise_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `type` varchar(50) NOT NULL,
  `subtype` varchar(50) DEFAULT NULL,
  `equipment` varchar(50) DEFAULT NULL,
  `difficulty` int DEFAULT NULL,
  `description` text,
  `demo_link` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`exercise_id`),
  UNIQUE KEY `name` (`name`),
  CONSTRAINT `exercise_chk_1` CHECK (((`difficulty` >= 1) and (`difficulty` <= 5)))
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `target`
--

DROP TABLE IF EXISTS `target`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `target` (
  `target_id` int NOT NULL AUTO_INCREMENT,
  `target_name` varchar(50) NOT NULL,
  `target_group` varchar(50) DEFAULT NULL,
  `target_function` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`target_id`),
  UNIQUE KEY `target_name` (`target_name`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `workout_sessions`
--

DROP TABLE IF EXISTS `workout_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `workout_sessions` (
  `session_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `session_name` varchar(100) DEFAULT NULL,
  `session_date` date NOT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `duration_minutes` int DEFAULT NULL,
  `bodyweight` decimal(5,2) DEFAULT NULL,
  `completed` tinyint(1) DEFAULT '1',
  `is_template` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`session_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `workout_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `workout_plan`
--

DROP TABLE IF EXISTS `workout_plan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `workout_plan` (
  `plan_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `plan_description` text,
  `plan_type` varchar(50) DEFAULT NULL,
  `number_of_days` int DEFAULT NULL,
  PRIMARY KEY (`plan_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `workout_plan_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `daily_workout_plan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `daily_workout_plan` (
  `daily_plan_id` int NOT NULL AUTO_INCREMENT,
  `workout_plan_id` int NOT NULL,
  `day` int NOT NULL,
  `wk_day` varchar(50) DEFAULT NULL,
  `session_id` int DEFAULT NULL,
  PRIMARY KEY (`daily_plan_id`),
  KEY `workout_plan_id` (`workout_plan_id`),
  KEY `session_id` (`session_id`),
  CONSTRAINT `daily_workout_plan_ibfk_1` FOREIGN KEY (`workout_plan_id`) REFERENCES `workout_plan` (`plan_id`) ON DELETE CASCADE,
  CONSTRAINT `daily_workout_plan_ibfk_2` FOREIGN KEY (`session_id`) REFERENCES `workout_sessions` (`session_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `exercise_history_summary`
--

DROP TABLE IF EXISTS `exercise_history_summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exercise_history_summary` (
  `summary_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `exercise_id` int NOT NULL,
  `total_workouts` int DEFAULT '0',
  `total_sets` int DEFAULT '0',
  `total_reps` int DEFAULT '0',
  `lifetime_volume` decimal(12,2) DEFAULT '0.00',
  `current_pr` decimal(6,2) DEFAULT NULL,
  `last_workout_date` date DEFAULT NULL,
  PRIMARY KEY (`summary_id`),
  UNIQUE KEY `unique_user_exercise` (`user_id`,`exercise_id`),
  KEY `exercise_id` (`exercise_id`),
  CONSTRAINT `exercise_history_summary_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `exercise_history_summary_ibfk_2` FOREIGN KEY (`exercise_id`) REFERENCES `exercise` (`exercise_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exercise_target_association`
--

DROP TABLE IF EXISTS `exercise_target_association`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exercise_target_association` (
  `association_id` int NOT NULL AUTO_INCREMENT,
  `exercise_id` int NOT NULL,
  `target_id` int NOT NULL,
  `intensity` varchar(20) NOT NULL,
  PRIMARY KEY (`association_id`),
  KEY `exercise_id` (`exercise_id`),
  KEY `target_id` (`target_id`),
  CONSTRAINT `exercise_target_association_ibfk_1` FOREIGN KEY (`exercise_id`) REFERENCES `exercise` (`exercise_id`) ON DELETE CASCADE,
  CONSTRAINT `exercise_target_association_ibfk_2` FOREIGN KEY (`target_id`) REFERENCES `target` (`target_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `goals`
--

DROP TABLE IF EXISTS `goals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `goals` (
  `goal_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `goal_type` varchar(100) NOT NULL,
  `goal_description` text,
  `target_value` decimal(8,2) NOT NULL,
  `current_value` decimal(8,2) DEFAULT NULL,
  `unit` varchar(20) NOT NULL,
  `exercise_id` int DEFAULT NULL,
  `start_date` date NOT NULL,
  `target_date` date DEFAULT NULL,
  `status` varchar(50) DEFAULT 'active',
  `completion_date` date DEFAULT NULL,
  PRIMARY KEY (`goal_id`),
  KEY `user_id` (`user_id`),
  KEY `exercise_id` (`exercise_id`),
  CONSTRAINT `goals_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `goals_ibfk_2` FOREIGN KEY (`exercise_id`) REFERENCES `exercise` (`exercise_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `progress`
--

DROP TABLE IF EXISTS `progress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `progress` (
  `progress_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `exercise_id` int NOT NULL,
  `date` date NOT NULL,
  `period_type` varchar(20) NOT NULL,
  `max_weight` decimal(6,2) DEFAULT NULL,
  `avg_weight` decimal(6,2) DEFAULT NULL,
  `total_volume` decimal(10,2) DEFAULT NULL,
  `workout_count` int DEFAULT NULL,
  PRIMARY KEY (`progress_id`),
  KEY `user_id` (`user_id`),
  KEY `exercise_id` (`exercise_id`),
  CONSTRAINT `progress_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `progress_ibfk_2` FOREIGN KEY (`exercise_id`) REFERENCES `exercise` (`exercise_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `session_exercises`
--

DROP TABLE IF EXISTS `session_exercises`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `session_exercises` (
  `session_exercise_id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `exercise_id` int NOT NULL,
  `exercise_order` int NOT NULL,
  `target_sets` int DEFAULT NULL,
  `target_reps` int DEFAULT NULL,
  `completed` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`session_exercise_id`),
  KEY `session_id` (`session_id`),
  KEY `exercise_id` (`exercise_id`),
  CONSTRAINT `session_exercises_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `workout_sessions` (`session_id`) ON DELETE CASCADE,
  CONSTRAINT `session_exercises_ibfk_2` FOREIGN KEY (`exercise_id`) REFERENCES `exercise` (`exercise_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sets`
--

DROP TABLE IF EXISTS `sets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sets` (
  `set_id` int NOT NULL AUTO_INCREMENT,
  `session_exercise_id` int NOT NULL,
  `set_number` int NOT NULL,
  `weight` decimal(6,2) DEFAULT NULL,
  `reps` int DEFAULT NULL,
  `rpe` int DEFAULT NULL,
  `completed` tinyint(1) DEFAULT '1',
  `is_warmup` tinyint(1) DEFAULT NULL,
  `completion_time` datetime DEFAULT NULL,
  PRIMARY KEY (`set_id`),
  KEY `session_exercise_id` (`session_exercise_id`),
  CONSTRAINT `sets_ibfk_1` FOREIGN KEY (`session_exercise_id`) REFERENCES `session_exercises` (`session_exercise_id`) ON DELETE CASCADE,
  CONSTRAINT `sets_chk_1` CHECK (((`rpe` >= 1) and (`rpe` <= 10)))
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_pb`
--

DROP TABLE IF EXISTS `user_pb`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_pb` (
  `pr_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `exercise_id` int NOT NULL,
  `pr_type` varchar(20) NOT NULL,
  `pb_weight` decimal(6,2) DEFAULT NULL,
  `pb_reps` int DEFAULT NULL,
  `pb_time` time DEFAULT NULL,
  `pb_date` date NOT NULL,
  `previous_pr` decimal(6,2) DEFAULT NULL,
  `notes` text,
  PRIMARY KEY (`pr_id`),
  KEY `user_id` (`user_id`),
  KEY `exercise_id` (`exercise_id`),
  CONSTRAINT `user_pb_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `user_pb_ibfk_2` FOREIGN KEY (`exercise_id`) REFERENCES `exercise` (`exercise_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_stats_log`
--

DROP TABLE IF EXISTS `user_stats_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_stats_log` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `date` date NOT NULL,
  `weight` decimal(5,2) NOT NULL,
  `neck` decimal(4,2) DEFAULT NULL,
  `waist` decimal(5,2) DEFAULT NULL,
  `hips` decimal(5,2) DEFAULT NULL,
  `body_fat_percentage` decimal(4,2) DEFAULT NULL,
  `notes` text,
  PRIMARY KEY (`log_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_stats_log_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `data_validation`
--

DROP TABLE IF EXISTS `data_validation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `data_validation` (
  `validation_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `set_id` int DEFAULT NULL,
  `exercise_id` int NOT NULL,
  `input_weight` decimal(6,2) NOT NULL,
  `expected_max` decimal(6,2) DEFAULT NULL,
  `flagged_as` varchar(20) DEFAULT NULL,
  `user_action` varchar(20) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  PRIMARY KEY (`validation_id`),
  KEY `user_id` (`user_id`),
  KEY `set_id` (`set_id`),
  KEY `exercise_id` (`exercise_id`),
  CONSTRAINT `data_validation_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `data_validation_ibfk_2` FOREIGN KEY (`set_id`) REFERENCES `sets` (`set_id`) ON DELETE SET NULL,
  CONSTRAINT `data_validation_ibfk_3` FOREIGN KEY (`exercise_id`) REFERENCES `exercise` (`exercise_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `workout_goal_link`
--

DROP TABLE IF EXISTS `workout_goal_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `workout_goal_link` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `goal` int DEFAULT NULL,
  `session` int NOT NULL,
  `created_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `session` (`session`),
  KEY `goal` (`goal`),
  CONSTRAINT `workout_goal_link_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_info` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `workout_goal_link_ibfk_2` FOREIGN KEY (`goal`) REFERENCES `goals` (`goal_id`) ON DELETE SET NULL,
  CONSTRAINT `workout_goal_link_ibfk_3` FOREIGN KEY (`session`) REFERENCES `workout_sessions` (`session_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

