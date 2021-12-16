-- Function: get_invoice_residual_amount(date,character varying)
-- select * from get_invoice_residual_amount('2021-12-06','INV/2021/000735231')
-- DROP FUNCTION get_invoice_residual_amount(date,character varying);

CREATE OR REPLACE FUNCTION get_invoice_residual_amount(invoice_date date,invoice_number character varying)
  RETURNS numeric AS
$BODY$
  DECLARE
    balance numeric;    
  BEGIN

	select COALESCE (sum(A.payment_amount),0) into balance
	from (
	select  av.origin,av.section_id,payment_full.move_id ,payment_full.id move_line_id,av.number,av.partner_id,av.date_invoice,paidmove.date,aml.reconcile_id,aml.id,payment_full.ref,coalesce(payment_full.credit,0) as payment_amount
	,avl.amount_original invoice_amount,(avl.amount_unreconciled-avl.amount) as balance
	from account_invoice av 
	left join account_move am  on av.move_id =am.id
	left join account_move_line aml on aml.move_id=am.id and aml.reconcile_id is not null
	left join account_voucher_line avl on avl.move_line_id=aml.id and avl.amount >0
	left join account_voucher avr on avr.id=avl.voucher_id 
	left join account_move paidmove on paidmove.id= avr.move_id
	left join account_move_reconcile amr on amr.id=aml.reconcile_id 
	left join account_move_line payment_full on payment_full.reconcile_id=amr.id  and  payment_full.move_id =paidmove.id 
	where av.state not in ('draft''cancel')
	and aml.id not in (payment_full.id)
	and payment_full.move_id !=am.id
	and av.type='out_invoice'
	and av.amount_total !=av.residual

	and paidmove.date >invoice_date
	and av.number=invoice_number
	
	union all 
	select av.origin,av.section_id,payment_partial.move_id,payment_partial.id move_line_id,av.number,av.partner_id,av.date_invoice,paidmove.date,aml.reconcile_id,aml.id,payment_partial.ref,coalesce(payment_partial.credit,0) as payment_amount,avl.amount_original invoice_amount,
	(avl.amount_unreconciled-avl.amount) as balance
	from account_invoice av 
	left join account_move am  on av.move_id =am.id
	left join account_move_line aml on aml.move_id=am.id and aml.reconcile_partial_id is not null
	left join account_voucher_line avl on avl.move_line_id=aml.id and avl.amount >0
	left join account_voucher avr on avr.id=avl.voucher_id 
	left join account_move paidmove on paidmove.id= avr.move_id
	left join account_move_reconcile amp on amp.id=aml.reconcile_partial_id
	left join account_move_line payment_partial on payment_partial.reconcile_partial_id=amp.id and  payment_partial.move_id =paidmove.id 
	 where av.state not in ('draft','cancel')
	and aml.id not in (payment_partial.id)
	and payment_partial.move_id !=am.id
	and av.amount_total !=av.residual
	and paidmove.date >invoice_date
	and av.number=invoice_number
	and av.type='out_invoice'
	)A;

   return balance;
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;