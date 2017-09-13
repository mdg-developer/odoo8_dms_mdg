-- Function: salary_payslip_report_net(character varying, date, date)
--select * from salary_payslip_report_net('2016-02-01','2016-02-29','Credit & Assets','card')
-- DROP FUNCTION salary_payslip_report_net(date, date,character varying,character varying);

CREATE OR REPLACE FUNCTION salary_payslip_report_net(
    IN date_from_param date,
    IN date_to_param date,
    IN dep_name character varying,
    IN payroll character varying)
  RETURNS TABLE(id bigint, name_related character varying, name character varying, amount numeric, bank_acc character varying) AS
$BODY$
DECLARE 
	emp_data_set RECORD;
	data_set RECORD;
	cla numeric;
	cla_1 numeric;
	val_cla numeric;
	v numeric;
	BEGIN  
	--Delete from salary_temp_table;
	cla=22;
	val_cla=0;
	v=0;
	DELETE FROM emp_temp1;
	DELETE from emp_temp2;
	RAISE NOTICE 'Starting Store Procedure.......';	

	--inserting the each employee information into employee_temp_table
	for emp_data_set in 
	select hj.id as job_id , hp.id as hp_id, hp.employee_id as emp_id,he.name_related as emp_name,hj.name as job_name from hr_employee he,hr_job hj,hr_payslip hp,hr_contract hc where hp.employee_id=he.id and hp.contract_id=hc.id and hc.job_id=hj.id and hp.date_from=date_from_param and hp.date_to=date_to_param group by hj.name,hp.employee_id,he.name_related,hp.id ,hj.id
	loop
		insert into emp_temp1(emp_cla,job_id,hp_id,job,emp_id,emp_name ,basic_salary ,allowance,contribution ,cla,total,ssb ,sff,total_value,income_tax, causlv,annuallv,unplv1,unplv2,medlv1,medlv2,medlv3,matlv,abslv1,abslv2,workld1,workld2,workld3,workld4,workld5)
		values(0,emp_data_set.job_id,emp_data_set.hp_id,emp_data_set.job_name,emp_data_set.emp_id,emp_data_set.emp_name ,0,0,0 ,0,0,0 ,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);
	end loop;
	--updating the basic salary
	for data_set in
	select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code='BASIC'
	loop
	update emp_temp1 ett
	set basic_salary=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;
	--updating the allowance
	for data_set in
	select ett.hp_id,sum(hpl.total) as total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code in ('ALL','TAL') group by ett.hp_id
	loop
	update emp_temp1 ett
	set allowance=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;
	--updating the contribution
	for data_set in
	select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code='CON'
	loop
	update emp_temp1 ett
	set contribution=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;
	--updating the SSB
	for data_set in
	select ett.hp_id as hp_id,hpl.code as code,hpl.total as total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code='SSBE'
	--select A.hp_id,(A.total+B.total) as total from (select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code='SSBE')A join (select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code='SSBER')B on A.hp_id=B.hp_id group by A.hp_id,A.total,B.total
	loop
	update emp_temp1 ett
	set ssb=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;
	--updating the cla
	for data_set in
	select hpi.amount,ett.hp_id from hr_payslip_input hpi,emp_temp1 ett where hpi.payslip_id=ett.hp_id and hpi.code='CLA'
	loop
	update emp_temp1 ett
	set cla=data_set.amount,cla1=data_set.amount
	where ett.hp_id = data_set.hp_id;

	end loop;
	--updating the sff
	for data_set in
	select hpi.amount,ett.hp_id from hr_payslip_input hpi,emp_temp1 ett where hpi.payslip_id=ett.hp_id and hpi.code='SFF'
	loop
	update emp_temp1 ett
	set sff=data_set.amount
	where ett.hp_id = data_set.hp_id;

	end loop;

-----Changes------
	--updating the cla by Job Title
	update emp_temp1 ett set emp_cla = 26 where lower(ett.job) like 'security%' or upper(ett.job) like 'Security%';
	--updating the cla by Job Title
	update emp_temp1 ett set emp_cla = 22 where lower(ett.job) not like 'security%' ;
