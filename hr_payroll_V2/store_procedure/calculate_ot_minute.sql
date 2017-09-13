-- Function: calculate_ot_minute(date, date, integer)

-- DROP FUNCTION calculate_ot_minute(date, date, integer);

CREATE OR REPLACE FUNCTION calculate_ot_minute(
    date_from date,
    date_to date,
    param_employee_id integer)
  RETURNS numeric AS
$BODY$
	DECLARE
		ot_hour NUMERIC;
		
	BEGIN
		

		RAISE NOTICE 'Starting to retrieve late minutes......';


             

		
SELECT SUM(CALC.ot_hours) into ot_hour FROM
(
 SELECT (date_part('HOUR',
   age(CASE WHEN DD.ot_end_time < AA.end_time THEN DD.ot_end_time ELSE AA.end_time END ::TIMESTAMP,
   CASE WHEN DD.ot_start_time > AA.start_time THEN DD.ot_start_time ELSE AA.start_time END ::TIMESTAMP))
   +(date_part('MINUTE',
   age(CASE WHEN DD.ot_end_time < AA.end_time THEN DD.ot_end_time ELSE AA.end_time END ::TIMESTAMP,
   CASE WHEN DD.ot_start_time > AA.start_time THEN DD.ot_start_time ELSE AA.start_time END ::TIMESTAMP)))/60)  as ot_hours FROM
	--AA.start_time,AA.end_time,DD.ot_start_time,DD.ot_end_time FROM
		(select AOT.start_time,AOT.end_time from 
		(
			select name + '6 hour'::interval + '30 minutes'::interval - '9 hour'::interval as start_time,
			name + '6 hour'::interval + '30 minutes'::interval as end_time
			from hr_attendance att 
			where att.employee_id =param_employee_id
			and action='sign_out'
			and att.name ::date
			between date_from and date_to
		)
		AOT)AA,
		(select DOT.ot_start_time,DOT.ot_end_time from
		(
		       select hdl.date_start + '6 hour'::interval + '30 minutes'::interval as start_time,
		       hdl.date_end + '6 hour'::interval + '30 minutes'::interval as end_time,
		       hdl.date_end + '6 hour'::interval + '30 minutes'::interval  as ot_start_time,
		       hdl.date_end + '6 hour'::interval + '30 minutes'::interval  + '5 hour'::interval as ot_end_time,
		       (hdl.day + '6 hour'::interval + '30 minutes'::interval)::date as day,
		       (hdl.day + '1 day'::interval + '6 hour'::interval + '30 minutes'::interval)::date as next_day
			from hr_employee_duty hd,hr_employee_duty_detail hdl where hd.id=hdl.duty_id
			and hd.employee_id=param_employee_id
			and hdl.day 
			between date_from and date_to
		)DOT)DD
)CALC
WHERE ot_hours >0
;



	
		RAISE NOTICE '%',ot_hour;
		RAISE NOTICE 'Total Late minutes successfully retrieved!....';
 
		return ot_hour;
	END;
	
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION calculate_ot_minute(date, date, integer)
  OWNER TO openerp;
