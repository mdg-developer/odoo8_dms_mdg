
-- View: financial_report_tree

CREATE OR REPLACE VIEW financial_report_tree AS 
 WITH RECURSIVE report_tree(id, name, sign, style_overwrite, sequence, depth, path, spacer) AS (
         SELECT tn.id,
            tn.name,
            tn.sign,
            tn.style_overwrite,
            tn.sequence,
            1 AS depth,
            ARRAY[tn.id] AS path,
            '    '::text AS spacer
           FROM account_financial_report tn
          WHERE tn.parent_id IS NULL
        UNION ALL
         SELECT c.id,
            (p.spacer || '    '::text) || c.name::text,
            c.sign,
            c.style_overwrite,
            c.sequence,
            p.depth + 1 AS depth,
            ((p.path || (p.depth + 1)) || c.sequence) || c.id,
            p.spacer || '    '::text AS spacer
           FROM report_tree p,
            account_financial_report c
          WHERE c.parent_id = p.id
        )
 SELECT row_number() OVER (ORDER BY n.path) AS row_number,
	    n.path[1] AS parent_id,
	    n.id,
	    n.name,
	    n.sign,
	    n.style_overwrite,
	    n.sequence,
	    n.depth,
	    n.path
   FROM report_tree n
  ORDER BY n.path;

ALTER TABLE financial_report_tree
  OWNER TO postgres;
CREATE OR REPLACE VIEW account_analytic_tree AS 
 WITH RECURSIVE account_analytic_tree(id, name, depth, path) AS (
         SELECT tn.id,
            tn.name,
            1 AS depth,
            ARRAY[tn.id] AS path,
            tn.parent_id
           FROM account_analytic_account tn
          WHERE parent_id IS NULL
        UNION ALL
         SELECT c.id,
            c.name,
            p.depth + 1 AS depth,
            p.path || c.id,
            c.parent_id
           FROM account_analytic_tree p,
            account_analytic_account c
          WHERE c.parent_id = p.id
        )
 SELECT n.parent_id,
    n.id,
    n.name,
    n.depth,
    n.path
   FROM account_analytic_tree n
  ORDER BY n.path;

ALTER TABLE account_analytic_tree
  OWNER TO postgres;

  
  
  
  -- View: analytic_report_tree

-- DROP VIEW analytic_report_tree;

CREATE OR REPLACE VIEW analytic_report_tree AS 
 WITH RECURSIVE aa_report_tree(id, name, depth, path, spacer) AS (
         SELECT tn.id,
            tn.name,
            1 AS depth,
            ARRAY[tn.id] AS path,
            '    '::text AS spacer
           FROM account_analytic_tree tn
          WHERE tn.parent_id IS NULL
        UNION ALL
         SELECT c.id,
            (p.spacer || '    '::text) || c.name::text,
            p.depth + 1 AS depth,
            (p.path || (p.depth + 1)) || c.id,
            p.spacer || '    '::text AS spacer
           FROM aa_report_tree p,
            account_analytic_tree c
          WHERE c.parent_id = p.id
        )
 SELECT n.path[1] AS parent_id,
    n.id,
    n.name,
    n.depth,
    n.path
   FROM aa_report_tree n
  ORDER BY n.path;

ALTER TABLE analytic_report_tree
  OWNER TO postgres;
  

-- Function: financial_report_balance_analytic(integer, integer, date, date, integer, integer, text, integer)

-- DROP FUNCTION financial_report_balance_analytic(integer, integer, date, date, integer, integer, text, integer);

CREATE OR REPLACE FUNCTION financial_report_balance_analytic(report_id integer, fiscal_year integer, start_date date, end_date date, start_period_id integer, end_period_id integer, state_cond text, analytic_id integer)
  RETURNS numeric AS
$BODY$
  DECLARE
    balance numeric;
    analytic_account_ids int[];
    account_ids int[];
    temp_account_id int[];
    r account_account_financial_report%rowtype;
    sql text :=   'select
                    COALESCE(sum((aml.debit - aml.credit)),0)
                  from account_move_line aml,
                    account_period period,
                    account_fiscalyear fiscalyear,
                    account_move
                  WHERE
                    aml.period_id = period.id AND
                    aml.move_id = account_move.id AND
                    period.fiscalyear_id = fiscalyear.id';

  BEGIN  
  
 
			
			    select array_agg(id) into analytic_account_ids 
			    from analytic_report_tree  where analytic_id  = ANY(PATH);

			    FOR r IN select *  from account_account_financial_report where report_line_id=$1

			    LOOP
			    
				select array_cat(account_ids,array_agg(id)) into account_ids from account_tree where r.account_id = ANY(PATH);

			    END LOOP;
			    
			    
			    IF account_ids IS NULL THEN
				return null;
			    END IF;
			    
			    IF account_ids IS NOT NULL THEN
				sql := sql || ' AND aml.account_id in ('|| array_to_string(account_ids, ',') ||')';
			    END IF;

			    IF analytic_account_ids IS NULL THEN
				sql := sql || ' AND aml.analytic_account_id is not null';
			    END IF;
			    
			    IF analytic_account_ids IS NOT NULL THEN
				sql := sql || ' AND aml.analytic_account_id in ('|| array_to_string(analytic_account_ids, ',') ||')';
			    END IF;
		    
    IF  fiscal_year>0 THEN
      sql := sql || ' AND fiscalyear.id = $2';
    END IF;

    IF  start_date > end_date and start_date is not null and end_date is not null THEN
      sql := sql || ' AND account_move.date between $3 and $4';
    END IF;

    IF  end_date is null and start_date is not null THEN
      sql := sql || ' AND account_move.date = $3';
    END IF;

     IF   start_date is null and end_date is not null THEN
      sql := sql || ' AND account_move.date = $4';
    END IF;

    IF start_period_id >0  and end_period_id >0 and start_period_id is not null and end_period_id is not null  THEN
      sql := sql || ' AND aml.period_id between $5 and $6';
    END IF;
    
   IF start_period_id >0  and end_period_id is null and start_period_id is not null THEN
      sql := sql || ' AND aml.period_id = $5 ';
    END IF;
       
   IF end_period_id >0  and start_period_id is null and end_period_id is not null THEN
      sql := sql || ' AND aml.period_id = $6 ';
    END IF;

 
    IF $7 = 'posted' THEN
       sql := sql || ' AND account_move.state = $7';
    END IF;

    EXECUTE sql into balance USING analytic_account_ids,fiscal_year,start_date,end_date,start_period_id,end_period_id,state_cond;
    IF balance < 0 THEN
    balance = balance * -1;
    END IF;
   return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION financial_report_balance_analytic(integer, integer, date, date, integer, integer, text, integer)
  OWNER TO postgres;
