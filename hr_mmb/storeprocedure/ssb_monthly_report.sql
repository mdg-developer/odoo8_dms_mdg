-- Function: ssb_monthly_report(date, date, character varying, character varying)

-- DROP FUNCTION ssb_monthly_report(date, date, character varying, character varying);

CREATE OR REPLACE FUNCTION ssb_monthly_report(IN from_date date, IN to_date date, IN condition character varying, IN branch character varying)
  RETURNS TABLE(id bigint, p_emp_name character varying, job_id1 integer, p_ssn_no character varying, p_dept_name character varying, p_dept_id integer, p_ssb_empr1 numeric, p_ssb_empr2 numeric, p_ssb_empr3 numeric, p_ssb_empr4 numeric, p_ssb_empr5 numeric, p_ssb_empr6 numeric, p_ssb_empr7 numeric, p_ssb_empr8 numeric, p_ssb_empr9 numeric, p_ssb_empr10 numeric, p_ssb_empr11 numeric, p_ssb_empr12 numeric, p_ssb_emp1 numeric, p_ssb_emp2 numeric, p_ssb_emp3 numeric, p_ssb_emp4 numeric, p_ssb_emp5 numeric, p_ssb_emp6 numeric, p_ssb_emp7 numeric, p_ssb_emp8 numeric, p_ssb_emp9 numeric, p_ssb_emp10 numeric, p_ssb_emp11 numeric, p_ssb_emp12 numeric, total1 numeric, total2 numeric, total3 numeric, total4 numeric, total5 numeric, total6 numeric, total7 numeric, total8 numeric, total9 numeric, total10 numeric, total11 numeric, total12 numeric) AS
$BODY$
declare 
	inform_data RECORD ;


	begin  
		RAISE NOTICE 'Starting Store Procedure.......';	 
	--Deleting Temp Table

	DELETE FROM ssb_monthly_temp;
	FOR inform_data
		IN		
		select emp_name,job_id,ssn_no,dept_name,dept_id,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%01-%') THEN ssb_empr END) as ssb_empr1,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%02-%') THEN ssb_empr END) as ssb_empr2,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%03-%') THEN ssb_empr END) as ssb_empr3,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%04-%') THEN ssb_empr END) as ssb_empr4,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%05-%') THEN ssb_empr END) as ssb_empr5,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%06-%') THEN ssb_empr END) as ssb_empr6,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%07-%') THEN ssb_empr END) as ssb_empr7,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%08-%') THEN ssb_empr END) as ssb_empr8,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%09-%') THEN ssb_empr END) as ssb_empr9,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%10-%') THEN ssb_empr END) as ssb_empr10,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%11-%') THEN ssb_empr END) as ssb_empr11,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%12-%') THEN ssb_empr END) as ssb_empr12,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%01-%') THEN ssb_emp END) as ssb_emp1,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%02-%') THEN ssb_emp END) as ssb_emp2,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%03-%') THEN ssb_emp END) as ssb_emp3,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%04-%') THEN ssb_emp END) as ssb_emp4,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%05-%') THEN ssb_emp END) as ssb_emp5,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%06-%') THEN ssb_emp END) as ssb_emp6,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%07-%') THEN ssb_emp END) as ssb_emp7,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%08-%') THEN ssb_emp END) as ssb_emp8,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%09-%') THEN ssb_emp END) as ssb_emp9,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%10-%') THEN ssb_emp END) as ssb_emp10,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%11-%') THEN ssb_emp END) as ssb_emp11,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%12-%') THEN ssb_emp END) as ssb_emp12,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%01-%') THEN ssb_empr+ssb_emp END) as total1,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%02-%') THEN ssb_empr+ssb_emp END) as total2,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%03-%') THEN ssb_empr+ssb_emp END) as total3,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%04-%') THEN ssb_empr+ssb_emp END) as total4,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%05-%') THEN ssb_empr+ssb_emp END) as total5,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%06-%') THEN ssb_empr+ssb_emp END) as total6,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%07-%') THEN ssb_empr+ssb_emp END) as total7,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%08-%') THEN ssb_empr+ssb_emp END) as total8,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%09-%') THEN ssb_empr+ssb_emp END) as total9,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%10-%') THEN ssb_empr+ssb_emp END) as total10,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%11-%') THEN ssb_empr+ssb_emp END) as total11,
