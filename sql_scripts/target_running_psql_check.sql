select pid as process_id,
       usename as username,
       datname as database_name,
       client_addr as client_address,
       application_name,
       backend_start,
       state,
       state_change
from pg_stat_activity
where usename='odoo'
    and datname='mdg_uat'
    and client_addr='172.31.11.143'
    and application_name='psql'