CREATE OR REPLACE FUNCTION all_dep_history(IN from_date date, IN condition character varying)
  RETURNS TABLE(p_id bigint, p_job_name character varying, p_dep_count_1 integer, p_dep_count_2 integer, p_dep_count_3 integer, p_dep_count_sum integer) AS
$BODY$
declare 
        job_data RECORD;
	first_record RECORD ;
	second_record RECORD;
	third_record RECORD;
	fourth_record RECORD;


	begin  
		RAISE NOTICE 'Starting Store Procedure.......';	 
	--Deleting Temp Table
                --select * from dep_history
		DELETE FROM dep_history;

	   FOR job_data IN
	            select name from hr_job
	   LOOP
		    INSERT INTO dep_history(
				    job_name,dep_count1,dep_count2,dep_count3,dep_countsum)
	            VALUES (job_data.name,0,0,0,0);	
           END LOOP;
	               
	        
	IF (condition ='provision') Then
	
	   FOR first_record IN
		select hj.name as job_name,0 as office,count(he.id) as branch,0 as onjob from hr_employee he,hr_job hj,hr_contract hc,hr_department hd
		where he.contract_id=hc.id
		and hc.employee_id=he.id
		and hc.job_id=hj.id
		and he.department_id=hd.id
		and he.department_id=hd.id
		and hc.date_start > from_date
		and hd.id in (select id from hr_department where name like '%Branch')
		group by hj.name
		union all 
		select hj.name as job_name,0 as office,0 as branch,count(he.id) as onjob from hr_employee he,hr_job hj,hr_contract hc,hr_department hd
		where he.contract_id=hc.id
		and hc.employee_id=he.id
		and hc.job_id=hj.id
		and he.department_id=hd.id
		and he.department_id=hd.id
		and hc.date_start > from_date
		and hd.id in (select id from hr_department where name like '%(On Job)')
		group by hj.name
		union all 
		select hj.name as job_name,count(he.id) as office,0 as branch,0 as onjob from hr_employee he,hr_job hj,hr_contract hc,hr_department hd
		where he.contract_id=hc.id
		and hc.employee_id=he.id
		and hc.job_id=hj.id
		and he.department_id=hd.id
		and he.department_id=hd.id
		and hc.date_start > from_date
		and hd.id not in (select id from hr_department where name like '%(On Job)')
		and hd.id not in (select id from hr_department where name like '%Branch')
		group by hj.name
	   LOOP
	       if (first_record.office >0 and first_record.branch=0 and first_record.onjob=0) Then 
	          update dep_history set dep_count1=first_record.office where job_name=first_record.job_name;
	       elseif(first_record.office =0 and first_record.branch>0 and first_record.onjob=0) Then
	          update dep_history set dep_count2=first_record.branch where job_name=first_record.job_name;
	       elseif(first_record.office =0 and first_record.branch=0 and first_record.onjob>0) Then
	          update dep_history set dep_count3=first_record.onjob where job_name=first_record.job_name;	          
	       end if;	   
	    END LOOP;
        END IF;
	IF (condition ='perminant') Then
	
	   FOR second_record IN
		select hj.name as job_name,0 as office,count(he.id) as branch,0 as onjob from hr_employee he,hr_job hj,hr_contract hc,hr_department hd
		where he.contract_id=hc.id
		and hc.employee_id=he.id
		and hc.job_id=hj.id
		and he.department_id=hd.id
		and he.department_id=hd.id
		and hc.date_start <=from_date
		and (hc.date_end >= from_date OR hc.date_end is null)
		and hd.id in (select id from hr_department where name like '%Branch')
		group by hj.name
		union all 
		select hj.name as job_name,0 as office,0 as branch,count(he.id) as onjob from hr_employee he,hr_job hj,hr_contract hc,hr_department hd
		where he.contract_id=hc.id
		and hc.employee_id=he.id
		and hc.job_id=hj.id
		and he.department_id=hd.id
		and he.department_id=hd.id
		and hc.date_start <=from_date
		and (hc.date_end >= from_date OR hc.date_end is null)
		and hd.id in (select id from hr_department where name like '%(On Job)')
		group by hj.name
		union all 
		select hj.name as job_name,count(he.id) as office,0 as branch,0 as onjob from hr_employee he,hr_job hj,hr_contract hc,hr_department hd
		where he.contract_id=hc.id
		and hc.employee_id=he.id
		and hc.job_id=hj.id
		and he.department_id=hd.id
		and he.department_id=hd.id
		and hc.date_start <=from_date
		and (hc.date_end >= from_date OR hc.date_end is null)
		and hd.id not in (select id from hr_department where name like '%(On Job)')
		and hd.id not in (select id from hr_department where name like '%Branch')
		group by hj.name
	   LOOP
	       if (second_record.office >0 and second_record.branch=0 and second_record.onjob=0) Then 
	          update dep_history set dep_count1=second_record.office where job_name=second_record.job_name;
	       elseif(second_record.office =0 and second_record.branch>0 and second_record.onjob=0) Then
	          update dep_history set dep_count2=second_record.branch where job_name=second_record.job_name;
	       elseif(second_record.office =0 and second_record.branch=0 and second_record.onjob>0) Then
	          update dep_history set dep_count3=second_record.onjob where job_name=second_record.job_name;	          
	       end if;	   
	   END LOOP;
        END IF;
	
	IF (condition ='branch_on_job') Then
	
	   FOR third_record IN
		select hj.name as job_name,0 as office,count(he.id) as branch,0 as onjob from hr_employee he,hr_job hj,hr_contract hc,hr_department hd
		where he.contract_id=hc.id
		and hc.employee_id=he.id
		and hc.job_id=hj.id
		and he.department_id=hd.id
		and he.department_id=hd.id
		and hd.id in (select id from hr_department where name like '%Branch')
		group by hj.name
		union all 
		select hj.name as job_name,0 as office,0 as branch,count(he.id) as onjob from hr_employee he,hr_job hj,hr_contract hc,hr_department hd
		where he.contract_id=hc.id
		and hc.employee_id=he.id
		and hc.job_id=hj.id
		and he.department_id=hd.id
		and he.department_id=hd.id
		and hd.id in (select id from hr_department where name like '%(On Job)')
		group by hj.name

	   LOOP
	       if (third_record.office >0 and third_record.branch=0 and third_record.onjob=0) Then 
	          update dep_history set dep_count1=third_record.office where job_name=third_record.job_name;
	       elseif(third_record.office =0 and third_record.branch>0 and third_record.onjob=0) Then
	          update dep_history set dep_count2=third_record.branch where job_name=third_record.job_name;
	       elseif(third_record.office =0 and third_record.branch=0 and third_record.onjob>0) Then
	          update dep_history set dep_count3=third_record.onjob where job_name=third_record.job_name;	          
	       end if;	   
	    END LOOP;
        END IF;
	IF (condition ='on_job') Then
	
	   FOR fourth_record IN

		select hj.name as job_name,0 as office,0 as branch,count(he.id) as onjob from hr_employee he,hr_job hj,hr_contract hc,hr_department hd
		where he.contract_id=hc.id
		and hc.employee_id=he.id
		and hc.job_id=hj.id
		and he.department_id=hd.id
		and he.department_id=hd.id
		and hd.id in (select id from hr_department where name like '%(On Job)')
		group by hj.name

	   LOOP
	       if (fourth_record.office >0 and fourth_record.branch=0 and fourth_record.onjob=0) Then 
	          update dep_history set dep_count1=fourth_record.office where job_name=fourth_record.job_name;
	       elseif(fourth_record.office =0 and fourth_record.branch>0 and fourth_record.onjob=0) Then
	          update dep_history set dep_count2=fourth_record.branch where job_name=fourth_record.job_name;
	       elseif(fourth_record.office =0 and fourth_record.branch=0 and fourth_record.onjob>0) Then
	          update dep_history set dep_count3=fourth_record.onjob where job_name=fourth_record.job_name;	          
	       end if;	   
	    END LOOP;
        END IF;
	
	RETURN QUERY select row_number() over (order by hj.sequence) as id,job_name,dep_count1,dep_count2,dep_count3,dep_count1+dep_count2+dep_count3 from dep_history dh,hr_job hj
	where hj.name =dh.job_name order by hj.sequence;
		    
		
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION all_dep_history(date, character varying)
  OWNER TO openerp;