SUM(CASE WHEN to_char(date, 'MM-dd') Like('%12-%') THEN ssb_empr+ssb_emp END) as total12
from
(select emp_name,job_id,date,ssn_no,dept_name , dept_id,  
            round(sum(coalesce(child.ssb_empr, 0))) as ssb_empr,round(sum(coalesce(child.ssb_emp, 0))) as ssb_emp
            from
            (
                select payslip.*,
                case
                    when lower(payslip_line.code) = lower('SSBER')
                    then payslip_line.total
                end as ssb_empr,
                case
                    when lower(payslip_line.code) = lower('SSBE')
                    then payslip_line.total
                end as ssb_emp      

                FROM
                (	
                    select HE.name_related as emp_name,HJ.id as job_id,HP.date_to as date,hp.id as payslip_id,HE.ssn_no,hd.name as dept_name, hd.id as dept_id,extract(month from HP.date_to) as month
                    from hr_contract HC ,hr_payslip HP,hr_job HJ,hr_employee HE,hr_department hd                                     
                    where HC.job_id=HJ.id
                    and HC.id=HP.contract_id
                    and HE.id=HP.employee_id
                    and HC.employee_id=HE.id
                    and hd.id= HE.department_id
                    and HP.date_to < to_date
                    and HP.date_from > from_date

                )payslip,
                (
                    select round(total,2) as total, slip_id, code
                    from hr_payslip_line 
                )payslip_line
                where payslip.payslip_id = payslip_line.slip_id
            )child
            group by emp_name, job_id,id,date,ssn_no,dept_name,dept_id)last
group by emp_name,job_id,ssn_no,dept_name,dept_id
					
		LOOP
		
            INSERT INTO ssb_monthly_temp(p_emp_name,p_job_id,p_ssn_no,p_dept_name,p_dept_id,p_ssb_empr1, p_ssb_empr2,p_ssb_empr3,p_ssb_empr4,p_ssb_empr5,p_ssb_empr6,p_ssb_empr7,
			p_ssb_empr8,p_ssb_empr9,p_ssb_empr10 , p_ssb_empr11 , p_ssb_empr12 , p_ssb_emp1 , p_ssb_emp2 , p_ssb_emp3 , p_ssb_emp4 , p_ssb_emp5 ,
			p_ssb_emp6 , p_ssb_emp7 , p_ssb_emp8 , p_ssb_emp9 , p_ssb_emp10 , p_ssb_emp11 , p_ssb_emp12 ,total1 ,total2 ,total3 ,total4 ,total5 ,
			total6 ,total7 ,total8 ,total9 ,total10 ,total11 ,total12 )
		    VALUES (inform_data.emp_name,inform_data.job_id,inform_data.ssn_no,inform_data.dept_name,inform_data.dept_id,inform_data.ssb_empr1, inform_data.ssb_empr2,inform_data.ssb_empr3,inform_data.ssb_empr4,inform_data.ssb_empr5,inform_data.ssb_empr6,inform_data.ssb_empr7,
			inform_data.ssb_empr8,inform_data.ssb_empr9,inform_data.ssb_empr10 , inform_data.ssb_empr11 , inform_data.ssb_empr12 , inform_data.ssb_emp1 , inform_data.ssb_emp2 , inform_data.ssb_emp3 , inform_data.ssb_emp4 , inform_data.ssb_emp5 ,
			inform_data.ssb_emp6 , inform_data.ssb_emp7 , inform_data.ssb_emp8 , inform_data.ssb_emp9 , inform_data.ssb_emp10 , inform_data.ssb_emp11 , inform_data.ssb_emp12 ,inform_data.total1 ,inform_data.total2 ,inform_data.total3 ,inform_data.total4 ,inform_data.total5 ,
			inform_data.total6 ,inform_data.total7 ,inform_data.total8 ,inform_data.total9 ,inform_data.total10 ,inform_data.total11 ,inform_data.total12);
		   

        END LOOP;
       -- RETURN QUERY select * from ssb_monthly_temp;

        IF condition = 'ALL' Then
		RETURN QUERY select row_number() over (order by hj.sequence) as id,ssb.* from ssb_monthly_temp ssb,hr_job hj where hj.id=ssb.p_job_id order by hj.sequence;
	ELSIF condition = 'HO' Then
		RETURN QUERY select row_number() over (order by hj.sequence) as id,smt.* from ssb_monthly_temp smt,hr_job hj where hj.id=smt.p_job_id and smt.p_dept_name not like '%Branch' order by hj.sequence;
	ELSE 
		RETURN QUERY select row_number() over (order by hj.sequence) as id,smt.* from ssb_monthly_temp smt,hr_job hj where hj.id=smt.p_job_id and smt.p_dept_name = branch order by hj.sequence;
	END IF;
	
 END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION ssb_monthly_report(date, date, character varying, character varying)
  OWNER TO odoo;
