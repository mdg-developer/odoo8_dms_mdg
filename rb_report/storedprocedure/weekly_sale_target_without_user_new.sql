-- Function: weekly_report_without_user(integer, character varying, integer)

-- DROP FUNCTION weekly_report_without_user(integer, character varying, integer);

CREATE OR REPLACE FUNCTION weekly_report_without_user(IN param_categ_id integer, IN param_week character varying, IN param_sale_team integer)
  RETURNS TABLE(p_id integer, name_tmpl character varying, categ_id integer, categ_name character varying, to_visit integer, p_target_amount numeric, p_t_qty numeric, categ_t_amt numeric, categ_t_qty numeric, act_visit numeric, new_olt_target numeric, new_olt integer, eff_shop integer, categ_v_s numeric, p_v_s numeric, s_date date, p_achi_qty numeric, p_achi_amt numeric, categ_achi_qty numeric, categ_achi_amt numeric, bln numeric) AS
$BODY$
	DECLARE weekly_data record;
	product_data record;
	week_setting_data record;
	target_line_record record;
	categ_achi_record record;
	p_name character varying; 
	param_categ_name character varying;
	effective_count integer;
	customer_visit integer;
	visit_count integer;
	outlet_count numeric;
	product_achieved_amt numeric;
	product_achieved_qty integer;
	
BEGIN
 
	DELETE FROM weekly_temp;


	SELECT from_date,to_date into week_setting_data from setting_week where name = param_week;

	SELECT name into param_categ_name from product_category where product_category.id = param_categ_id;

	FOR product_data 
	IN 
		SELECT pp.id,pp.name_template  from product_product pp,product_template pt where pp.product_tmpl_id = pt.id and pt.categ_id = param_categ_id order by pp.id asc
	LOOP

	FOR weekly_data
	IN
		select date_of_month::date  from (select week_setting_data.from_date::date + sun *'1day'::interval as date_of_month from generate_series(0,(select (week_setting_data.to_date::date  - week_setting_data.from_date::date))) sun )A
	LOOP 
	
	INSERT INTO weekly_temp(product_id,product_name,category_id,category_name,date, shop_to_visit,product_target_amt, category_target_amt,product_target_qty,category_target_qty, actual_visit, new_outlet, categ_vs_qty,product_vs_qty, effective_shop,product_achieve_amount,product_achieve_qty,category_achieve_amount,category_achieve_qty,balance)
	VALUES (product_data.id,product_data.name_template,param_categ_id,param_categ_name,weekly_data.date_of_month,0, 0, 0,0,0,0, 0, 0,0,0,0,0,0,0,0);

	select st.outlet_target,stl.target_amt as product_target_amt,stl.target_qty as product_target_qty ,st.total_shop_to_visit as total_shop_to_visit ,categ_target_amt,categ_target_qty into target_line_record from sale_target_line stl,sale_target st,crm_case_section css,setting_week sw 
	where stl.target_id = st.id and css.id = st.sale_team and sw.id=st.week and st.sale_team = param_sale_team and st.schedule ='weekly' and sw.name=param_week and stl.product_id =product_data.id and st.category_id =param_categ_id group by stl.product_id,stl.target_amt,st.total_shop_to_visit,stl.target_qty,st.outlet_target, categ_target_amt,categ_target_qty;

	update weekly_temp set shop_to_visit = COALESCE(target_line_record.total_shop_to_visit,null), 
	new_outlet_target = COALESCE(target_line_record.outlet_target,null),
	product_target_amt= COALESCE(target_line_record.product_target_amt,null),
	product_target_qty = COALESCE(target_line_record.product_target_qty,null), 
	category_target_amt= COALESCE(target_line_record.categ_target_amt,null),
	category_target_qty = COALESCE(target_line_record.categ_target_qty,null) 
	where product_id = product_data.id;
	
	select count(*) into  effective_count from mobile_sale_order mso,tablets_information ti where mso.date>= week_setting_data.from_date and  mso.date<= week_setting_data.to_date and ti.id = mso.tablet_id and ti.sale_team_id = param_sale_team and mso.void_flag = 'none';
	select count(*) into visit_count from customer_visit cv where (cv.date+ '6 hour'::interval + '30 minutes'::interval)::date = weekly_data.date_of_month and cv.sale_team = param_sale_team;
	raise notice 'visit_count(%)', visit_count;
	select count(*) into outlet_count from res_partner where mobile_customer ='t' and section_id = param_sale_team and create_date::date = weekly_data.date_of_month;

	update weekly_temp set actual_visit = COALESCE(effective_count,null)+COALESCE(visit_count,null), effective_shop = COALESCE(effective_count,null), new_outlet = COALESCE(outlet_count,null) where date = weekly_data.date_of_month and product_id = product_data.id;
	update weekly_temp set effective_shop= null where effective_shop=0;
	update weekly_temp set new_outlet= null where new_outlet=0;

	select sum(msol.product_uos_qty) into product_achieved_qty from mobile_sale_order mso,mobile_sale_order_line msol ,tablets_information ti where mso.id = msol.order_id and ti.id = mso.tablet_id and (mso.date+ '6 hour'::interval + '30 minutes'::interval)::date = weekly_data.date_of_month and ti.sale_team_id = param_sale_team and mso.void_flag = 'none' and msol.product_id = product_data.id;
	select sum(product_uos_qty) as categ_achi_qty ,sum(sub_total) as categ_achi_amt into categ_achi_record from mobile_sale_order_line msol,mobile_sale_order mso , product_product pp, product_template pt,tablets_information ti where msol.product_id = pp.id and pp.product_tmpl_id = pt.id and (mso.date+ '6 hour'::interval + '30 minutes'::interval)::date = weekly_data.date_of_month and msol.order_id = mso.id and pt.categ_id = param_categ_id and ti.id = mso.tablet_id and ti.sale_team_id = param_sale_team;
	select sum(msol.sub_total) into product_achieved_amt from mobile_sale_order mso,mobile_sale_order_line msol ,tablets_information ti where mso.id = msol.order_id and ti.id = mso.tablet_id and ti.sale_team_id = param_sale_team and mso.void_flag = 'none' and (mso.date+ '6 hour'::interval + '30 minutes'::interval)::date = weekly_data.date_of_month and msol.product_id = product_data.id;

	update weekly_temp set product_achieve_amount=COALESCE(product_achieved_amt,null),
	product_achieve_qty = COALESCE(product_achieved_qty,null) , 
	product_vs_qty = (COALESCE(product_achieved_qty,null)/target_line_record.product_target_qty::float)*100,
	category_achieve_amount=COALESCE(categ_achi_record.categ_achi_amt,null), 
	category_achieve_qty = COALESCE(categ_achi_record.categ_achi_qty,null) , 
	categ_vs_qty = (COALESCE(categ_achi_record.categ_achi_qty,null) /target_line_record.categ_target_qty::float)*100,
	balance = COALESCE(product_achieved_amt,null)-COALESCE(target_line_record.product_target_amt,null)
	where date = weekly_data.date_of_month and product_id = product_data.id;
	update weekly_temp set shop_to_visit=null where shop_to_visit=0;