-----Changes------
	--updating the income_tax
	for data_set in
	select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code='ICT'
	loop
	update emp_temp1 ett
	set income_tax=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;
	
	--updating the causlv to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='causlv'
 	loop
 	update emp_temp1 ett
	set causlv=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the annuallv to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='earnlv'
 	loop
 	update emp_temp1 ett
	set annuallv=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the unplv1 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='unplv1'
 	loop
 	update emp_temp1 ett
	set unplv1=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the unplv2 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='unplv2'
 	loop
 	update emp_temp1 ett
	set unplv2=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the medlv1 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='medlv1'
 	loop
 	update emp_temp1 ett
	set medlv1=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the medlv2 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='medlv2'
 	loop
 	update emp_temp1 ett
	set medlv2=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the medlv3 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='medlv3'
 	loop
 	update emp_temp1 ett
	set medlv3=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the matlv to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='matlv'
 	loop
 	update emp_temp1 ett
	set matlv=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the abslv1 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='abslv1'
 	loop
 	update emp_temp1 ett
	set abslv1=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the abslv2 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='abslv2'
 	loop
 	update emp_temp1 ett
	set abslv2=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the workld1 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld1'
 	loop
 	update emp_temp1 ett
	set workld1=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	--updating the workld2 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld2'
 	loop
 	update emp_temp1 ett
	set workld2=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
		
	--updating the workld3 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld3'
 	loop
 	update emp_temp1 ett
	set workld3=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
		
	--updating the workld4 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld4'
 	loop
 	update emp_temp1 ett
	set workld4=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the workld5 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld5'
 	loop
 	update emp_temp1 ett
	set workld5=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;


	---updating the two type of cla into variable cla and cla_1
	--for security job type
	select ett.emp_cla into cla_1 from emp_temp1 ett where lower(ett.job) like 'security%' or upper(ett.job) like 'Security%';
	--for normal job type
	select ett.emp_cla into cla from emp_temp1 ett where lower(ett.job) not like 'security%';
	
	--calculating all condition for each employee
	----for normal employee
	for data_set in 
	select * from emp_temp1 ett where lower(ett.job) not like 'security%' 
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
		if data_set.abslv2 >= 3 then
			cla= cla-7-data_set.abslv2;
		end if;
		if data_set.abslv2 <3 then
			cla=cla-data_set.abslv2;
		end if;
	end if;
	Raise  notice 'abslv2 %',data_set.abslv2;
	Raise  notice 'workld1%',data_set.workld1;	
	if count(data_set.workld1)>=3 then
		--if data_set.workld1 <= 2 then
			--cla= cla-(0.5*data_set.workld1);
		--end if;
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


		if count(data_set.workld4)>=3 then
		--if -ata_set.workld4 <= 2 then
			--cla= cla-(0.5*data_set.workld4);
		--end if;
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

--	if count(data_set.workld2)>=0 then
--		if data_set.workld2>=1 then
--			cla=cla-(0.5*data_set.workld2);
--			end if;
--			end if;
--
--	if count(data_set.workld5)>=0 then
--
--	if data_set.workld5>=1 then 
--	cla=cla-(0.5*data_set.workld5);
--	end if;
--	end if;
	Raise NOTICE 'This is original%',cla;
	Raise NOTICE 'This is sff calculation';
	if cla>0 and data_set.sff>0 then
		cla=cla-((data_set.sff/(data_set.cla/2))*0.5);
		RAISE NOTICE 'Entering SFF%',cla;
	end if;
	
	val_cla = cla*data_set.cla;
	RAISE NOTICE 'THIS IS TOTAL CLA AFTER CALCULATION %',val_cla;
	v=cla;
	select ett.emp_cla into cla from emp_temp1 ett where lower(ett.job) not like 'security%';
	update emp_temp1 ett
	set cla=round(val_cla),cla_day=v
	where ett.hp_id = data_set.hp_id;
	end loop;
	RAISE NOTICE '----------END OF CLA CALCULATION----------';



	--calculating all condition for each employee
	----for Job Type employee(SECURITY)
	for data_set in 
	select * from emp_temp1 ett where lower(ett.job) like 'security%'
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
		if data_set.abslv2 >= 3 then
			cla= cla-7-data_set.abslv2;
		end if;
		if data_set.abslv2 <3 then
			cla=cla-data_set.abslv2;
		end if;
	end if;
	Raise  notice 'abslv2 %',data_set.abslv2;
	Raise  notice 'workld1%',data_set.workld1;	



	if count(data_set.workld1)>=3 then
		--if data_set.workld1 <= 2 then
			--cla_1= cla_1-(0.5*data_set.workld1);
		--end if;
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


		if count(data_set.workld4)>=3 then
		--if data_set.workld4 <= 2 then
			--cla_1= cla_1-(0.5*data_set.workld4);
		--end if;
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

