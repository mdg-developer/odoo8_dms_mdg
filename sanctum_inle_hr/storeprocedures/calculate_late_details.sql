-- Function: calculate_late_minutes(date, date, integer)

-- DROP FUNCTION calculate_late_minutes(date, date, integer);

CREATE OR REPLACE FUNCTION calculate_late_minutes(from_date date, to_date date, param_employee_id integer)
  RETURNS numeric AS
$BODY$
	DECLARE
		late_count NUMERIC;
		
	BEGIN
		

		RAISE NOTICE 'Starting to retrieve late minutes......';

		--Get total late mintes < 15 minutes
		
	select count(AB.total_late_mins)  into late_count from 
                  (
               select floor((AA.attendance-B.start_time)*60) as total_late_mins from (
               select A.attendance,A.att_date::date
               from
               (
		select 
		(date_part('hour', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)) +
		(((date_part('minute', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)))/30)*0.5)) as attendance,att.name + '6 hour'::interval + '30 minutes'::interval as att_date 
		from hr_attendance att 
		where att.employee_id = param_employee_id
		and action='sign_in'
		and att.name+ '6 hour'::interval + '30 minutes'::interval
		between from_date and to_date
		)A)AA,

		(

            select HDRD.date,RCA.hour_from as start_time
                 from hr_duty_roster HDR,hr_duty_roster_detail HDRD,resource_calendar RC,resource_calendar_attendance RCA
                 where HDR.working_hours_id=RC.id
                 and RC.id=RCA.calendar_id
                 and RCA.calendar_id=HDR.working_hours_id
                 and HDR.id=HDRD.roster_id
                 and HDR.employee_id = param_employee_id
                 and HDR.state='assign'
                 and HDRD.date between from_date and to_date
                 group by HDR.employee_id,HDRD.date,RCA.hour_from		
		)B		
       where AA.att_date=b.date
       and AA.attendance > B.start_time

    )AB where AB.total_late_mins  >=15;


	
		RAISE NOTICE '%',late_count;
		RAISE NOTICE 'Total Late minutes successfully retrieved!....';

		return late_count;
	END;
	
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION calculate_late_minutes(date, date, integer)
  OWNER TO openerp;
