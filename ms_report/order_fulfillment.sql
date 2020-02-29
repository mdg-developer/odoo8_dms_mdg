select rp.name customer,rp.customer_code,so.name sale_order,inv.number invoice_number,
rb.name branch,ccs.name sales_team,
date_invoice invoice_date,date_order::date sale_order_date,
date_invoice-(date_order::date) diff_days
from account_invoice inv
left join sale_order so on (inv.origin=so.name)
left join res_partner rp on (inv.partner_id=rp.id)
left join res_branch rb on (inv.branch_id=rb.id)
left join crm_case_section ccs on (inv.section_id=ccs.id)
where inv.state not in ('draft','cancel')
and inv.type='out_invoice'