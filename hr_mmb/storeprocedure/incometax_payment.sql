-- Function: incometax_payment_report(date, date)

-- DROP FUNCTION incometax_payment_report(date, date);
--select * from incometax_payment_report('2015-04-01','2016-03-31')
CREATE OR REPLACE FUNCTION incometax_payment_report(
    IN from_date_param date,
    IN to_date_param date)
  RETURNS TABLE(id bigint, p_emp_name character varying, p_dep_name character varying, p_job_name character varying, p_join_date date, p_nrc_no character varying, p_mon_wage double precision, p_year_wage double precision, p_blw double precision, p_marital character varying, p_wf_spouse numeric, p_wf_child numeric, p_wf_parent numeric, p_social_contribution numeric, p_li_amount double precision, p_amount1 numeric, p_amount2 numeric, p_amount3 numeric, p_in_tax numeric, p_bail_out_tax numeric, r_bail_out_tax numeric, p_average_tax numeric, p_average_mon_tax numeric) AS
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
        r_bail_tax_amount numeric=0;
        bail_tax_amount numeric=0;
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

		DELETE FROM incometax_payment_temp;
       
		
	FOR inform_data
		IN
		select emp_name,emp_name_id,dep_name,job_name,join_date,identification_id,montly_wage,year_wage,basic_labour_welfare,marital,social_contribution,li_amount,children,is_father_inlaw,is_mother_inlaw,is_fam_father,is_fam_mother,bail_out_tax
                from(
		select * ,((wage+contribution+allowance)+(cla_amount*day)) as montly_wage, (((wage+contribution+allowance)+(cla_amount*day))*12) as year_wage,((((wage+contribution+allowance)+(cla_amount*day))*12)*0.20) as basic_labour_welfare
		,((wage*12)*0.02) as social_contribution
		,(life_insurance/year) as li_amount
		from
		(select he.name_related as emp_name_id,he.id as emp_name,hd.name as dep_name,hj.name as job_name,trial_date_start as join_date,children,is_fam_father,is_fam_mother,is_father_inlaw,is_mother_inlaw,he.identification_id,hc.wage,hc.contribution,hc.allowance,marital,year,life_insurance,hj.cla_amount,hj.day
		from hr_employee he,hr_contract hc,hr_department hd ,hr_job hj
		, tax_payment tp
		where he.id=hc.employee_id
		and hd.id=he.department_id
		and tp.employee_id = he.id
		and hc.job_id=hj.id group by 
		he.name_related,hd.name,hj.name,hc.trial_date_start,he.children, he.is_fam_father, he.is_fam_mother,
		he.is_father_inlaw, is_mother_inlaw,he.id,he.identification_id,hc.wage,hc.contribution,hc.allowance,marital,year,life_insurance,hj.cla_amount,hj.day,hj.cla_amount,hj.day
		)A,
		(select sum(amount)as bail_out_tax,employee_id as emp_id from tax_payment where from_date >= from_date_param and to_date <= to_date_param group by employee_id 
		)B where A.emp_name=B.emp_id)C
	LOOP	
		RAISE NOTICE 'Inform_data.marital ===%',inform_data.marital;	 
	        RAISE NOTICE 'Inform_data.children ====%',inform_data.children;	 
	        
	        SELECT EXTRACT(YEAR FROM  to_date_param::date) into next_year;   

	        select (next_year||'-03'||'-01')::date into year_date;

	        SELECT (date_part('year',age(year_date::date, (trial_date_end +interval '1 days')::date)) * 12 )+date_part('month',age(year_date::date, (trial_date_end +interval '1 days')::date)) into w_month from hr_contract where employee_id=inform_data.emp_name;   
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
		    INSERT INTO incometax_payment_temp(emp_name,dep_name,job_name,join_date,nrc_no,mon_wage,year_wage,blw,marital,wf_spouse,wf_child,wf_parent
		    ,social_contribution,li_amount,amount1,amount2,amount3,in_tax,bail_out_tax)
		    VALUES (inform_data.emp_name,inform_data.dep_name,inform_data.job_name,inform_data.join_date,inform_data.identification_id,inform_data.montly_wage
		    ,inform_data.year_wage ,inform_data.basic_labour_welfare,inform_data.marital ,0,0,f_amount,inform_data.social_contribution,inform_data.li_amount,0,0,0,in_tax,inform_data.bail_out_tax);
		elseif (inform_data.marital!='single' and inform_data.children=0 or inform_data.children is null) Then
		    inform_data.marital='Yes';
		    if (inform_data.li_amount is Null) then
	               inform_data.li_amount=0.0;
	            end if;

		    in_tax= inform_data.year_wage-(inform_data.basic_labour_welfare+inform_data.social_contribution+inform_data.li_amount+1000000+f_amount) ;         
		    RAISE NOTICE 'in_taxin_taxin_taxin_tax-------%',in_tax;

		    INSERT INTO incometax_payment_temp(emp_name,dep_name,job_name,join_date,nrc_no,mon_wage,year_wage,blw,marital,wf_spouse,wf_child,wf_parent
		    ,social_contribution,li_amount,amount1,amount2,amount3,in_tax,bail_out_tax)
		    VALUES (inform_data.emp_name,inform_data.dep_name,inform_data.job_name,inform_data.join_date,inform_data.identification_id,inform_data.montly_wage
		    ,inform_data.year_wage ,inform_data.basic_labour_welfare,inform_data.marital ,1000000,0,f_amount,inform_data.social_contribution,inform_data.li_amount,0,0,0,in_tax,inform_data.bail_out_tax);
		elseif (inform_data.marital!='single' and inform_data.children>0) Then
		    inform_data.marital='Yes';
		    if (inform_data.li_amount is Null) then
	               inform_data.li_amount=0.0;
	            end if;
		    child_amt=(inform_data.children * 500000);
		    in_tax= inform_data.year_wage-(inform_data.basic_labour_welfare+inform_data.social_contribution+inform_data.li_amount+1000000+child_amt+f_amount);
		    INSERT INTO incometax_payment_temp(emp_name,dep_name,job_name,join_date,nrc_no,mon_wage,year_wage,blw,marital,wf_spouse,wf_child,wf_parent
		    ,social_contribution,li_amount,amount1,amount2,amount3,in_tax,bail_out_tax)
		    VALUES (inform_data.emp_name,inform_data.dep_name,inform_data.job_name,inform_data.join_date,inform_data.identification_id,inform_data.montly_wage
		    ,inform_data.year_wage ,inform_data.basic_labour_welfare,inform_data.marital ,1000000,child_amt,f_amount,inform_data.social_contribution,inform_data.li_amount,0,0,0,in_tax,inform_data.bail_out_tax);			    	
		end if;
        End LOOP;
	For
	        last_data
	        In
	        select * from incometax_payment_temp
	        
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
		        Update incometax_payment_temp Set amount1=result where emp_name=last_data.emp_name;
		        RAISE NOTICE 'amount2-------%',c_amount2;		  
		        if(c_amount2>5000000) Then
			        c_amount3=c_amount2-5000000;
			        RAISE NOTICE 'amount3-------%',c_amount3;
			        result=((5000000*0.10)+150000);
			        Update incometax_payment_temp Set amount2=result where emp_name=last_data.emp_name;	  
		                
				if(c_amount3>10000000) Then
				        c_amount4=c_amount3-10000000;
				        result=((10000000*0.15)+650000);
				        Update incometax_payment_temp Set amount3=result where emp_name=last_data.emp_name;	  
				else
				        result=((c_amount3)*0.15);
				        Update incometax_payment_temp Set amount3=result where emp_name=last_data.emp_name;
				end if;	  

		        else
			        result=((c_amount2)*0.10);
			        RAISE NOTICE 'result-------%',result;
			        Update incometax_payment_temp Set amount2=result where emp_name=last_data.emp_name;
		        end if;	
	        else
				result=((c_amount1)*0.05);
				RAISE NOTICE 'result1-------%',result;

				Update incometax_payment_temp Set amount1=result where emp_name=last_data.emp_name;		  

	        end if;	
	     end if;


        END LOOP;
        RETURN QUERY select row_number() over (order by hj.sequence) as id,he.name_related,ipt.dep_name,ipt.job_name,ipt.join_date,
		  ipt.nrc_no,ipt.mon_wage,ipt.year_wage,ipt.blw,ipt.marital,ipt.wf_spouse,ipt.wf_child,ipt.wf_parent,ipt.social_contribution,ipt.li_amount,ipt.amount1,ipt.amount2,ipt.amount3,ipt.in_tax,
                  ipt.bail_out_tax,((amount1+amount2+amount3) - bail_out_tax) as r_bail_out_tax,(amount1+amount2+amount3) as average_tax, (amount1+amount2+amount3)/12 as average_monthly_tax 
                     from incometax_payment_temp ipt,hr_job hj,hr_employee he
                     where hj.name =ipt.job_name
                     and he.id = ipt.emp_name
                     order by hj.sequence;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION incometax_payment_report(date, date)
  OWNER TO openerp;
