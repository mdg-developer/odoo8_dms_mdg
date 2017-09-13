-- Function: leave_summary_report(date, date,integer)
--select * from leave_summary_report('2015-05-01','2015-05-31',1847)
-- DROP FUNCTION leave_summary_report(date, date,integer);

CREATE OR REPLACE FUNCTION leave_summary_report(IN from_date date, IN to_date date, IN dept_id integer)
  RETURNS TABLE(p_id bigint, p_ab numeric, p_un numeric, p_me numeric, p_employee integer, p_cal_allocated numeric, p_causal numeric, p_earn_allcated numeric, p_earn numeric, p_cal_balance numeric, p_earn_balance numeric, p_unpaid1 numeric, p_unpaid2 numeric, p_medical1 numeric, p_medical2 numeric, p_medical3 numeric, p_maternity numeric, p_absent1 numeric, p_absent2 numeric, p_job character varying, p_emp_name character varying) AS
$BODY$
declare 
	report_data RECORD ;
	employee_data  RECORD ;
	temp Numeric; 


	begin  
		RAISE NOTICE 'Starting Store Procedure.......';	 
	--Deleting Temp Table
	--select * from hr_employee
		DELETE FROM report_temp;

	IF dept_id IS NULL THEN
		FOR employee_data
			IN
			select distinct hre.name_related,hj.name as job from hr_holidays hhs,hr_employee hre,hr_job hj,hr_contract hc where hhs.employee_id=hre.id and hj.id=hc.job_id and hre.id=hc.employee_id

		LOOP	
			INSERT INTO report_temp(employee,cal_allocated ,causal ,cal_balance,earn_allcated ,earn ,earn_balance ,unpaid1 ,unpaid2 ,medical1 ,medical2 ,
			medical3,maternity ,absent1 ,absent2 ,job ,emp_name)
			VALUES (0,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0,
			0,0 ,0 ,0 ,employee_data.job,employee_data.name_related);
			    
		END LOOP; 

	ELSIF dept_id=1873 THEN
		FOR employee_data
			IN
			select distinct hre.name_related,hj.name as job from hr_holidays hhs,hr_employee hre,hr_job hj,hr_contract hc,hr_department hd where hhs.employee_id=hre.id and hj.id=hc.job_id and hre.id=hc.employee_id and hre.department_id=hd.id
			and hd.id in (select id from hr_department where parent_id in (select id from hr_department where id=dept_id))
		LOOP	
			INSERT INTO report_temp(employee,cal_allocated ,causal ,cal_balance,earn_allcated ,earn ,earn_balance ,unpaid1 ,unpaid2 ,medical1 ,medical2 ,
			medical3,maternity ,absent1 ,absent2 ,job ,emp_name)
			VALUES (0,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0,
			0,0 ,0 ,0 ,employee_data.job,employee_data.name_related);
			    
		END LOOP; 

	ELSE
		FOR employee_data
			IN
				select distinct hre.name_related,hj.name as job from hr_holidays hhs,hr_employee hre,hr_job hj,hr_contract hc,hr_department hd where hhs.employee_id=hre.id and hj.id=hc.job_id and hre.id=hc.employee_id and hre.department_id=hd.id
				and hd.id=dept_id

		LOOP	
				INSERT INTO report_temp(employee,cal_allocated ,causal ,cal_balance,earn_allcated ,earn ,earn_balance ,unpaid1 ,unpaid2 ,medical1 ,medical2 ,
				medical3,maternity ,absent1 ,absent2 ,job ,emp_name)
				VALUES (0,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0,
				0,0 ,0 ,0 ,employee_data.job,employee_data.name_related);
			    
		END LOOP; 
	END IF;

	FOR report_data
	 
	IN      
                SELECT
                    min(hrs.id) as id,hhs.code,
                    rr.name as name,
                    sum(hrs.number_of_days) as no_of_leaves,
                    0 as allocated,0 as leave,
                    hhs.name as leave_type,
                    hj.name as job
                FROM
                    hr_holidays as hrs, hr_employee as hre,hr_job as hj,
                    resource_resource as rr,hr_holidays_status as hhs
                WHERE
                    hrs.employee_id = hre.id and
                    hre.resource_id =  rr.id and
                    hhs.id = hrs.holiday_status_id and
                    hj.id=hre.job_id 
                    --and  hrs.date_from::date between from_date and to_date
                GROUP BY
                    rr.name,rr.user_id,hhs.name,hj.name,hhs.code

                union all
                SELECT
                    min(hrs.id) as id,hhs.code,
                    rr.name as name, 0 as no_of_leaves,
                    sum(hrs.number_of_days) as allocated,0 as leave,
                    hhs.name as leave_type,
                    hj.name as job
                FROM
                    hr_holidays as hrs, hr_employee as hre,hr_job as hj,
                    resource_resource as rr,hr_holidays_status as hhs
                WHERE
                    hrs.employee_id = hre.id and
                    hre.resource_id =  rr.id and
                    hhs.id = hrs.holiday_status_id and
                    hj.id=hre.job_id 
                    --and  hrs.date_from::date between from_date and to_date
                    and hrs.number_of_days >0
                GROUP BY
                    rr.name,rr.user_id,hhs.name,hj.name,hhs.code
                union all
                SELECT
                    min(hrs.id) as id,hhs.code,
                    rr.name as name, 0 as no_of_leaves,
                    0 as allocated,sum(hrs.number_of_days) as leave,
                    hhs.name as leave_type,
                    hj.name as job
                FROM
                    hr_holidays as hrs, hr_employee as hre,hr_job as hj,
                    resource_resource as rr,hr_holidays_status as hhs
                WHERE
                    hrs.employee_id = hre.id and
                    hre.resource_id =  rr.id and
                    hhs.id = hrs.holiday_status_id and
                    hj.id=hre.job_id 
                    --and  hrs.date_from::date between from_date and to_date
                    and hrs.number_of_days <0
                GROUP BY
                    rr.name,rr.user_id,hhs.name,hj.name,hhs.code
           LOOP
                RAISE NOTICE 'Starting Store Procedure.......%',report_data.leave_type;
                RAISE NOTICE 'Starting Store Procedure.......%',report_data.no_of_leaves;
                RAISE NOTICE 'Starting Store Procedure.......%',report_data.allocated;
                RAISE NOTICE 'Starting Store Procedure.......%',report_data.leave;
                RAISE NOTICE 'Starting Store Procedure.......%',report_data.name;

                if report_data.code='CAUSLV' and report_data.leave=0 and report_data.no_of_leaves=0 Then
                    
		    Update report_temp Set cal_allocated=report_data.allocated where emp_name=report_data.name;
		end if;	                
		if report_data.code='CAUSLV' and report_data.no_of_leaves =0 and report_data.allocated=0 Then
		    Update report_temp Set causal=-report_data.leave where emp_name=report_data.name;
		end if;                
		if report_data.code='CAUSLV' and report_data.allocated =0 and report_data.leave=0 Then
		    Update report_temp Set cal_balance=report_data.no_of_leaves where emp_name=report_data.name;
		end if;
                if report_data.code='EARNLV' and report_data.leave=0 and report_data.no_of_leaves=0 Then
                    
		    Update report_temp Set earn_allcated=report_data.allocated where emp_name=report_data.name;
		end if;	                
		if report_data.code='EARNLV' and report_data.no_of_leaves =0 and report_data.allocated=0Then
		    Update report_temp Set earn=-report_data.leave where emp_name=report_data.name;
		end if;                
		if report_data.code='EARNLV' and report_data.allocated =0 and report_data.leave =0 Then
		    Update report_temp Set earn_balance=report_data.no_of_leaves where emp_name=report_data.name;
		end if;
                if report_data.code='UNPLV1' and report_data.allocated =0 and report_data.leave =0  Then
		    Update report_temp Set unpaid1=report_data.no_of_leaves where emp_name=report_data.name;
		end if;
                if report_data.code='UNPLV2' and report_data.allocated =0 and report_data.leave =0 Then
		    Update report_temp Set unpaid2=report_data.no_of_leaves where emp_name=report_data.name;
		end if;
                if report_data.code='MEDLV1' and report_data.allocated =0 and report_data.leave =0  Then
		    Update report_temp Set medical1=report_data.no_of_leaves where emp_name=report_data.name;
		end if;
                if report_data.code='MEDLV2' and report_data.allocated =0 and report_data.leave =0 Then
		    Update report_temp Set medical2=report_data.no_of_leaves where emp_name=report_data.name;
		end if;
                if report_data.code='MEDLV3' and report_data.allocated =0 and report_data.leave =0  Then
		    Update report_temp Set medical3=report_data.no_of_leaves where emp_name=report_data.name;
		end if;
                if report_data.code='MATLV' and report_data.allocated =0 and report_data.leave =0 Then
		    Update report_temp Set maternity=-report_data.no_of_leaves where emp_name=report_data.name;
		end if;												
                if report_data.code='ABSLV1' and report_data.allocated =0 and report_data.leave =0  Then
		    Update report_temp Set absent1=report_data.no_of_leaves where emp_name=report_data.name;
		end if;
                if report_data.code='ABSLV2' and report_data.allocated =0 and report_data.leave =0 Then
		    Update report_temp Set absent2=report_data.no_of_leaves where emp_name=report_data.name;
		end if;		

		
	END LOOP;
		 	        
	        RETURN QUERY select row_number() over (order by hj.sequence) as serial_number,-(absent1+absent2) as absent,-(unpaid1+unpaid2) as unpaid ,-(medical1+medical2+medical3) as medical ,rt.* 
			     from report_temp rt,hr_job hj
			     where rt.job=hj.name
			     order by hj.sequence;

	
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION leave_summary_report(date, date, integer)
  OWNER TO openerp;