--	if count(data_set.workld2)>=0 then
--		if data_set.workld2>=1 then
--			cla_1=cla_1-(0.5*data_set.workld2);
--			end if;
--			end if;
--
--	if count(data_set.workld5)>=0 then
--
--	if data_set.workld5>=1 then 
--	cla_1=cla_1-(0.5*data_set.workld5);
--	end if;
--	end if;
	RAISE NOTICE 'This is cla_1 %',cla_1;
	if cla_1 >0 and data_set.sff>0 then
		cla_1=cla_1-(data_set.sff/(data_set.cla));
		RAISE NOTICE 'Entering SFF%',cla_1;
	end if;
	val_cla = cla_1*data_set.cla;
	RAISE NOTICE 'THIS IS TOTAL CLA AFTER CALCULATION %',payroll;
	v=cla_1;
	select ett.emp_cla into cla_1 from emp_temp1 ett where lower(ett.job) like 'security%' or upper(ett.job) like 'Security%';
	update emp_temp1 ett
	set cla=round(val_cla),cla_day=v
	where ett.hp_id = data_set.hp_id;
	end loop;
	RAISE NOTICE '----------END OF CLA CALCULATION----------';
	RAISE NOTICE 'PAYYYYYYYYYYYYYYYYYYY %',payroll;

	
	--inserting the total value to employee_temp
	for data_set in 
	select ett.emp_cla,ett.cla_day,ett.cla1,ett.job_id,ett.hp_id,ett.job,count(ett.job_id) as total_emp,ett.emp_name,ett.basic_salary,ett.allowance,ett.contribution,ett.cla,(ett.basic_salary+ett.allowance+ett.contribution+ett.cla) as total,ett.ssb,ett.income_tax,((ett.basic_salary+ett.allowance+ett.contribution+ett.cla)-(ett.ssb+ett.income_tax)) as total_value from emp_temp1 ett group by ett.emp_cla,ett.cla1,ett.cla_day,ett.basic_salary,ett.allowance,ett.contribution,ett.cla,ett.ssb,ett.income_tax,ett.job,ett.emp_name,ett.hp_id,ett.job_id
	loop
	insert into emp_temp2(emp_cla,cla_day,cla1,job, emp_name, job_id , total_emp, basic_salary, allowance, contribution, cla , total, ssb, total_value, income_tax)
	values(data_set.emp_cla,data_set.cla_day,data_set.cla1,data_set.job, data_set.emp_name, data_set.job_id , data_set.total_emp, data_set.basic_salary, data_set.allowance, data_set.contribution, data_set.cla , data_set.total, data_set.ssb, data_set.total_value, data_set.income_tax);
	end loop;

	
	RAISE NOTICE 'Ending Store Procedure.......';	
	IF dep_name is Null and payroll ='card' Then
	   RETURN QUERY select row_number() over (order by et.job_id) as id,et.emp_name as name_related,et.job as name,et.total_value as amount,rp.acc_number as bank_acc
	   from emp_temp2 et,res_partner_bank rp,hr_employee he
	                where he.name_related =et.emp_name
	                and rp.id=he.bank_account_id
	                and he.payroll_bank is True
	                order by et.job_id;
	ELSEIF dep_name is Null and payroll ='cash' Then
	   RETURN QUERY select row_number() over (order by et.job_id) as id,et.emp_name as name_related,et.job as name,et.total_value as amount,varchar'' as bank_acc
	   from emp_temp2 et,hr_employee he
	                where he.name_related =et.emp_name
	                and he.payroll_cash is True
	                order by et.job_id;	                
	ELSEIF dep_name is not Null and payroll ='card' Then
	   RETURN QUERY select row_number() over (order by et.job_id) as id,et.emp_name as name_related,et.job as name,et.total_value as amount,rp.acc_number as bank_acc
	   from emp_temp2 et,res_partner_bank rp,hr_employee he,hr_department hd 
	                where he.name_related =et.emp_name
	                and rp.id=he.bank_account_id
	                and he.department_id=hd.id 
	                and hd.name=dep_name
	                and he.payroll_bank is True
	                order by et.job_id;
	ELSEIF dep_name is not Null and payroll ='cash' Then
	   RETURN QUERY select row_number() over (order by et.job_id) as id,et.emp_name as name_related,et.job as name,et.total_value as amount,varchar''  as bank_acc
	   from emp_temp2 et,hr_employee he,hr_department hd 
	                where he.name_related =et.emp_name
	                and he.department_id=hd.id 
	                and hd.name=dep_name
	                and he.payroll_cash is True	                
	                order by et.job_id;	                      
	END IF;

	
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION salary_payslip_report_net(date, date,character varying,character varying)
  OWNER TO openerp;



-- Function: salary_payslip_report(integer, date, date)
--select * from salary_payslip_report(null,'2016-02-01','2016-02-29')
-- DROP FUNCTION salary_payslip_report(integer, date, date);

CREATE OR REPLACE FUNCTION salary_payslip_report(
    IN dep_id integer,
    IN date_from_param date,
    IN date_to_param date)
  RETURNS TABLE(emp_cla integer, emp_name character varying, job character varying, job_id integer, total_emp integer, basic_salary numeric, allowance numeric, travel_all numeric,contribution numeric, cla numeric, total numeric, ssb numeric, total_value numeric, income_tax numeric, cla1 numeric, cla_day numeric) AS
