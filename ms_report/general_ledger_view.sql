-- View: general_ledger_view;
-- select * from general_ledger_view;
-- DROP VIEW general_ledger_view;

CREATE OR REPLACE VIEW general_ledger_view
 AS
	select aml.date,ap.name period,am.state status,
	((am.write_date at time zone 'utc' )at time zone 'asia/rangoon')::date closed_on,
	am.name entry,aj.code journal_code,(select code from account_account where id=aa.parent_id) parent_account,
	(select name from account_account where id=aa.parent_id) parent_description,aa.type internal_type,
	aat.name account_type,aa.active,centralized,aa.code account,aa.name account_description,aml.note account_internal_notes,
	aaa.name analytic_account,rp.name partner,aj.name journal,
	(select name from res_partner rp,res_users ru where rp.id=ru.partner_id and ru.id=am.create_uid) responsible,
	rb.name branch,am.ref reference,aml.name as label,concat(aa.code,'-',aa.name) counter_part,debit,credit,
	(sum(debit-credit) OVER (ORDER BY aml.date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)) balance
	from account_move am
	left join account_move_line aml on (am.id=aml.move_id)
	left join account_period ap on (am.period_id=ap.id)
	left join account_journal aj on (am.journal_id=aj.id)
	left join account_account aa on (aml.account_id=aa.id)
	left join account_account_type aat on (aa.user_type=aat.id)
	left join res_partner rp on (aml.partner_id=rp.id)
	left join account_analytic_account aaa on (aml.analytic_account_id=aaa.id)
	left join res_branch rb on (aml.branch_id=rb.id)	
	order by aml.date;