-- Function: salary_calculation(date, date)

-- DROP FUNCTION salary_calculation(date, date);

CREATE OR REPLACE FUNCTION salary_calculation(IN date_from_param date, IN date_to_param date)
  RETURNS TABLE(emp_cla integer, job character varying, job_id integer, total_emp integer, basic_salary numeric, allowance numeric, contribution numeric, cla numeric, total numeric, ssb numeric, total_value numeric, income_tax numeric) AS
$BODY$
DECLARE 
	emp_data_set RECORD;
	data_set RECORD;
	val_cla numeric;
	cla numeric;
	cla_1 numeric;
	
	BEGIN  
	val_cla=0;
	DELETE FROM employee_temp_table;
	DELETE from employee_temp;
	RAISE NOTICE 'Starting Store Procedure.......';	

	--inserting the each employee information into employee_temp_table
	for emp_data_set in 
	select hj.id as job_id , hp.id as hp_id, hp.employee_id as emp_id,he.name_related as emp_name,hj.name as job_name from hr_employee he,hr_job hj,hr_payslip hp where hp.employee_id=he.id and he.job_id=hj.id and hp.date_from=date_from_param and hp.date_to=date_to_param group by hj.name,hp.employee_id,he.name_related,hp.id ,hj.id
	loop
		insert into employee_temp_table(emp_cla,job_id,hp_id,job,emp_id,emp_name ,basic_salary ,allowance,contribution ,cla,total,ssb ,total_value,income_tax ,causlv,annuallv,unplv1,unplv2,medlv1,medlv2,medlv3,matlv,abslv1,abslv2,workld1,workld2,workld3,workld4,workld5)
		values(0,emp_data_set.job_id,emp_data_set.hp_id,emp_data_set.job_name,emp_data_set.emp_id,emp_data_set.emp_name ,0,0,0 ,0,0,0 ,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);
	end loop;
	--updating the basic salary
	for data_set in
	select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,employee_temp_table ett where hpl.slip_id=ett.hp_id and code='BASIC'
	loop
	update employee_temp_table ett
	set basic_salary=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;
	--updating the allowance
	for data_set in
	select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,employee_temp_table ett where hpl.slip_id=ett.hp_id and code='ALL'
	loop
	update employee_temp_table ett
	set allowance=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;
	--updating the contribution
	for data_set in
	select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,employee_temp_table ett where hpl.slip_id=ett.hp_id and code='CON'
	loop
	update employee_temp_table ett
	set contribution=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;
	--updating the SSB
	for data_set in
	select ett.hp_id as hp_id,hpl.code as code,hpl.total as total from hr_payslip_line hpl,employee_temp_table ett where hpl.slip_id=ett.hp_id and code='SSBE'

	--select A.hp_id,(A.total+B.total) as total from (select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,employee_temp_table ett where hpl.slip_id=ett.hp_id and code='SSBE')A join (select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,employee_temp_table ett where hpl.slip_id=ett.hp_id and code='SSBER')B on A.hp_id=B.hp_id group by A.hp_id,A.total,B.total
	loop
	update employee_temp_table ett
	set ssb=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;
	--updating the cla
	for data_set in
	select hpi.amount,ett.hp_id from hr_payslip_input hpi,employee_temp_table ett where hpi.payslip_id=ett.hp_id and hpi.code='CLA'
	loop
	update employee_temp_table ett
	set cla=data_set.amount
	where ett.hp_id = data_set.hp_id;

	end loop;

-----Changes------
	--updating the cla by Job Title
	update employee_temp_table ett set emp_cla = 26 where lower(ett.job) like 'security%' or upper(ett.job) like 'Security%';
	--updating the cla by Job Title
	update employee_temp_table ett set emp_cla = 22 where lower(ett.job) not like 'security%' ;