$BODY$
DECLARE 
	emp_data_set RECORD;
	data_set RECORD;
	cla numeric;
	cla_1 numeric;
	val_cla numeric;
	v numeric;
	BEGIN  
	--Delete from salary_temp_table;
	cla=22;
	val_cla=0;
	v=0;
	DELETE FROM emp_temp1;
	DELETE from emp_temp2;
	RAISE NOTICE 'Starting Store Procedure.......';	

	--inserting the each employee information into employee_temp_table
	for emp_data_set in 
	select hj.id as job_id , hp.id as hp_id, hp.employee_id as emp_id,he.name_related as emp_name,hj.name as job_name from hr_employee he,hr_job hj,hr_payslip hp,hr_contract hc where hp.employee_id=he.id and hp.contract_id=hc.id and hc.job_id=hj.id and hp.date_from=date_from_param and hp.date_to=date_to_param group by hj.name,hp.employee_id,he.name_related,hp.id ,hj.id
	loop
	insert into emp_temp1(emp_cla,job_id,hp_id,job,emp_id,emp_name ,basic_salary ,allowance,travel_all,contribution ,cla,total,ssb ,sff,total_value,income_tax, causlv,annuallv,unplv1,unplv2,medlv1,medlv2,medlv3,matlv,abslv1,abslv2,workld1,workld2,workld3,workld4,workld5)
			values(0,emp_data_set.job_id,emp_data_set.hp_id,emp_data_set.job_name,emp_data_set.emp_id,emp_data_set.emp_name ,0,0,0 ,0,0,0,0 ,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);
	end loop;

	--updating the basic salary
	for data_set in
	select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code='BASIC'
	loop
	update emp_temp1 ett
	set basic_salary=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;
	--updating the allowance
	for data_set in
	select ett.hp_id,sum(hpl.total) as total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code in ('ALL','TAL') group by ett.hp_id
	loop
	update emp_temp1 ett
	set allowance=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;
	--updating the contribution
	for data_set in
	select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code='CON'
	loop
	update emp_temp1 ett
	set contribution=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;
	--updating the SSB
	for data_set in
	select ett.hp_id as hp_id,hpl.code as code,hpl.total as total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code='SSBE'
	--select A.hp_id,(A.total+B.total) as total from (select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code='SSBE')A join (select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code='SSBER')B on A.hp_id=B.hp_id group by A.hp_id,A.total,B.total
	loop
	update emp_temp1 ett
	set ssb=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;
	--updating the cla
	for data_set in
	select hpi.amount,ett.hp_id from hr_payslip_input hpi,emp_temp1 ett where hpi.payslip_id=ett.hp_id and hpi.code='CLA'
	loop
	update emp_temp1 ett
	set cla=data_set.amount,cla1=data_set.amount
	where ett.hp_id = data_set.hp_id;

	end loop;
	--updating the sff
	for data_set in
	select hpi.amount,ett.hp_id from hr_payslip_input hpi,emp_temp1 ett where hpi.payslip_id=ett.hp_id and hpi.code='SFF'
	loop
	update emp_temp1 ett
	set sff=data_set.amount
	where ett.hp_id = data_set.hp_id;

	end loop;

-----Changes------
	--updating the cla by Job Title
	update emp_temp1 ett set emp_cla = 26 where lower(ett.job) like 'security%' or upper(ett.job) like 'Security%';
	--updating the cla by Job Title
	update emp_temp1 ett set emp_cla = 22 where lower(ett.job) not like 'security%' ;
-----Changes------
	--updating the income_tax
	for data_set in
	select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code='ICT'
	loop
	update emp_temp1 ett
	set income_tax=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;
	
	--updating the causlv to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='causlv'
 	loop
 	update emp_temp1 ett
	set causlv=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the annuallv to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='earnlv'
 	loop
 	update emp_temp1 ett
	set annuallv=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the unplv1 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='unplv1'
 	loop
 	update emp_temp1 ett
	set unplv1=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the unplv2 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='unplv2'
 	loop
 	update emp_temp1 ett
	set unplv2=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the medlv1 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='medlv1'
 	loop
 	update emp_temp1 ett
	set medlv1=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the medlv2 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='medlv2'
 	loop
 	update emp_temp1 ett
	set medlv2=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the medlv3 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='medlv3'
 	loop
 	update emp_temp1 ett
	set medlv3=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the matlv to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='matlv'
 	loop
 	update emp_temp1 ett
	set matlv=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the abslv1 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='abslv1'
 	loop
 	update emp_temp1 ett
	set abslv1=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the abslv2 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='abslv2'
 	loop
 	update emp_temp1 ett
	set abslv2=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the workld1 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld1'
 	loop
 	update emp_temp1 ett
	set workld1=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the workld2 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld2'
 	loop
 	update emp_temp1 ett
	set workld2=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
		
	--updating the workld3 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld3'
 	loop
 	update emp_temp1 ett
	set workld3=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
		
	--updating the workld4 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld4'
 	loop
 	update emp_temp1 ett
	set workld4=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the workld5 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld5'
 	loop
 	update emp_temp1 ett
	set workld5=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;


	---updating the two type of cla into variable cla and cla_1
	--for security job type
	select ett.emp_cla into cla_1 from emp_temp1 ett where lower(ett.job) like 'security%' or upper(ett.job) like 'Security%';
	--for normal job type
	select ett.emp_cla into cla from emp_temp1 ett where lower(ett.job) not like 'security%';
	
	--calculating all condition for each employee
	----for normal employee
	for data_set in 
	select * from emp_temp1 ett where lower(ett.job) not like 'security%' 
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
		if data_set.abslv2 >= 3 then
			cla= cla-7-data_set.abslv2;
		end if;
		if data_set.abslv2 <3 then
			cla=cla-data_set.abslv2;
		end if;
	end if;
	Raise  notice 'abslv2 %',data_set.abslv2;
	Raise  notice 'workld1%',data_set.workld1;	
	if count(data_set.workld1)>=3 then
		--if data_set.workld1 <= 2 then
			--cla= cla-(0.5*data_set.workld1);
		--end if;
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


		if count(data_set.workld4)>=3 then
		--if -ata_set.workld4 <= 2 then
			--cla= cla-(0.5*data_set.workld4);
		--end if;
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

