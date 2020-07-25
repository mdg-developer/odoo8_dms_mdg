-- select * from insert_daily_customer_target_byn();
-- DROP FUNCTION insert_daily_customer_target_byn();

CREATE OR REPLACE FUNCTION insert_daily_customer_target_byn()
  RETURNS void AS
$BODY$

	DECLARE
  	customer record;
	target_id integer;
	product record;
	month1_sale numeric;
	month2_sale numeric;
	month3_sale numeric;
	divisor integer;
	total_sale numeric;
	avg_sale numeric;
	product_price numeric;
	percentage_growth_value numeric;
	target_amount numeric;
	percentage_growth_amount numeric;
	final_ams numeric;
	customer_ams numeric;
	current_month_sale numeric;
	ach_percent numeric;
	ams_total_data numeric;
	ams_budget_value_data numeric;
	month_out_todate_data numeric;
	ams_balance_data numeric;
	
BEGIN
		
	for customer in select rp.id,rp.name,customer_code,outlet.id outlet,rc.id city,rt.id township,street,rb.id branch,
					frequency_id,class_id,sales_channel,rp.delivery_team_id
					from res_partner rp
					left join outlettype_outlettype outlet on (rp.outlet_type=outlet.id)
					left join res_city rc on (rp.city=rc.id)
					left join res_township rt on (rp.township=rt.id)
					left join res_branch rb on (rp.branch_id=rb.id)
					where rp.active=True 
					and rp.customer=True
					and mobile_customer!=True
					and rb.branch_code='BYN'
	loop			
		
		delete from customer_target where partner_id=customer.id;
		
		WITH customer_target AS (
			insert into customer_target(partner_id,outlet_type,township,city,address,date,
			frequency_id,class_id,sales_channel,branch_id,delivery_team_id)
			values(customer.id,customer.outlet,customer.township,customer.city,
			   	customer.street,now()::date,
				customer.frequency_id,customer.class_id,customer.sales_channel,customer.branch,customer.delivery_team_id)
			RETURNING id
		)
		
		SELECT id into target_id
    	FROM customer_target;	
		
		RAISE NOTICE 'inserted customer target id(%)', target_id;
				
		ams_total_data = 0;
		ams_budget_value_data = 0;
		month_out_todate_data = 0;
		ams_balance_data = 0;
		
		for product in select distinct pp.id,name_template,pp.sequence,report_uom_id 
					   from sales_target_outlet_line line,sales_target_outlet st,product_product pp,product_template pt
					   where st.id=line.sale_ids
					   and line.product_id=pp.id
					   and pp.product_tmpl_id=pt.id						  
					   and st.year=date_part('year',current_date)::character varying
					   and st.month=to_char(now(),'MM')
		loop
			
			month1_sale = 0.00;
			month2_sale = 0.00;
			month3_sale = 0.00;
			divisor = 0;
			total_sale = 0.00;
			avg_sale = 0.00;
			product_price = 0.00;
			percentage_growth_value = 0.00;
			target_amount = 0.00;
			percentage_growth_amount = 0.00;
			final_ams = 0.00;
			customer_ams = 0.00;
			current_month_sale = 0.00;
			ach_percent = 0.00;
						
			select COALESCE(sum(product_quantity),0.00) into month1_sale
			from 
			(   select 
				(quantity*(select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=inv_line.uos_id)) as product_quantity
				from account_invoice_line inv_line,account_invoice inv,product_product pp,product_template pt
				where inv_line.invoice_id=inv.id
				and inv_line.product_id=pp.id
				and pp.product_tmpl_id=pt.id
				and inv.type='out_invoice'
				and inv.state in ('open','paid')
				and foc!=true
				and inv.partner_id=customer.id
				and product_id=product.id
				and date_invoice between (select date_trunc('month', current_date - interval '3' month)::date)
				and (select ((date_trunc('month', current_date - interval '3' month)+ INTERVAL '1 MONTH - 1 day'))::date)
				group by inv_line.quantity,inv_line.uos_id,pt.uom_id,pt.big_uom_id
			)A;
			
			if month1_sale > 0 then
				divisor = divisor + 1;
			end if;
			
			select COALESCE(sum(product_quantity),0.00) into month2_sale
			from 
			(   select 
				(quantity*(select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=inv_line.uos_id)) as product_quantity
				from account_invoice_line inv_line,account_invoice inv,product_product pp,product_template pt
				where inv_line.invoice_id=inv.id
				and inv_line.product_id=pp.id
				and pp.product_tmpl_id=pt.id
				and inv.type='out_invoice'
				and inv.state in ('open','paid')
				and foc!=true
				and inv.partner_id=customer.id
				and product_id=product.id
				and date_invoice between (select date_trunc('month', current_date - interval '2' month)::date)
				and (select ((date_trunc('month', current_date - interval '2' month)+ INTERVAL '1 MONTH - 1 day'))::date)
				group by inv_line.quantity,inv_line.uos_id,pt.uom_id,pt.big_uom_id
			)A;
			
			if month2_sale > 0 then
				divisor = divisor + 1;
			end if;
				
			select COALESCE(sum(product_quantity),0.00) into month3_sale
			from 
			(   select 
				(quantity*(select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=inv_line.uos_id)) as product_quantity
				from account_invoice_line inv_line,account_invoice inv,product_product pp,product_template pt
				where inv_line.invoice_id=inv.id
				and inv_line.product_id=pp.id
				and pp.product_tmpl_id=pt.id
				and inv.type='out_invoice'
				and inv.state in ('open','paid')
				and foc!=true
				and inv.partner_id=customer.id
				and product_id=product.id
				and date_invoice between (select date_trunc('month', current_date - interval '1' month)::date)
				and (select ((date_trunc('month', current_date - interval '1' month)+ INTERVAL '1 MONTH - 1 day'))::date)
				group by inv_line.quantity,inv_line.uos_id,pt.uom_id,pt.big_uom_id
			)A;
			
			if month3_sale > 0 then
				divisor = divisor + 1;
			end if;
				
			total_sale = month1_sale + month2_sale + month3_sale;
			
            if divisor > 0 then
            	avg_sale = round(total_sale / divisor, 2);
			end if;		
						
			select COALESCE(new_price,0.00) into product_price
			from product_pricelist_item 
			where price_version_id in ( select id from product_pricelist_version where pricelist_id=1 and active=True) 
			and product_id=product.id
			and product_uom_id=product.report_uom_id;
			
			if product_price is null then
				product_price = 0.00;
			end if;		
						
			select COALESCE(percentage_growth,0.00),
			product_uom_qty*(select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=product_uom) as product_uom_qty
			into percentage_growth_value,target_amount
			from sales_target_outlet target
			inner join sales_target_outlet_line line on (target.id=line.sale_ids)
			left join target_outlets_rel rel on (rel.target_id=target.id)
			where year=date_part('year',current_date)::character varying
			and month=to_char(now(),'MM')
			and outlet_id=customer.outlet
			and product_id=product.id;		
			
			if percentage_growth_value is null then
				percentage_growth_value = 0.00;
			end if;
			
			if target_amount is null then
				target_amount = 0.00;
			end if;		
						
			percentage_growth_amount = avg_sale * round(percentage_growth_value / 100.00, 2);
            final_ams = percentage_growth_amount + avg_sale;            		
			
			if final_ams > target_amount then
				customer_ams = final_ams;
			end if;

			if target_amount > final_ams then
				customer_ams = target_amount;
			end if;		
						
			select COALESCE(sum(product_quantity),0.00) product_quantity into current_month_sale
			from 
			(   select 
				quantity*(select floor(round(1/factor,2)) as ratio from product_uom where active = true and id=inv_line.uos_id) as product_quantity
				from account_invoice_line inv_line,account_invoice inv,product_product pp,product_template pt
				where inv_line.invoice_id=inv.id
				and inv_line.product_id=pp.id
				and pp.product_tmpl_id=pt.id
				and inv.type='out_invoice'
				and inv.state in ('open','paid')
				and foc!=true
				and inv.partner_id=customer.id
				and product_id=product.id
				and date_invoice between (select date_trunc('month', current_date)::date)
				and (select ((date_trunc('month', current_date)+ INTERVAL '1 MONTH - 1 day'))::date)
				group by inv_line.quantity,inv_line.uos_id,pt.uom_id,pt.big_uom_id
			)A;		
						
			if customer_ams > 0 then
                ach_percent = (current_month_sale / customer_ams) * 100;
			end if;
						
			ams_total_data = ams_total_data + (avg_sale * product_price);
			ams_budget_value_data = ams_total_data * 0.05;
								
			if ams_budget_value_data > 50000 then
                ams_budget_value_data = 50000;
			end if;				
						
			select COALESCE(sum(total_value),0.00) into month_out_todate_data
			from product_transactions
			where date_part('month', (SELECT date)) =date_part('month', (SELECT current_timestamp)) 
			and customer_id = customer.id;		
						
			insert into customer_target_line(line_id,product_id,sequence,month1,month2,month3,"6ams",
			ams_value,target_qty,ach_qty,ach_percent,gap_qty)
			values(target_id,product.id,product.sequence,month1_sale,month2_sale,month3_sale,avg_sale,
			COALESCE(avg_sale,0.00)*COALESCE(product_price,0.00),customer_ams,current_month_sale,ach_percent,customer_ams - current_month_sale);
			
			update customer_target
			set ams_total=COALESCE(ams_total_data,0.00),
				ams_buget_total=COALESCE(ams_budget_value_data,0.00),
				month_out_todate=COALESCE(month_out_todate_data,0.00),
				ams_balance=COALESCE(ams_budget_value_data,0.00)-COALESCE(month_out_todate_data,0.00)
			where id=target_id;
			
			raise notice 'inserted customer target line';
			
		end loop;			
				
	end loop;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;