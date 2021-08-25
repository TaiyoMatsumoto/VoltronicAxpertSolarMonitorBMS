CREATE TABLE `axpert`.`QPIWS` (
  `created` timestamp NOT NULL DEFAULT current_timestamp(),
  `var1` varchar(36) DEFAULT NULL,
  `var2` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`created`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
