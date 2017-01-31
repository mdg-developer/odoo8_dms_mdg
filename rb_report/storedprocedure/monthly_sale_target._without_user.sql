-- Table: montly_temp

-- DROP TABLE montly_temp;

CREATE TABLE montly_temp
(
  product_name character varying,
  product_id integer,
  category_id integer,
  category_name character varying,
  shop_to_visit integer,
  proudct_target_amt numeric,
  category_target_amt numeric,
  actual_visit numeric,
  new_outlet integer,
  new_outlet_target integer,
  categ_vs_qty numeric,
  product_vs_qty numeric,
  effective_shop integer,
  date date,
  categ_carried_qty numeric,
  categ_carried_amt numeric,
  product_target_qty numeric,
  product_achieve_qty numeric,
  product_achieve_amount numeric,
  category_target_qty numeric,
  category_achieve_qty numeric,
  category_achieve_amount numeric,
  quantity_balance numeric,
  amount_balance numeric,
  id serial NOT NULL,
  CONSTRAINT report_temp5_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

-- Table: montly_filter_temp

-- DROP TABLE montly_filter_temp;

CREATE TABLE montly_filter_temp
(
  sequence_no integer,
  week character varying,
  product_name character varying,
  product_id integer,
  category_name character varying,
  shop_to_visit integer,
  proudct_target_amt numeric,
  category_target_amt numeric,
  actual_visit numeric,
  new_outlet integer,
  new_outlet_target integer,
  categ_vs_qty numeric,
  product_vs_qty numeric,
  effective_shop integer,
  categ_carried_qty numeric,
  categ_carried_amt numeric,
  new_target_qty numeric,
  new_target_amt numeric,
  product_target_qty numeric,
  product_achieve_qty numeric,
  product_achieve_amount numeric,
  category_target_qty numeric,
  category_achieve_qty numeric,
  category_achieve_amount numeric,
  qty_balance numeric,
  amt_balance numeric,
  id serial NOT NULL,
  CONSTRAINT montly_filter_temp_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

-- Function: monthly_report_without_user(integer, date, date, integer)

-- DROP FUNCTION monthly_report_without_user(integer, date, date, integer);

CREATE OR REPLACE FUNCTION monthly_report_without_user(IN param_categ_id integer, IN param_from_date date, IN param_to_date date, IN param_sale_team integer)
  RETURNS TABLE(seq_no integer, r_week character varying, pro_name character varying, p_id integer, categ_name character varying, s_to_visit integer, p_target_amt numeric, c_target_amt numeric, a_visit numeric, new_out integer, new_out_target integer, cat_vs_qty numeric, pro_vs_qty numeric, eff_shop integer, c_carried_qty numeric, c_carried_amt numeric, new_target_quantity numeric, new_target_amount numeric, pro_target_qty numeric, pro_achieve_qty numeric, pro_achieve_amount numeric, categ_target_qty numeric, categ_achieve_qty numeric, categ_achieve_amount numeric, qty_balan numeric, amt_balan numeric) AS
$BODY$
	DECLARE
	
	weekly_data record;
	montly_filter_temp_record record;
	montly_update_carried_record record;
	temp_reocrd record;
	week_setting_record record;
	week_setting_data record;
	monthly_data record;
	product_data record;
	categ_achi_record record;
	target_line_record record;
	cat_name character varying;
	effective_count numeric;
	customer_visit numeric;
	visit_count numeric;
	outlet_count numeric;
	product_achieved_amt numeric;
	product_achieved_qty integer;
	name_week record;

	BEGIN
		RAISE NOTICE 'Starting Store Procedure.......';

	--Deleting Temp Table
	
	DELETE FROM montly_temp;
	DELETE FROM montly_filter_temp;
	SELECT name into cat_name from product_category where id = param_categ_id;
	

	-- Retrieve product_id id 
	FOR monthly_data
		IN
		select date_of_month::date  from (
				select param_from_date::date + sun *'1day'::interval as date_of_month
						from generate_series(0,(select (param_to_date::date  - param_from_date::date))) sun
						)A

		
	LOOP	

	FOR product_data 
	 IN  
		select pp.id,pp.name_template from product_product pp , product_template pt
		where pp.product_tmpl_id = pt.id
		and pt.categ_id = param_categ_id	
		/*
		  select pp.id,pp.name_template from product_template pt
		  inner join product_product pp 
		  on pt.id=pp.product_tmpl_id 
		  where main_group in 
		  (select pm.id  from res_users res
		  inner join product_maingroup_res_users_rel rel 
		  on  res.id=rel.res_users_id
		  inner join  product_maingroup pm
		  on pm.id=rel.product_maingroup_id
		  where res.id=user_id) and pt.categ_id = param_categ_id */
	  LOOP
		INSERT INTO montly_temp(product_id,product_name,category_name,
			    date, shop_to_visit, proudct_target_amt,product_target_qty,
			    category_target_amt,category_target_qty,
			    actual_visit, 
			    new_outlet, product_vs_qty , categ_vs_qty, 
			    effective_shop,product_achieve_amount,product_achieve_qty,
			    category_achieve_amount,category_achieve_qty,
			    quantity_balance,amount_balance)
		    VALUES (product_data.id,product_data.name_template,cat_name,monthly_data.date_of_month,0, 0,0,0, 0,0, 0, 0,0, 
					    0,0,0,0,0,0,0);
					    
	 END LOOP;
	 END LOOP;

	FOR weekly_data
		IN
		
		select date as m_date,product_id as p_id from montly_temp

		LOOP

			FOR name_week
					
				IN select name,from_date,to_date from setting_week where from_date>=param_from_date and to_date<=param_to_date

				LOOP

					select st.outlet_target,stl.date,stl.target_amt as product_target_amt,stl.target_qty as product_target_qty ,
					st.total_shop_to_visit as total_shop_to_visit,st.categ_target_qty,st.categ_target_amt
					into target_line_record 
					from sale_target_line stl,sale_target st,crm_case_section css,setting_week sw
					where stl.target_id = st.id
					and css.id = st.sale_team
					and sw.id=st.week 
					and st.sale_team = param_sale_team
					and st.category_id = param_categ_id
					and st.schedule ='weekly'
					and sw.name=name_week.name
					--and sw.from_date>=param_from_date and sw.to_date<=param_to_date
					--and stl.date =  weekly_data.m_date
					and stl.product_id = weekly_data.p_id
					--and sw.from_date>=param_from_date and sw.to_date<=param_to_date
					group by stl.product_id,stl.target_amt,stl.target_qty,st.total_shop_to_visit,
					stl.date,st.outlet_target,st.categ_target_qty,st.categ_target_amt;
					--order by stl.date asc;
				
					--update shop_to_visit,target_amt,target_qty
					update montly_temp set shop_to_visit = COALESCE(target_line_record.total_shop_to_visit,null),
					new_outlet_target = COALESCE(target_line_record.outlet_target,null),
					proudct_target_amt= COALESCE(target_line_record.product_target_amt,null),
					product_target_qty = COALESCE(target_line_record.product_target_qty,null),
					category_target_amt= COALESCE(target_line_record.categ_target_amt,null),
					category_target_qty = COALESCE(target_line_record.categ_target_qty,null)
					where product_id = weekly_data.p_id
					and date>=name_week.from_date and date<=name_week.to_date;
					--and date = weekly_data.m_date;

				

					--get effective count
					select count(*) into effective_count 
					from mobile_sale_order mso,tablets_information ti
					where  mso.date>= name_week.from_date and  mso.date<=name_week.to_date
					and ti.id = mso.tablet_id
					and ti.sale_team_id = param_sale_team
					and mso.void_flag = 'none';

					--get customer visit count
					
					select count(*) into customer_visit 
					from customer_visit cv
					where cv.date = weekly_data.m_date
					and cv.sale_team = param_sale_team;
					
					--get new outlet 
					
					select count(*) into outlet_count 
					from res_partner 
					where mobile_customer ='t' 
					and section_id = param_sale_team
					and create_date::date = weekly_data.m_date;
					
					--update actual visit ,effective_count
					update montly_temp set actual_visit = COALESCE(effective_count,null)+COALESCE(visit_count,null), 
					effective_shop = COALESCE(effective_count,null),
					new_outlet = outlet_count
					--where date = weekly_data.m_date
					where date>=name_week.from_date and date<=name_week.to_date
					and product_id = weekly_data.p_id;

			
					--Closing Day Results
				
					--get achieve qty
					
					select sum(msol.product_uos_qty) into product_achieved_qty 
					from mobile_sale_order mso,mobile_sale_order_line msol ,tablets_information ti
					where mso.id = msol.order_id
					and ti.id = mso.tablet_id
					and mso.date = weekly_data.m_date
					--and  mso.date>= name_week.from_date and  mso.date<=name_week.to_date
					and ti.sale_team_id = param_sale_team
					and mso.void_flag = 'none'
					and msol.product_id = weekly_data.p_id;

					--get categ achieved qty
				
					select sum(product_uos_qty) as categ_achi_qty ,sum(sub_total) as categ_achi_amt 
					into categ_achi_record from mobile_sale_order_line msol,mobile_sale_order mso ,
					product_product pp, product_template pt,tablets_information ti
					where msol.product_id = pp.id
					and pp.product_tmpl_id = pt.id
					and ti.id = mso.tablet_id
					and mso.date = weekly_data.m_date
					--and  mso.date>= name_week.from_date and  mso.date<=name_week.to_date
					and msol.order_id = mso.id
					and pt.categ_id = param_categ_id
					and ti.sale_team_id = param_sale_team;
					--and msol.product_id = weekly_data.p_id;
					
					--get sub total
					
					select sum(msol.sub_total)::numeric into product_achieved_amt 
					from mobile_sale_order mso,mobile_sale_order_line msol ,tablets_information ti
					where mso.id = msol.order_id
					and ti.id = mso.tablet_id
					and ti.sale_team_id = param_sale_team
					and mso.void_flag = 'none'
					and mso.date = weekly_data.m_date
					--and  mso.date>= name_week.from_date and  mso.date<=name_week.to_date
					and msol.product_id = weekly_data.p_id;

					--finally update data 
					
					update montly_temp set 
					product_achieve_amount=COALESCE(product_achieved_amt,null),
					product_achieve_qty = COALESCE(product_achieved_qty,null) ,
					product_vs_qty = (COALESCE(product_achieved_qty,null)/target_line_record.product_target_qty::float)*100,
					--product_vs_qty = 100 * (COALESCE(product_achieved_qty,null)/target_line_record.product_target_qty::float),
					category_achieve_amount= COALESCE(categ_achi_record.categ_achi_amt,null),
					category_achieve_qty = COALESCE(categ_achi_record.categ_achi_qty,null) ,
					
					categ_vs_qty = 100  *(COALESCE(categ_achi_record.categ_achi_qty,null)/target_line_record.categ_target_qty::float),
					quantity_balance = COALESCE(target_line_record.categ_target_qty,null)-COALESCE(categ_achi_record.categ_achi_qty,null),
					amount_balance=COALESCE(product_achieved_amt,null)-COALESCE(target_line_record.product_target_amt,null)
					--amount_balance = COALESCE(target_line_record.categ_target_amt,null)-COALESCE(categ_achi_record.categ_achi_amt,null)
					where date = weekly_data.m_date
					--where date>=name_week.from_date and date<=name_week.to_date
					and product_id = weekly_data.p_id;
					
					
			
			END LOOP;
			
	END LOOP;


	FOR montly_filter_temp_record
	IN 

	--add data to temp records
	select sequence ,week_name as week,product_id as p_id,product_name as p_name,category_name as c_name,sum(shop_to_visit)::numeric as to_visit,
		sum(proudct_target_amt) as p_target_amt ,
		sum(product_target_qty) as product_t_qty,
		sum(category_target_amt) as category_target_amount ,
		sum(category_target_qty) as category_t_qty,
		sum(actual_visit) as act_visit,
		sum(new_outlet) as new_olt,sum(new_outlet_target)::numeric as new_olt_target ,
		sum(effective_shop) as eff_shop,
		sum(COALESCE(product_vs_qty,null)) as p_vs_qty,
		sum(COALESCE(categ_vs_qty,null)) as c_vs_qty,
		sum(product_achieve_qty) as product_achi_qty,
		sum(product_achieve_amount) as product_achi_amt , 
		sum(category_achieve_qty) as categ_achieve_qty,
		sum(category_achieve_amount) as categ_achi_amt , 
		sum(categ_carried_qty) as category_carried_qty,
		sum(categ_carried_qty) as category_carried_amt,
		sum(amount_bln) as amount_bln_new ,
		sum(quantity_bln) as quantity_bln_new
		 from (
			select  sw.sequence,mt.categ_carried_qty,mt.categ_carried_amt,mt.product_id,mt.category_name,mt.product_name ,mt.shop_to_visit,sw.name as week_name,proudct_target_amt as proudct_target_amt ,
			category_target_amt as category_target_amt ,
			sum(actual_visit) as actual_visit, sum(new_outlet) as new_outlet
			,new_outlet_target as new_outlet_target 
			,effective_shop as effective_shop,
			sum(product_vs_qty) as product_vs_qty,sum(categ_vs_qty) as categ_vs_qty,
			sum(product_achieve_qty) as product_achieve_qty,
			sum(product_achieve_amount) as product_achieve_amount , 
			sum(category_achieve_qty) as category_achieve_qty,
			sum(category_achieve_amount) as category_achieve_amount,
			sum(amount_balance) as amount_bln,
			sum(quantity_balance) as quantity_bln,
			mt.product_target_qty as product_target_qty,
			mt.category_target_qty as category_target_qty
			from montly_temp mt,setting_week sw
			where mt.date::date in (select date_of_month::date  from (
				select sw.from_date::date + sun *'1day'::interval as date_of_month
				from generate_series(0,(select (sw.to_date::date  - sw.from_date::date))) sun
				)A)
			group by mt.categ_carried_qty,mt.categ_carried_amt,sw.name,sw.sequence,
			mt.shop_to_visit,new_outlet_target,mt.product_id,mt.product_name,mt.category_name,proudct_target_amt,category_target_amt,mt.product_target_qty,mt.category_target_qty,effective_shop
			order by sw.name asc
		)A
		group by week_name,product_id, category_name,product_name,sequence,category_target_qty
		order by product_id,sequence
		
	LOOP
	
	--INSERT INTO montly_filter_temp table select * from montly_filter_temp where product_id=22
	
	INSERT INTO montly_filter_temp(
            sequence_no, week, product_name, product_id, category_name, 
            shop_to_visit, proudct_target_amt, category_target_amt, actual_visit, 
            new_outlet, new_outlet_target, categ_vs_qty, product_vs_qty, 
            effective_shop, categ_carried_qty, categ_carried_amt,new_target_amt,new_target_qty, product_target_qty, 
            product_achieve_qty, product_achieve_amount, category_target_qty, 
            category_achieve_qty, category_achieve_amount, qty_balance,amt_balance)
	VALUES (
	    montly_filter_temp_record.sequence, montly_filter_temp_record.week, montly_filter_temp_record.p_name, 
	    montly_filter_temp_record.p_id, montly_filter_temp_record.c_name, montly_filter_temp_record.to_visit, 
            montly_filter_temp_record.p_target_amt, montly_filter_temp_record.category_target_amount, 
            montly_filter_temp_record.act_visit, montly_filter_temp_record.new_olt,
            montly_filter_temp_record.new_olt_target, montly_filter_temp_record.c_vs_qty, montly_filter_temp_record.p_vs_qty, 
            montly_filter_temp_record.eff_shop, 0, 0, 0,0,
            montly_filter_temp_record.product_t_qty, 
            montly_filter_temp_record.product_achi_qty,montly_filter_temp_record.product_achi_amt, 
            montly_filter_temp_record.category_t_qty, montly_filter_temp_record.categ_achieve_qty, 
            montly_filter_temp_record.categ_achi_amt, montly_filter_temp_record.quantity_bln_new,montly_filter_temp_record.amount_bln_new);

	    --update carried category qty and amt
	    
	    
	END LOOP;
	FOR montly_update_carried_record
	IN 
		select sequence_no,product_id,qty_balance,amt_balance,category_target_amt,category_target_qty from montly_filter_temp
	LOOP
		update montly_filter_temp set categ_carried_qty = montly_update_carried_record.qty_balance,
		categ_carried_amt = montly_update_carried_record.amt_balance,new_target_qty = montly_update_carried_record.qty_balance+montly_update_carried_record.category_target_qty,
		new_target_amt = montly_update_carried_record.category_target_amt + montly_update_carried_record.amt_balance
		where product_id = montly_update_carried_record.product_id and sequence_no = montly_update_carried_record.sequence_no + 1;
               --update null for zero values
		update montly_filter_temp set effective_shop=null where effective_shop=0;
		update montly_filter_temp set categ_carried_qty=null where categ_carried_qty=0;
		update montly_filter_temp set categ_carried_amt=null where categ_carried_amt=0;
		update montly_filter_temp set new_target_qty=null where new_target_qty=0;
		update montly_filter_temp set new_target_amt=null where new_target_amt=0;

		update montly_filter_temp set shop_to_visit=null where shop_to_visit=0;
		update montly_filter_temp set category_target_qty=null where category_target_qty=0;
		update montly_filter_temp set category_target_amt=null where category_target_amt=0;
		update montly_filter_temp set product_target_qty=null where product_target_qty=0;
		update montly_filter_temp set proudct_target_amt=null where proudct_target_amt=0;
		update montly_filter_temp set actual_visit=null where actual_visit=0;
		update montly_filter_temp set new_outlet=null where new_outlet=0;

		
	END LOOP;
	
	RAISE NOTICE 'Ending Store Procedure.......';

		RETURN QUERY select sequence_no as seq_no, week as r_week, product_name as pro_name ,product_id as p_id , 
		category_name as categ_name  ,shop_to_visit as  s_to_visit ,proudct_target_amt as p_target_amt , 
		category_target_amt as c_target_amt , 
		actual_visit as  a_visit,new_outlet as  new_out ,new_outlet_target new_out_target , 
	        COALESCE(round((sum(category_achieve_qty)/category_target_qty)*100,2),null)  as cat_vs_qty , 
		COALESCE(round((sum(product_achieve_qty)/product_target_qty)*100,2),null) as pro_vs_qty , 
		effective_shop as eff_shop ,COALESCE(categ_carried_qty,null) as c_carried_qty ,COALESCE(categ_carried_amt,null) as c_carried_amt , 
		new_target_qty as new_target_quantity,new_target_amt as new_target_amount,
		product_target_qty as pro_target_qty , 
		sum(product_achieve_qty) as pro_achieve_qty ,sum(product_achieve_amount) as pro_achieve_amount ,category_target_qty as categ_target_qty , 
		sum(category_achieve_qty) as categ_achieve_qty , 
		sum(category_achieve_amount) as categ_achieve_amount ,
		qty_balance as qty_balan,
		sum(product_achieve_amount)- proudct_target_amt   as amt_balan 
		from montly_filter_temp
		group by sequence_no,week,product_name,product_id,category_name,shop_to_visit,proudct_target_amt,category_target_amt,
		actual_visit,new_outlet,new_outlet_target,effective_shop,c_carried_qty,	
		new_target_quantity,c_carried_amt,new_target_amt,product_target_qty,categ_target_qty,qty_balance;
	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;