-----Changes------
	
	--updating the income_tax
	for data_set in
	select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,employee_temp_table ett where hpl.slip_id=ett.hp_id and code='ICT'
	loop
	update employee_temp_table ett
	set income_tax=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;




	--updating the causlv to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,employee_temp_table ett where hpw.payslip_id=ett.hp_id and LOWER(code)='causlv'
 	loop
 	update employee_temp_table ett
	set causlv=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the annuallv to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,employee_temp_table ett where hpw.payslip_id=ett.hp_id and LOWER(code)='annuallv'
 	loop
 	update employee_temp_table ett
	set annuallv=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the unplv1 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,employee_temp_table ett where hpw.payslip_id=ett.hp_id and LOWER(code)='unplv1'
 	loop
 	update employee_temp_table ett
	set unplv1=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the unplv2 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,employee_temp_table ett where hpw.payslip_id=ett.hp_id and LOWER(code)='unplv2'
 	loop
 	update employee_temp_table ett
	set unplv2=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the medlv1 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,employee_temp_table ett where hpw.payslip_id=ett.hp_id and LOWER(code)='medlv1'
 	loop
 	update employee_temp_table ett
	set medlv1=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the medlv2 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,employee_temp_table ett where hpw.payslip_id=ett.hp_id and LOWER(code)='medlv2'
 	loop
 	update employee_temp_table ett
	set medlv2=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the medlv3 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,employee_temp_table ett where hpw.payslip_id=ett.hp_id and LOWER(code)='medlv3'
 	loop
 	update employee_temp_table ett
	set medlv3=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the matlv to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,employee_temp_table ett where hpw.payslip_id=ett.hp_id and LOWER(code)='matlv'
 	loop
 	update employee_temp_table ett
	set matlv=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the abslv1 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,employee_temp_table ett where hpw.payslip_id=ett.hp_id and LOWER(code)='abslv1'
 	loop
 	update employee_temp_table ett
	set abslv1=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the abslv2 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,employee_temp_table ett where hpw.payslip_id=ett.hp_id and LOWER(code)='abslv2'
 	loop
 	update employee_temp_table ett
	set abslv2=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the workld1 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,employee_temp_table ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld1'
 	loop
 	update employee_temp_table ett
	set workld1=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the workld2 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,employee_temp_table ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld2'
 	loop
 	update employee_temp_table ett
	set workld2=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
		
	--updating the workld3 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,employee_temp_table ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld3'
 	loop
 	update employee_temp_table ett
	set workld3=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
		
	--updating the workld4 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,employee_temp_table ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld4'
 	loop
 	update employee_temp_table ett
	set workld4=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the workld5 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,employee_temp_table ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld5'
 	loop
 	update employee_temp_table ett
	set workld5=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	---updating the two type of cla into variable cla and cla_1
	--for security job type
	select ett.emp_cla into cla_1 from employee_temp_table ett where lower(ett.job) like 'security%' or upper(ett.job) like 'Security%';
	--for normal job type
	select ett.emp_cla into cla from employee_temp_table ett where lower(ett.job) not like 'security%';

	--calculating all condition for each employee
	---for Normal CLA
	for data_set in 
	select * from employee_temp_table ett where lower(ett.job) not like 'security%' 
	loop

	if count(data_set.causlv)>=0 then
	cla=cla-data_set.causlv;
	end if;
	
	if count(data_set.annuallv)>=0 then
	cla=cla-data_set.annuallv;
	end if;
	
	if count(data_set.unplv1)>=0 then
	cla=cla-data_set.unplv1;
	end if;
	
	if count(data_set.unplv2)>=0 then
	cla=cla-data_set.unplv2;
	
	end if;
	
	if count(data_set.medlv1)>=0 then
	cla=cla-data_set.medlv1;
	end if;
	
	if count(data_set.medlv2)>=0 then
	cla=cla-data_set.medlv2;
	end if;
	
	if count(data_set.medlv3)>=0 then
	cla=cla-data_set.medlv3;
	end if;
	
	if count(data_set.matlv)>=0 then
	cla=cla-data_set.matlv;
	end if;
	Raise  notice 'abslv1 %',data_set.abslv1;
	if count(data_set.abslv1)>=0 then
		if data_set.abslv1 >=3 then
			cla= cla-10;
		end if;
		if data_set.abslv1 <3 then
			cla= cla-data_set.abslv1;
		end if;
	end if;
	Raise  notice 'abslv1 %',data_set.abslv1;
	Raise  notice 'abslv2 %',data_set.abslv2::integer;
	
	if count(data_set.abslv2)>=0 then
		if data_set.abslv2 = 3 then
			cla= cla-10;
		end if;
		if data_set.abslv2 <3 then
			cla=cla-data_set.abslv2;
		end if;
	end if;
	Raise  notice 'abslv2 %',data_set.abslv2;
	Raise  notice 'workld1%',data_set.workld1;	
	if count(data_set.workld1)>=0 then
		-- if data_set.workld1 <= 2 then
