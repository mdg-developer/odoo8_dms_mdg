-- Function: emp_per_pro_sum(date, character varying, character varying)

-- DROP FUNCTION emp_per_pro_sum(date, character varying, character varying);

CREATE OR REPLACE FUNCTION emp_per_pro_sum(IN from_date date, IN dept character varying, IN condition character varying)
  RETURNS TABLE(p_id bigint, p_job_name character varying, per integer, pro integer, sum integer) AS
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
                --select * from emp_per_pro
		DELETE FROM emp_per_pro;

	   FOR job_data IN
	            select name from hr_job
	   LOOP
		    INSERT INTO emp_per_pro(
				    job_name,per,pro,sum)
	            VALUES (job_data.name,0,0,0);	
           END LOOP;         

	IF (condition ='resignation') Then
	
	   FOR fourth_record  IN
		select B.job_name,B.per,B.pro,(B.per+B.pro) as sum from (
		select A.job_name,sum(A.per) as  per ,sum(A.pro) as pro,j_id from (
		select hj.sequence as j_id,hj.name as job_name, 0 as per, count(hc.employee_id) as pro from hr_employee he,hr_contract hc,hr_job hj,hr_department hd
		where he.department_id=hd.id
		and hc.employee_id=he.id
		and hj.id=hc.job_id
		and hc.date_end is not null and hc.date_end<from_date
		and hd.id in (select id from hr_department where name=dept)
		group by job_name,he.id,hc.job_id,hj.id

		Union All
		select hj.sequence as j_id,hj.name as job_name, count(hc.employee_id) as per,0 as pro from hr_employee he,hr_contract hc,hr_job hj,hr_department hd
		where he.department_id=hd.id
		and hc.employee_id=he.id
		and hj.id=hc.job_id
		and hc.date_end is not null and hc.date_end<from_date
		and hc.trial_date_end >= current_date
		and hd.id in (select id from hr_department where name=dept)
		group by job_name,he.id,hc.job_id,hj.id)A	
		group by job_name,j_id
		order by j_id)B
		order by j_id

		LOOP
				update emp_per_pro set job_name=fourth_record .job_name,per=fourth_record .per,pro=fourth_record.pro,sum=fourth_record.sum where job_name=fourth_record .job_name ;				
	         
		END LOOP;
        END IF;
	IF (condition ='all_employee') Then
	
	   FOR fifth_record  IN
		select B.job_name,B.per,B.pro,(B.per+B.pro) as sum from (
		select A.job_name,sum(A.per) as  per ,sum(A.pro) as pro,j_id from (
		select hj.sequence as j_id,hj.name as job_name, 0 as per, count(hc.employee_id) as pro from hr_employee he,hr_contract hc,hr_job hj,hr_department hd
		where he.department_id=hd.id
		and hc.employee_id=he.id
		and hj.id=hc.job_id
		and hc.date_start >from_date
		and hd.id in (select id from hr_department where name=dept)
		group by job_name,he.id,hc.job_id,hj.id

		Union All
		select hj.sequence as j_id,hj.name as job_name, count(hc.employee_id) as per,0 as pro from hr_employee he,hr_contract hc,hr_job hj,hr_department hd
		where he.department_id=hd.id
		and hc.employee_id=he.id
		and hj.id=hc.job_id
		and hc.date_start <=from_date
		and (hc.date_end >= from_date OR hc.date_end is null)
		and hd.id in (select id from hr_department where name=dept)
		group by job_name,he.id,hc.job_id,hj.id)A	
		group by A.job_name,j_id
		order by j_id)B
		order by j_id

		LOOP
				update emp_per_pro set job_name=fifth_record .job_name,per=fifth_record .per,pro=fifth_record.pro,sum=fifth_record.sum where job_name=fifth_record .job_name ;				
	         
		END LOOP;
        END IF;	
	
	RETURN QUERY select row_number() over (order by hj.sequence) as id,job_name,epp.per,epp.pro,epp.sum from emp_per_pro epp,hr_job hj
	where hj.name=epp.job_name
	group by hj.name ,hj.id,epp.job_name,epp.per,epp.pro,epp.sum
	order by hj.sequence;		    
		
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION emp_per_pro_sum(date, character varying, character varying)
  OWNER TO openerp;
