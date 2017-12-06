-- View: financial_report_tree

-- DROP VIEW financial_report_tree;

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
  OWNER TO odoo;
