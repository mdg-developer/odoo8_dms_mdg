--account tree
CREATE OR REPLACE VIEW account_tree AS
  WITH RECURSIVE account_tree(id, name,  depth, path) AS (
    SELECT tn.id, tn.name,1 AS depth,
                          ARRAY[tn.id] AS path,tn.parent_left, tn.parent_right
    FROM account_account tn  where id=1

    UNION ALL
    SELECT c.id, c.name, p.depth + 1 AS depth,
      p.path || c.id,c.parent_left,c.parent_right
    FROM account_tree p, account_account c where c.parent_id = p.id

  )
  SELECT  parent_left AS parent_id, n.id, n.name, n.depth, n.path, parent_left, parent_right
  FROM account_tree n ORDER BY n.path;
  
  
 ---financial_report_tree
CREATE OR REPLACE VIEW financial_report_tree AS
  WITH RECURSIVE report_tree(id, name, sequence, depth, path) AS (
    SELECT tn.id, tn.name, tn.sequence,tn.parent_id, 1 AS depth,
                                        ARRAY[tn.id] AS path
    FROM account_financial_report tn
    WHERE tn.parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, c.sequence,c.parent_id, p.depth + 1 AS depth,
      p.path || c.id,
    FROM report_tree p, account_financial_report c
    WHERE c.parent_id = p.id
  )
  SELECT n.path[1] AS parent_id,n.parent_id as parent, n.id, n.name, n.sequence, n.depth, n.path
  FROM report_tree n
  ORDER BY n.path;

ALTER TABLE financial_report_tree
OWNER TO postgres;



-- View: financial_report_view

-- DROP VIEW financial_report_view;

CREATE OR REPLACE VIEW financial_report_view AS
  WITH account_move_line AS (
      SELECT account_account_financial_report.report_line_id,
        res_company.name AS company_name,
        account_account.name AS account_name,
        account_move_line.date AS txn_date,
        account_period.name AS period_name,
        account_fiscalyear.name AS fiscal_year,
        account_move_line.analytic_account_id, account_move.state,
        account_move_line.debit + account_move_line.credit AS balance
      FROM account_account, account_fiscalyear, account_period,
        public.account_move_line, account_move, res_company,
        account_account_financial_report
      WHERE account_fiscalyear.id = account_period.fiscalyear_id AND account_move_line.period_id = account_period.id AND account_move_line.account_id = account_account.id AND account_move_line.move_id = account_move.id
  ), analytic_account_move AS (
      SELECT ll.report_line_id, ll.company_name, ll.account_name,
        ll.txn_date, ll.period_name, ll.fiscal_year, ll.analytic_account_id,
        ll.state, ll.balance,
        COALESCE(account_analytic_account.name, 'Default'::character varying) AS analytic_code
      FROM account_move_line ll
        LEFT JOIN account_analytic_account ON ll.analytic_account_id = account_analytic_account.id
  )
  SELECT row_number() OVER (ORDER BY t.id) AS rownum, t.parent_id,
         t.name AS financial_report_name, t.path, am.company_name, am.account_name,
    am.txn_date, am.period_name, am.fiscal_year, am.balance, am.analytic_code,
    am.state
  FROM financial_report_tree t
    LEFT JOIN analytic_account_move am ON t.id = am.report_line_id
  WHERE am.txn_date IS NOT NULL
  ORDER BY row_number() OVER (ORDER BY t.id);

ALTER TABLE financial_report_view
OWNER TO postgres;


---financial_report_balance
create or replace function financial_report_balance(report_id INTEGER, fiscal_year Integer, period_id INTEGER, state_cond TEXT)
  returns NUMERIC  AS
  $$
  DECLARE
    balance NUMERIC;
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

                    IF account_ids IS NOT NULL THEN
                        sql := sql || ' AND aml.account_id in ('|| array_to_string(account_ids, ',') ||')';
	            END IF;
		    RAISE NOTICE ' SQL (%)', sql;
    IF fiscal_year IS NOT NULL or fiscal_year>0 THEN
      sql := sql || ' AND fiscalyear.id = $2';
    END IF;

    IF period_id IS NOT NULL or period_id>0 THEN
      sql := sql || ' AND aml.period_id = $3';
    END IF;

    IF state_cond = 'posted' THEN
       sql := sql || ' AND account_move.state = ''posted''';
    END IF;
    RAISE NOTICE ' SQL (%)', sql;
    EXECUTE sql into balance USING account_ids,fiscal_year,period_id,state_cond;
    IF balance < 0 THEN
    balance = balance * -1;

    END IF;
    RETURN balance;
  END;
  $$
LANGUAGE plpgsql;
