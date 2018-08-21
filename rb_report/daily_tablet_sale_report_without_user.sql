-- Table: public.daily_sale_temp
-- select * from daily_sale_temp
-- DROP TABLE public.daily_sale_temp;
-- committed_date(21-08-2018) //add product_category for storeprocedure error
CREATE TABLE public.daily_sale_temp
(
  date date,
  vr_no character varying,
  customer_code character varying,
  customerid integer,
  customer character varying,
  product character varying,
  product_uos_qty double precision,
  price_unit double precision,
  sub_total double precision,
  discount double precision,
  discount_amt double precision,
  net_total double precision,
  sale_group character varying,
  m_status character varying,
  type character varying,
  township character varying,
  village character varying,
  city character varying,
  channel character varying,
  territory character varying,
  state character varying,
  delivery_remark character varying,
  additional_discount double precision,
  sale_plan_day_name character varying,
  sale_plan_trip_name character varying,
  void character varying,
  id integer,
  product_code character varying,
  branch character varying,
  main_group character varying,
  product_category character varying
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.daily_sale_temp
  OWNER TO openerp;

  
-- Function: public.daily_sale_report_without_user(date, date, integer, integer, integer)
-- select * from daily_sale_report_without_user('2018-07-01','2018-07-02',null,null,null,1)
-- DROP FUNCTION public.daily_sale_report_without_user(date, date, integer, integer, integer,integer);
-- committed_date(21-08-2018)//binding brand and branch by user_id // add discount_amount and net_total column
CREATE OR REPLACE FUNCTION public.daily_sale_report_without_user(
    IN from_date date,
    IN to_date date,
    IN m_group integer,
    IN param_branch integer,
    IN param_team integer,
    IN usr_id integer)
  RETURNS TABLE(date date, vr_no character varying, customer_code character varying, customerid integer, customer character varying, 
product character varying, product_uos_qty double precision, price_unit double precision,sub_total double precision, discount double precision,
discount_amt double precision,net_total double precision,sale_group character varying, m_status character varying, type character varying, 
township character varying, village character varying,city character varying, channel character varying, territory character varying, 
state character varying, delivery_remark character varying,additional_discount double precision, sale_plan_day_name character varying, 
sale_plan_trip_name character varying,void character varying,vid integer,product_code character varying, branch character varying, 
main_group character varying, product_category character varying) AS
$BODY$
DECLARE 
data_record record;
up_record record;

Begin
  delete from daily_sale_temp;

for data_record in  select (s.date+ '6 hour'::interval + '30 minutes'::interval)::date as date,s.name as vr_no,s.customer_code,r.id as customerid,r.name as customer , p.name_template as product,l.product_uos_qty,l.price_unit as sprice_unit,l.sub_total,
l.discount,l.discount_amt,(l.price_unit *l.product_uos_qty) as net_total,c.name as sale_group ,s.m_status,s.type ,tp.name as township,r.village as village,ci.name as city,sc.name as channel, rs.name as state,s.delivery_remark ,s.additional_discount,
s.void_flag,p.default_code as product_code,branch.name as branch,pm.name as main_group,pc.name as product_category
from mobile_sale_order s
left join mobile_sale_order_line l  on s.id = l.order_id 
left join product_product p on l.product_id = p.id
left join product_template t on p.product_tmpl_id = t.id
left join product_maingroup pm on t.main_group=pm.id
left join product_category pc on t.categ_id=pc.id
left join res_partner r on s.partner_id = r.id
left join tablets_information tb on tb.id = s.tablet_id
left join crm_case_section c on tb.sale_team_id = c.id
left join res_country_state rs on r.state_id = rs.id 
left join sale_channel sc on sc.id = r.sales_channel
left join res_branch branch on branch.id=r.branch_id
left join res_city ci on r.city = ci.id
left join res_township  tp on  r.township = tp.id
where (s.date+ '6 hour'::interval + '30 minutes'::interval)::date between from_date and to_date
and t.main_group in (select mrel.main_group from res_main_group_rel mrel where mrel.user_id=usr_id)
and c.id in(select trel.team_id from res_sale_teams_rel trel where trel.user_id=usr_id)	
and branch.id in (select brel.bid from res_branch_users_rel brel where brel.user_id=usr_id)		
loop
insert into daily_sale_temp(date,vr_no,customer_code,customerid,customer,product,product_uos_qty,price_unit,sub_total,discount,
discount_amt,net_total,sale_group,m_status,type,township,village ,city,channel, state,delivery_remark,additional_discount,
sale_plan_day_name ,sale_plan_trip_name,void,product_code,branch,main_group,product_category)
values(data_record.date,data_record.vr_no,data_record.customer_code,data_record.customerid,data_record.customer,
data_record.product,data_record.product_uos_qty,data_record.sprice_unit,data_record.sub_total,data_record.discount,
data_record.discount_amt,data_record.net_total,data_record.sale_group,data_record.m_status ,data_record.type,data_record.township ,
data_record.village,data_record.city,data_record.channel,data_record.state,data_record.delivery_remark,data_record.additional_discount,
'','',data_record.void_flag,data_record.product_code,data_record.branch,data_record.main_group,data_record.product_category);
end loop;

	--update sale_plan_day 
	for up_record 
	in 
	  select  spd.name sday,mso.name as mso_name 
	  from mobile_sale_order mso,sale_plan_day spd 
	  where 
	  --mso.sale_plan_day_id is not null and 
	  spd.id = mso.sale_plan_day_id 
	 

	loop
	update daily_sale_temp dtemp
	set sale_plan_day_name = up_record.sday
	where dtemp.vr_no = up_record.mso_name;
	end loop;

	--update sale_plan_trip 
	--select * from daily_sale_temp t ,mobile_sale_order m where t.vr_no = m. name
	for up_record 
	in 
	  select spt.name as tname,mso.name as mso_name 
	  from mobile_sale_order mso,sale_plan_trip spt 
	  where  
	  --mso.sale_plan_trip_id is not null and 
	  spt.id = mso.sale_plan_trip_id
        --select * from daily_sale_temp
	loop
	update daily_sale_temp dtemp
	set sale_plan_trip_name = up_record.tname 
	where dtemp.vr_no = up_record.mso_name;
	end loop;

update daily_sale_temp dst
set   price_unit = null
where dst.price_unit= 0;

update daily_sale_temp dst
set   discount = null
where dst.discount= 0;

update daily_sale_temp dst
set   sub_total = null
where dst.sub_total= 0;

update daily_sale_temp dst
set   additional_discount = null
where dst.additional_discount= 0;


update daily_sale_temp dst set void='Unvoid' where dst.void like 'none';
update daily_sale_temp dst set void='Voided' where dst.void like 'voided';

	IF m_group IS NULL AND param_branch IS NULL AND param_team IS NULL THEN
		return  query select * from daily_sale_temp ds;
	ELSEIF m_group IS NOT NULL AND param_branch IS NULL AND param_team IS NULL THEN
		return  query select ds.* from daily_sale_temp ds,product_product pp,product_template pt where ds.product_code=pp.default_code and pp.product_tmpl_id=pt.id and pt.main_group=m_group;
	ELSEIF m_group IS NULL AND param_branch IS NOT NULL AND param_team IS NOT NULL THEN
		return  query select ds.* from daily_sale_temp ds,res_partner res,crm_case_section cs where ds.customerid=res.id and ds.sale_group=cs.code and res.branch_id=param_branch and cs.id=param_team;
	ELSEIF m_group IS NULL AND param_branch IS NOT NULL AND param_team IS NULL THEN
		return  query select ds.* from daily_sale_temp ds,res_partner res where ds.customerid=res.id and res.branch_id=param_branch;
	ELSEIF m_group IS NULL AND param_branch IS NULL AND param_team IS NOT NULL THEN
		return  query select ds.* from daily_sale_temp ds,crm_case_section cs where ds.sale_group=cs.code and cs.id=param_team;
	ELSEIF m_group IS NOT NULL AND param_branch IS NOT NULL AND param_team IS NULL THEN
		return  query select ds.* from daily_sale_temp ds,res_partner res,product_product pp,product_template pt where ds.customerid=res.id and ds.product_code=pp.default_code and pp.product_tmpl_id=pt.id and pt.main_group=m_group and res.branch_id=param_branch;
	ELSEIF m_group IS NOT NULL AND param_branch IS NULL AND param_team IS NOT NULL THEN
		return  query select ds.* from daily_sale_temp ds,crm_case_section cs,res_partner res,product_product pp,product_template pt where ds.customerid=res.id and ds.sale_group=cs.code and ds.product_code=pp.default_code and pp.product_tmpl_id=pt.id and pt.main_group=m_group and cs.id=param_team;
	ELSEIF m_group IS NOT NULL AND param_branch IS NOT NULL AND param_team IS NOT NULL THEN
		return  query select ds.* 
		from daily_sale_temp ds,crm_case_section cs,
		res_partner res,product_product pp,product_template pt 
		where ds.customerid=res.id and ds.product_code=pp.default_code and ds.sale_group=cs.code
		and pp.product_tmpl_id=pt.id and pt.main_group=m_group and res.branch_id=param_branch and cs.id=param_team;						
	END IF;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION public.daily_sale_report_without_user(date, date, integer, integer, integer, integer)
  OWNER TO openerp;

------------ old -------------------------------------------
-- Function: daily_sale_report_without_user(date, date, integer, integer)
-- DROP FUNCTION daily_sale_report_without_user(date, date, integer, integer);
CREATE OR REPLACE FUNCTION daily_sale_report_without_user(IN from_date date, IN to_date date, IN m_group integer, IN param_branch integer)
  RETURNS TABLE(date date, vr_no character varying, customer_code character varying, customerid integer, customer character varying, product character varying, product_uos_qty double precision, price_unit double precision, discount double precision, sub_total double precision, sale_group character varying, m_status character varying, type character varying, township character varying, village character varying, city character varying, channel character varying, territory character varying, state character varying, delivery_remark character varying, additional_discount double precision, sale_plan_day_name character varying, sale_plan_trip_name character varying, void character varying, vid integer, product_code character varying, branch character varying, main_group character varying) AS
$BODY$
DECLARE 
data_record record;
up_record record;

Begin
  delete from daily_sale_temp;

for data_record in  select (s.date+ '6 hour'::interval + '30 minutes'::interval)::date as date,s.name as vr_no,s.customer_code,r.id as customerid,r.name as customer , p.name_template as product,l.product_uos_qty,l.price_unit as sprice_unit,l.discount,
l.sub_total,c.name as sale_group ,s.m_status,s.type ,tp.name as  township,ci.name as city,sc.name as channel, rs.name as state,s.delivery_remark ,s.additional_discount,s.void_flag,p.default_code as product_code,branch.name as branch,pm.name as main_group
from mobile_sale_order s
left join mobile_sale_order_line l  on s.id = l.order_id 
left join product_product p on l.product_id = p.id
left join product_template t on p.product_tmpl_id = t.id
left join product_maingroup pm on t.main_group=pm.id
left join res_partner r on s.partner_id = r.id
left join tablets_information tb on tb.id = s.tablet_id
left join crm_case_section c on tb.sale_team_id = c.id
left join res_country_state rs on r.state_id = rs.id 
left join sale_channel sc on sc.id = r.sales_channel
left join res_branch branch on branch.id=r.branch_id
left join res_city ci on r.city = ci.id
left join res_township  tp on  r.township = tp.id
where (s.date+ '6 hour'::interval + '30 minutes'::interval)::date between from_date and to_date
						
loop
insert into daily_sale_temp(date,vr_no,customer_code,customerid,customer,product,product_uos_qty,price_unit,discount,sub_total,sale_group,m_status ,
type,township ,city,channel, state,delivery_remark,additional_discount,sale_plan_day_name ,sale_plan_trip_name,void,product_code,branch,main_group)
values(data_record.date,data_record.vr_no,data_record.customer_code,data_record.customerid,data_record.customer,data_record.product,data_record.product_uos_qty,
data_record.sprice_unit,data_record.discount,data_record.sub_total,data_record.sale_group,data_record.m_status ,data_record.type,
data_record.township ,data_record.city,data_record.channel,
data_record.state,data_record.delivery_remark,data_record.additional_discount,'','',data_record.void_flag,data_record.product_code,data_record.branch,data_record.main_group);
end loop;

	--update sale_plan_day 
	for up_record 
	in 
	  select  spd.name sday,mso.name as mso_name 
	  from mobile_sale_order mso,sale_plan_day spd 
	  where 
	  --mso.sale_plan_day_id is not null and 
	  spd.id = mso.sale_plan_day_id 
	 

	loop
	update daily_sale_temp dtemp
	set sale_plan_day_name = up_record.sday
	where dtemp.vr_no = up_record.mso_name;
	end loop;

	--update sale_plan_trip 
	--select * from daily_sale_temp t ,mobile_sale_order m where t.vr_no = m. name
	for up_record 
	in 
	  select spt.name as tname,mso.name as mso_name 
	  from mobile_sale_order mso,sale_plan_trip spt 
	  where  
	  --mso.sale_plan_trip_id is not null and 
	  spt.id = mso.sale_plan_trip_id
        --select * from daily_sale_temp
	loop
	update daily_sale_temp dtemp
	set sale_plan_trip_name = up_record.tname 
	where dtemp.vr_no = up_record.mso_name;
	end loop;

update daily_sale_temp dst
set   price_unit = null
where dst.price_unit= 0;

update daily_sale_temp dst
set   discount = null
where dst.discount= 0;

update daily_sale_temp dst
set   sub_total = null
where dst.sub_total= 0;

update daily_sale_temp dst
set   additional_discount = null
where dst.additional_discount= 0;


update daily_sale_temp dst set void='Unvoid' where dst.void like 'none';
update daily_sale_temp dst set void='Voided' where dst.void like 'voided';

	IF m_group IS NULL AND param_branch IS NULL THEN
		return  query select * from daily_sale_temp ds;
	ELSEIF m_group IS NOT NULL AND param_branch IS NULL THEN
		return  query select ds.* from daily_sale_temp ds,product_product pp,product_template pt where ds.product_code=pp.default_code and pp.product_tmpl_id=pt.id and pt.main_group=m_group;
	ELSEIF m_group IS NULL AND param_branch IS NOT NULL THEN
		return  query select ds.* from daily_sale_temp ds,res_partner res where ds.customerid=res.id and res.branch_id=param_branch;
	ELSEIF m_group IS NOT NULL AND param_branch IS NOT NULL THEN
		return  query select ds.* from daily_sale_temp ds,res_partner res,product_product pp,product_template pt where ds.customerid=res.id and ds.product_code=pp.default_code and pp.product_tmpl_id=pt.id and pt.main_group=m_group and res.branch_id=param_branch;		
	END IF;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION daily_sale_report_without_user(date, date, integer, integer)
  OWNER TO openerp;

