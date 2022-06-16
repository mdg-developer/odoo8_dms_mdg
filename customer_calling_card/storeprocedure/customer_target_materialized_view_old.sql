--select * from mv_customer_target_view
--Drop Materialized View mv_customer_target_view;

CREATE MATERIALIZED VIEW mv_customer_target_view
as

	with customer as (
		select rp.id customer_id,rp.name,customer_code,outlet.id outlet,rc.id city,rt.id township,street,rb.id branch,
		frequency_id,class_id,sales_channel,rp.delivery_team_id
		from res_partner rp
		left join outlettype_outlettype outlet on (rp.outlet_type=outlet.id)
		left join res_city rc on (rp.city=rc.id)
		left join res_township rt on (rp.township=rt.id)
		left join res_branch rb on (rp.branch_id=rb.id)
		where rp.active=True 
		and rp.customer=True
		and mobile_customer!=True 
	),
	target_product as (
		select distinct pp.id,name_template,pp.sequence,pt.uom_id as report_uom_id 
		from sales_target_outlet_line line,sales_target_outlet st,product_product pp,product_template pt
		where st.id=line.sale_ids
		and line.product_id=pp.id
		and pp.product_tmpl_id=pt.id						  
		and st.year=date_part('year',current_date)::character varying
		and st.month=to_char(now(),'MM')
	),
	product_price as (
		select COALESCE(new_price,0.00) new_price,product_id,product_uom_id
		from product_pricelist_item 
		where price_version_id in ( select id 
									from product_pricelist_version 
									where pricelist_id=1 and active=True) 	  
	),
	month1_sale as (
		select COALESCE(sum(product_quantity),0.00) qty,partner_id,product_id
		from 
		(   select 
			case when inv_line.uos_id=pt.uom_id then sum(round(quantity,0)) when inv_line.uos_id=pt.report_uom_id then sum(round(quantity*(select floor(round(1/factor,2)) from product_uom where id=report_uom_id),0)) end as product_quantity,
			inv.partner_id,product_id
			from account_invoice_line inv_line,account_invoice inv,product_product pp,product_template pt
			where inv_line.invoice_id=inv.id
			and inv_line.product_id=pp.id
			and pp.product_tmpl_id=pt.id
			and inv.type='out_invoice'
			and inv.state in ('open','paid')
			and foc!=true			
			and date_invoice between (select date_trunc('month', current_date - interval '3' month)::date)
			and (select ((date_trunc('month', current_date - interval '3' month)+ INTERVAL '1 MONTH - 1 day'))::date)
			group by inv_line.quantity,inv_line.uos_id,pt.uom_id,pt.report_uom_id,inv.partner_id,product_id
		)A
		group by partner_id,product_id
	),
	month2_sale as (
		select COALESCE(sum(product_quantity),0.00) qty,partner_id,product_id
		from 
		(   select 
			case when inv_line.uos_id=pt.uom_id then sum(round(quantity,0)) when inv_line.uos_id=pt.report_uom_id then sum(round(quantity*(select floor(round(1/factor,2)) from product_uom where id=report_uom_id),0)) end as product_quantity,
			inv.partner_id,product_id
			from account_invoice_line inv_line,account_invoice inv,product_product pp,product_template pt
			where inv_line.invoice_id=inv.id
			and inv_line.product_id=pp.id
			and pp.product_tmpl_id=pt.id
			and inv.type='out_invoice'
			and inv.state in ('open','paid')
			and foc!=true
			and date_invoice between (select date_trunc('month', current_date - interval '2' month)::date)
			and (select ((date_trunc('month', current_date - interval '2' month)+ INTERVAL '1 MONTH - 1 day'))::date)
			group by inv_line.quantity,inv_line.uos_id,pt.uom_id,pt.report_uom_id,inv.partner_id,product_id
		)A
		group by partner_id,product_id
	),
	month3_sale as (
		select COALESCE(sum(product_quantity),0.00) qty,partner_id,product_id
		from 
		(   select 
			case when inv_line.uos_id=pt.uom_id then sum(round(quantity,0)) when inv_line.uos_id=pt.report_uom_id then sum(round(quantity*(select floor(round(1/factor,2)) from product_uom where id=report_uom_id),0)) end as product_quantity,
			inv.partner_id,product_id
			from account_invoice_line inv_line,account_invoice inv,product_product pp,product_template pt
			where inv_line.invoice_id=inv.id
			and inv_line.product_id=pp.id
			and pp.product_tmpl_id=pt.id
			and inv.type='out_invoice'
			and inv.state in ('open','paid')
			and foc!=true			
			and date_invoice between (select date_trunc('month', current_date - interval '1' month)::date)
			and (select ((date_trunc('month', current_date - interval '1' month)+ INTERVAL '1 MONTH - 1 day'))::date)
			group by inv_line.quantity,inv_line.uos_id,pt.uom_id,pt.report_uom_id,inv.partner_id,product_id
		)A
		group by partner_id,product_id
	),
	target_info as (
		select COALESCE(percentage_growth,0.00) percentage_growth_value,
		product_uom_qty target_amount,outlet_id,product_id
		from sales_target_outlet target
		inner join sales_target_outlet_line line on (target.id=line.sale_ids)
		left join target_outlets_rel rel on (rel.target_id=target.id)
		where year=date_part('year',current_date)::character varying
		and month=to_char(now(),'MM')		
	),
	current_month_sale_record as (
		select COALESCE(sum(product_quantity),0.00) product_quantity,partner_id,product_id
		from 
		(   select 
			case when inv_line.uos_id=pt.uom_id then sum(round(quantity,0)) when inv_line.uos_id=pt.report_uom_id then sum(round(quantity*(select floor(round(1/factor,2)) from product_uom where id=report_uom_id),0)) end as product_quantity,
		 	inv.partner_id,product_id
			from account_invoice_line inv_line,account_invoice inv,product_product pp,product_template pt
			where inv_line.invoice_id=inv.id
			and inv_line.product_id=pp.id
			and pp.product_tmpl_id=pt.id
			and inv.type='out_invoice'
			and inv.state in ('open','paid')
			and foc!=true			
			and date_invoice between (select date_trunc('month', current_date)::date)
			and (select ((date_trunc('month', current_date)+ INTERVAL '1 MONTH - 1 day'))::date)
			group by inv_line.quantity,inv_line.uos_id,pt.uom_id,pt.report_uom_id,inv.partner_id,product_id
		)A
		group by partner_id,product_id
	),
	product_trans as (
		select COALESCE(sum(total_value),0.00) total_value,customer_id
		from product_transactions
		where date_part('month', (SELECT date)) =date_part('month', (SELECT current_timestamp)) 
		group by customer_id
	),
	target_line as (
		select *,
		case when target_qty > 0 then (ach_qty / target_qty) * 100
		else 0.00 end as ach_percent,
		(CEIL(target_qty) - CEIL(ach_qty)) gap_qty
		from 
		(
			select *,
			case when final_ams > target_amount then COALESCE(ceil(final_ams),0.00)
				 when target_amount > final_ams then COALESCE(ceil(target_amount),0.00)
			end as target_qty,
			(select COALESCE(sum(product_quantity),0.00) from current_month_sale_record cm where cm.partner_id=customer_id and cm.product_id=product_id) ach_qty
			from
			(
				select *,
				round((avg_sale * round(percentage_growth_value / 100.00, 2))+avg_sale,2) final_ams
				from 
				(
					select *,
					case when divisor > 0 then round((total_sale_qty/divisor),2) else total_sale_qty end as avg_sale,
					case when divisor > 0 then round(round((total_sale_qty/divisor),2)*unit_price,2) else round(total_sale_qty*unit_price,2) end as ams_value,
					(select ti.percentage_growth_value from target_info ti where ti.outlet_id=outlet and ti.product_id=B.product_id),
					(select ti.target_amount from target_info ti where ti.outlet_id=outlet and ti.product_id=B.product_id)
					from 
					(
						select *,
						month1_sale_qty+month2_sale_qty+month3_sale_qty total_sale_qty,
						case when month1_sale_qty = 0 and month2_sale_qty = 0 and month2_sale_qty = 0 then 0
							when month1_sale_qty > 0 and month2_sale_qty > 0 and month3_sale_qty > 0 then 3 
							when (month1_sale_qty > 0 and month2_sale_qty > 0) or (month1_sale_qty > 0 and month3_sale_qty > 0) or (month2_sale_qty > 0 and month3_sale_qty > 0) then 2 
							else 1 	 
							end as divisor
						from
						(		
							select c.customer_id,now()::date target_date,c.name customer_name,c.customer_code,c.outlet,c.city,c.township,c.street,c.branch,
							c.frequency_id,c.class_id,c.sales_channel,c.delivery_team_id,tp.id product_id,tp.name_template,tp.sequence,
							tp.report_uom_id,	
							(select COALESCE(new_price,0.00) from product_price where product_id=tp.id and product_uom_id=report_uom_id) unit_price,	
							case when (select qty from month1_sale where partner_id=c.customer_id and product_id=tp.id) is null then 0.00
							else(select qty from month1_sale where partner_id=c.customer_id and product_id=tp.id) end as month1_sale_qty,
							case when (select qty from month2_sale where partner_id=c.customer_id and product_id=tp.id) is null then 0.00
							else(select qty from month2_sale where partner_id=c.customer_id and product_id=tp.id) end as month2_sale_qty,
							case when (select qty from month3_sale where partner_id=c.customer_id and product_id=tp.id) is null then 0.00
							else(select qty from month3_sale where partner_id=c.customer_id and product_id=tp.id) end as month3_sale_qty
							from customer c
							CROSS JOIN target_product tp
						)A
					)B
				)C
			)D
		)E
	)
	select ROW_NUMBER () OVER (ORDER BY customer_id) id,*,
	(ams_buget_total-month_out_todate) ams_balance
	from 
	(
		select *,
		(select ROUND(COALESCE(sum(tl.ams_value),0.00),0) from target_line tl where tl.customer_id=customer_id) ams_total,
		case when (select ROUND(COALESCE(sum(tl.ams_value),0.00),0) from target_line tl where tl.customer_id=customer_id) * 0.05 > 50000 then 50000
		else (select ROUND(COALESCE(sum(tl.ams_value),0.00),0) from target_line tl where tl.customer_id=customer_id) * 0.05 
		end as ams_buget_total,
		(select COALESCE(sum(trans.total_value),0) from product_trans trans where trans.customer_id=customer_id) month_out_todate 
		from target_line
		group by customer_id,target_date,customer_name,customer_code,outlet,city,township,street,branch,frequency_id,
		class_id,sales_channel,delivery_team_id,product_id,name_template,sequence,report_uom_id,unit_price,month1_sale_qty,
		month2_sale_qty,month3_sale_qty,total_sale_qty,divisor,avg_sale,ams_value,percentage_growth_value,target_amount,
		final_ams,target_qty,ach_qty,ach_percent,gap_qty
	)F
   
  