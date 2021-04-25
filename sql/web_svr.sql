CREATE TABLE IF NOT EXISTS `test` (
  `id` bigint(20) NOT NULL COMMENT 'id',
  `val` bigint(20) NOT NULL COMMENT 'val',
  `name` varchar(30) NOT NULL COMMENT 'name',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='测试表';