END LOOP;
END LOOP;

	RETURN QUERY select product_id as p_id, product_name as name_tmpl,category_id as categ_id,category_name as categ_name, shop_to_visit as to_visit, product_target_amt as p_target_amount,product_target_qty as p_t_qty, category_target_amt as categ_t_amt,category_target_qty as categ_t_qty ,actual_visit as act_visit, new_outlet_target as new_olt_target ,new_outlet as new_olt, effective_shop as eff_shop, COALESCE(Round(sum(categ_vs_qty),2),null) as categ_v_s ,COALESCE(round(sum(product_vs_qty),2),null) as p_v_s , null::date as s_date , sum(product_achieve_qty) as p_achi_qty , sum(product_achieve_amount) as p_achi_amt , sum(category_achieve_qty) as categ_achi_qty, sum(category_achieve_amount) as categ_achi_amt, sum(product_achieve_amount)-product_target_amt  as bln from weekly_temp 
	 where shop_to_visit  is not null 
	 group by product_id,name_tmpl,categ_id,categ_name,to_visit,p_target_amount,p_t_qty,categ_t_amt,categ_t_qty,act_visit,new_olt_target,new_olt,effective_shop order by product_id asc,s_date asc;
	  
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;


-- Table: weekly_temp

-- DROP TABLE weekly_temp;

CREATE TABLE weekly_temp
(
  product_name character varying,
  product_id integer,
  category_id integer,
  category_name character varying,
  shop_to_visit integer,
  product_target_amt numeric,
  category_target_amt numeric,
  actual_visit numeric,
  new_outlet_target numeric,
  new_outlet integer,
  categ_vs_qty numeric,
  product_vs_qty numeric,
  effective_shop integer,
  date date,
  product_target_qty numeric,
  product_achieve_qty numeric,
  product_achieve_amount numeric,
  category_target_qty numeric,
  category_achieve_qty numeric,
  category_achieve_amount numeric,
  balance numeric,
  id serial NOT NULL,
  CONSTRAINT report_temp2_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