-- 			cla= cla-(0.5*data_set.workld1);
-- 		end if;
		if data_set.workld1 = 3 then
			cla=cla-2;
		end if;
	
		if data_set.workld1 = 4 then
			cla= cla-2;
		end if;

		
	
		if data_set.workld1 >= 5 and data_set.workld1 <= 7 then
			cla=cla-4;
		end if;
	
		if data_set.workld1 >= 8 and data_set.workld1 <= 14 then
			cla= cla-5;
		end if;
	
		if data_set.workld1 >= 15 then
			cla=0;
		end if;
	end if;


		if count(data_set.workld4)>=0 then
	-- 	if data_set.workld4 <= 2 then
-- 			cla= cla-(0.5*data_set.workld4);
-- 		end if;
		if data_set.workld4 = 3 then
			cla=cla-2;
		end if;
	
		if data_set.workld4 = 4 then
			cla= cla-2;
		end if;

		
	
		if data_set.workld4 >= 5 and data_set.workld4 <= 7 then
			cla=cla-4;
		end if;
	
		if data_set.workld4 >= 8 and data_set.workld4 <= 14 then
			cla= cla-5;
		end if;
	
		if data_set.workld4 >= 15 then
			cla=0;
		end if;
	end if;

	if count(data_set.workld2)>=0 then
		if data_set.workld2>=1 then
			cla=cla-(0.5*data_set.workld2);
			end if;
			end if;

	if count(data_set.workld5)>=0 then

	if data_set.workld5>=1 then 
	cla=cla-(0.5*data_set.workld5);
	end if;
	end if;
	
	RAISE NOTICE 'This is cla %',cla;
	val_cla = cla*data_set.cla;
	RAISE NOTICE 'THIS IS TOTAL CLA AFTER CALCULATION %',val_cla;
	select ett.emp_cla into cla from employee_temp_table ett where lower(ett.job) not like 'security%';
	update employee_temp_table ett
	set cla=val_cla
	where ett.hp_id = data_set.hp_id;
	val_cla=0;
	end loop;
	---for security CLA
	for data_set in 
	select * from employee_temp_table ett where lower(ett.job) like 'security%' 
	loop

	if count(data_set.causlv)>=0 then
	cla_1=cla_1-data_set.causlv;
	end if;
	
	if count(data_set.annuallv)>=0 then
	cla_1=cla_1-data_set.annuallv;
	end if;
	
	if count(data_set.unplv1)>=0 then
	cla_1=cla_1-data_set.unplv1;
	end if;
	
	if count(data_set.unplv2)>=0 then
	cla_1=cla_1-data_set.unplv2;
	
	end if;
	
	if count(data_set.medlv1)>=0 then
	cla_1=cla_1-data_set.medlv1;
	end if;
	
	if count(data_set.medlv2)>=0 then
	cla_1=cla_1-data_set.medlv2;
	end if;
	
	if count(data_set.medlv3)>=0 then
	cla_1=cla_1-data_set.medlv3;
	end if;
	
	if count(data_set.matlv)>=0 then
	cla_1=cla_1-data_set.matlv;
	end if;
	Raise  notice 'abslv1 %',data_set.abslv1;
	if count(data_set.abslv1)>=0 then
		if data_set.abslv1 >=3 then
			cla_1= cla_1-10;
		end if;
		if data_set.abslv1 <3 then
			cla_1= cla_1-data_set.abslv1;
		end if;
	end if;
	Raise  notice 'abslv1 %',data_set.abslv1;
	Raise  notice 'abslv2 %',data_set.abslv2::integer;
	
	if count(data_set.abslv2)>=0 then
		if data_set.abslv2 = 3 then
			cla_1= cla_1-10;
		end if;
		if data_set.abslv2 <3 then
			cla_1=cla_1-data_set.abslv2;
		end if;
	end if;
	Raise  notice 'abslv2 %',data_set.abslv2;
	Raise  notice 'workld1%',data_set.workld1;	
	if count(data_set.workld1)>=0 then
	-- 	if data_set.workld1 <= 2 then
