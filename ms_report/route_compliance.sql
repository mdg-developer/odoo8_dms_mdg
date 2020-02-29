with visit as(
select date::date,sale_team_id,sale_plan_day_id,customer_id,count(customer_id) visit_count from customer_visit where sale_plan_day_id is not null
group by date::date,sale_team_id,sale_plan_day_id,customer_id limit 100
),
visist_plan_actual as(
select v.date,p.name as partner_name,team.code sale_team,b.name branch_name,sum(COALESCE(fre.frequency_count,0)) frequency_count,sum(v.visit_count) visit_count
from sale_plan_day_line pline 
left join visit v on pline.line_id=v.sale_plan_day_id and pline.partner_id = v.customer_id
left join sale_plan_day pday on pday.id =v.sale_plan_day_id
left join res_partner p on v.customer_id=p.id
left join plan_frequency fre on fre.id =p.frequency_id
left join crm_case_section team on team.id = pday.sale_team
left join res_branch b on b.id = pday.branch_id
group by v.date,p.name,team.code,b.name)
select date,partner_name,sale_team,branch_name,frequency_count,visit_count, (frequency_count/visit_count) as compliance_percentage from visist_plan_actual;
;