--	if count(data_set.workld2)>=0 then
--		if data_set.workld2>=1 then
--			cla=cla-(0.5*data_set.workld2);
--			end if;
--			end if;
--
--	if count(data_set.workld5)>=0 then
--
--	if data_set.workld5>=1 then 
--	cla=cla-(0.5*data_set.workld5);
--	end if;
--	end if;
	Raise NOTICE 'This is original%',cla;
	Raise NOTICE 'This is sff calculation';
	if cla>0 and data_set.sff>0 then
		cla=cla-((data_set.sff/(data_set.cla/2))*0.5);
		RAISE NOTICE 'Entering SFF%',cla;
	end if;
	
	val_cla = cla*data_set.cla;
	RAISE NOTICE 'THIS IS TOTAL CLA AFTER CALCULATION %',val_cla;
	v=cla;
	select ett.emp_cla into cla from emp_temp1 ett where lower(ett.job) not like 'security%';
	update emp_temp1 ett
	set cla=round(val_cla),cla_day=v
	where ett.hp_id = data_set.hp_id;
	end loop;
	RAISE NOTICE '----------END OF CLA CALCULATION----------';



	--calculating all condition for each employee
	----for Job Type employee(SECURITY)
	for data_set in 
	select * from emp_temp1 ett where lower(ett.job) like 'security%'
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
		if data_set.abslv2 >= 3 then
			cla= cla-7-data_set.abslv2;
		end if;
		if data_set.abslv2 <3 then
			cla=cla-data_set.abslv2;
		end if;
	end if;

	Raise  notice 'abslv2 %',data_set.abslv2;
	Raise  notice 'workld1%',data_set.workld1;	



	if count(data_set.workld1)>=3 then
		--if data_set.workld1 <= 2 then
			--cla_1= cla_1-(0.5*data_set.workld1);
		--end if;
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


		if count(data_set.workld4)>=3 then
		--if data_set.workld4 <= 2 then
			--cla_1= cla_1-(0.5*data_set.workld4);
		--end if;
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

--	if count(data_set.workld2)>=0 then
--		if data_set.workld2>=1 then
--			cla_1=cla_1-(0.5*data_set.workld2);
--			end if;
--			end if;
--
--	if count(data_set.workld5)>=0 then
--
--	if data_set.workld5>=1 then 
--	cla_1=cla_1-(0.5*data_set.workld5);
--	end if;
--	end if;
	RAISE NOTICE 'This is cla_1 %',cla_1;
	if cla_1 >0 and data_set.sff>0 then
		cla_1=cla_1-(data_set.sff/(data_set.cla));
		RAISE NOTICE 'Entering SFF%',cla_1;
	end if;
	val_cla = cla_1*data_set.cla;
	RAISE NOTICE 'THIS IS TOTAL CLA AFTER CALCULATION %',val_cla;
	v=cla_1;
	select ett.emp_cla into cla_1 from emp_temp1 ett where lower(ett.job) like 'security%' or upper(ett.job) like 'Security%';
	update emp_temp1 ett
	set cla=round(val_cla),cla_day=v
	where ett.hp_id = data_set.hp_id;
	end loop;
	RAISE NOTICE '----------END OF CLA CALCULATION----------';

	
	--inserting the total value to employee_temp
	for data_set in 
	select ett.emp_cla,ett.cla_day,ett.cla1,ett.job_id,ett.hp_id,ett.job,count(ett.job_id) as total_emp,ett.emp_name,ett.basic_salary,ett.allowance,ett.travel_all,ett.contribution,ett.cla,(ett.basic_salary+ett.allowance+ett.contribution+ett.cla) as total,ett.ssb,ett.income_tax,
	((ett.basic_salary+ett.allowance+ett.contribution+ett.cla)-(ett.ssb+ett.income_tax)) as total_value from emp_temp1 ett 
	group by ett.emp_cla,ett.cla1,ett.cla_day,ett.basic_salary,ett.allowance,ett.contribution,ett.cla,ett.ssb,ett.income_tax,ett.job,ett.emp_name,ett.hp_id,ett.job_id,ett.travel_all
	loop
	insert into emp_temp2(emp_cla,cla_day,cla1,job, emp_name, job_id , total_emp, basic_salary, allowance,travel_all, contribution, cla , total, ssb, total_value, income_tax)
	values(data_set.emp_cla,data_set.cla_day,data_set.cla1,data_set.job, data_set.emp_name, data_set.job_id , data_set.total_emp, data_set.basic_salary, data_set.allowance,0, data_set.contribution, data_set.cla , data_set.total, data_set.ssb, data_set.total_value, data_set.income_tax);
	end loop;

	
	RAISE NOTICE 'Ending Store Procedure.......';	
	IF dep_id is Null Then
	   RETURN QUERY select * from emp_temp2;
	else 
	   RETURN QUERY select et.* from emp_temp2 et,hr_employee he,hr_department hd where et.emp_name=he.name_related and
	   he.department_id=hd.id and hd.id=dep_id;
	END IF;

	
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION salary_payslip_report(integer, date, date)
  OWNER TO openerp;



  
