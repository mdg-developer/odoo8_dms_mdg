-- Function: emp_count_with_job(date, character varying, character varying)

-- DROP FUNCTION emp_count_with_job(date, character varying, character varying);

CREATE OR REPLACE FUNCTION emp_count_with_job(IN from_date date, IN dept character varying, IN condition character varying)
  RETURNS TABLE(p_id bigint, p_job_name character varying, count integer) AS
$BODY$
declare 
    job_data RECORD;
	first_record RECORD ;
	second_record RECORD;
	third_record RECORD;
	fourth_record RECORD;
	fifth_record RECORD;

	begin  
		RAISE NOTICE 'Starting Store Procedure.......';	 
	--Deleting Temp Table
                --select * from emp_count
		DELETE FROM emp_count;

	   FOR job_data IN
	            select name from hr_job
	   LOOP
		    INSERT INTO emp_count(
				    job_name,count)
	            VALUES (job_data.name,0);	
           END LOOP;
	               
	        
	IF (condition ='provision') Then
	
	   FOR first_record IN
		select hj.name as job_name,count(hd.id) as count from hr_employee he,hr_job hj,hr_contract hc,hr_department hd
		where he.department_id=hd.id
		and hc.employee_id=he.id
		and hj.id=hc.job_id
		and hc.date_start >from_date
		and hd.id in (select id from hr_department where name=dept)
		group by hj.name			
		
		LOOP
				update emp_count set job_name=first_record.job_name,count=first_record.count where job_name=first_record.job_name ;				
	         
		END LOOP;
        END IF;
	IF (condition ='perminant') Then
	
	   FOR second_record IN
		select hj.name as job_name,count(he.id) as count from hr_employee he,hr_job hj,hr_contract hc,hr_department hd
		where he.department_id=hd.id
		and hc.employee_id=he.id
		and hj.id=hc.job_id
		and hc.date_start <=from_date
		and (hc.date_end >=from_date OR hc.date_end is null)
		and hd.id in (select id from hr_department where name=dept)
		group by hj.name

	   LOOP
	        update emp_count set job_name=second_record.job_name,count=second_record.count where job_name=second_record.job_name ;				

	   END LOOP;
        END IF;	
       
	IF (condition ='resignation') Then
	
	   FOR fourth_record  IN
		select hj.name as job_name,count(he.id) as count from hr_employee he,hr_job hj,hr_contract hc,hr_department hd
		where he.department_id=hd.id
		and hc.employee_id=he.id
		and hj.id=hc.job_id
		and hc.date_end is not null and hc.date_end<from_date
		and hd.id in (select id from hr_department where name=dept)
		group by hj.name	
		
		LOOP
				update emp_count set job_name=fourth_record .job_name,count=fourth_record .count where job_name=fourth_record .job_name ;				
	         
		END LOOP;
        END IF;
	IF (condition ='all_employee') Then
	
	FOR fifth_record  IN
		select A. job_name,A.count from(
		select hj.name as job_name,count(he.id) as count  from hr_employee he,hr_job hj,hr_contract hc,hr_department hd
		where he.department_id=hd.id
		and hc.employee_id=he.id
		and hj.id=hc.job_id	
		and (
		(hc.date_start <=from_date
		and (hc.date_end >=from_date  OR hc.date_end is null))
		OR (hc.date_start >from_date AND hc.date_end is null)
		)
		and hd.id in (select id from hr_department where name=dept)
		group by hj.name)A
		group by A.job_name,A.count
		order by job_name
		LOOP
				update emp_count set job_name=fifth_record .job_name,count=fifth_record .count where job_name=fifth_record .job_name ;				
	         
		END LOOP;
        END IF;
	
	
	RETURN QUERY select row_number() over (order by hj.sequence) as id,job_name,ec.count from emp_count ec,hr_job hj
	where hj.name=ec.job_name
	group by hj.name ,hj.id,ec.job_name,ec.count
	order by hj.sequence;		    
		
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION emp_count_with_job(date, character varying, character varying)
  OWNER TO openerp;
