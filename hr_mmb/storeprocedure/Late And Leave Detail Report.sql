-- Function: calculate_forget_fingerprint_sign_in_deduction(date, date, integer)

-- DROP FUNCTION calculate_forget_fingerprint_sign_in_deduction(date, date, integer);

CREATE OR REPLACE FUNCTION calculate_forget_fingerprint_sign_in_deduction(IN from_date date, IN to_date date, IN param_department_id integer)
  RETURNS TABLE(fp_no_press_date date, employee_id integer) AS
$BODY$
  DECLARE
		sign_in_forget_days RECORD;
		emp_id RECORD;
		
  BEGIN
	delete from fb_days_temp;

	RAISE NOTICE 'Starting to retrieve sign_in Deduction times.....';

	IF param_department_id IS NULL THEN
		FOR emp_id
			IN
			    select id as emp_id from hr_employee 
			LOOP
	  
				---Get total sign_in_deduction Times
				FOR sign_in_forget_days	
				IN
					select AA.sign_in_day as sign_in_day,AA.employee_id as e_id
					   from (
					select  A.att_date::date as sign_in_day,A.employee_id
					  from
					  (
					select 
					att.name + '6 hour'::interval + '30 minutes'::interval as att_date,att.employee_id
					from hr_attendance att 
					where att.employee_id = emp_id.emp_id
					and action='sign_out'
					and att.name+ '6 hour'::interval + '30 minutes'::interval
					between from_date and to_date
					)A
					)AA
					where AA.sign_in_day not in
					(
					select att_date::date as in_date from(
					 select 
					(date_part('hour', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)) +
					(((date_part('minute', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)))/30)*0.5)) as attendance,att.name + '6 hour'::interval + '30 minutes'::interval as att_date 
					from hr_attendance att 
					where att.employee_id = emp_id.emp_id
					and action='sign_in'
					and att.name+ '6 hour'::interval + '30 minutes'::interval
					between from_date and to_date
					)A
					)
				LOOP
					  INSERT INTO fb_days_temp(
						    fp_no_days,emp_id)
					  VALUES (sign_in_forget_days.sign_in_day,sign_in_forget_days.e_id);	

					
					
					RAISE NOTICE 'Total sign in deduction successfully retrieved!....';
				END LOOP;

		END LOOP;

	ELSIF param_department_id=1873 THEN
		FOR emp_id
			IN
			    select id as emp_id from hr_employee where department_id in (select id from hr_department where parent_id in (select id from hr_department where id=param_department_id))
			LOOP
	  
				---Get total sign_in_deduction Times
				FOR sign_in_forget_days	
				IN
					select AA.sign_in_day as sign_in_day,AA.employee_id as e_id
					   from (
					select  A.att_date::date as sign_in_day,A.employee_id
					  from
					  (
					select 
					att.name + '6 hour'::interval + '30 minutes'::interval as att_date,att.employee_id
					from hr_attendance att 
					where att.employee_id = emp_id.emp_id
					and action='sign_out'
					and att.name+ '6 hour'::interval + '30 minutes'::interval
					between from_date and to_date
					)A
					)AA
					where AA.sign_in_day not in
					(
					select att_date::date as in_date from(
					 select 
					(date_part('hour', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)) +
					(((date_part('minute', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)))/30)*0.5)) as attendance,att.name + '6 hour'::interval + '30 minutes'::interval as att_date 
					from hr_attendance att 
					where att.employee_id = emp_id.emp_id
					and action='sign_in'
					and att.name+ '6 hour'::interval + '30 minutes'::interval
					between from_date and to_date
					)A
					)
				LOOP
					  INSERT INTO fb_days_temp(
						    fp_no_days,emp_id)
					  VALUES (sign_in_forget_days.sign_in_day,sign_in_forget_days.e_id);	

					
					
					RAISE NOTICE 'Total sign in deduction successfully retrieved!....';
				END LOOP;

		END LOOP;

	ELSE

		FOR emp_id
		IN
		    select id as emp_id from hr_employee where department_id=param_department_id
		LOOP
	  
			---Get total sign_in_deduction Times
			FOR sign_in_forget_days	
			IN
				select AA.sign_in_day as sign_in_day,AA.employee_id as e_id
				   from (
				select  A.att_date::date as sign_in_day,A.employee_id
				  from
				  (
				select 
				att.name + '6 hour'::interval + '30 minutes'::interval as att_date,att.employee_id
				from hr_attendance att 
				where att.employee_id = emp_id.emp_id
				and action='sign_out'
				and att.name+ '6 hour'::interval + '30 minutes'::interval
				between from_date and to_date
				)A
				)AA
				where AA.sign_in_day not in
				(
				select att_date::date as in_date from(
				 select 
				(date_part('hour', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)) +
				(((date_part('minute', cast(to_char(name::timestamp at time zone 'utc', 'yyyy-mm-dd hh24:mi:ss tz') as timestamp)))/30)*0.5)) as attendance,att.name + '6 hour'::interval + '30 minutes'::interval as att_date 
				from hr_attendance att 
				where att.employee_id = emp_id.emp_id
				and action='sign_in'
				and att.name+ '6 hour'::interval + '30 minutes'::interval
				between from_date and to_date
				)A
				)
			LOOP
				  INSERT INTO fb_days_temp(
					    fp_no_days,emp_id)
				  VALUES (sign_in_forget_days.sign_in_day,sign_in_forget_days.e_id);	

				
				
				RAISE NOTICE 'Total sign in deduction successfully retrieved!....';
			END LOOP;

		END LOOP;

	END IF;

               RETURN QUERY select * from fb_days_temp order by fp_no_days asc;
        
	END;
	
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION calculate_forget_fingerprint_sign_in_deduction(date, date, integer)
  OWNER TO openerp;

