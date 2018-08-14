
-- DROP VIEW financial_report_tree;
--account tree
CREATE OR REPLACE VIEW financial_report_tree AS
  WITH RECURSIVE report_tree(id, name, sequence, depth, path,spacer) AS (
    SELECT tn.id, tn.name, tn.sequence, 1 AS depth,
                                        ARRAY[tn.id] AS path, '    ' AS spacer
    FROM account_financial_report tn
    WHERE tn.parent_id IS NULL
    UNION ALL
    SELECT c.id,  p.spacer||'    '||c.name, c.sequence, p.depth + 1 AS depth,
      p.path || (p.depth + 1 ) || c.sequence|| c.id, p.spacer||'    ' as spacer
    FROM report_tree p, account_financial_report c
    WHERE c.parent_id = p.id
  )
  SELECT n.path[1] AS parent_id, n.id, n.name, n.sequence, n.depth, n.path
  FROM report_tree n
  ORDER BY n.path;
  
--account financial_report_balance
create or replace function financial_report_balance(report_id INTEGER, fiscal_year Integer, period_id INTEGER, state_cond TEXT)
  returns numeric  AS
  $$
  DECLARE
    balance numeric;
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


                     -- select account_id from account_account_financial_report where report_line_id=report_id
                    FOR r IN select *  from account_account_financial_report where report_line_id=$1
                    LOOP
                    raise NOTICE ' searching id(%)',r.account_id;
			select array_cat(account_ids,array_agg(id)) into account_ids from account_tree where r.account_id = ANY(PATH);
                    END LOOP;
                    --there is not account and return null for that
		     IF account_ids IS NULL THEN
			return null;
		     END IF;
                    IF account_ids IS NOT NULL THEN
                        sql := sql || ' AND aml.account_id in ('|| array_to_string(account_ids, ',') ||')';
	            END IF;
		    RAISE NOTICE ' SQL (%)', sql;
    IF  fiscal_year>0 THEN
      sql := sql || ' AND fiscalyear.id = $2';
    END IF;

    IF period_id>0 THEN
      sql := sql || ' AND aml.period_id = $3';
    END IF;

    IF $4 = 'posted' THEN
       sql := sql || ' AND account_move.state = $4';
    END IF;
    RAISE NOTICE ' SQL (%)', sql;
    EXECUTE sql into balance USING account_ids,fiscal_year,period_id,state_cond;
    IF balance < 0 THEN
    balance = balance * -1;
    END IF;
        RAISE NOTICE 'balance (%)', balance;

   return balance;
  END;
  $$
LANGUAGE plpgsql;


--account tree

CREATE OR REPLACE VIEW account_tree AS 
 WITH RECURSIVE account_tree(id, name, depth, path) AS (
                 SELECT tn.id, tn.name, 1 AS depth, ARRAY[tn.id] AS path, 
                    tn.parent_left, tn.parent_right
                   FROM account_account tn
                  WHERE tn.id = 1
        UNION ALL 
                 SELECT c.id, c.name, p.depth + 1 AS depth, p.path || c.id, 
                    c.parent_left, c.parent_right
                   FROM account_tree p, account_account c
                  WHERE c.parent_id = p.id
        )
 SELECT n.parent_left AS parent_id, n.id, n.name, n.depth, n.path, 
    n.parent_left, n.parent_right
   FROM account_tree n
  ORDER BY n.path;

