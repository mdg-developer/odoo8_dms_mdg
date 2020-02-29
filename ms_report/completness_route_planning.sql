with assign_outlets as(
select pday.id sale_plan_day,p.id as partner_id,inv.id as invoice_id,inv.date_invoice,pday.sale_team,COALESCE(fre.frequency_count,0) frequency_count,inv.branch_id,inv.city,p.name as partner_name 
from mobile_sale_order ms
left join sale_order s on ms.name=s.tb_ref_no
left join account_invoice inv on inv.origin = s.name
left join sale_plan_day pday on pday.id =ms.sale_plan_day_id
left join sale_plan_day_line dayline on dayline.line_id = pday.id
left join crm_case_section team on team.id = pday.sale_team 
left join res_partner p on p.id = dayline.partner_id
left join plan_frequency fre on fre.id =p.frequency_id
where inv.state not in ('cancel') and p.frequency_id is not null
limit 5
),
assign_outlets_planned as(
select partner_id,sum(frequency_count) as planned_outlet  from 	 
(select partner_id, sale_plan_day,frequency_count from assign_outlets
	group by partner_id,sale_plan_day,frequency_count) partner_plan group by partner_id
), 
frinal_data as(
select a.partner_name,pt.description,a.date_invoice,team.code sale_team,b.name branch_name,
c.name as city,plan.planned_outlet,count(a.invoice_id) as actual
from assign_outlets a
left join account_invoice_line invline on invline.invoice_id=a.invoice_id
left join product_product p on invline.product_id=p.id
left join product_template pt on pt.id= p.product_tmpl_id
left join crm_case_section team on team.id = a.sale_team 
left join res_branch b on b.id = a.branch_id
left join res_city c on c.id=a.city
left join assign_outlets_planned plan on plan.partner_id=a.partner_id
group by a.partner_name,pt.description,a.date_invoice,team.code,b.name,c.name,plan.planned_outlet)

select partner_name,description,date_invoice,sale_team,branch_name,city,planned_outlet,actual,((actual - planned_outlet) / planned_outlet) * 100 as percentage from frinal_data
;