-- Function: salary_calculation_employee(integer, date, date)
--select * from salary_payslip_report(null,'2016-02-01','2016-02-29')
-- DROP FUNCTION salary_calculation_employee(integer, date, date);

CREATE OR REPLACE FUNCTION salary_calculation_employee(
    IN job_param integer,
    IN date_from_param date,
    IN date_to_param date)
  RETURNS TABLE(emp_cla integer, emp_name character varying, job character varying, job_id integer, total_emp integer, basic_salary numeric, allowance numeric,  travel_all numeric,contribution numeric, cla numeric, total numeric, ssb numeric, total_value numeric, income_tax numeric, cla1 numeric, cla_day numeric) AS
$BODY$
DECLARE 
	emp_data_set RECORD;
	data_set RECORD;
	cla numeric;
	cla_1 numeric;
	val_cla numeric;
	v numeric;
	BEGIN  
	--Delete from salary_temp_table;
	cla=22;
	val_cla=0;
	v=0;
	--select * from emp_temp1;
	DELETE FROM emp_temp1;
	DELETE from emp_temp2;
	RAISE NOTICE 'Starting Store Procedure.......';	

	--inserting the each employee information into employee_temp_table
	IF job_param is Null Then
		for emp_data_set in 
			--select hj.id as job_id , hp.id as hp_id, hp.employee_id as emp_id,he.name_related as emp_name,hj.name as job_name from hr_employee he,hr_contract hc,hr_job hj,hr_payslip hp where hp.employee_id=he.id and hc.employee_id=he.id 
	select hj.id as job_id , hp.id as hp_id, hp.employee_id as emp_id,he.name_related as emp_name,hj.name as job_name from hr_employee he,hr_job hj,hr_payslip hp,hr_contract hc where hp.employee_id=he.id and hp.contract_id=hc.id and hc.job_id=hj.id 
	and hp.date_from=date_from_param and hp.date_to=date_to_param group by hj.name,hp.employee_id,he.name_related,hp.id ,hj.id

			--and hp.date_from=date_from_param and hp.date_to=date_to_param group by hj.name,hp.employee_id,he.name_related,hp.id ,hj.id
		loop
			insert into emp_temp1(emp_cla,job_id,hp_id,job,emp_id,emp_name ,basic_salary ,allowance,travel_all,contribution ,cla,total,ssb ,sff,total_value,income_tax, causlv,annuallv,unplv1,unplv2,medlv1,medlv2,medlv3,matlv,abslv1,abslv2,workld1,workld2,workld3,workld4,workld5)
			values(0,emp_data_set.job_id,emp_data_set.hp_id,emp_data_set.job_name,emp_data_set.emp_id,emp_data_set.emp_name ,0,0,0 ,0,0,0,0 ,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);
		end loop;
	else 
		for emp_data_set in 
			select hj.id as job_id , hp.id as hp_id, hp.employee_id as emp_id,he.name_related as emp_name,hj.name as job_name from hr_employee he,hr_contract hc,hr_job hj,hr_payslip hp where hj.id=job_param and hp.employee_id=he.id and hc.job_id=			   job_param and hc.employee_id=he.id and hp.date_from=date_from_param and hp.date_to=date_to_param group by hj.name,hp.employee_id,he.name_related,hp.id ,hj.id
		loop
			insert into emp_temp1(emp_cla,job_id,hp_id,job,emp_id,emp_name ,basic_salary ,allowance,travel_all,contribution ,cla,total,ssb ,sff,total_value,income_tax, causlv,annuallv,unplv1,unplv2,medlv1,medlv2,medlv3,matlv,abslv1,abslv2,workld1,workld2,workld3,			  workld4,workld5)
			values(0,emp_data_set.job_id,emp_data_set.hp_id,emp_data_set.job_name,emp_data_set.emp_id,emp_data_set.emp_name ,0,0,0,0 ,0,0,0 ,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);
		end loop;
	END IF;

	--updating the basic salary
	for data_set in
	select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code='BASIC'
	loop
	update emp_temp1 ett
	set basic_salary=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;
	--updating the allowance
	for data_set in
		select ett.hp_id,hpl.total  from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code ='ALL'  
	loop	
		update emp_temp1 ett
		set allowance=data_set.total
		where ett.hp_id=data_set.hp_id;

	end loop;

	for data_set in
		select ett.hp_id,hpl.total as total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code = 'TAL'
	loop
	update emp_temp1 ett
	set travel_all=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;	
	--updating the contribution
	for data_set in
	select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code='CON'
	loop
	update emp_temp1 ett
	set contribution=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;
	--updating the SSB
	for data_set in
	select ett.hp_id as hp_id,hpl.code as code,hpl.total as total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code='SSBE'
	--select A.hp_id,(A.total+B.total) as total from (select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code='SSBE')A join (select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code='SSBER')B on A.hp_id=B.hp_id group by A.hp_id,A.total,B.total
	loop
	update emp_temp1 ett
	set ssb=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;
	--updating the cla
	for data_set in
	select hpi.amount,ett.hp_id from hr_payslip_input hpi,emp_temp1 ett where hpi.payslip_id=ett.hp_id and hpi.code='CLA'
	loop
	update emp_temp1 ett
	set cla=data_set.amount,cla1=data_set.amount
	where ett.hp_id = data_set.hp_id;

	end loop;

	--updating the sff
	for data_set in
	select hpi.amount,ett.hp_id from hr_payslip_input hpi,emp_temp1 ett where hpi.payslip_id=ett.hp_id and hpi.code='SFF'
	loop
	update emp_temp1 ett
	set sff=data_set.amount
	where ett.hp_id = data_set.hp_id;

	end loop;
