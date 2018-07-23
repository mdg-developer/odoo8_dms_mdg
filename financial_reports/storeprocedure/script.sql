-- Table: analytic_branch_report

-- DROP TABLE analytic_branch_report;

CREATE TABLE analytic_branch_report
(
  name character varying,
  branch character varying,
  analytic_account character varying,
  balance numeric,
  path integer[],
  depth integer,
  sequence integer
)
WITH (
  OIDS=FALSE
);
ALTER TABLE analytic_branch_report
  OWNER TO openerp;

-- Function: financial_report_balance_analytic_branch(integer, integer, date, date, integer, integer, text, text, text)

-- DROP FUNCTION financial_report_balance_analytic_branch(integer, integer, date, date, integer, integer, text, text, text);

CREATE OR REPLACE FUNCTION financial_report_balance_analytic_branch(IN report_id integer, IN fiscal_year integer, IN start_date date, IN end_date date, IN start_period_id integer, IN end_period_id integer, IN state_cond text, IN analytic_ids text, IN branch_ids text)
  RETURNS TABLE(branch character varying, analytic_account character varying, balance numeric) AS
$BODY$
 DECLARE
   balance numeric;
   analytic_account_ids int[];
   account_ids int[];
   temp_account_id int[];
   r account_account_financial_report%rowtype;
   i integer;
   sql text :=   'select
                   branch.branch_code branch,aa.name analytic_account,COALESCE(sum((aml.debit - aml.credit)),0) balance
                 from account_move_line aml,
                   account_period period,
                   account_fiscalyear fiscalyear,
                   account_move,
                   res_branch branch,
                   account_analytic_account aa
                 WHERE
                   aml.period_id = period.id AND
                   aml.move_id = account_move.id AND
                   period.fiscalyear_id = fiscalyear.id AND
                   aml.branch_id=branch.id AND
                   aml.analytic_account_id=aa.id';

 BEGIN  		    

			    FOREACH i IN ARRAY regexp_split_to_array(analytic_ids, ',')
			    LOOP 				   
				   if analytic_account_ids is null then
					select array_agg(id) into analytic_account_ids 
					from analytic_report_tree  where i = ANY(PATH);					
				   elsif analytic_account_ids is not null then
					select array_append(analytic_account_ids,i) into analytic_account_ids;					
				   end if;
			    END LOOP;							    

			    FOR r IN select *  from account_account_financial_report where report_line_id=report_id

			    LOOP
			    
				select array_cat(account_ids,array_agg(id)) into account_ids from account_tree where r.account_id = ANY(PATH);
				
			    END LOOP;

			    IF account_ids IS NULL THEN
				return;
			    END IF;
			    
			    IF account_ids IS NOT NULL THEN
				sql := sql || ' AND aml.account_id in ('|| array_to_string(account_ids, ',') ||')';
			    END IF;
			    
			    IF analytic_account_ids IS NOT NULL THEN
				sql := sql || ' AND aml.analytic_account_id in ('|| array_to_string(analytic_account_ids, ',') ||')';
			    END IF;		    
			    
			    IF branch_ids IS NOT NULL THEN
				sql := sql || ' AND aml.branch_id in ('|| branch_ids ||')';
			    END IF;
		    
   IF  fiscal_year>0 THEN
     sql := sql || ' AND fiscalyear.id = '|| fiscal_year;
   END IF;

   IF  start_date > end_date and start_date is not null and end_date is not null THEN
     sql := sql || ' AND account_move.date between ''' || start_date || ''' and ''' || end_date || ''' ';
   END IF;

   IF  end_date is null and start_date is not null THEN
     sql := sql || ' AND account_move.date = ''' || start_date || ''' ';
   END IF;

    IF   start_date is null and end_date is not null THEN
     sql := sql || ' AND account_move.date = ''' || end_date || ''' ';
   END IF;

   IF start_period_id >0  and end_period_id >0 and start_period_id is not null and end_period_id is not null  THEN
     sql := sql || ' AND aml.period_id between ''' || start_period_id || ''' and ''' || end_period_id || ''' ';
   END IF;
   
  IF start_period_id >0  and end_period_id is null and start_period_id is not null THEN
     sql := sql || ' AND aml.period_id = '|| start_period_id;
   END IF;
      
  IF end_period_id >0  and start_period_id is null and end_period_id is not null THEN
     sql := sql || ' AND aml.period_id = '|| end_period_id;
   END IF;

   IF $7 = 'posted' THEN
      sql := sql || ' AND account_move.state = "posted" ';
   END IF;

   sql := sql || ' group by aa.name,branch.branch_code';

  Return QUERY EXECUTE sql;
 END;
 $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;

-- Function: financial_report_analytic_horizontal(integer, integer, date, date, integer, integer, text, text, text)

-- DROP FUNCTION financial_report_analytic_horizontal(integer, integer, date, date, integer, integer, text, text, text);

CREATE OR REPLACE FUNCTION financial_report_analytic_horizontal(IN report_id integer, IN fiscal_year integer, IN start_date date, IN end_date date, IN start_period_id integer, IN end_period_id integer, IN state_cond text, IN analytic_ids text, IN branch_ids text)
  RETURNS TABLE(name character varying, branch character varying, analytic_account character varying, balance numeric, path integer[] ,depth integer,sequence integer) AS
$BODY$
 DECLARE
	reports record;
	record record;
	branch character varying;
	analytic_account character varying;
	balance numeric; 
 BEGIN  

	delete from analytic_branch_report;
	
	for reports in select * from financial_report_tree where parent_id=report_id and id!=parent_id
	loop	
		if EXISTS(select * from financial_report_balance_analytic_branch(reports.id,fiscal_year,start_date,end_date,start_period_id,end_period_id,state_cond,analytic_ids,branch_ids)) then
			for record in select * from financial_report_balance_analytic_branch(reports.id,fiscal_year,start_date,end_date,start_period_id,end_period_id,state_cond,analytic_ids,branch_ids)
			loop							
				insert into analytic_branch_report(name,branch,analytic_account,balance,path,depth,sequence) values(reports.name,record.branch,record.analytic_account,record.balance*reports.sign,reports.path,reports.depth,reports.sequence);		
			end loop;			
		else
			balance=0.00;
			branch='test';
			analytic_account='test analytic account';
			insert into analytic_branch_report(name,branch,analytic_account,balance,path,depth,sequence) values(reports.name,branch,analytic_account,balance*reports.sign,reports.path,reports.depth,reports.sequence);		
		end if;
		
	end loop;
	
	return query select * from analytic_branch_report order by sequence;
 END;
 $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;