-- 			cla_1= cla_1-(0.5*data_set.workld1);
-- 		end if;
		if data_set.workld1 = 3 then
			cla_1=cla_1-2;
		end if;
	
		if data_set.workld1 = 4 then
			cla_1= cla_1-2;
		end if;

		
	
		if data_set.workld1 >= 5 and data_set.workld1 <= 7 then
			cla_1=cla_1-4;
		end if;
	
		if data_set.workld1 >= 8 and data_set.workld1 <= 14 then
			cla_1= cla_1-5;
		end if;
	
		if data_set.workld1 >= 15 then
			cla_1=0;
		end if;
	end if;


		if count(data_set.workld4)>=0 then
-- 		if data_set.workld4 <= 2 then
-- 			cla_1= cla_1-(0.5*data_set.workld4);
-- 		end if;
		if data_set.workld4 = 3 then
			cla_1=cla_1-2;
		end if;
	
		if data_set.workld4 = 4 then
			cla_1= cla_1-2;
		end if;

		
	
		if data_set.workld4 >= 5 and data_set.workld4 <= 7 then
			cla_1=cla_1-4;
		end if;
	
		if data_set.workld4 >= 8 and data_set.workld4 <= 14 then
			cla_1= cla_1-5;
		end if;
	
		if data_set.workld4 >= 15 then
			cla_1=0;
		end if;
	end if;

	if count(data_set.workld2)>=0 then
		if data_set.workld2>=1 then
			cla_1=cla_1-(0.5*data_set.workld2);
			end if;
			end if;

	if count(data_set.workld5)>=0 then

	if data_set.workld5>=1 then 
	cla_1=cla_1-(0.5*data_set.workld5);
	end if;
	end if;
	
	RAISE NOTICE 'This is cla %',cla_1;
	val_cla = cla_1*data_set.cla;
	RAISE NOTICE 'THIS IS TOTAL CLA AFTER CALCULATION %',val_cla;
	select ett.emp_cla into cla_1 from employee_temp_table ett where lower(ett.job) like 'security%' or upper(ett.job) like 'Security%';
	update employee_temp_table ett
	set cla=val_cla
	where ett.hp_id = data_set.hp_id;
	val_cla=0;
	end loop;
	
	RAISE NOTICE '----------END OF CLA CALCULATION----------';







		--inserting the total value to employee_temp
	for data_set in 
	select ett.emp_cla,ett.job_id,ett.job,count(ett.job_id) as total_emp,sum(ett.basic_salary) as basic_salary,sum(ett.allowance) as allowance,sum(ett.contribution) as contribution,sum(ett.cla) as cla,sum(ett.total) as total,sum(ett.ssb) as ssb,sum(ett.total_value) as total_value,sum(ett.income_tax) as income_tax from employee_temp_table ett group by ett.emp_cla,ett.job_id,ett.job
	loop
	insert into employee_temp(emp_cla,job,job_id ,total_emp,basic_salary,allowance,contribution,cla,total,ssb,total_value,income_tax)
	values(data_set.emp_cla,data_set.job,data_set.job_id ,data_set.total_emp,data_set.basic_salary,data_set.allowance,data_set.contribution,data_set.cla,data_set.total,data_set.ssb,data_set.total_value,data_set.income_tax);
	end loop;

	--updating the total and total_value to employee_temp
	for data_set in 
	select et.job_id,(et.basic_salary+et.allowance+et.contribution+et.cla) as total,((et.basic_salary+et.allowance+et.contribution+et.cla)-(et.income_tax+et.ssb)) as total_value from employee_temp et
	loop
	update employee_temp et
	set total=data_set.total, total_value = data_set.total_value
	where et.job_id = data_set.job_id;
	end loop;
	
	RAISE NOTICE 'Ending Store Procedure.......';	
	RETURN QUERY select * from employee_temp;
	
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION salary_calculation(date, date)
  OWNER TO odoo;
