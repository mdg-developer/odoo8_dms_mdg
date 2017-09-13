-- Function: calculate_ot_count(date, date, integer)

-- DROP FUNCTION calculate_ot_count(date, date, integer);

CREATE OR REPLACE FUNCTION calculate_ot_count(
    date_from date,
    date_to date,
    param_employee_id integer)
  RETURNS numeric AS
$BODY$
	DECLARE
		ot_count NUMERIC;
		
	BEGIN
		

		RAISE NOTICE 'Starting to retrieve late minutes......';


             

		--Get total late mintes < 10 minutes
		
SELECT COUNT(CALC.ot_hours) into ot_count FROM
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
			and att.name::date
			between date_from and date_to
		)
		AOT)AA,
		(select DOT.ot_start_time,DOT.ot_end_time from
		(
		       select hdl.date_start + '6 hour'::interval + '30 minutes'::interval as start_time,
		       hdl.date_end + '6 hour'::interval + '30 minutes'::interval as end_time,
		       hdl.date_end + '6 hour'::interval + '30 minutes'::interval  as ot_start_time,
		       hdl.date_end + '6 hour'::interval + '30 minutes'::interval + '5 hour'::interval as ot_end_time,
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


	
		RAISE NOTICE '%',ot_count;
		RAISE NOTICE 'Total Late minutes successfully retrieved!....';

		return ot_count;
	END;
	
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION calculate_ot_count(date, date, integer)
  OWNER TO openerp;

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
-- Function: calculate_sunday_overtime(date, date, integer)

-- DROP FUNCTION calculate_sunday_overtime(date, date, integer);

CREATE OR REPLACE FUNCTION calculate_sunday_overtime(
    IN from_date date,
    IN to_date date,
    IN param_employee_id integer)
  RETURNS TABLE(sunday_ot double precision, sign_in_day bigint) AS
$BODY$
	DECLARE
		
		sunday_ot NUMERIC;
	BEGIN
		RAISE NOTICE 'Starting to save Employee Overtime.......';
		EXECUTE 'drop table if exists sunday_temp';
	        EXECUTE ' create temp table sunday_temp AS	
               SELECT C.sunday_ot_hr as sunday_ot,C.sign_in_day from
	               (	
                        select sum(B.attendance-A.attendance)  as sunday_ot_hr,count (sign_in_day) as sign_in_day from(
                        select HA.name::date as sign_in_day,(DATE_PART(''HOUR'', CAST(to_char(HA.name::timestamp at time zone ''UTC'', ''YYYY-MM-DD HH24:MI:SS TZ'') AS TIMESTAMP)) + 
			(((DATE_PART(''MINUTE'', CAST(to_char(HA.name::timestamp at time zone ''UTC'', ''YYYY-MM-DD HH24:MI:SS TZ'') AS TIMESTAMP)))/30)*0.5)) Attendance
			 from hr_attendance HA,hr_employee HE
			where action= ''sign_in''
			and HE.id=HA.employee_id
			and extract(dow from HA.name) = 0
			and HA.name::date not in (select date::date from hr_gazetted_holiday)
		       and HE.id =  '''||param_employee_id||'''
			AND HA.name::date
			BETWEEN  '''||from_date||'''
			AND   '''||to_date||''')A,
			(select HA.name::date as sign_out_day,(DATE_PART(''HOUR'', CAST(to_char(HA.name::timestamp at time zone ''UTC'', ''YYYY-MM-DD HH24:MI:SS TZ'') AS TIMESTAMP)) + 
			(((DATE_PART(''MINUTE'', CAST(to_char(HA.name::timestamp at time zone ''UTC'', ''YYYY-MM-DD HH24:MI:SS TZ'') AS TIMESTAMP)))/30)*0.5)) Attendance
			 from hr_attendance HA,hr_employee HE
			where action= ''sign_out''
			and HE.id=HA.employee_id
			and extract(dow from HA.name) = 0
			and HA.name::date not in (select date::date from hr_gazetted_holiday)
		        and HE.id =  '''||param_employee_id||'''
			AND HA.name::date
			BETWEEN  '''||from_date||'''
			AND   '''||to_date||''')B
		        where  A.sign_in_day=B.sign_out_day 
		        )C';
	
			   
		RAISE NOTICE 'Total OT Hours successfully retrieved!....';

		return query select * from sunday_temp;	
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION calculate_sunday_overtime(date, date, integer)
  OWNER TO openerp;

-- Function: gazetted_day_ot(date, date, integer)

-- DROP FUNCTION gazetted_day_ot(date, date, integer);

CREATE OR REPLACE FUNCTION gazetted_day_ot(
    IN from_date date,
    IN to_date date,
    IN param_employee_id integer)
  RETURNS TABLE(gazetted_hr double precision, gazetted_count bigint) AS
$BODY$
	DECLARE
		payslip RECORD;
		total_charges NUMERIC=0;
		gazetted_count NUMERIC;
		contract_wage NUMERIC;
		gz_ot_hrs NUMERIC;
		gz_amt NUMERIC;
		full_hr_charges NUMERIC;
		half_hr_charges NUMERIC;
	BEGIN
	-- Retrieve Payslip Date From and Date To
		
	--select gazetted amount 
	
	--For 7 Hrs Full 
	EXECUTE 'drop table if exists gazetted_temp';
	EXECUTE ' create temp table gazetted_temp AS	
	SELECT C.total_hrs_per_day ,C.gazetted_count  from
	(	
		SELECT sum(A.attendance - B.attendance) as total_hrs_per_day, count(A.name) as gazetted_count from 
			(
			select HA.name ,(DATE_PART(''HOUR'', CAST(to_char(HA.name::timestamp at time zone ''UTC'', ''YYYY-MM-DD HH24:MI:SS TZ'') AS TIMESTAMP)) + 
			(((DATE_PART(''MINUTE'', CAST(to_char(HA.name::timestamp at time zone ''UTC'', ''YYYY-MM-DD HH24:MI:SS TZ'') AS TIMESTAMP)))/30)*0.5)) Attendance,
			 HA.name as sign_out_day from hr_gazetted_holiday HGA , hr_attendance HA ,hr_employee HE
			where HA.action=''sign_out'' 
			and HGA.date = HA.name :: date
			and HE.id = HA.employee_id
			and HE.id =  '''||param_employee_id||'''
			--AND HA.name::date
			--BETWEEN from_date
			--AND to_date
			)A ,

		(
		select HA.name as sign_in_time ,
		(DATE_PART(''HOUR'', CAST(to_char(HA.name::timestamp at time zone ''UTC'', ''YYYY-MM-DD HH24:MI:SS TZ'') AS TIMESTAMP)) + 
		(((DATE_PART(''MINUTE'', CAST(to_char(HA.name::timestamp at time zone ''UTC'', ''YYYY-MM-DD HH24:MI:SS TZ'') AS TIMESTAMP)))/30)*0.5)) Attendance,
		HA.name as sign_in_day  from hr_gazetted_holiday HGA , hr_attendance HA , hr_employee HE
		where HA.action=''sign_in''
		and HGA.date = HA.name :: date
		and HE.id = HA.employee_id
		and HE.id =  '''||param_employee_id||'''
		--AND HA.name::date
		--BETWEEN from_date
		--AND to_date		
		)B
		where A.sign_out_day::date = B.sign_in_day ::date
	)C';
	--delete from gazetted_temp;

	Return QUERY select * from gazetted_temp;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION gazetted_day_ot(date, date, integer)
  OWNER TO openerp;
