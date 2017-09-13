-- Function: incomtax_oneyear_report()
--select * from incomtax_oneyear_report()
-- DROP FUNCTION incomtax_oneyear_report();

CREATE OR REPLACE FUNCTION incomtax_oneyear_report()
  RETURNS TABLE(id bigint, p_emp_name character varying, p_dep_name character varying, p_job_name character varying, p_join_date date, p_nrc_no character varying, p_mon_wage double precision, p_year_wage double precision, p_blw double precision, p_marital character varying, p_wf_spouse numeric, p_wf_child numeric, p_wf_parent numeric, p_social_contribution numeric, p_li_amount double precision, p_amount1 numeric, p_amount2 numeric, p_amount3 numeric, p_in_tax numeric, p_average_tax numeric, p_average_mon_tax numeric) AS
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
	now_month integer;

	begin  
		RAISE NOTICE 'Starting Store Procedure.......';	 
	--Deleting Temp Table

		DELETE FROM incometax_temp;
	FOR inform_data
		IN
		select contract_id,emp_name,dep_name,job_name,join_date,identification_id,montly_wage,year_wage,basic_labour_welfare,marital,social_contribution,li_amount,children,is_father_inlaw,is_mother_inlaw,is_fam_father,is_fam_mother
                from(
		select * ,((wage+contribution+allowance)+(cla_amount*day)) as montly_wage, (((wage+contribution+allowance)+(cla_amount*day))*12) as year_wage,((((wage+contribution+allowance)+(cla_amount*day))*12)*0.20) as basic_labour_welfare
		,((wage*12)*0.02) as social_contribution
		,(life_insurance/year) as li_amount
		from
		(select he.name_related as emp_name,hd.name as dep_name,hj.name as job_name,trial_date_start as join_date,children,is_fam_father,is_fam_mother,is_father_inlaw,is_mother_inlaw,

		he.identification_id,hc.wage,hc.contribution,hc.allowance,marital,year,life_insurance,hj.cla_amount,hj.day,hc.id as contract_id
		from hr_employee he,hr_contract hc,hr_department hd ,hr_job hj
		where he.id=hc.employee_id
		and hd.id=he.department_id
		and hc.job_id=hj.id
		--and identification_id is null or  identification_id
		order by hj.id)A)B		
		
	LOOP	
		RAISE NOTICE 'Inform_data.marital ===%',inform_data.marital;	 
	        RAISE NOTICE 'Inform_data.children ====%',inform_data.children;	
	        SELECT EXTRACT(MONTH FROM now()::date) into now_month;   
	        
	        IF now_month=1 or now_month=2 or now_month=3 Then
	            SELECT EXTRACT(YEAR FROM now()::date) into next_year;   
	        ELSE
	            SELECT EXTRACT(YEAR FROM now()::date)+1 into next_year;   
	        END IF;

	        select (next_year||'-03'||'-01')::date into year_date;

	        SELECT (date_part('year',age(year_date::date, (hc.trial_date_end +interval '1 days')::date)) * 12 )+date_part('month',age(year_date::date, (hc.trial_date_end +interval '1 days')::date)) into w_month from hr_contract hc where hc.id=inform_data.contract_id;   
	        IF w_month >=12 Then
	           w_month=12;
	        ELSEIF  w_month <12 Then
	            w_month=w_month;
	        END IF;
	        
		inform_data.year_wage=inform_data.montly_wage*w_month;
		inform_data.basic_labour_welfare=inform_data.year_wage*0.20;
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
		    INSERT INTO incometax_temp(emp_name,dep_name,job_name,join_date,nrc_no,mon_wage,year_wage,blw,marital,wf_spouse,wf_child,wf_parent
		    ,social_contribution,li_amount,amount1,amount2,amount3,in_tax)
		    VALUES (inform_data.emp_name,inform_data.dep_name,inform_data.job_name,inform_data.join_date,inform_data.identification_id,inform_data.montly_wage
		    ,inform_data.year_wage ,inform_data.basic_labour_welfare,inform_data.marital ,0,0,f_amount,inform_data.social_contribution,inform_data.li_amount,0,0,0,in_tax);
		elseif (inform_data.marital!='single' and inform_data.children=0 or inform_data.children is Null) Then
		    inform_data.marital='Yes';
		    if (inform_data.li_amount is Null) then
	               inform_data.li_amount=0.0;
	            end if;
		    in_tax= inform_data.year_wage-(inform_data.basic_labour_welfare+inform_data.social_contribution+inform_data.li_amount+1000000+f_amount) ;         
		    INSERT INTO incometax_temp(emp_name,dep_name,job_name,join_date,nrc_no,mon_wage,year_wage,blw,marital,wf_spouse,wf_child,wf_parent
		    ,social_contribution,li_amount,amount1,amount2,amount3,in_tax)
		    VALUES (inform_data.emp_name,inform_data.dep_name,inform_data.job_name,inform_data.join_date,inform_data.identification_id,inform_data.montly_wage
		    ,inform_data.year_wage ,inform_data.basic_labour_welfare,inform_data.marital ,1000000,0,f_amount,inform_data.social_contribution,inform_data.li_amount,0,0,0,in_tax);
		elseif (inform_data.marital!='single' and inform_data.children>0) Then
		    inform_data.marital='Yes';
		    if (inform_data.li_amount is Null) then
	               inform_data.li_amount=0.0;
	            end if;
		    child_amt=(inform_data.children * 500000);
		    in_tax= inform_data.year_wage-(inform_data.basic_labour_welfare+inform_data.social_contribution+inform_data.li_amount+1000000+child_amt+f_amount);
		    INSERT INTO incometax_temp(emp_name,dep_name,job_name,join_date,nrc_no,mon_wage,year_wage,blw,marital,wf_spouse,wf_child,wf_parent
		    ,social_contribution,li_amount,amount1,amount2,amount3,in_tax)
		    VALUES (inform_data.emp_name,inform_data.dep_name,inform_data.job_name,inform_data.join_date,inform_data.identification_id,inform_data.montly_wage
		    ,inform_data.year_wage ,inform_data.basic_labour_welfare,inform_data.marital ,1000000,child_amt,f_amount,inform_data.social_contribution,inform_data.li_amount,0,0,0,in_tax);			    	
		end if;
        End LOOP;
	For
	        last_data
	        In
	        select * from incometax_temp
	        
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
		        Update incometax_temp Set amount1=result where emp_name=last_data.emp_name;
		        RAISE NOTICE 'amount2-------%',c_amount2;		  
		        if(c_amount2>5000000) Then
			        c_amount3=c_amount2-5000000;
			        RAISE NOTICE 'amount3-------%',c_amount3;
			        result=((5000000*0.10)+150000);
			        Update incometax_temp Set amount2=result where emp_name=last_data.emp_name	;	  
		                
				if(c_amount3>10000000) Then
				        c_amount4=c_amount3-10000000;
				        result=((10000000*0.15)+650000);
				        Update incometax_temp Set amount3=result where emp_name=last_data.emp_name;	  
				else
				        result=((c_amount3)*0.15);
				        Update incometax_temp Set amount3=result where emp_name=last_data.emp_name;
				end if;	  

		        else
			        result=((c_amount2)*0.10);
			        RAISE NOTICE 'result-------%',result;
			        Update incometax_temp Set amount2=result where emp_name=last_data.emp_name;
		        end if;	
	        else
				result=((c_amount1)*0.05);
				RAISE NOTICE 'result1-------%',result;

				Update incometax_temp Set amount1=result where emp_name=last_data.emp_name;		  

	        end if;	
	     end if;


        END LOOP;
        

        RETURN QUERY select row_number() over (order by hj.sequence) as id,it.*,(amount1+amount2+amount3) as average_tax, (amount1+amount2+amount3)/12 as average_monthly_tax
                     from incometax_temp it,hr_job hj
                     where hj.name=it.job_name
                     order by hj.sequence;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION incomtax_oneyear_report()
  OWNER TO openerp;
