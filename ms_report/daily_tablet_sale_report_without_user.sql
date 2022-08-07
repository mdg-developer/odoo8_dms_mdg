-- Function: daily_sale_report_without_user(date, date)

-- DROP FUNCTION daily_sale_report_without_user(date, date);

CREATE OR REPLACE FUNCTION daily_sale_report_without_user(IN from_date date, IN to_date date)
  RETURNS TABLE(date date, vr_no character varying, customer_code character varying, customerid integer, customer character varying, product character varying, product_uos_qty double precision, price_unit double precision, discount double precision, sub_total double precision, sale_group character varying, m_status character varying, type character varying, township character varying, channel character varying, territory character varying, state character varying, delivery_remark character varying, additional_discount double precision, sale_plan_day_name character varying, sale_plan_trip_name character varying, void character varying, vid integer, product_code character varying) AS
$BODY$
DECLARE 
data_record record;
up_record record;

Begin
  delete from daily_sale_temp;

  --delete from temp_table1;
  ---first five field


for data_record in  select s.date as date,s.name as vr_no,s.customer_code,r.id as customerid,r.name as customer , p.name_template as product,l.product_uos_qty,l.price_unit as sprice_unit,l.discount,
l.sub_total,c.name as sale_group ,s.m_status,s.type ,rt.name as township ,sc.name as channel, rs.name as state,s.delivery_remark ,s.additional_discount,s.void_flag,p.default_code as product_code
from mobile_sale_order s
left join mobile_sale_order_line l  on s.id = l.order_id 
left join product_product p on l.product_id = p.id
left join product_template t on p.product_tmpl_id = t.id
left join res_partner r on s.partner_id = r.id
left join res_township rt on r.township=rt.id
left join tablets_information tb on tb.id = s.tablet_id
left join crm_case_section c on tb.sale_team_id = c.id
left join res_country_state rs on r.state_id = rs.id 
left join sale_channel sc on sc.id = r.sales_channel
where s.date::date between from_date and to_date
						
loop
insert into daily_sale_temp(date,vr_no,customer_code,customerid,customer,product,product_uos_qty,price_unit,discount,sub_total,sale_group,m_status ,
type,township ,channel, state,delivery_remark,additional_discount,sale_plan_day_name ,sale_plan_trip_name,void,product_code)
values(data_record.date,data_record.vr_no,data_record.customer_code,data_record.customerid,data_record.customer,data_record.product,data_record.product_uos_qty,
data_record.sprice_unit,data_record.discount,data_record.sub_total,data_record.sale_group,data_record.m_status ,data_record.type,
data_record.township ,data_record.channel,
data_record.state,data_record.delivery_remark,data_record.additional_discount,'','',data_record.void_flag,data_record.product_code);
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
	
	return  query select * from daily_sale_temp ds ;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION daily_sale_report_without_user(date, date)
  OWNER TO openerp;


  
  -- Function: daily_sale_report_without_user(date, date, integer)

-- DROP FUNCTION daily_sale_report_without_user(date, date, integer);

CREATE OR REPLACE FUNCTION daily_sale_report_without_user(IN from_date date, IN to_date date, IN m_group integer)
  RETURNS TABLE(date date, vr_no character varying, customer_code character varying, customerid integer, customer character varying, product character varying, product_uos_qty double precision, price_unit double precision, discount double precision, sub_total double precision, sale_group character varying, m_status character varying, type character varying, township character varying, channel character varying, territory character varying, state character varying, delivery_remark character varying, additional_discount double precision, sale_plan_day_name character varying, sale_plan_trip_name character varying, void character varying, vid integer, product_code character varying) AS
$BODY$
DECLARE 
data_record record;
up_record record;

Begin
  delete from daily_sale_temp;

  --delete from temp_table1;


if m_group is null then
		EXECUTE 'select * from daily_sale_report_without_user($1,$2)' using from_date,to_date;
end if;

for data_record in  select s.date as date,s.name as vr_no,s.customer_code,r.id as customerid,r.name as customer , p.name_template as product,l.product_uos_qty,l.price_unit as sprice_unit,l.discount,
l.sub_total,c.name as sale_group ,s.m_status,s.type ,rt.name as township ,sc.name as channel, rs.name as state,s.delivery_remark ,s.additional_discount,s.void_flag,p.default_code as product_code
from mobile_sale_order s
left join mobile_sale_order_line l  on s.id = l.order_id 
left join product_product p on l.product_id = p.id
left join product_template t on p.product_tmpl_id = t.id
left join product_maingroup pm on t.main_group=pm.id
left join res_partner r on s.partner_id = r.id
left join res_township rt on r.township=rt.id
left join tablets_information tb on tb.id = s.tablet_id
left join crm_case_section c on tb.sale_team_id = c.id
left join res_country_state rs on r.state_id = rs.id 
left join sale_channel sc on sc.id = r.sales_channel
where s.date::date between from_date and to_date
and pm.id=m_group
						
loop
insert into daily_sale_temp(date,vr_no,customer_code,customerid,customer,product,product_uos_qty,price_unit,discount,sub_total,sale_group,m_status ,
type,township ,channel, state,delivery_remark,additional_discount,sale_plan_day_name ,sale_plan_trip_name,void,product_code)
values(data_record.date,data_record.vr_no,data_record.customer_code,data_record.customerid,data_record.customer,data_record.product,data_record.product_uos_qty,
data_record.sprice_unit,data_record.discount,data_record.sub_total,data_record.sale_group,data_record.m_status ,data_record.type,
data_record.township ,data_record.channel,
data_record.state,data_record.delivery_remark,data_record.additional_discount,'','',data_record.void_flag,data_record.product_code);
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
	
	return  query select * from daily_sale_temp ds ;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION daily_sale_report_without_user(date, date, integer)
  OWNER TO openerp;

   
  
-- Table: daily_sale_temp

-- DROP TABLE daily_sale_temp;

CREATE TABLE daily_sale_temp
(
  date date,
  vr_no character varying,
  customer_code character varying,
  customerid integer,
  customer character varying,
  product character varying,
  product_uos_qty double precision,
  price_unit double precision,
  discount double precision,
  sub_total double precision,
  sale_group character varying,
  m_status character varying,
  type character varying,
  township character varying,
  channel character varying,
  territory character varying,
  state character varying,
  delivery_remark character varying,
  additional_discount double precision,
  sale_plan_day_name character varying,
  sale_plan_trip_name character varying,
  void character varying,
  id serial NOT NULL,
  product_code character varying,
  CONSTRAINT report_temp6_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE daily_sale_temp
  OWNER TO openerp;