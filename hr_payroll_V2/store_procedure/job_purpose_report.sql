-- Table: job_purpose

-- DROP TABLE job_purpose;

CREATE TABLE job_purpose
(
  id bigint,
  emp_name character varying,
  age numeric,
  salary numeric,
  contact character varying,
  apply_date date,
  experience character varying,
  education character varying,
  quality character varying,
  remark character varying,
  job_name character varying
)
WITH (
  OIDS=FALSE
);
ALTER TABLE job_purpose
  OWNER TO openerp;




-- Function: job_purpose_report(integer, character varying)

-- DROP FUNCTION job_purpose_report(integer, character varying);

CREATE OR REPLACE FUNCTION job_purpose_report(
    IN param_job_id integer,
    IN param_state character varying)
  RETURNS TABLE(ser_no bigint, id bigint, p_emp_name character varying, p_age numeric, p_salary numeric, p_contact character varying, p_apply_date date, p_experience character varying, p_education character varying, p_quality character varying, p_remark character varying, p_job_name character varying) AS
$BODY$
declare 

	inform_data RECORD ;
	app_data RECORD ;
	purpose_data RECORD;
	edu_symbol Char;
	ex_symbol Char;
        qual_symbol Char;

	
           
	begin  
		RAISE NOTICE 'Starting Store Procedure.......';	 
	--Deleting Temp Table

		DELETE FROM job_purpose;
            
                
        FOR app_data In
        

                select hp.id,hp.partner_name,EXTRACT(YEAR FROM age(current_date,hp.birthday)) as age,salary_expected as salary,hj.state,
                res.name||'#'||res.street||'#'||res.street2||'#'||res.city||'#'||res.email||'#-Phone:'||res.mobile as partner_mobile
                ,apply_date,job_id,hj.name as job_name from hr_applicant hp ,hr_job hj,res_partner res
                where hj.id=hp.job_id 
                and res.id=hp.partner_id    
		and hp.job_id=param_job_id


                          
        LOOP
                 Insert Into job_purpose(id,emp_name,age,salary,contact,apply_date,experience,education,quality,remark,job_name)
                 Values (app_data.id,app_data.partner_name,app_data.age,app_data.salary,app_data.partner_mobile,app_data.apply_date,Null,Null,Null,'',app_data.job_name);
        END LOOP;
        
	FOR inform_data In


	    select job_id,A.id as applicant_id,partner_name as applicant_name,date_part as age,salary_expected as salary,apply_date,exper,edu,qual,name as remark from 
		(select * from (
		  SELECT t1.*, t2.exper,'' as edu ,'' as qual
		  FROM (select hp.id,hp.partner_name,EXTRACT(YEAR FROM age(current_date,hp.birthday)),salary_expected,apply_date,source_id,job_id from hr_applicant hp)AS t1
		  LEFT JOIN (select employee_id,he.name as exper from hr_experience_applicant he) AS t2
		  ON t1.id=t2.employee_id
		Union all
		  SELECT t1.*, '' as exper,t2.exper as edu ,'' as qual
		  FROM (select hp.id,hp.partner_name,EXTRACT(YEAR FROM age(current_date,hp.birthday)),salary_expected,apply_date,source_id,job_id from hr_applicant hp)AS t1
		  LEFT JOIN (select employee_id,he.name as exper from hr_academic_applicant he) AS t2
		  ON t1.id=t2.employee_id
		Union all
		  SELECT t1.*, '' as exper,'' as edu ,t2.exper as qual
		  FROM (select hp.id,hp.partner_name,EXTRACT(YEAR FROM age(current_date,hp.birthday)),salary_expected,apply_date,source_id,job_id from hr_applicant hp)AS t1
		  LEFT JOIN (select employee_id,he.name as exper from hr_certification_applicant he) AS t2
		  ON t1.id=t2.employee_id
		  )A
		 order by A.partner_name) As A
	         LEFT JOIN (select hs.id as source_id,name from hr_recruitment_source hs) As B
                 ON A.source_id =B.source_id
                 where job_id =param_job_id
             LOOP
                  RAISE NOTICE 'applicant_name.......%',inform_data.applicant_name;	 

                  FOR purpose_data IN                  
                      select jp.id,emp_name,experience,education,quality,remark from job_purpose jp where jp.emp_name=inform_data.applicant_name
                  LOOP                    
                      ex_symbol='#';
                      edu_symbol='#';
                      qual_symbol='#';
                      IF purpose_data.experience is  Null Then
                         ex_symbol = '';
                         purpose_data.experience='';
                      END IF;
                      IF purpose_data.education is  Null Then
                         edu_symbol = '';
                         purpose_data.education='';
                      END IF;
                      IF purpose_data.quality is  Null Then
                         qual_symbol = '';
                         purpose_data.quality='';
                      END IF;                                                
                      IF length(inform_data.exper)>1 Then
                      
                          Update job_purpose jp SET  experience =inform_data.exper||ex_symbol||purpose_data.experience,remark=inform_data.remark
                          Where jp.id=inform_data.applicant_id And jp.emp_name=inform_data.applicant_name;
                      End If;
                      IF length(inform_data.edu)>1 Then

                          Update job_purpose jp SET  education =inform_data.edu||edu_symbol||purpose_data.education,remark=inform_data.remark
                          Where jp.id=inform_data.applicant_id And jp.emp_name=inform_data.applicant_name;
                      End If;
                      IF length(inform_data.qual)>1 Then

                          Update job_purpose jp SET  quality =inform_data.qual||qual_symbol||purpose_data.quality,remark=inform_data.remark
                          Where jp.id=inform_data.applicant_id And jp.emp_name=inform_data.applicant_name;
                      End If;                                            
                  END LOOP;

                             
             END LOOP;
             IF (param_state='all') Then
                 
                 RETURN QUERY select row_number() over (order by hj.id) as ser_no,hj.* from job_purpose hj;
             elseif param_state = 'recruit' then
                 RETURN QUERY select row_number() over (order by hj.id) as ser_no,hj.* from job_purpose hj,hr_job hb
                 where hb.name=hj.job_name
                 and hb.state='recruit';
             END IF;


 END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION job_purpose_report(integer, character varying)
  OWNER TO openerp;