-----Changes------
	--updating the cla by Job Title
	update emp_temp1 ett set emp_cla = 26 where lower(ett.job) like 'security%' or upper(ett.job) like 'Security%';
	--updating the cla by Job Title
	update emp_temp1 ett set emp_cla = 22 where lower(ett.job) not like 'security%' ;
-----Changes------
	--updating the income_tax
	for data_set in
	select ett.hp_id,hpl.code,hpl.total from hr_payslip_line hpl,emp_temp1 ett where hpl.slip_id=ett.hp_id and code='ICT'
	loop
	update emp_temp1 ett
	set income_tax=data_set.total
	where ett.hp_id=data_set.hp_id;

	end loop;
	
	--updating the causlv to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='causlv'
 	loop
 	update emp_temp1 ett
	set causlv=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the annuallv to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='earnlv'
 	loop
 	update emp_temp1 ett
	set annuallv=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the unplv1 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='unplv1'
 	loop
 	update emp_temp1 ett
	set unplv1=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the unplv2 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='unplv2'
 	loop
 	update emp_temp1 ett
	set unplv2=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the medlv1 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='medlv1'
 	loop
 	update emp_temp1 ett
	set medlv1=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the medlv2 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='medlv2'
 	loop
 	update emp_temp1 ett
	set medlv2=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the medlv3 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='medlv3'
 	loop
 	update emp_temp1 ett
	set medlv3=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the matlv to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='matlv'
 	loop
 	update emp_temp1 ett
	set matlv=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the abslv1 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='abslv1'
 	loop
 	update emp_temp1 ett
	set abslv1=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the abslv2 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='abslv2'
 	loop
 	update emp_temp1 ett
	set abslv2=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the workld1 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld1'
 	loop
 	update emp_temp1 ett
	set workld1=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the workld2 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld2'
 	loop
 	update emp_temp1 ett
	set workld2=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
		
	--updating the workld3 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld3'
 	loop
 	update emp_temp1 ett
	set workld3=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
		
	--updating the workld4 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld4'
 	loop
 	update emp_temp1 ett
	set workld4=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;
	
	--updating the workld5 to emp_temp1
	for data_set in 
	select ett.hp_id,hpw.code,hpw.number_of_days from hr_payslip_worked_days hpw,emp_temp1 ett where hpw.payslip_id=ett.hp_id and LOWER(code)='workld5'
 	loop
 	update emp_temp1 ett
	set workld5=data_set.number_of_days
	where ett.hp_id=data_set.hp_id;
	end loop;


	---updating the two type of cla into variable cla and cla_1
	--for security job type
	select ett.emp_cla into cla_1 from emp_temp1 ett where lower(ett.job) like 'security%' or upper(ett.job) like 'Security%';
	--for normal job type
	select ett.emp_cla into cla from emp_temp1 ett where lower(ett.job) not like 'security%';
	
	--calculating all condition for each employee
	----for normal employee
	for data_set in 
	select * from emp_temp1 ett where lower(ett.job) not like 'security%' 
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
		if data_set.abslv2 >= 3 then
			cla= cla-7-data_set.abslv2;
		end if;
		if data_set.abslv2 <3 then
			cla=cla-data_set.abslv2;
		end if;
	end if;
	Raise  notice 'abslv2 %',data_set.abslv2;
	Raise  notice 'workld1%',data_set.workld1;	
	if count(data_set.workld1)>=0 then
	-- 	if data_set.workld1 <= 2 then
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
		-- if data_set.workld4 <= 2 then
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

