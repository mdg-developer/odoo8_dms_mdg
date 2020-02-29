
CREATE OR REPLACE VIEW public.inactive_customer_status AS 

select res.id,customer_code,res.name as customer_name,case when res.active=True then 'True' when res.active=False then 'False' end as active,
case when res.mobile_customer=True then 'True' when res.mobile_customer=False then 'False' end as mobile_customer,array_to_string(array_agg(distinct rpc.name),', ') AS tags,
case when res.active=True and mobile_customer=True then 'Pending' 
when res.active=True and mobile_customer=False then 'Registered' 
when res.active=False  then 'Inactive' 
end as customer_status,
array_to_string(array_agg(distinct ccs.name),', ') AS sales_team,rt.code township,street,display_name,outlet.name outlet
from res_partner res,sale_team_customer_rel rel,res_township rt,crm_case_section ccs,res_partner_res_partner_category_rel crel,res_partner_category rpc,
outlettype_outlettype outlet
where res.id=rel.partner_id 
and res.township=rt.id
and rel.sale_team_id=ccs.id
and rpc.id=crel.category_id
and res.id=crel.partner_id
and outlet.id=res.outlet_type
and res.id not in (
select partner_id
from account_invoice 
where date_invoice between current_date-90 and current_date 
group by partner_id
)
group by res.id,customer_code,res.name,res.active,mobile_customer,res.active,rt.code ,street,display_name,outlet.name
order by customer_code;

ALTER TABLE public.inactive_customer_status
  OWNER TO odoo;