-- Function: calculate_leave_days(date, date, integer)

-- DROP FUNCTION calculate_leave_days(date, date, integer);


CREATE OR REPLACE FUNCTION calculate_leave_days(IN from_date date, IN to_date date, IN param_department_id integer)
  RETURNS TABLE(hole_day date, half_day date, param_emp_id integer, hold_name character varying, half_name character varying) AS
$BODY$
	DECLARE a_record RECORD;
	DECLARE record_back RECORD;
	DECLARE new_a_record RECORD;
	DECLARE leave_record RECORD;
	 
	BEGIN
	        delete from leave_days_temp;
	        --select * from leave_days_temp;
		RAISE NOTICE 'Starting to calculate leave days.......';
  		
		IF param_department_id IS NULL THEN

		       FOR leave_record
		       IN
			    select id as emp_id from hr_employee
		       LOOP

				FOR a_record 
					IN	
					select date_from::date,date_to::date ,employee_id,name,number_of_days_temp from (
					select date_from,date_to,employee_id,hh.name,hh.number_of_days_temp from hr_holidays hh ,hr_holidays_status hhs
					where hh.holiday_status_id=hhs.id
					and hh.number_of_days_temp =0.5
					union all
					select date_from,date_to,employee_id,hh.name,hh.number_of_days_temp from hr_holidays hh ,hr_holidays_status hhs
					where hh.holiday_status_id=hhs.id
					and hh.number_of_days_temp >=1
					)A
					where employee_id= leave_record.emp_id
					
				LOOP

					FOR new_a_record 
					IN   
						select * from(
						select date_of_month::date from (
										select a_record.date_from::date + sun *'1day'::interval as date_of_month
												from generate_series(0,(select (a_record.date_to::date - a_record.date_from::date))) sun
												)A)B where date_of_month between from_date and to_date
					LOOP
					
					RAISE NOTICE 'date_of_month % ',new_a_record.date_of_month;

					IF (a_record.number_of_days_temp>=1)Then
					   RAISE NOTICE 'date_of_month111111 % ',new_a_record.date_of_month;
					   INSERT INTO leave_days_temp(hold_leave_days,half_leave_days,emp_id,hold_leave_name)
					   VALUES (new_a_record.date_of_month,Null,a_record.employee_id,a_record.name);				
					   ELSEIF (a_record.number_of_days_temp=0.5) Then
					   RAISE NOTICE 'date_of_month222222222 % ',new_a_record.date_of_month;
					   INSERT INTO leave_days_temp(hold_leave_days,half_leave_days,emp_id,hold_leave_name)
					   VALUES (Null,new_a_record.date_of_month,a_record.employee_id,a_record.name);				
					   END IF;
					

					
					END LOOP;
				
				

				END LOOP;
			END LOOP;

		ELSIF param_department_id=1873 THEN

			  FOR leave_record
			       IN
				    select id as emp_id from hr_employee where department_id in (select id from hr_department where parent_id in (select id from hr_department where id=param_department_id))
			       LOOP

					FOR a_record 
						IN	
						select date_from::date,date_to::date ,employee_id,name,number_of_days_temp from (
						select date_from,date_to,employee_id,hh.name,hh.number_of_days_temp from hr_holidays hh ,hr_holidays_status hhs
						where hh.holiday_status_id=hhs.id
						and hh.number_of_days_temp =0.5
						union all
						select date_from,date_to,employee_id,hh.name,hh.number_of_days_temp from hr_holidays hh ,hr_holidays_status hhs
						where hh.holiday_status_id=hhs.id
						and hh.number_of_days_temp >=1
						)A
						where employee_id= leave_record.emp_id
						
					LOOP

						FOR new_a_record 
						IN   
							select * from(
							select date_of_month::date from (
											select a_record.date_from::date + sun *'1day'::interval as date_of_month
													from generate_series(0,(select (a_record.date_to::date - a_record.date_from::date))) sun
													)A)B where date_of_month between from_date and to_date
						LOOP
						
						RAISE NOTICE 'date_of_month % ',new_a_record.date_of_month;

						IF (a_record.number_of_days_temp>=1)Then
						   RAISE NOTICE 'date_of_month111111 % ',new_a_record.date_of_month;
						   INSERT INTO leave_days_temp(hold_leave_days,half_leave_days,emp_id,hold_leave_name)
						   VALUES (new_a_record.date_of_month,Null,a_record.employee_id,a_record.name);				
						   ELSEIF (a_record.number_of_days_temp=0.5) Then
						   RAISE NOTICE 'date_of_month222222222 % ',new_a_record.date_of_month;
						   INSERT INTO leave_days_temp(hold_leave_days,half_leave_days,emp_id,hold_leave_name)
						   VALUES (Null,new_a_record.date_of_month,a_record.employee_id,a_record.name);				
						   END IF;
						

						
						END LOOP;
					
					

					END LOOP;
				END LOOP;
		ELSE
			  FOR leave_record
			       IN
				    select id as emp_id from hr_employee where department_id=param_department_id
			       LOOP

					FOR a_record 
						IN	
						select date_from::date,date_to::date ,employee_id,name,number_of_days_temp from (
						select date_from,date_to,employee_id,hh.name,hh.number_of_days_temp from hr_holidays hh ,hr_holidays_status hhs
						where hh.holiday_status_id=hhs.id
						and hh.number_of_days_temp =0.5
						union all
						select date_from,date_to,employee_id,hh.name,hh.number_of_days_temp from hr_holidays hh ,hr_holidays_status hhs
						where hh.holiday_status_id=hhs.id
						and hh.number_of_days_temp >=1
						)A
						where employee_id= leave_record.emp_id
						
					LOOP

						FOR new_a_record 
						IN   
							select * from(
							select date_of_month::date from (
											select a_record.date_from::date + sun *'1day'::interval as date_of_month
													from generate_series(0,(select (a_record.date_to::date - a_record.date_from::date))) sun
													)A)B where date_of_month between from_date and to_date
						LOOP
						
						RAISE NOTICE 'date_of_month % ',new_a_record.date_of_month;

						IF (a_record.number_of_days_temp>=1)Then
						   RAISE NOTICE 'date_of_month111111 % ',new_a_record.date_of_month;
						   INSERT INTO leave_days_temp(hold_leave_days,half_leave_days,emp_id,hold_leave_name)
						   VALUES (new_a_record.date_of_month,Null,a_record.employee_id,a_record.name);				
						   ELSEIF (a_record.number_of_days_temp=0.5) Then
						   RAISE NOTICE 'date_of_month222222222 % ',new_a_record.date_of_month;
						   INSERT INTO leave_days_temp(hold_leave_days,half_leave_days,emp_id,hold_leave_name)
						   VALUES (Null,new_a_record.date_of_month,a_record.employee_id,a_record.name);				
						   END IF;
						

						
						END LOOP;
					
					

					END LOOP;
				END LOOP;
		END IF;
		
	RAISE NOTICE 'Leave Days Successfully Saved!';
	
	RETURN QUERY select * from leave_days_temp;
		    
		
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION calculate_leave_days(date, date, integer)
  OWNER TO openerp;


