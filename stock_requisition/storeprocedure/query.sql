-- View good_issue_note_report:
-- select * from good_issue_note_report;
-- DROP VIEW good_issue_note_report;

CREATE OR REPLACE VIEW good_issue_note_report
 AS

	select a.qty_on_hand,sum(a.total_issue_qty) as total_issue_qty,gin_id,product_id
	from (
		  select (select COALESCE (sum(qty),0)
		  from stock_quant
		  where product_id =line.product_id and location_id = note.to_location_id)  as qty_on_hand,
		  line.product_id,line.issue_quantity as issue_quantity,
		  (line.issue_quantity*(select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=product_uom) )as total_issue_qty,
		  note.id gin_id
		  from good_issue_note_line line,good_issue_note note
		  where  line.line_id=note.id
	)a
	group by product_id,qty_on_hand,product_id,gin_id;


