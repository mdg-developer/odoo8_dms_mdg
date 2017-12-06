-- View: account_tree

-- DROP VIEW account_tree;

CREATE OR REPLACE VIEW account_tree AS 
 WITH RECURSIVE account_tree(id, name, depth, path) AS (
         SELECT tn.id,
            tn.name,
            1 AS depth,
            ARRAY[tn.id] AS path,
            tn.parent_left,
            tn.parent_right
           FROM account_account tn
        UNION ALL
         SELECT c.id,
            c.name,
            p.depth + 1 AS depth,
            p.path || c.id,
            c.parent_left,
            c.parent_right
           FROM account_tree p,
            account_account c
          WHERE c.parent_id = p.id
        )
 SELECT n.parent_left AS parent_id,
    n.id,
    n.name,
    n.depth,
    n.path,
    n.parent_left,
    n.parent_right
   FROM account_tree n
  ORDER BY n.path;

ALTER TABLE account_tree
  OWNER TO odoo;
