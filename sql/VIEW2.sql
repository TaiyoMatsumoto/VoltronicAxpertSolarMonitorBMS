CREATE OR REPLACE
ALGORITHM = UNDEFINED VIEW `axpert`.`VIEW2` AS
select
    from_unixtime(truncate(unix_timestamp(`axpert`.`QPIGS`.`created`) / 3600, 0) * 3600) AS `h`,
    avg(`axpert`.`QPIGS`.`var6` + 60) AS `var1`,
    avg(`axpert`.`QPIGS`.`var13` * `axpert`.`QPIGS`.`var14`) AS `var2`
from
    `axpert`.`QPIGS`
group by
    from_unixtime(truncate(unix_timestamp(`axpert`.`QPIGS`.`created`) / 3600, 0) * 3600)
order by
    from_unixtime(truncate(unix_timestamp(`axpert`.`QPIGS`.`created`) / 3600, 0) * 3600) desc;
