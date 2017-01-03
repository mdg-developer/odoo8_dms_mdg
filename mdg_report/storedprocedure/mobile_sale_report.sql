-- Function: saleorder_report_without_user(date, date, integer, integer)

-- DROP FUNCTION saleorder_report_without_user(date, date, integer, integer);

CREATE OR REPLACE FUNCTION saleorder_report_without_user(IN from_date date, IN to_date date, IN m_group integer, IN param_branch integer)
  RETURNS TABLE(order_id character varying, customer character varying, customer_code character varying, branch_code character varying, saleplanname character varying, saleplanday character varying, saleplantrip character varying, warehouse character varying, sale_date character varying, paymenttype character varying, deliverremark character varying, totalamount numeric, totaldiscount numeric, discount numeric, deductionamount numeric, product character varying, quantity numeric, sale_team character varying, salemanname character varying, location_name character varying, paid_amount numeric, paid character varying, void character varying, subtotal numeric, voucher character varying, unit_price numeric, tablet character varying, visit_reason character varying, grand_total double precision, promotion_line character varying, product_id integer, main_group character varying, vid integer) AS
$BODY$
DECLARE 
data_record record;
sale_record record;
pm_id numeric;
Begin
  delete from report_temp1;

	for data_record in 
	
	select * from
	(select * from
	(select * from
	(select * From 
	(select * from 
	(select * from 
	(select * from 
	(select * from 
	(select * from 
	(select * from
	(select * from
	(select * from 
	(select * from 
	(select msol.product_id,
		msol.sub_total,
		msol.discount,
		msol.price_unit,
		msol.product_uos_qty,
		mso.id as mobil_sale_id,
		mso.partner_id as mos_partner_id,
		mso.sale_plan_day_id,
		mso.customer_code,
		mso.sale_plan_trip_id,
		mso.paid,mso.warehouse_id,
		mso.date,mso.delivery_remark,
		mso.deduction_amount,
		mso.user_id,
		mso.tablet_id,
		mso.name as order_id,
		mso.location_id,
		mso.amount_total - mso.deduction_amount as grand,
		mso.paid,
		mso.void_flag,
		mso.paid_amount,
		mso.sale_plan_name,
		mso.additional_discount,
		mso.amount_total,
		mso.type as payment_type,
		mso.m_status ,
		mso.void_flag,
		mso.sale_team,pm.name as main_group
		from mobile_sale_order mso
		left join mobile_sale_order_line msol on mso.id=msol.order_id
                left join product_product pp on pp.id= msol.product_id
		left join product_template pt on pt.id= pp.product_tmpl_id
                left join product_maingroup pm on pt.main_group=pm.id where from_date<=(mso.date+ '6 hour'::interval + '30 minutes'::interval)::date and (mso.date+ '6 hour'::interval + '30 minutes'::interval)::date<=to_date)A 
		left join (select id ,name,branch_id from res_partner)B on A.mos_partner_id = B.id)C 
		left join (select id ,name as branch_code from sale_branch)D on C.branch_id=D.id)E 
		left join (select id,name as sale_plan_day from sale_plan_day )F on E.sale_plan_day_id=F.id)G 
		left join (select id ,name as sale_plan_trip from sale_plan_trip)H on G.sale_plan_trip_id = H.id)I 
		left join (select id,name as warehouse_name from stock_warehouse)J on I.warehouse_id=J.id)K 
		left join (select id,name_template product_name from product_product )L on K.product_id=L.id)M 
		left join (select id,name as sale_team_name from crm_case_section)N on M.sale_team=N.id)O 
		left join (select ru.id, rp.name as sale_man_name from res_users ru,res_partner rp where rp.id=ru.partner_id)P on O.user_id=P.id)R 
		left join (select id,name as customer_name from res_partner) S on R.mos_partner_id =S.id )X 
		left join (select a.id as locate_id , b.name||'/'|| a.name as location_name From stock_location a ,stock_location b where a.location_id=b.id)Z on Z.locate_id=X.location_id)E
		left join (select id,name as tablet_name from tablets_information)T on E.tablet_id=T.id)JJ)J1
		left join  (select   U.promo_line_id ,string_agg (V.name,',') promotion_name from mso_promotion_line U inner join 
		 mobile_sale_order  J1
		 on U.promo_line_id= J1.id inner join
		 promos_rules  V 
		 on V.id= U.pro_id
		 group by   U.promo_line_id )U on U.promo_line_id=J1.mobil_sale_id
	
	loop
	insert into report_temp1(product_id,main_group,order_id ,
	customer,
	customer_code ,
	branch_code ,
	saleplanname,
	saleplanday,
	saleplantrip ,
	warehouse ,
	sale_date,
	paymenttype ,
	deliverremark ,
	totaldiscount,
	totalamount,
	discount ,
	deductionamount,
	product,
	quantity ,
	sale_team ,
	salemanname,
	location_name,
	paid_amount,
	grand_total,
	paid,
	void,
	subtotal,
	voucher,unit_price,
	tablet,visit_reason, promotion_line
	)
	values(data_record.product_id,
	data_record.main_group,
	data_record.order_id,
	data_record.customer_name,
	data_record.customer_code,
	data_record.branch_code,
	data_record.sale_plan_name,
	data_record.sale_plan_day,
	data_record.sale_plan_trip,
	data_record.warehouse_name,
	data_record.date,
	data_record.payment_type,
	data_record.delivery_remark,
	data_record.additional_discount,
	data_record.amount_total,
	data_record.discount,
	data_record.deduction_amount,
	data_record.product_name,
	data_record.product_uos_qty,
	data_record.sale_team_name,
	data_record.sale_man_name,data_record.location_name,data_record.paid_amount,data_record.amount_total- data_record.deduction_amount,data_record.paid,data_record.void_flag,data_record.sub_total,'',data_record.price_unit,data_record.tablet_name,'' , data_record.promotion_name);
	end loop;
	
	--update zero as null
	update report_temp1 rt set discount =null where rt.discount::integer=0;
	update report_temp1 rt set totalamount =null where rt.totalamount::integer=0;
	update report_temp1 rt set deductionamount =null where rt.deductionamount::integer=0;
	update report_temp1 rt set quantity =null where rt.quantity::integer=0;
	update report_temp1 rt set totaldiscount =null where rt.totaldiscount::integer=0;
	update report_temp1 rt set subtotal=null where rt.subtotal::integer=0;
	update report_temp1 rt set paid_amount=null where rt.paid_amount::integer=0;
	update report_temp1 rt set unit_price=null where rt.unit_price::integer=0;
	update report_temp1 rt set paid='Yes' where rt.paid like 'true';
	update report_temp1 rt set paid='No' where rt.paid like 'false';
	update report_temp1 rt set void='Unvoid' where rt.void like 'none';
	update report_temp1 rt set void='Voided' where rt.void like 'voided';
	--customer visit they not bought the products
	for data_record in 
	select * from (select * from (select *from (select * from (select * from (select cv.* from customer_visit  cv left join sale_plan_day sd on sd.id=cv.sale_plan_day_id where from_date<=(cv.date+ '6 hour'::interval + '30 minutes'::interval)::date and (cv.date+ '6 hour'::interval + '30 minutes'::interval)::date<=to_date)A 
	left join (select res.id,res.name customer_name,
	-- res.brand,
	branch.name as branch_name from res_partner res,sale_branch branch where res.branch_id=branch.id )B on A.customer_id=B.id)C 
	left join (select id,name as tablet_name from tablets_information)D on D.id=C.tablet_id)E 
	left join (select id,name as sale_team_name from crm_case_section)F on F.id=E.sale_team_id)G
	left join (select id,name as sale_plan_name from sale_plan_day)H on H.id=G.sale_plan_day_id)I
	left join (select id,name as sale_plan_trip_name from sale_plan_trip)J on J.id=I.sale_plan_trip_id
	loop
	insert into report_temp1(order_id ,
													customer,
													customer_code ,
													branch_code ,
													saleplanname,
													saleplanday,
													saleplantrip ,
													warehouse ,
													sale_date,
													paymenttype ,
													deliverremark ,
													totaldiscount,
													totalamount,
													discount ,
													deductionamount,
													product,
													quantity ,
													sale_team ,
													salemanname,
													location_name,
													paid_amount,
													grand_total,
													paid,
													void,
													subtotal,
													voucher,unit_price,
													tablet,visit_reason
	)
	values(data_record.id,data_record.customer_name,data_record.customer_code,data_record.branch_name,data_record.sale_plan_name,data_record.sale_plan_name,data_record.sale_plan_trip_name,'',data_record.date::date,'','',0,0,0,0,'',0,data_record.sale_team_name,'','',0,0,'','',0,'',0,data_record.tablet_name,data_record.visit_reason);	

	end loop;	

	IF m_group IS NULL AND param_branch IS NULL THEN
		return  query select * from report_temp1  order by sale_date,order_id;
	ELSEIF m_group IS NOT NULL AND param_branch IS NULL THEN
		return  query select report.* from report_temp1 report,product_product pp,product_template pt where pp.id=report.product_id and pt.id=pp.product_tmpl_id and pt.main_group=m_group order by sale_date,order_id;
	ELSEIF m_group IS NULL AND param_branch IS NOT NULL THEN
		return  query select * from report_temp1 report where report.branch_code in (select name from sale_branch where id=param_branch) order by sale_date,order_id;
	ELSEIF m_group IS NOT NULL AND param_branch IS NOT NULL THEN
		return  query select report.* from report_temp1 report,product_product pp,product_template pt where pp.id=report.product_id and pt.id=pp.product_tmpl_id and pt.main_group=m_group and report.branch_code=(select name from sale_branch where id=param_branch) order by sale_date,order_id;
	END IF;

	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
  
-- Table: report_temp1

-- DROP TABLE report_temp1;

CREATE TABLE report_temp1
(
  order_id character varying,
  customer character varying,
  customer_code character varying,
  branch_code character varying,
  saleplanname character varying,
  saleplanday character varying,
  saleplantrip character varying,
  warehouse character varying,
  sale_date character varying,
  paymenttype character varying,
  deliverremark character varying,
  totalamount numeric,
  totaldiscount numeric,
  discount numeric,
  deductionamount numeric,
  product character varying,
  quantity numeric,
  sale_team character varying,
  salemanname character varying,
  location_name character varying,
  paid_amount numeric,
  paid character varying,
  void character varying,
  subtotal numeric,
  voucher character varying,
  unit_price numeric,
  tablet character varying,
  visit_reason character varying,
  grand_total double precision,
  promotion_line character varying,
  product_id integer,
  main_group character varying,
  id integer NOT NULL DEFAULT nextval('report_temp1_id_seq1'::regclass),
  CONSTRAINT report_temp1_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);