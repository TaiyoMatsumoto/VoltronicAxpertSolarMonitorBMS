CREATE OR REPLACE
ALGORITHM = UNDEFINED VIEW `axpert`.`VIEW1` AS
select
    from_unixtime(truncate(unix_timestamp(`axpert`.`SDM230`.`created`) / 3600, 0) * 3600) AS `h`,
    if(avg(`axpert`.`SDM230`.`var8`) > 0,
    avg(`axpert`.`SDM230`.`var8`),
    0) AS `var1`,
    if(avg(`axpert`.`SDM230`.`var8`) < 0,
    avg(`axpert`.`SDM230`.`var8`),
    0) AS `var2`
from
    `axpert`.`SDM230`
group by
    from_unixtime(truncate(unix_timestamp(`axpert`.`SDM230`.`created`) / 3600, 0) * 3600)
order by
    from_unixtime(truncate(unix_timestamp(`axpert`.`SDM230`.`created`) / 3600, 0) * 3600) desc;