--	if count(data_set.workld2)>=0 then
--		if data_set.workld2>=1 then
--			cla=cla-(0.5*data_set.workld2);
--			end if;
--			end if;
--
--	if count(data_set.workld5)>=0 then
--
--	if data_set.workld5>=1 then 
--	cla=cla-(0.5*data_set.workld5);
--	end if;
--	end if;
	if cla>0 and data_set.sff>0 then
		
		RAISE NOTICE 'This is cla %',cla;
		cla=cla-(data_set.sff/(data_set.cla));
		Raise NOTICE 'This is sff calculation result%',cla;
		Raise NOTICE 'This is sff calculation result%',round(cla)*data_set.cla;
		RAISE NOTICE 'This is cla %',cla;
	
	end if;
	val_cla = cla*data_set.cla;
	RAISE NOTICE 'THIS IS TOTAL CLA AFTER CALCULATION %',val_cla;
	v=cla;
	select ett.emp_cla into cla from emp_temp1 ett where lower(ett.job) not like 'security%';
	update emp_temp1 ett
	set cla=val_cla,cla_day=v
	where ett.hp_id = data_set.hp_id;
	end loop;
	RAISE NOTICE '----------END OF CLA CALCULATION----------';



	--calculating all condition for each employee
	----for Job Type employee(SECURITY)
	for data_set in 
	select * from emp_temp1 ett where lower(ett.job) like 'security%'
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
		if data_set.abslv2 >= 3 then
			cla= cla-7-data_set.abslv2;
		end if;
		if data_set.abslv2 <3 then
			cla=cla-data_set.abslv2;
		end if;
	end if;
	Raise  notice 'abslv2 %',data_set.abslv2;
	Raise  notice 'workld1%',data_set.workld1;	



	if count(data_set.workld1)>=0 then
		-- if data_set.workld1 <= 2 then
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
		-- if data_set.workld4 <= 2 then
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

--	if count(data_set.workld2)>=0 then
--		if data_set.workld2>=1 then
--			cla_1=cla_1-(0.5*data_set.workld2);
--			end if;
--			end if;
--
--	if count(data_set.workld5)>=0 then
--
--	if data_set.workld5>=1 then 
--	cla_1=cla_1-(0.5*data_set.workld5);
--	end if;
--	end if;
	if cla>0 and data_set.sff>0 then
		
		RAISE NOTICE 'This is cla %',cla_1;
		Raise NOTICE 'This is sff calculation';
		cla_1=cla_1-((data_set.sff/(data_set.cla/2))*0.5);
		Raise NOTICE 'This is sff calculation result%',cla_1;
		Raise NOTICE 'This is sff calculation result%',round(cla_1)*data_set.cla;
		RAISE NOTICE 'This is cla_1 %',cla_1;
	end if;
	val_cla = cla_1*data_set.cla;
	RAISE NOTICE 'THIS IS TOTAL CLA AFTER CALCULATION %',val_cla;
	v=cla_1;
	select ett.emp_cla into cla_1 from emp_temp1 ett where lower(ett.job) like 'security%' or upper(ett.job) like 'Security%';
	update emp_temp1 ett
	set cla=val_cla,cla_day=v
	where ett.hp_id = data_set.hp_id;
	end loop;
	RAISE NOTICE '----------END OF CLA CALCULATION----------';

	
	--inserting the total value to employee_temp
	for data_set in 
	select ett.emp_cla,ett.cla_day,ett.cla1,ett.job_id,ett.hp_id,ett.job,count(ett.job_id) as total_emp,ett.emp_name,ett.basic_salary,ett.allowance,ett.travel_all,ett.contribution,ett.cla,
	(ett.basic_salary+ett.allowance+ett.contribution+ett.cla+ett.travel_all) as total,ett.ssb,ett.income_tax,((ett.basic_salary+ett.allowance+ett.contribution+ett.cla+ett.travel_all)-(ett.ssb+ett.income_tax)) as total_value from emp_temp1 ett 
	group by ett.emp_cla,ett.cla1,ett.cla_day,ett.basic_salary,ett.allowance,ett.contribution,ett.cla,ett.ssb,ett.income_tax,ett.job,ett.emp_name,ett.hp_id,ett.job_id,ett.travel_all
	loop
	insert into emp_temp2(emp_cla,cla_day,cla1,job, emp_name, job_id , total_emp, basic_salary, allowance,travel_all,contribution, cla , total, ssb, total_value, income_tax)
	values(data_set.emp_cla,data_set.cla_day,data_set.cla1,data_set.job, data_set.emp_name, data_set.job_id , data_set.total_emp, data_set.basic_salary, data_set.allowance,data_set.travel_all, data_set.contribution, data_set.cla , data_set.total, data_set.ssb, data_set.total_value, data_set.income_tax);
	end loop;

	RAISE NOTICE 'Ending Store Procedure.......';	
	RETURN QUERY select * from emp_temp2;
	
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION salary_calculation_employee(integer, date, date)
  OWNER TO openerp;

