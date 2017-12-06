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
  OWNER TO odoo;
