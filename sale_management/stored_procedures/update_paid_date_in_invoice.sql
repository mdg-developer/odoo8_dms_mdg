--select * from update_paid_date_in_invoice(1128804)
--drop function update_paid_date_in_invoice();

CREATE OR REPLACE FUNCTION update_paid_date_in_invoice(invoice_id integer)
  RETURNS void AS
$BODY$
DECLARE	
	invoice_paid_date date;	
	invoice record;	
	sql text :='select max(A.date)::date as payment_date
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
				where aml.id not in (payment_full.id)
				and payment_full.move_id !=am.id
				and av.id=$1
				union all 
				select av.origin,av.section_id,payment_partial.move_id,payment_partial.id move_line_id,av.number,av.partner_id,av.date_invoice,paidmove.date,aml.reconcile_id,aml.id,payment_partial.ref,coalesce(payment_partial.credit,0) as payment_amount,avl.amount_original invoice_amount,(avl.amount_unreconciled-avl.amount) as balance
				from account_invoice av 
				left join account_move am  on av.move_id =am.id
				left join account_move_line aml on aml.move_id=am.id and aml.reconcile_partial_id is not null
				left join account_voucher_line avl on avl.move_line_id=aml.id and avl.amount >0
				left join account_voucher avr on avr.id=avl.voucher_id 
				left join account_move paidmove on paidmove.id= avr.move_id
				left join account_move_reconcile amp on amp.id=aml.reconcile_partial_id
				left join account_move_line payment_partial on payment_partial.reconcile_partial_id=amp.id and  payment_partial.move_id =paidmove.id 
				where aml.id not in (payment_partial.id)
				and payment_partial.move_id !=am.id
				and av.id=$2
				)A,account_move am,account_journal aj,crm_case_section crm,res_partner rp
				where  A.move_id =am.id
				and am.journal_id = aj.id
				and A.section_id =crm.id
				and A.partner_id =rp.id';
BEGIN	 
	 
	EXECUTE sql into invoice_paid_date USING invoice_id,invoice_id; 
	update account_invoice set paid_date=invoice_paid_date where id=invoice_id;	
		
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
