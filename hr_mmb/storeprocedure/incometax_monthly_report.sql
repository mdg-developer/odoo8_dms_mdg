-- Function: incomtax_monthly_report(date, date)
--select * from incomtax_monthly_report('2015-04-01','2016-03-31')
-- DROP FUNCTION incomtax_monthly_report(date, date);



CREATE OR REPLACE FUNCTION incomtax_monthly_report(IN p_from_date date, IN p_to_date date)
  RETURNS TABLE(id bigint, p_emp_name character varying, p_job_name character varying, p_average_tax numeric, p_average_mon_tax numeric, p_april double precision, p_may double precision, p_june double precision, p_july double precision, p_aug double precision, p_sep double precision, p_oct double precision, p_nov double precision, p_dec double precision, p_jan double precision, p_feb double precision, p_march double precision) AS
$BODY$
declare 
	inform_data RECORD ;
	last_data RECORD ;
	child_amt  numeric=0 ;
	in_tax  numeric=0 ;
	last_amount numeric=0 ;
        c_amount1 numeric=0 ;
        c_amount2 numeric=0 ;
        c_amount3 numeric=0 ;
        c_amount4 numeric=0 ;
        result  numeric=0 ;
        f_amount numeric=0;
        is_father boolean;
        is_mother boolean;
	is_f_inlaw boolean;
	is_m_inlaw boolean;
	next_year integer ;
	w_month integer;
	year_date date;	


	begin  
		RAISE NOTICE 'Starting Store Procedure.......';	 
	--Deleting Temp Table

		DELETE FROM monthly_incometax_temp;
	FOR inform_data
		IN
		select emp_id,con_id,emp_name,dep_name,job_name,join_date,identification_id,montly_wage,year_wage,basic_labour_welfare,marital,social_contribution,li_amount,children,is_father_inlaw,is_mother_inlaw,is_fam_father,is_fam_mother
                from(
		select * ,((wage+contribution+allowance)+(cla_amount*day)) as montly_wage, (((wage+contribution+allowance)+(cla_amount*day))*12) as year_wage,((((wage+contribution+allowance)+(cla_amount*day))*12)*0.20) as basic_labour_welfare
		,((wage*12)*0.02) as social_contribution
		,(life_insurance/year) as li_amount
		from
		(select he.id as emp_id,hc.id as con_id,he.name_related as emp_name,hd.name as dep_name,hj.name as job_name,trial_date_start as join_date,children,is_fam_father,is_fam_mother,is_father_inlaw,is_mother_inlaw,

		he.identification_id,hc.wage,hc.contribution,hc.allowance,marital,year,life_insurance,hj.cla_amount,hj.day
		from hr_employee he,hr_contract hc,hr_department hd ,hr_job hj
		where he.id=hc.employee_id
		and hd.id=he.department_id
		and hc.job_id=hj.id)A)B

	LOOP	
		RAISE NOTICE 'Inform_data.marital ===%',inform_data.marital;	 
	        RAISE NOTICE 'Inform_data.children ====%',inform_data.children;	 
  SELECT EXTRACT(YEAR FROM  p_to_date::date) into next_year;   

	        select (next_year||'-03'||'-01')::date into year_date;

	        SELECT (date_part('year',age(year_date::date, (hc.trial_date_end +interval '1 days')::date)) * 12 )+date_part('month',age(year_date::date, (hc.trial_date_end +interval '1 days')::date)) into w_month from hr_contract hc where hc.id=inform_data.con_id;   
	        IF w_month >=12 Then
	           w_month=12;
	        ELSEIF  w_month <12 Then
	            w_month=w_month;
	        END IF;
	        
		inform_data.year_wage=inform_data.montly_wage*w_month;
		inform_data.basic_labour_welfare=inform_data.year_wage*0.20;
	        RAISE NOTICE 'inform_data.year_wage%',inform_data.year_wage;		        
                is_father=inform_data.is_fam_father;
		is_mother=inform_data.is_fam_mother;
		is_f_inlaw=inform_data.is_father_inlaw;
		is_m_inlaw=inform_data.is_mother_inlaw;
		if (is_father=True and is_mother=True and is_f_inlaw=True and is_m_inlaw=True)Then
		    f_amount=4000000.00;
		elseif (is_father=True and is_mother=True and is_f_inlaw=True and is_m_inlaw=False)Then
		    f_amount=3000000.00;
		elseif (is_father=True and is_mother=True and is_f_inlaw=False and is_m_inlaw=False)Then
		    f_amount=2000000.00;
		elseif (is_father=True and is_mother=False and is_f_inlaw=False and is_m_inlaw=False)Then
		    f_amount=1000000.00;
		elseif (is_father=False and is_mother=True and is_f_inlaw=True and is_m_inlaw=True)Then
		    f_amount=3000000.00;
	        elseif (is_father=False and is_mother=True and is_f_inlaw=False and is_m_inlaw=True)Then
		    f_amount=2000000.00;
		elseif (is_father=False and is_mother=True and is_f_inlaw=True and is_m_inlaw=False)Then
		    f_amount=2000000.00;
	        elseif (is_father=False and is_mother=True and is_f_inlaw=False and is_m_inlaw=False)Then
		    f_amount=1000000.00;
		elseif (is_father=False and is_mother=False and is_f_inlaw=True and is_m_inlaw=True)Then
		    f_amount=2000000.00;
		elseif (is_father=False and is_mother=False and is_f_inlaw=False and is_m_inlaw=True)Then
		    f_amount=1000000.00;
		elseif (is_father=False and is_mother=False and is_f_inlaw=True and is_m_inlaw=False)Then
		    f_amount=1000000.00;
		elseif (is_father=True and is_mother=False and is_f_inlaw=True and is_m_inlaw=True)Then
		    f_amount=3000000.00;
		elseif (is_father=True and is_mother=False and is_f_inlaw=False and is_m_inlaw=True)Then
		    f_amount=2000000.00;
		elseif (is_father=True and is_mother=True and is_f_inlaw=False and is_m_inlaw=True)Then
		    f_amount=3000000.00;
		elseif (is_father=True and is_mother=False and is_f_inlaw=True and is_m_inlaw=False)Then
		    f_amount=2000000.00;
		else
		    f_amount=0.00;
	        end if;
	        RAISE NOTICE 'f_amount-------%',f_amount;
                RAISE NOTICE 'employee-------%',inform_data.emp_name;
	        if (inform_data.marital='single') Then
	            inform_data.marital='No';	
	            if (inform_data.li_amount is Null) then
	               inform_data.li_amount=0.0;	   
	            end if;         
	            in_tax= inform_data.year_wage-(inform_data.basic_labour_welfare+inform_data.social_contribution+inform_data.li_amount+f_amount) ;         
                     RAISE NOTICE 'in_taxin_taxin_taxin_tax-------%',in_tax;
		    INSERT INTO monthly_incometax_temp(emp_id,emp_name,dep_name,job_name,join_date,nrc_no,mon_wage,year_wage,blw,marital,wf_spouse,wf_child,wf_parent
		    ,social_contribution,li_amount,amount1,amount2,amount3,in_tax)
		    VALUES (inform_data.emp_id,inform_data.emp_name,inform_data.dep_name,inform_data.job_name,inform_data.join_date,inform_data.identification_id,inform_data.montly_wage
		    ,inform_data.year_wage ,inform_data.basic_labour_welfare,inform_data.marital ,0,0,f_amount,inform_data.social_contribution,inform_data.li_amount,0,0,0,in_tax);
		elseif (inform_data.marital!='single' and inform_data.children=0 or inform_data.children is null) Then
		    inform_data.marital='Yes';
		    if (inform_data.li_amount is Null) then
	               inform_data.li_amount=0.0;
	            end if;
		    in_tax= inform_data.year_wage-(inform_data.basic_labour_welfare+inform_data.social_contribution+inform_data.li_amount+1000000+f_amount) ;         
		    INSERT INTO monthly_incometax_temp(emp_id,emp_name,dep_name,job_name,join_date,nrc_no,mon_wage,year_wage,blw,marital,wf_spouse,wf_child,wf_parent
		    ,social_contribution,li_amount,amount1,amount2,amount3,in_tax)
		    VALUES (inform_data.emp_id,inform_data.emp_name,inform_data.dep_name,inform_data.job_name,inform_data.join_date,inform_data.identification_id,inform_data.montly_wage
		    ,inform_data.year_wage ,inform_data.basic_labour_welfare,inform_data.marital ,1000000,0,f_amount,inform_data.social_contribution,inform_data.li_amount,0,0,0,in_tax);
		elseif (inform_data.marital!='single' and inform_data.children>0) Then
		    inform_data.marital='Yes';
		    if (inform_data.li_amount is Null) then
	               inform_data.li_amount=0.0;
	            end if;
		    child_amt=(inform_data.children * 500000);
		    in_tax= inform_data.year_wage-(inform_data.basic_labour_welfare+inform_data.social_contribution+inform_data.li_amount+1000000+child_amt+f_amount);
		    INSERT INTO monthly_incometax_temp(emp_id,emp_name,dep_name,job_name,join_date,nrc_no,mon_wage,year_wage,blw,marital,wf_spouse,wf_child,wf_parent
		    ,social_contribution,li_amount,amount1,amount2,amount3,in_tax)
		    VALUES (inform_data.emp_id,inform_data.emp_name,inform_data.dep_name,inform_data.job_name,inform_data.join_date,inform_data.identification_id,inform_data.montly_wage
		    ,inform_data.year_wage ,inform_data.basic_labour_welfare,inform_data.marital ,1000000,child_amt,f_amount,inform_data.social_contribution,inform_data.li_amount,0,0,0,in_tax);			    	
		end if;
        End LOOP;
	For
	        last_data
	        In
	        select * from monthly_incometax_temp
	        
	LOOP
	       last_amount=last_data.in_tax;
	       if(last_amount >0)Then
	       
	          c_amount1=last_amount-2000000;
	       else
	          c_amount1=0.0;
	       end if;
	       RAISE NOTICE 'c_amount1%',c_amount1;
	       RAISE NOTICE 'last_data.emp_name%',last_data.emp_name;
               if(c_amount1>0) Then
	        if(c_amount1>3000000) Then
		        c_amount2=c_amount1-3000000;
		        result=(3000000*0.05);
		        Update monthly_incometax_temp Set amount1=result where emp_name=last_data.emp_name;
		        RAISE NOTICE 'amount2-------%',c_amount2;		  
		        if(c_amount2>5000000) Then
			        c_amount3=c_amount2-5000000;
			        RAISE NOTICE 'amount3-------%',c_amount3;
			        result=((5000000*0.10)+150000);
			        Update monthly_incometax_temp Set amount2=result where emp_name=last_data.emp_name	;	  
		                
				if(c_amount3>10000000) Then
				        c_amount4=c_amount3-10000000;
				        result=((10000000*0.15)+650000);
				        Update monthly_incometax_temp Set amount3=result where emp_name=last_data.emp_name;	  
				else
				        result=((c_amount3)*0.15);
				        Update monthly_incometax_temp Set amount3=result where emp_name=last_data.emp_name;
				end if;	  

		        else
			        result=((c_amount2)*0.10);
			        RAISE NOTICE 'result-------%',result;
			        Update monthly_incometax_temp Set amount2=result where emp_name=last_data.emp_name;
		        end if;	
	        else
				result=((c_amount1)*0.05);
				RAISE NOTICE 'result1-------%',result;

				Update monthly_incometax_temp Set amount1=result where emp_name=last_data.emp_name;		  

	        end if;	
	     end if;


        END LOOP;
        RETURN QUERY select row_number() over (order by hj.sequence) as id,emp_name,job_name,(amount1+amount2+amount3) as average_tax, (amount1+amount2+amount3)/12 as average_monthly_tax,
        SUM(CASE WHEN to_char(from_date, 'MM-dd') Like('%04-%') THEN tp.amount END) as april,
        SUM(CASE WHEN to_char(from_date, 'MM-dd') Like('%05-%') THEN tp.amount END) as may,
        SUM(CASE WHEN to_char(from_date, 'MM-dd') Like('%06-%') THEN tp.amount END) as june,
        SUM(CASE WHEN to_char(from_date, 'MM-dd') Like('%07-%') THEN tp.amount END) as july,
        SUM(CASE WHEN to_char(from_date, 'MM-dd') Like('%08-%') THEN tp.amount END) as aug,
        SUM(CASE WHEN to_char(from_date, 'MM-dd') Like('%09-%') THEN tp.amount END) as sep,
        SUM(CASE WHEN to_char(from_date, 'MM-dd') Like('%10-%') THEN tp.amount END) as oct,
        SUM(CASE WHEN to_char(from_date, 'MM-dd') Like('%11-%') THEN tp.amount END) as nov,
        SUM(CASE WHEN to_char(from_date, 'MM-dd') Like('%12-%') THEN tp.amount END) as dec,
        SUM(CASE WHEN to_char(from_date, 'MM-dd') Like('%01-%') THEN tp.amount END) as jan,
        SUM(CASE WHEN to_char(from_date, 'MM-dd') Like('%02-%') THEN tp.amount END) as feb,
        SUM(CASE WHEN to_char(from_date, 'MM-dd') Like('%03-%') THEN tp.amount END) as march   
        from monthly_incometax_temp it,tax_payment tp ,hr_job hj
        where it.emp_id=tp.employee_id and tp.from_date > p_from_date and to_date < p_to_date
        and hj.name=it.job_name
        Group By tp.employee_id,it,emp_name,it.job_name,it.amount1,it.amount2,it.amount3,hj.sequence
        order by hj.sequence;
        END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION incomtax_monthly_report(date, date)
  OWNER TO odoo;
