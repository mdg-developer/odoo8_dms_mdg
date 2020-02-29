CREATE OR REPLACE VIEW public.average_time_spent_per_outlet_visit AS 

select a.*,difference::character varying(64) diff_time,time::character varying(64) original_time from 
(select((cv.date at time zone 'utc') at time zone 'asia/rangoon')::date as date,
cast (cv.date::timestamp
   at time zone 'UTC' at time zone 'asia/rangoon' as time) as time,ti.mac_address tablet_id,
res.name,ccs.name sale_team,spd.name sale_plan_day,cv.visit_reason reason,rt.name township,
case when cv.image is null then 'No'
	 when cv.image is not null  then 'Yes'
end as image,cv.date -LAG(cv.date)OVER (ORDER BY cv.date ) as difference,
cv.other_reason remark
from customer_visit cv
left join res_partner res on res.id = cv.customer_id 
left join crm_case_section ccs on  ccs.id = cv.sale_team_id
left join res_branch rb on rb.id = cv.branch_id
left join sale_plan_day spd on spd.id = cv.sale_plan_day_id
left join tablets_information ti on ti.id=cv.tablet_id
left join res_township rt on rt.id=res.township
where cv.date::date ='2020-02-29'
group by ccs.name,cv.date,ti.mac_address,res.name,spd.name,cv.visit_reason,rt.name,cv.image,cv.other_reason
order by cv.date,ccs.name)a;

ALTER TABLE public.average_time_spent_per_outlet_visit
  OWNER TO odoo;