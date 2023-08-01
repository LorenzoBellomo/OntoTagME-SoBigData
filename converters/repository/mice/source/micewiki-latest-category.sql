--
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
/CREATE TABLE `category` (
  `cat_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `cat_title` varbinary(255) NOT NULL DEFAULT '',
  `cat_pages` int(11) NOT NULL DEFAULT '0',
  `cat_subcats` int(11) NOT NULL DEFAULT '0',
  `cat_files` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`cat_id`),
  UNIQUE KEY `cat_title` (`cat_title`),
  KEY `cat_pages` (`cat_pages`)
) ENGINE=InnoDB AUTO_INCREMENT=247504998 DEFAULT CHARSET=binary;

INSERT INTO `category` VALUES (1659,'DMI',45,17,1);