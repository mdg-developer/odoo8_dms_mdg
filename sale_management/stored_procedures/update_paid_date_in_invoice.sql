--select * from update_paid_date_in_invoice(1128804)
--drop function update_paid_date_in_invoice();

CREATE OR REPLACE FUNCTION update_paid_date_in_invoice(invoice_id integer)
  RETURNS void AS
$BODY$
DECLARE	
	invoice_paid_date date;	
	invoice record;	
	sql text :='select max(date)::date as payment_date
                from
                (
                    select am.date
                    from account_invoice inv,account_move am,account_move_line aml,account_move_reconcile amr
                    where inv.move_id=am.id
                    and am.id=aml.move_id
                    and aml.reconcile_id=amr.id
                    and inv.id=$1
                    union
                    select am.date
                    from account_invoice inv,account_move am,account_move_line aml,account_move_reconcile amr
                    where inv.move_id=am.id
                    and am.id=aml.move_id
                    and aml.reconcile_partial_id=amr.id
                    and inv.id=$2
                )A';
BEGIN	 
	 
	EXECUTE sql into invoice_paid_date USING invoice_id,invoice_id; 
	update account_invoice set paid_date=invoice_paid_date where id=invoice_id;	
		
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
