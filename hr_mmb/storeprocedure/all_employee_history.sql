CREATE OR REPLACE FUNCTION all_employee_history(IN from_date date, IN condition character varying)
  RETURNS TABLE(id bigint, p_job_name character varying, p_count_1 integer, p_count_2 integer, p_count_sum integer) AS
$BODY$
declare 
        job_data RECORD;
	recordone RECORD ;
	recordtwo RECORD;
	recordthree RECORD;


	begin  
		RAISE NOTICE 'Starting Store Procedure.......';	 
	--Deleting Temp Table
                --select * from emp_history
		DELETE FROM emp_history;

	   FOR job_data IN
	            select name from hr_job
	   LOOP
		    INSERT INTO emp_history(
				    job_name,count1,count2,countsum)
			  VALUES (job_data.name,0,0,0);	
           END LOOP;
	               
	        
	IF (condition ='provision') Then
	
	   FOR recordone IN
		select  job_name,male,female from(
		select hj.name as job_name,count(he.id) as male ,0 as female  from hr_employee he,hr_job hj,hr_contract hc
		where hc.id=he.contract_id
		and hc.job_id=hj.id
		and he.gender ='male'
		and hc.date_start > from_date
		and hc.date_end is null
		group by hj.name
		union all
		select hj.name as job_name,0 as male ,count(he.id) as female  from hr_employee he,hr_job hj,hr_contract hc
		where hc.id=he.contract_id
		and hc.job_id=hj.id
		and he.gender ='female'
		and hc.date_start > from_date
		and hc.date_end is null
		group by hj.name)A
		group by job_name,male,female
	   LOOP
	       if (recordone.male =0) Then 
	          update emp_history set count2=recordone.female where job_name=recordone.job_name;
	       elseif(recordone.female =0) Then
	          update emp_history set count1=recordone.male where job_name=recordone.job_name;
	       end if;	   
	       END LOOP;
        END IF;

	IF (condition ='perminant') Then
	
	   FOR recordtwo IN
		select  job_name,male,female from(
		select hj.name as job_name,count(he.id) as male ,0 as female  from hr_employee he,hr_job hj,hr_contract hc
		where hc.id=he.contract_id
		and hc.job_id=hj.id
		and he.gender ='male'
		and hc.date_start <= from_date
		and (hc.date_end >= from_date OR hc.date_end is null)
		group by hj.name
		union all
		select hj.name as job_name,0 as male ,count(he.id) as female  from hr_employee he,hr_job hj,hr_contract hc
		where hc.id=he.contract_id
		and hc.job_id=hj.id
		and he.gender ='female'
		and hc.date_start <=from_date
		and (hc.date_end >= from_date OR hc.date_end is null)
		group by hj.name)A
		group by job_name,male,female
	   LOOP
	       if (recordtwo.male =0) Then 
	          update emp_history set count2=recordtwo.female where job_name=recordtwo.job_name;
	       elseif(recordtwo.female =0) Then
	          update emp_history set count1=recordtwo.male where job_name=recordtwo.job_name;
	       end if;	   
	       END LOOP;
        END IF;
	IF (condition ='all_employee') Then
	
	   FOR recordthree IN
		select  job_name,male,female from(
		select hj.name as job_name,count(he.id) as male ,0 as female  from hr_employee he,hr_job hj,hr_contract hc
		where hc.id=he.contract_id
		and hc.job_id=hj.id
		and he.gender ='male'
		and (
		(hc.date_start <= from_date
		and (hc.date_end >= from_date OR hc.date_end is null))
		OR (hc.date_start > from_date AND hc.date_end is null)
		)
		group by hj.name
		union all
		select hj.name as job_name,0 as male ,count(he.id) as female  from hr_employee he,hr_job hj,hr_contract hc
		where hc.id=he.contract_id
		and hc.job_id=hj.id
		and he.gender ='female'
		and (
		(hc.date_start <= from_date
		and (hc.date_end >= from_date OR hc.date_end is null))
		OR (hc.date_start > from_date AND hc.date_end is null)
		)
		group by hj.name)A
		group by job_name,male,female
		order by job_name
	   LOOP
	       if (recordthree.male =0) Then 
	          update emp_history set count2=recordthree.female where job_name=recordthree.job_name;
	       elseif(recordthree.female =0) Then
	          update emp_history set count1=recordthree.male where job_name=recordthree.job_name;
	       end if;
	       
	   END LOOP;
        END IF;


	
	RETURN QUERY select row_number() over (order by hj.sequence) as id,job_name,count1,count2,count1+count2 from emp_history eh,hr_job hj 
	             where hj.name=eh.job_name
	             order by hj.sequence;
		    
		
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION all_employee_history(date, character varying)
  OWNER TO openerp;