-- Function: calculate_leave_days(integer)
--select * from calculate_leave_and_late_days('2015-04-01','2015-04-30',2)
--select name,* from hr_job
-- DROP FUNCTION calculate_leave_and_late_days(date,date,integer);

CREATE OR REPLACE FUNCTION calculate_leave_and_late_days(IN from_date date, IN to_date date, IN param_dep_id integer)
  RETURNS TABLE(id bigint, param_emp_name character varying, param_job_name character varying, param_dep_name character varying, param_no_fp date, param_whole_leave date, param_half_leave date, param_late_day date, param_action character varying) AS
$BODY$
	DECLARE first_record RECORD;
	DECLARE second_record RECORD;
	DECLARE third_record RECORD;
	DECLARE fourth_record RECORD;
	DECLARE fifth_record RECORD;
	DECLARE no_fb RECORD;
        DECLARE no_fb_data RECORD;
        DECLARE late_leave RECORD;
        DECLARE leave RECORD;
        DECLARE leave_data RECORD;

        DECLARE late_leave_data RECORD;


BEGIN
        Delete from leave_late_temp;

	IF param_dep_id IS NULL THEN
		FOR first_record
			IN
			    select he.id as emp_id,he.name_related,hj.name,hd.name from hr_employee he,hr_job hj,hr_department hd,hr_contract hc
			    where he.id=hc.employee_id
			    and hc.job_id=hj.id
			    and he.department_id=hd.id
			   
			LOOP                  
			    FOR  second_record 
			    IN
				select hpll.code,hpll.active_start_time,hpll.active_end_time,hpll.policy_id ,hpg.name,hc.employee_id,pay_day,hc.job_id
				from hr_policy_line_late hpll,hr_policy_group hpg,hr_contract hc,hr_policy_group_late_rel hrel,hr_policy_late hpl
				where hpg.id=hrel.group_id
				and hrel.late_id=hpl.id
				and hpl.id=hpll.policy_id
				and hc.policy_group_id=hpg.id
				and hpll.code='WORKLD1'
				and hc.employee_id=first_record.emp_id
				Union All
				select hpll.code,hpll.active_start_time,hpll.active_end_time,hpll.policy_id ,hpg.name,hc.employee_id,pay_day,hc.job_id
				from hr_policy_line_late hpll,hr_policy_group hpg,hr_contract hc,hr_policy_group_late_rel hrel,hr_policy_late hpl
				where hpg.id=hrel.group_id
				and hrel.late_id=hpl.id
				and hpl.id=hpll.policy_id
				and hc.policy_group_id=hpg.id
				and hpll.code='WORKLD4'
				and hc.employee_id=first_record.emp_id
			    LOOP
			      RAISE NOTICE 'Employee_id,,,,,,,,,,%',second_record.employee_id;
			      IF (second_record.code='WORKLD1')Then
				RAISE NOTICE 'job,,,,,,,,,,%',second_record.job_id;
				RAISE NOTICE 'second_record.active_start_time,,,,,,,,,%',second_record.active_start_time;
				RAISE NOTICE 'second_record.active_end_time,,,,,,,,,%',second_record.active_end_time;	       
				FOR third_record
				IN
					select ha.name::date as att_date,cast(ha.name as time) +interval '6.5 hour'as in_time,ha.employee_id,he.name_related as e_name,hj.name as j_name,hd.name as d_name
					from hr_attendance ha,hr_employee he,hr_job hj,hr_department hd,hr_contract hc
					where he.id=hc.employee_id
					and ha.employee_id=he.id
					and hc.job_id=hj.id
					and he.department_id=hd.id
					and action='sign_in'
					and extract(dow from ha.name) != 6
					and ha.employee_id=second_record.employee_id
					and ha.name::date between from_date and to_date
					and cast(ha.name as time) +interval '6.5 hour' 
					between (cast(second_record.active_start_time as time)+ interval '0 hour') and (cast(second_record.active_end_time as time)+ interval '0 hour')
				LOOP
					RAISE NOTICE 'third_record.att_date,,,,,,,,,%',third_record.att_date;

					INSERT INTO leave_late_temp(emp_name,job_name,dep_name,no_fp,whole_leave,half_leave,late_day,action)
					Values (third_record.e_name,third_record.j_name,third_record.d_name,Null,Null,Null,third_record.att_date,'late '||third_record.in_time);
				END LOOP;
				
						
			      ELSEIF (second_record.code='WORKLD4' and second_record.job_id!=6)Then

				FOR fourth_record
				IN
					select ha.name::date as att_date,cast(ha.name as time) +interval '6.5 hour'as in_time,ha.employee_id,he.name_related as e_name,hj.name as j_name,hd.name as d_name
					from hr_attendance ha,hr_employee he,hr_job hj,hr_department hd,hr_contract hc
					where he.id=hc.employee_id
					and ha.employee_id=he.id
					and hc.job_id=hj.id
					and he.department_id=hd.id
					and action='sign_in'
					and extract(dow from ha.name) != 6
					and ha.name::date between from_date and to_date

					and ha.name::date=second_record.pay_day			
					and ha.employee_id=second_record.employee_id
					and cast(ha.name as time) +interval '6.5 hour' 
					between (cast(second_record.active_start_time as time)+ interval '0 hour') and (cast(second_record.active_end_time as time)+ interval '0 hour')
				LOOP
					INSERT INTO leave_late_temp(emp_name,job_name,dep_name,no_fp,whole_leave,half_leave,late_day,action)
					Values (fourth_record.e_name,fourth_record.j_name,fourth_record.d_name,Null,Null,Null,fourth_record.att_date,'late '||fourth_record.in_time);
				END LOOP;  
			      ELSEIF (second_record.code='WORKLD4' and second_record.job_id=6)Then
				RAISE NOTICE 'job,11111,,,,,,,,,%',second_record.job_id;
			      
				FOR fifth_record
				IN

				
					select ha.name::date as att_date,cast(ha.name as time) +interval '6.5 hour'as in_time,ha.employee_id,he.name_related as e_name,hj.name as j_name,hd.name as d_name
					from hr_attendance ha,hr_employee he,hr_job hj,hr_department hd,hr_contract hc
					where he.id=hc.employee_id
					and ha.employee_id=he.id
					and hc.job_id=hj.id
					and he.department_id=hd.id
					and action='sign_in'
					and extract(dow from ha.name) != 6
					and ha.employee_id=second_record.employee_id
					and ha.name::date between from_date and to_date

					and cast(ha.name as time) +interval '6.5 hour' 
					between (cast(second_record.active_start_time as time)+ interval '0 hour') and (cast(second_record.active_end_time as time)+ interval '0 hour')
				LOOP
					RAISE NOTICE 'fifth_record.att_date,,,,,,,,,%',fifth_record.att_date;
				
					INSERT INTO leave_late_temp(emp_name,job_name,dep_name,no_fp,whole_leave,half_leave,late_day,action)
					Values (fifth_record.e_name,fifth_record.j_name,fifth_record.d_name,Null,Null,Null,fifth_record.att_date,'late '||fifth_record.in_time);
				END LOOP; 
			       END IF;     
			     END LOOP;
			END LOOP;

	ELSIF param_dep_id=1873 THEN

		FOR first_record
			IN
			    select he.id as emp_id,he.name_related,hj.name,hd.name from hr_employee he,hr_job hj,hr_department hd,hr_contract hc
			    where he.id=hc.employee_id
			    and hc.job_id=hj.id
			    and he.department_id=hd.id
			    and he.department_id in (select hd.id from hr_department hd where hd.parent_id in (select hd.id from hr_department hd where hd.id=param_dep_id))
			   
			LOOP                  
			    FOR  second_record 
			    IN
				select hpll.code,hpll.active_start_time,hpll.active_end_time,hpll.policy_id ,hpg.name,hc.employee_id,pay_day,hc.job_id
				from hr_policy_line_late hpll,hr_policy_group hpg,hr_contract hc,hr_policy_group_late_rel hrel,hr_policy_late hpl
				where hpg.id=hrel.group_id
				and hrel.late_id=hpl.id
				and hpl.id=hpll.policy_id
				and hc.policy_group_id=hpg.id
				and hpll.code='WORKLD1'
				and hc.employee_id=first_record.emp_id
				Union All
				select hpll.code,hpll.active_start_time,hpll.active_end_time,hpll.policy_id ,hpg.name,hc.employee_id,pay_day,hc.job_id
				from hr_policy_line_late hpll,hr_policy_group hpg,hr_contract hc,hr_policy_group_late_rel hrel,hr_policy_late hpl
				where hpg.id=hrel.group_id
				and hrel.late_id=hpl.id
				and hpl.id=hpll.policy_id
				and hc.policy_group_id=hpg.id
				and hpll.code='WORKLD4'
				and hc.employee_id=first_record.emp_id
			    LOOP
			      RAISE NOTICE 'Employee_id,,,,,,,,,,%',second_record.employee_id;
			      IF (second_record.code='WORKLD1')Then
				RAISE NOTICE 'job,,,,,,,,,,%',second_record.job_id;
				RAISE NOTICE 'second_record.active_start_time,,,,,,,,,%',second_record.active_start_time;
				RAISE NOTICE 'second_record.active_end_time,,,,,,,,,%',second_record.active_end_time;	       
				FOR third_record
				IN
					select ha.name::date as att_date,cast(ha.name as time) +interval '6.5 hour'as in_time,ha.employee_id,he.name_related as e_name,hj.name as j_name,hd.name as d_name
					from hr_attendance ha,hr_employee he,hr_job hj,hr_department hd,hr_contract hc
					where he.id=hc.employee_id
					and ha.employee_id=he.id
					and hc.job_id=hj.id
					and he.department_id=hd.id
					and action='sign_in'
					and extract(dow from ha.name) != 6
					and ha.employee_id=second_record.employee_id
					and ha.name::date between from_date and to_date
					and cast(ha.name as time) +interval '6.5 hour' 
					between (cast(second_record.active_start_time as time)+ interval '0 hour') and (cast(second_record.active_end_time as time)+ interval '0 hour')
				LOOP
					RAISE NOTICE 'third_record.att_date,,,,,,,,,%',third_record.att_date;

					INSERT INTO leave_late_temp(emp_name,job_name,dep_name,no_fp,whole_leave,half_leave,late_day,action)
					Values (third_record.e_name,third_record.j_name,third_record.d_name,Null,Null,Null,third_record.att_date,'late '||third_record.in_time);
				END LOOP;
				
						
			      ELSEIF (second_record.code='WORKLD4' and second_record.job_id!=6)Then

				FOR fourth_record
				IN
					select ha.name::date as att_date,cast(ha.name as time) +interval '6.5 hour'as in_time,ha.employee_id,he.name_related as e_name,hj.name as j_name,hd.name as d_name
					from hr_attendance ha,hr_employee he,hr_job hj,hr_department hd,hr_contract hc
					where he.id=hc.employee_id
					and ha.employee_id=he.id
					and hc.job_id=hj.id
					and he.department_id=hd.id
					and action='sign_in'
					and extract(dow from ha.name) != 6
					and ha.name::date between from_date and to_date

					and ha.name::date=second_record.pay_day			
					and ha.employee_id=second_record.employee_id
					and cast(ha.name as time) +interval '6.5 hour' 
					between (cast(second_record.active_start_time as time)+ interval '0 hour') and (cast(second_record.active_end_time as time)+ interval '0 hour')
				LOOP
					INSERT INTO leave_late_temp(emp_name,job_name,dep_name,no_fp,whole_leave,half_leave,late_day,action)
					Values (fourth_record.e_name,fourth_record.j_name,fourth_record.d_name,Null,Null,Null,fourth_record.att_date,'late '||fourth_record.in_time);
				END LOOP;  
			      ELSEIF (second_record.code='WORKLD4' and second_record.job_id=6)Then
				RAISE NOTICE 'job,11111,,,,,,,,,%',second_record.job_id;
			      
				FOR fifth_record
				IN

				
					select ha.name::date as att_date,cast(ha.name as time) +interval '6.5 hour'as in_time,ha.employee_id,he.name_related as e_name,hj.name as j_name,hd.name as d_name
					from hr_attendance ha,hr_employee he,hr_job hj,hr_department hd,hr_contract hc
					where he.id=hc.employee_id
					and ha.employee_id=he.id
					and hc.job_id=hj.id
					and he.department_id=hd.id
					and action='sign_in'
					and extract(dow from ha.name) != 6
					and ha.employee_id=second_record.employee_id
					and ha.name::date between from_date and to_date

					and cast(ha.name as time) +interval '6.5 hour' 
					between (cast(second_record.active_start_time as time)+ interval '0 hour') and (cast(second_record.active_end_time as time)+ interval '0 hour')
				LOOP
					RAISE NOTICE 'fifth_record.att_date,,,,,,,,,%',fifth_record.att_date;
				
					INSERT INTO leave_late_temp(emp_name,job_name,dep_name,no_fp,whole_leave,half_leave,late_day,action)
					Values (fifth_record.e_name,fifth_record.j_name,fifth_record.d_name,Null,Null,Null,fifth_record.att_date,'late '||fifth_record.in_time);
				END LOOP; 
			       END IF;     
			     END LOOP;
			END LOOP;

	ELSE
	
		FOR first_record
		IN
		    select he.id as emp_id,he.name_related,hj.name,hd.name from hr_employee he,hr_job hj,hr_department hd,hr_contract hc
		    where he.id=hc.employee_id
		    and hc.job_id=hj.id
		    and he.department_id=hd.id
		    and he.department_id=param_dep_id
		LOOP                  
		    FOR  second_record 
		    IN
			select hpll.code,hpll.active_start_time,hpll.active_end_time,hpll.policy_id ,hpg.name,hc.employee_id,pay_day,hc.job_id
			from hr_policy_line_late hpll,hr_policy_group hpg,hr_contract hc,hr_policy_group_late_rel hrel,hr_policy_late hpl
			where hpg.id=hrel.group_id
			and hrel.late_id=hpl.id
			and hpl.id=hpll.policy_id
			and hc.policy_group_id=hpg.id
			and hpll.code='WORKLD1'
			and hc.employee_id=first_record.emp_id
			Union All
			select hpll.code,hpll.active_start_time,hpll.active_end_time,hpll.policy_id ,hpg.name,hc.employee_id,pay_day,hc.job_id
			from hr_policy_line_late hpll,hr_policy_group hpg,hr_contract hc,hr_policy_group_late_rel hrel,hr_policy_late hpl
			where hpg.id=hrel.group_id
			and hrel.late_id=hpl.id
			and hpl.id=hpll.policy_id
			and hc.policy_group_id=hpg.id
			and hpll.code='WORKLD4'
			and hc.employee_id=first_record.emp_id
		    LOOP
		      RAISE NOTICE 'Employee_id,,,,,,,,,,%',second_record.employee_id;
		      IF (second_record.code='WORKLD1')Then
			RAISE NOTICE 'job,,,,,,,,,,%',second_record.job_id;
			RAISE NOTICE 'second_record.active_start_time,,,,,,,,,%',second_record.active_start_time;
			RAISE NOTICE 'second_record.active_end_time,,,,,,,,,%',second_record.active_end_time;	       
			FOR third_record
			IN
				select ha.name::date as att_date,cast(ha.name as time) +interval '6.5 hour'as in_time,ha.employee_id,he.name_related as e_name,hj.name as j_name,hd.name as d_name
				from hr_attendance ha,hr_employee he,hr_job hj,hr_department hd,hr_contract hc
				where he.id=hc.employee_id
				and ha.employee_id=he.id
				and hc.job_id=hj.id
				and he.department_id=hd.id
				and action='sign_in'
				and extract(dow from ha.name) != 6
				and ha.employee_id=second_record.employee_id
				and ha.name::date between from_date and to_date
				and cast(ha.name as time) +interval '6.5 hour' 
				between (cast(second_record.active_start_time as time)+ interval '0 hour') and (cast(second_record.active_end_time as time)+ interval '0 hour')
			LOOP
				RAISE NOTICE 'third_record.att_date,,,,,,,,,%',third_record.att_date;

				INSERT INTO leave_late_temp(emp_name,job_name,dep_name,no_fp,whole_leave,half_leave,late_day,action)
				Values (third_record.e_name,third_record.j_name,third_record.d_name,Null,Null,Null,third_record.att_date,'late '||third_record.in_time);
			END LOOP;
			
					
		      ELSEIF (second_record.code='WORKLD4' and second_record.job_id!=6)Then

			FOR fourth_record
			IN
				select ha.name::date as att_date,cast(ha.name as time) +interval '6.5 hour'as in_time,ha.employee_id,he.name_related as e_name,hj.name as j_name,hd.name as d_name
				from hr_attendance ha,hr_employee he,hr_job hj,hr_department hd,hr_contract hc
				where he.id=hc.employee_id
				and ha.employee_id=he.id
				and hc.job_id=hj.id
				and he.department_id=hd.id
				and action='sign_in'
				and extract(dow from ha.name) != 6
				and ha.name::date between from_date and to_date

				and ha.name::date=second_record.pay_day			
				and ha.employee_id=second_record.employee_id
				and cast(ha.name as time) +interval '6.5 hour' 
				between (cast(second_record.active_start_time as time)+ interval '0 hour') and (cast(second_record.active_end_time as time)+ interval '0 hour')
			LOOP
				INSERT INTO leave_late_temp(emp_name,job_name,dep_name,no_fp,whole_leave,half_leave,late_day,action)
				Values (fourth_record.e_name,fourth_record.j_name,fourth_record.d_name,Null,Null,Null,fourth_record.att_date,'late '||fourth_record.in_time);
			END LOOP;  
		      ELSEIF (second_record.code='WORKLD4' and second_record.job_id=6)Then
			RAISE NOTICE 'job,11111,,,,,,,,,%',second_record.job_id;
		      
			FOR fifth_record
			IN

			
				select ha.name::date as att_date,cast(ha.name as time) +interval '6.5 hour'as in_time,ha.employee_id,he.name_related as e_name,hj.name as j_name,hd.name as d_name
				from hr_attendance ha,hr_employee he,hr_job hj,hr_department hd,hr_contract hc
				where he.id=hc.employee_id
				and ha.employee_id=he.id
				and hc.job_id=hj.id
				and he.department_id=hd.id
				and action='sign_in'
				and extract(dow from ha.name) != 6
				and ha.employee_id=second_record.employee_id
				and ha.name::date between from_date and to_date

				and cast(ha.name as time) +interval '6.5 hour' 
				between (cast(second_record.active_start_time as time)+ interval '0 hour') and (cast(second_record.active_end_time as time)+ interval '0 hour')
			LOOP
				RAISE NOTICE 'fifth_record.att_date,,,,,,,,,%',fifth_record.att_date;
			
				INSERT INTO leave_late_temp(emp_name,job_name,dep_name,no_fp,whole_leave,half_leave,late_day,action)
				Values (fifth_record.e_name,fifth_record.j_name,fifth_record.d_name,Null,Null,Null,fifth_record.att_date,'late '||fifth_record.in_time);
			END LOOP; 
		       END IF;     
		     END LOOP;
		END LOOP;

	END IF;

	RAISE NOTICE 'Leave Days Successfully Saved!';
	FOR no_fb IN
	    select * from calculate_forget_fingerprint_sign_in_deduction(from_date, to_date, param_dep_id)
	LOOP
                FOR no_fb_data
	        IN
			select he.name_related as e_name,hj.name as j_name,hd.name as d_name
			from hr_employee he,hr_job hj,hr_department hd,hr_contract hc
			where he.id=hc.employee_id
			and hc.job_id=hj.id
			and he.department_id=hd.id	
			and he.id=no_fb.employee_id			
		LOOP
	
	               INSERT INTO leave_late_temp(emp_name,job_name,dep_name,no_fp,whole_leave,half_leave,late_day,action)
		        Values (no_fb_data.e_name,no_fb_data.j_name,no_fb_data.d_name,no_fb.fp_no_press_date,Null,Null,Null,'No FP(In)');
	        END LOOP;
	 END LOOP;
	 FOR leave IN
	     select * from calculate_leave_days(from_date, to_date, param_dep_id)
	 LOOP
          FOR leave_data
	        IN
			select he.name_related as e_name,hj.name as j_name,hd.name as d_name
			from hr_employee he,hr_job hj,hr_department hd,hr_contract hc
			where he.id=hc.employee_id
			and hc.job_id=hj.id
			and he.department_id=hd.id	
			and he.id=leave.param_emp_id			
		LOOP
		
		      if (leave.half_day is Null) Then
	      	        RAISE NOTICE 'leave.hole_day,,,,,,,,%',leave.hole_day;
	
	                INSERT INTO leave_late_temp(emp_name,job_name,dep_name,no_fp,whole_leave,half_leave,late_day,action)
		        Values (leave_data.e_name,leave_data.j_name,leave_data.d_name,Null,leave.hole_day,Null,Null,leave.hold_name);
		      elseif (leave.hole_day is Null) Then
	                RAISE NOTICE 'leave.half_day,,,,,,,,,%',leave.half_day;
	
	                INSERT INTO leave_late_temp(emp_name,job_name,dep_name,no_fp,whole_leave,half_leave,late_day,action)
		        Values (leave_data.e_name,leave_data.j_name,leave_data.d_name,Null,Null,leave.half_day,Null,leave.hold_name);
                      END if;
	        END LOOP;
	END LOOP;
	 
	
	RETURN QUERY select row_number() over (order by hj.sequence) as id,llt.* from leave_late_temp llt,hr_job hj
	             where llt.job_name=hj.name
	             order by hj.sequence;
		    
		
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION calculate_leave_and_late_days(date, date, integer)
  OWNER TO openerp;
