-- Function: payroll_figure_report(date, date, integer, numeric, numeric)

-- DROP FUNCTION payroll_figure_report(date, date, integer, numeric, numeric);

CREATE OR REPLACE FUNCTION payroll_figure_report(
    IN from_date date,
    IN to_date date,
    IN param_fun_unit integer,
    IN param_head_count numeric,
    IN param_total_amount numeric)
  RETURNS TABLE(ser_no bigint, func_id integer, parent_id integer, functional_unit character varying, structure character varying, head_count numeric, sum numeric, parent_fun_unit character varying, action text) AS
$BODY$
	DECLARE
		
	BEGIN
	----select * from temp_stuff
		DROP TABLE IF EXISTS temp_stuff;
		CREATE TEMPORARY TABLE temp_stuff AS
		(select DENSE_RANK() over (order by B.name) as Ser_no,A.*,B.name as Parent_Fun_Unit  ,CASE WHEN A.Structure='Permanent Salary Employee Structure' THEN 'PSE'
			    WHEN A.Structure='Daily Worker Salary Structure' THEN 'PDW'  END as Action from 
		(select fig.Func_ID,
		fig.Parent_ID,
		fig.Functional_Unit,
		fig.Structure,
		SUM(count) as count,
		SUM(total)
		from
		(
		select hf.id as Func_ID,
		hf.parent_id as Parent_ID,
		hf.name as Functional_Unit,
		dc.department_id as Dept_ID,
		hd.name as Department_Name,
		ps.name as Structure,
		dc.counter as count,
		ps.id,
		mix.total
		from
		(
		select department_id,struct_id,count(employee_id) as counter
		from hr_contract
		where department_id is not null
		and employee_id in
		(
		select distinct(employee_id)
		from hr_payslip
		where date_from = from_date
		and date_to =to_date
		)
		group by department_id,struct_id
		having count(employee_id)>0
		order by department_id
		)dc,
		(
		select tt.department_id,
		tt.struct_id,SUM(tt.total) as total
		from
		(
		select he.contract_id,hc.struct_id,he.department_id,ps.name as structure,psl.total as total
		from hr_payslip_line psl,hr_payslip hp,
		hr_employee he,
		hr_contract hc,
		hr_payroll_structure ps
		where psl.code='NET'
		and hp.id=psl.slip_id
		and psl.employee_id=he.id
		and he.contract_id=hc.id
		and hc.struct_id=ps.id
		and hp.date_from = from_date
		and hp.date_to =to_date
		order by department_id


		)tt
		group by tt.department_id,tt.struct_id
		order by tt.department_id
		)mix,
		hr_payroll_structure ps,
		hr_department hd,
		hr_functional_units hf
		where dc.department_id=mix.department_id
		and hd.id=dc.department_id
		and hd.id=mix.department_id
		and hf.id=hd.hr_functional_units_id
		and hf.parent_id is not null
		and mix.struct_id=ps.id
		and dc.struct_id=ps.id
		and mix.struct_id=dc.struct_id
		order by hf.id,mix.struct_id
		)fig
		group by fig.Func_ID,
		fig.parent_ID,
		fig.Functional_Unit,
		fig.Structure
		order by fig.Func_ID)A,
		(select hf.name,hf.id from hr_functional_units hf)B
		where A.parent_ID=B.id
		order by A.Func_ID);
		Insert Into temp_stuff(ser_no,func_id,parent_id,functional_unit,structure,count,sum,parent_fun_unit,Action)
		VALUES (2,36,23,'YANGON FACTORY',null,param_head_count,param_total_amount,'MANUFACTURING','TDW');

			   
		RAISE NOTICE 'Total OT Hours successfully retrieved!....';
                If (param_fun_unit is null) Then
			Return query select * from temp_stuff;	
		Else 
		    	Return query select * from temp_stuff where parent_id =param_fun_unit;	
		End If;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION payroll_figure_report(date, date, integer, numeric, numeric)
  OWNER TO openerp;
