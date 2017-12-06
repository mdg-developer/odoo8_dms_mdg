-- View: account_analytic_tree

-- DROP VIEW account_analytic_tree;

CREATE OR REPLACE VIEW account_analytic_tree AS 
 WITH RECURSIVE account_analytic_tree(id, name, depth, path) AS (
         SELECT tn.id,
            tn.name,
            1 AS depth,
            ARRAY[tn.id] AS path,
            tn.parent_id
           FROM account_analytic_account tn
          WHERE tn.parent_id IS NULL
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
  OWNER TO odoo;
