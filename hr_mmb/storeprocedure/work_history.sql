-- Function: work_history_report(integer)

-- DROP FUNCTION work_history_report(integer);

CREATE OR REPLACE FUNCTION work_history_report(IN param_emp_id integer)
  RETURNS TABLE(emp_name character varying, job_name character varying, dep_name character varying, from_date date, to_date date) AS
$BODY$
  DECLARE
	f_record RECORD;
	s_record RECORD;
	t_record RECORD;
	start_date date;
		
  BEGIN
	delete from work_histroy_temp;
        select trial_date_start into start_date from hr_contract where employee_id=param_emp_id;
	RAISE NOTICE 'Starting to retrieve sign_in Deduction times.....';
     FOR f_record 
        In        
	select id,employee_id as emp_id,src_id as src_job,dst_id as dst_job,src_department_id as src_department_id,dst_department_id as dst_dep_id,date as effected_date,date-1 as last_date from hr_department_transfer
	where state='done'
        and id in (select min(id) from hr_department_transfer where employee_id=param_emp_id)
        and employee_id=param_emp_id
     LOOP
	INSERT INTO work_histroy_temp(emp_id,job_id,dep_id,f_date,t_date)
	VALUES (f_record.emp_id,f_record.src_job,f_record.src_department_id,start_date,f_record.last_date);	
     END LOOP;



     FOR t_record 
        In        
	select id,employee_id as emp_id,src_id as src_job,dst_id as dst_job,src_department_id as src_department_id,dst_department_id as dst_dep_id,date as effected_date,date-1 as last_date from hr_department_transfer
	where state='done'
        and employee_id=param_emp_id
        order by id asc

     LOOP
        UPDATE work_histroy_temp SET t_date = t_record.last_date where t_date is Null and job_id=t_record.src_job;
        INSERT INTO work_histroy_temp(emp_id,job_id,dep_id,f_date,t_date)
	VALUES (t_record.emp_id,t_record.dst_job,t_record.dst_dep_id,t_record.effected_date,Null);
     END LOOP;
     
     
     RETURN QUERY select he.name_related,hj.name,hd.name,wh.f_date,wh.t_date from work_histroy_temp wh,hr_employee he,hr_job hj,hr_department hd
     where wh.emp_id=he.id
     and wh.job_id=hj.id
     and wh.dep_id=hd.id
     order by f_date asc;
        
     END;
	
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION work_history_report(integer)
  OWNER TO openerp;
