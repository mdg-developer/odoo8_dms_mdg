-- Function: sign_out_absence(date, date)

-- DROP FUNCTION sign_out_absence(date, date);

CREATE OR REPLACE FUNCTION sign_out_absence(IN from_date date, IN to_date date)
  RETURNS TABLE(sign_in_day date, emp_name character varying) AS
$BODY$
  DECLARE
        sign_out_forget_days RECORD;
        emp_data RECORD;

   begin  
           RAISE NOTICE 'Starting Store Procedure.......';	 

           DELETE FROM fp_out_absence;
	   FOR emp_data IN
	            select id as employee_id from hr_employee
	   LOOP
            FOR sign_out_forget_days	
		IN
			select AA.sign_in_day as sign_in_day,AA.emp_name as e_id
			 from (
			       select  A.att_date::date as sign_in_day,A.employee_id,A.emp_name
			      from
			      (
			    select 
			    att.name + '6 hour'::interval + '30 minutes'::interval as att_date,att.employee_id,he.name_related as emp_name
			    from hr_attendance att ,hr_employee he
			    where action='sign_in'
			    and he.id=att.employee_id
			    and att.employee_id = emp_data.employee_id

			    and att.name::date
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
			    where action='sign_out'
			    and att.employee_id = emp_data.employee_id
			    
			    and att.name::date
			    between from_date and to_date
			    )A
			    )
		LOOP
			  INSERT INTO fp_out_absence(
				    fp_out_absence,emp_id)
			  VALUES (sign_out_forget_days.sign_in_day,sign_out_forget_days.e_id);	

			
			
			RAISE NOTICE 'Total sign in deduction successfully retrieved!....';
		END LOOP;

	END LOOP;
               RETURN QUERY select * from fp_out_absence group by emp_id,fp_out_absence order by fp_out_absence asc ;
        
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION sign_out_absence(date, date)
  OWNER TO openerp;
