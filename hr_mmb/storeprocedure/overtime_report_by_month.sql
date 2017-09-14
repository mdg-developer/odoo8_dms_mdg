-- Function: overtime_report_by_month(integer, date, date)
--select * from overtime_report_by_month('2787','2015-05-01','2015-05-31')
-- DROP FUNCTION overtime_report_by_month(integer, date, date);

CREATE OR REPLACE FUNCTION overtime_report_by_month(IN param_employee_id integer, IN from_date date, IN to_date date)
  RETURNS TABLE(id bigint, p_emp_name character varying, p_dep_name character varying, p_job_name character varying, p_att_date date, p_in_time time without time zone, p_out_time time without time zone, p_ot_hour double precision, p_amount numeric) AS
$BODY$
declare 
	inform_data RECORD ;


	begin  
		RAISE NOTICE 'Starting Store Procedure.......';	 
	--Deleting Temp Table

		DELETE FROM overtime_temp;
	FOR inform_data
		IN		

			SELECT C.*, (C.Attendance-18) as ot_hrs ,0 as worked_hours FROM
			(
			SELECT B.employee_id , B.name_related ,B.department, B.job , B.Attendance, B.att_date,A.in_time,B.out_time
			FROM
			(
			select employee_id,name_related,department,job,Attendance,att_date,in_time from(
			select HE.id as employee_id ,HE.name_related , HD.name as department , HJ.name as job ,(DATE_PART('HOUR', CAST(to_char(HA.name::timestamp at time zone 'UTC', 'YYYY-MM-DD HH24:MI:SS TZ') AS TIMESTAMP))
			+ (((DATE_PART('MINUTE', CAST(to_char(HA.name::timestamp at time zone 'UTC', 'YYYY-MM-DD HH24:MI:SS TZ') AS TIME)))/30)*0.5)) Attendance, day as sign_in_day
			,HA.name::date as att_date,cast(HA.name as time) +interval '6.5 hour'as in_time
			from hr_attendance HA , hr_employee HE ,hr_department HD , hr_job HJ,hr_contract HC
			where HA.action = 'sign_in'
			and extract(dow from HA.name) != 6
			and HE.id = HA.employee_id
			and HE.department_id = HD.id
			and HC.job_id = HJ.id
			and HC.employee_id=HE.id
			and HA.employee_id=param_employee_id
			AND ha.name::date
			BETWEEN from_date
			AND to_date
			)A
			) A,
			( select employee_id,name_related,department,job,Attendance,att_date,out_time from(
			select HE.id as employee_id ,HE.name_related , HD.name as department , HJ.name as job ,(DATE_PART('HOUR', CAST(to_char(HA.name::timestamp at time zone 'UTC', 'YYYY-MM-DD HH24:MI:SS TZ') AS TIMESTAMP))
			+ (((DATE_PART('MINUTE', CAST(to_char(HA.name::timestamp at time zone 'UTC', 'YYYY-MM-DD HH24:MI:SS TZ') AS TIME)))/30)*0.5)) Attendance, day as sign_in_day
			,HA.name::date as att_date,cast(HA.name as time) +interval '6.5 hour'as out_time
			from hr_attendance HA , hr_employee HE ,hr_department HD , hr_job HJ,hr_contract HC
			where HA.action = 'sign_out'
			and extract(dow from HA.name) != 6
			and HE.id = HA.employee_id
			and HE.department_id = HD.id
			and HC.job_id = HJ.id
			and HC.employee_id=HE.id
			and HA.employee_id=param_employee_id
			AND ha.name::date
			BETWEEN from_date
			AND to_date
			)A
			where Attendance>18
			) B
			WHERE A.att_date = B.att_date
			and A.employee_id = B.employee_id
			)C
			Union all

	                select B.employee_id,B.name_related,B.department,B.job,B.Attendance,A.sign_in_day,A.in_time,B.out_time,0 as ot_hrs,B.worked_hours from(
                        select HA.name::date as sign_in_day,(DATE_PART('HOUR', CAST(to_char(HA.name::timestamp at time zone 'UTC', 'YYYY-MM-DD HH24:MI:SS TZ') AS TIMESTAMP)) + 
			(((DATE_PART('MINUTE', CAST(to_char(HA.name::timestamp at time zone 'UTC', 'YYYY-MM-DD HH24:MI:SS TZ') AS TIMESTAMP)))/30)*0.5)) Attendance,cast(HA.name as time) +interval '6.5 hour'as in_time
			 from hr_attendance HA,hr_employee HE 
			where action= 'sign_in'
			and HE.id=HA.employee_id
			and extract(dow from HA.name) = 6
			and HA.name::date not in (select date::date from hr_gazetted_holiday)
			and HE.id =param_employee_id
			and HA.name::date
			BETWEEN from_date
			AND to_date
			)A,
			(select  HA.name::date as sign_out_day,HE.id as employee_id ,HE.name_related , HD.name as department , HJ.name as job,(DATE_PART('HOUR', CAST(to_char(HA.name::timestamp at time zone 'UTC', 'YYYY-MM-DD HH24:MI:SS TZ') AS TIMESTAMP)) + 
			(((DATE_PART('MINUTE', CAST(to_char(HA.name::timestamp at time zone 'UTC', 'YYYY-MM-DD HH24:MI:SS TZ') AS TIMESTAMP)))/30)*0.5)) Attendance,HA.name::date as att_date,cast(HA.name as time) +interval '6.5 hour'as out_time,HA.worked_hours
			 from hr_attendance HA,hr_employee HE,hr_department HD , hr_job HJ,hr_contract HC
			where action= 'sign_out'
			and HE.id=HA.employee_id
			and HE.department_id = HD.id
			and HC.job_id = HJ.id
			and HC.employee_id=HE.id
			and extract(dow from HA.name) = 6
			and HA.name::date not in (select date::date from hr_gazetted_holiday)
			and HE.id = param_employee_id
			and HA.name::date
			BETWEEN from_date
			AND to_date
			)B
		        where  A.sign_in_day=B.sign_out_day 		
		LOOP
		
                    INSERT INTO overtime_temp(emp_name,dep_name,job_name,att_date,in_time,out_time,ot_hour,amount)
		    VALUES (inform_data.name_related,inform_data.department,inform_data.job,inform_data.att_date,inform_data.in_time,inform_data.out_time,0,0);
		    if(inform_data.ot_hrs >= 1 and inform_data.ot_hrs < 2) Then
		      Update overtime_temp Set ot_hour=inform_data.ot_hrs,amount=600 where att_date=inform_data.att_date;
		    elseif(inform_data.ot_hrs >= 2 and inform_data.ot_hrs < 3) Then
		      Update overtime_temp Set ot_hour=inform_data.ot_hrs,amount=800 where att_date=inform_data.att_date;
		    elseif(inform_data.ot_hrs >= 3 and inform_data.ot_hrs < 4) Then
		      Update overtime_temp Set ot_hour=inform_data.ot_hrs,amount=1000 where att_date=inform_data.att_date;
		    elseif(inform_data.worked_hours >=4 and inform_data.worked_hours < 8) Then
		      Update overtime_temp Set ot_hour=inform_data.worked_hours,amount=700 where att_date=inform_data.att_date;
		    elseif(inform_data.worked_hours >=8) Then
		      Update overtime_temp Set ot_hour=inform_data.worked_hours,amount=1200 where att_date=inform_data.att_date;
		    end if;

               END LOOP;
               RETURN QUERY select row_number() over (order by hj.sequence) as id,ot.* 
                            from overtime_temp ot,hr_job hj
                            where ot.job_name=hj.name
                            order by hj.sequence;

                         --   select * from hr_employee where name_related like 'ဦးခ်မ္းၿငိမ္းေက်ာ္'
 END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION overtime_report_by_month(integer, date, date)
  OWNER TO openerp;


                