CREATE OR REPLACE VIEW public.summary_of_key_reasons_for_no_visit AS 

select customer_visit.id,customer_visit.customer_name,customer_code,township,branch,customer_visit.visit_reason,SalePlanDay,SalePlanTrip,customer_visit.date as visit_date,other_reason,effective.Effective_Customer,effective.date_invoice,effective.InvoiceNo from
(
select partner.name as customer_name,township.name as township ,partner.customer_code,branch.name as branch ,cv.visit_reason,(select name  from sale_plan_day where id = cv.sale_plan_day_id)SalePlanDay,
(select name  from sale_plan_trip where id = cv.sale_plan_trip_id)SalePlanTrip,cv.other_reason,cv.id,cv.sale_team_id,cv.branch_id, cv.customer_id,cv.date::date 
from customer_visit cv,crm_case_section ccs,res_township township,res_partner partner,res_branch branch
where ccs.id=cv.sale_team_id
and partner.id=cv.customer_id
and cv.township_id =township.id
and branch.id =cv.branch_id 
group by cv.sale_team_id,cv.branch_id,cv.date,cv.customer_id,cv.visit_reason,cv.id, partner.name ,township.name,partner.customer_code,branch.name
)customer_visit
left join 
(
select inv.section_id,inv.branch_id,ccs.name team,inv.partner_id,inv.date_invoice ,partner.name as  Effective_Customer,inv.number as InvoiceNo
from account_invoice inv,crm_case_section ccs ,res_partner partner
where inv.section_id=ccs.id
and inv.partner_id=partner.id
and inv.state not in ('cancel')

group by inv.section_id,ccs.id,inv.branch_id,inv.date_invoice,inv.partner_id,partner.name,inv.number
)effective 
on customer_visit.date=effective.date_invoice 
and effective.partner_id =customer_visit.customer_id;

ALTER TABLE public.summary_of_key_reasons_for_no_visit
  OWNER TO odoo;




