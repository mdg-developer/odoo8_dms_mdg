--select * from get_customer_target_multi_customer(ARRAY[28477])
--select * from get_customer_target_multi_customer(ARRAY[182553,46997,28477])
--select * from get_customer_target_multi_customer(ARRAY[46997])

CREATE OR REPLACE FUNCTION get_customer_target_multi_customer(IN param_customer integer[])
  RETURNS TABLE(id bigint,partner_id integer,product_id integer,uom_id integer,ach_qty numeric,target_qty double precision,
				gap_qty double precision,month1_sale numeric,month2_sale numeric,month3_sale numeric,ams_total numeric,
				ams_budget_total numeric,month_out_todate numeric,ams_balance numeric) AS
$BODY$
    DECLARE       	             
	
	sql text := 'with 	
	invoice_amt  as (
				select COALESCE(sum(amount_total),0) as inv_total_amt,partner_id from account_invoice 
				where date_invoice between (select date_trunc(''month'', current_date - interval '''|| 3 ||''' month)::date)
				and (select ((date_trunc(''month'', current_date - interval ''3'' month)+ INTERVAL ''3 MONTH - 1 day''))::date)
				group by partner_id
				),
				target_info as (
					select COALESCE(percentage_growth,0) percentage_growth_value,
					product_uom_qty target_amount,outlet_id,product_id
					from sales_target_outlet target
					inner join sales_target_outlet_line line on (target.id=line.sale_ids)
					left join target_outlets_rel rel on (rel.target_id=target.id)
					where year=date_part(''year'',current_date)::character varying
					and month=to_char(now(),''MM'')		
				),
				product_trans as (
					select COALESCE(sum(total_value),0) total_value,customer_id partner_id
					from product_transactions
					where date_part(''month'', (SELECT date)) =date_part(''month'', (SELECT current_timestamp)) 
					group by customer_id
				),
				target_line as (
					select *,
					case when target_qty > 0 then (ach_qty / target_qty) * 100
					else 0 end as ach_percent,
					(target_qty - ach_qty) gap_qty,now()::date target_date
					from
					(	select *,
						case when final_ams > target_amount then COALESCE(ceil(final_ams),0)
							 when target_amount > final_ams then COALESCE(ceil(target_amount),0)
						end as target_qty
						from
						(	select *,
							round((avg_sale * round(percentage_growth_value / 100, 2))+avg_sale,2) final_ams
							from
							(	select *,
								case when divisor > 0 then round((total_sale_qty/divisor),2) else total_sale_qty end as avg_sale,
								--case when divisor > 0 then round(round((total_sale_qty/divisor),2)*unit_price,2) else round(total_sale_qty*unit_price,2) end as ams_value,
								((select  COALESCE((amt.inv_total_amt),0) from invoice_amt amt where amt.partner_id =BB.partner_id)/divisor
								  )as ams_value,
								(select ti.percentage_growth_value from target_info ti where ti.outlet_id=BB.outlet_type and ti.product_id=BB.product_id),
								(select COALESCE(sum(ti.target_amount),0) as target_amount from target_info ti where ti.outlet_id=BB.outlet_type and ti.product_id=BB.product_id)
								from
								(	select partner_id,customer_code,outlet_type,city,township,street,branch_id,frequency_id,class_id,
									sales_channel,delivery_team_id,product_id,uom_id,sum(month1_sale) month1_sale,sum(month2_sale) month2_sale,
									sum(month3_sale) month3_sale,sum(ach_qty) ach_qty,
									sum(month1_sale)+sum(month2_sale)+sum(month3_sale) total_sale_qty,
									3 as divisor
									from
									(	select 
										case when month1_rec.partner_id is not null then month1_rec.partner_id
											 when month2_rec.partner_id is not null then month2_rec.partner_id 
											 when month3_rec.partner_id is not null then month3_rec.partner_id 
											 when current_rec.partner_id is not null then current_rec.partner_id end as partner_id,
										case when month1_rec.customer_code is not null then month1_rec.customer_code
											 when month2_rec.customer_code is not null then month2_rec.customer_code
											 when month3_rec.customer_code is not null then month3_rec.customer_code 
											 when current_rec.customer_code is not null then current_rec.customer_code end as customer_code,
										case when month1_rec.outlet_type is not null then month1_rec.outlet_type
											 when month2_rec.outlet_type is not null then month2_rec.outlet_type
											 when month3_rec.outlet_type is not null then month3_rec.outlet_type
											 when current_rec.outlet_type is not null then current_rec.outlet_type end as outlet_type,
										case when month1_rec.city is not null then month1_rec.city
											 when month2_rec.city is not null then month2_rec.city
											 when month3_rec.city is not null then month3_rec.city
											 when current_rec.city is not null then current_rec.city end as city,
										case when month1_rec.township is not null then month1_rec.township
											 when month2_rec.township is not null then month2_rec.township
											 when month3_rec.township is not null then month3_rec.township
											 when current_rec.township is not null then current_rec.township end as township,
										case when month1_rec.street is not null then month1_rec.street
											 when month2_rec.street is not null then month2_rec.street
											 when month3_rec.street is not null then month3_rec.street
											 when current_rec.street is not null then current_rec.street end as street,
										case when month1_rec.branch_id is not null then month1_rec.branch_id
											 when month2_rec.branch_id is not null then month2_rec.branch_id
											 when month3_rec.branch_id is not null then month3_rec.branch_id
											 when current_rec.branch_id is not null then current_rec.branch_id end as branch_id,
										case when month1_rec.frequency_id is not null then month1_rec.frequency_id
											 when month2_rec.frequency_id is not null then month2_rec.frequency_id
											 when month3_rec.frequency_id is not null then month3_rec.frequency_id
											 when current_rec.frequency_id is not null then current_rec.frequency_id end as frequency_id,
										case when month1_rec.class_id is not null then month1_rec.class_id
											 when month2_rec.class_id is not null then month2_rec.class_id
											 when month3_rec.class_id is not null then month3_rec.class_id
											 when current_rec.class_id is not null then current_rec.class_id end as class_id,
										case when month1_rec.sales_channel is not null then month1_rec.sales_channel
											 when month2_rec.sales_channel is not null then month2_rec.sales_channel
											 when month3_rec.sales_channel is not null then month3_rec.sales_channel
											 when current_rec.sales_channel is not null then current_rec.sales_channel end as sales_channel,
										case when month1_rec.delivery_team_id is not null then month1_rec.delivery_team_id
											 when month2_rec.delivery_team_id is not null then month2_rec.delivery_team_id
											 when month3_rec.delivery_team_id is not null then month3_rec.delivery_team_id
											 when current_rec.delivery_team_id is not null then current_rec.delivery_team_id end as delivery_team_id,
										case when month1_rec.product_id is not null then month1_rec.product_id
											 when month2_rec.product_id is not null then month2_rec.product_id
											 when month3_rec.product_id is not null then month3_rec.product_id 
											 when current_rec.product_id is not null then current_rec.product_id end as product_id,
										case when month1_rec.uom_id is not null then month1_rec.uom_id
											 when month2_rec.uom_id is not null then month2_rec.uom_id
											 when month3_rec.uom_id is not null then month3_rec.uom_id
											 when current_rec.uom_id is not null then current_rec.uom_id end as uom_id,
								
										COALESCE(month1_sale,0) month1_sale,COALESCE(month2_sale,0) month2_sale,
										COALESCE(month3_sale,0) month3_sale,COALESCE(CEIL(product_quantity),0) ach_qty
										from
										(
											select COALESCE(sum(product_quantity),0) month1_sale,partner_id,customer_code,outlet_type,township,city,street,branch_id,
											frequency_id,class_id,sales_channel,delivery_team_id,product_id,uom_id
											from 
											(   select 
												case when inv_line.uos_id=pt.uom_id then sum(round(quantity,0)) when inv_line.uos_id=pt.report_uom_id then sum(round(quantity*(select floor(round(1/factor,2)) from product_uom where id=report_uom_id),0)) end as product_quantity,
												inv.partner_id,customer_code,rp.outlet_type,rp.township,rp.city,rp.street,rp.branch_id,
												frequency_id,class_id,sales_channel,rp.delivery_team_id,inv_line.product_id,pt.uom_id
												from account_invoice_line inv_line,account_invoice inv,product_product pp,product_template pt,
												sales_target_outlet_line line,sales_target_outlet st,res_partner rp
												where inv_line.invoice_id=inv.id
												and inv_line.product_id=pp.id
												and pp.product_tmpl_id=pt.id
												and st.id=line.sale_ids
												and line.product_id=inv_line.product_id
												and inv.partner_id=rp.id
												and st.year=date_part(''year'',current_date)::character varying
												and st.month=to_char(now(),''MM'')
												and inv.type=''out_invoice''
												and inv.state in (''open'',''paid'')
												and foc!=true and inv.partner_id in ('|| array_to_string(param_customer, ',') ||')
												and date_invoice between (select date_trunc(''month'', current_date - interval '''|| 3 ||''' month)::date)
												and (select ((date_trunc(''month'', current_date - interval ''3'' month)+ INTERVAL ''1 MONTH - 1 day''))::date)
												group by inv_line.quantity,inv_line.uos_id,pt.uom_id,pt.report_uom_id,inv.partner_id,customer_code,
												rp.outlet_type,rp.township,rp.city,rp.street,rp.branch_id,
												frequency_id,class_id,sales_channel,rp.delivery_team_id,inv_line.product_id,pt.uom_id
											)A
											group by partner_id,product_id,customer_code,outlet_type,township,city,street,branch_id,frequency_id,
											class_id,sales_channel,delivery_team_id,uom_id
										)month1_rec
										full outer join
										(
											select COALESCE(sum(product_quantity),0) month2_sale,partner_id,customer_code,outlet_type,city,
											township,street,frequency_id,branch_id,class_id,sales_channel,delivery_team_id,product_id,uom_id
											from 
											(   select 
												case when inv_line.uos_id=pt.uom_id then sum(round(quantity,0)) when inv_line.uos_id=pt.report_uom_id then sum(round(quantity*(select floor(round(1/factor,2)) from product_uom where id=report_uom_id),0)) end as product_quantity,
												inv.partner_id,customer_code,rp.outlet_type,rp.city,rp.township,rp.street,
												rp.branch_id,frequency_id,class_id,sales_channel,rp.delivery_team_id,inv_line.product_id,pt.uom_id
												from account_invoice_line inv_line,account_invoice inv,product_product pp,product_template pt,
												sales_target_outlet_line line,sales_target_outlet st,res_partner rp
												where inv_line.invoice_id=inv.id
												and inv_line.product_id=pp.id
												and pp.product_tmpl_id=pt.id
												and st.id=line.sale_ids
												and line.product_id=inv_line.product_id
												and inv.partner_id=rp.id
												and st.year=date_part(''year'',current_date)::character varying
												and st.month=to_char(now(),''MM'')
												and inv.type=''out_invoice''
												and inv.state in (''open'',''paid'')
												and foc!=true and inv.partner_id in ('|| array_to_string(param_customer, ',') ||')
												and date_invoice between (select date_trunc(''month'', current_date - interval '''||2||''' month)::date)
												and (select ((date_trunc(''month'', current_date - interval ''2'' month)+ INTERVAL ''1 MONTH - 1 day''))::date)
												group by inv_line.quantity,inv_line.uos_id,pt.uom_id,pt.report_uom_id,inv.partner_id,customer_code,inv_line.product_id,
												customer_code,pt.uom_id,rp.outlet_type,rp.city,rp.township,rp.street,rp.branch_id,frequency_id,class_id,
												sales_channel,rp.delivery_team_id
											)B
											group by partner_id,customer_code,product_id,uom_id,outlet_type,city,township,street,branch_id,
											frequency_id,class_id,sales_channel,delivery_team_id
										)month2_rec on (month1_rec.partner_id=month2_rec.partner_id and month1_rec.product_id=month2_rec.product_id)
										full outer join
										(
											select COALESCE(sum(product_quantity),0) month3_sale,partner_id,customer_code,outlet_type,city,
											township,street,branch_id,frequency_id,class_id,sales_channel,delivery_team_id,product_id,uom_id
											from 
											(   select 
												case when inv_line.uos_id=pt.uom_id then sum(round(quantity,0)) when inv_line.uos_id=pt.report_uom_id then sum(round(quantity*(select floor(round(1/factor,2)) from product_uom where id=report_uom_id),0)) end as product_quantity,
												inv.partner_id,customer_code,rp.outlet_type,rp.city,rp.township,rp.street,
												rp.branch_id,frequency_id,class_id,sales_channel,rp.delivery_team_id,inv_line.product_id,pt.uom_id
												from account_invoice_line inv_line,account_invoice inv,product_product pp,product_template pt,
												sales_target_outlet_line line,sales_target_outlet st,res_partner rp
												where inv_line.invoice_id=inv.id
												and inv_line.product_id=pp.id
												and pp.product_tmpl_id=pt.id
												and st.id=line.sale_ids
												and line.product_id=inv_line.product_id
												and inv.partner_id=rp.id
												and st.year=date_part(''year'',current_date)::character varying
												and st.month=to_char(now(),''MM'')
												and inv.type=''out_invoice''
												and inv.state in (''open'',''paid'')
												and foc!=true and inv.partner_id in ('|| array_to_string(param_customer, ',') ||')
												and date_invoice between (select date_trunc(''month'', current_date - interval '''||1||''' month)::date)
												and (select ((date_trunc(''month'', current_date - interval ''1'' month)+ INTERVAL ''1 MONTH - 1 day''))::date)
												group by inv_line.quantity,inv_line.uos_id,pt.uom_id,pt.report_uom_id,inv.partner_id,inv_line.product_id,
												customer_code,pt.uom_id,rp.outlet_type,rp.city,rp.township,rp.street,rp.branch_id,frequency_id,class_id,
												sales_channel,rp.delivery_team_id
											)C
											group by partner_id,customer_code,outlet_type,product_id,uom_id,city,township,street,branch_id,frequency_id,
											class_id,sales_channel,delivery_team_id
										)month3_rec on (month1_rec.partner_id=month3_rec.partner_id and month1_rec.product_id=month3_rec.product_id)
										full outer join
										(
											select COALESCE(sum(product_quantity),0) product_quantity,partner_id,customer_code,outlet_type,
											city,township,street,branch_id,frequency_id,class_id,sales_channel,delivery_team_id,product_id,uom_id
											from 
											(   select 
												case when inv_line.uos_id=pt.uom_id then sum(round(quantity,0)) when inv_line.uos_id=pt.report_uom_id then sum(round(quantity*(select floor(round(1/factor,2)) from product_uom where id=report_uom_id),0)) end as product_quantity,
												inv.partner_id,customer_code,rp.outlet_type,rp.city,rp.township,rp.street,
												rp.branch_id,frequency_id,class_id,sales_channel,rp.delivery_team_id,inv_line.product_id,pt.uom_id
												from account_invoice_line inv_line,account_invoice inv,product_product pp,product_template pt,
												sales_target_outlet_line line,sales_target_outlet st,res_partner rp
												where inv_line.invoice_id=inv.id
												and inv_line.product_id=pp.id
												and pp.product_tmpl_id=pt.id
												and st.id=line.sale_ids
												and line.product_id=inv_line.product_id
												and inv.partner_id=rp.id		
												and st.year=date_part(''year'',current_date)::character varying
												and st.month=to_char(now(),''MM'')
												and inv.type=''out_invoice''
												and inv.state in (''open'',''paid'')
												and foc!=true and inv.partner_id in ('|| array_to_string(param_customer, ',') ||')
												and date_invoice between (select date_trunc(''month'', current_date)::date)
												and (select ((date_trunc(''month'', current_date)+ INTERVAL ''1 MONTH - 1 day''))::date)
												group by inv_line.quantity,inv_line.uos_id,pt.uom_id,pt.report_uom_id,inv.partner_id,inv_line.product_id,
												customer_code,pt.uom_id,rp.outlet_type,rp.city,rp.township,rp.street,rp.branch_id,frequency_id,class_id,
												sales_channel,rp.delivery_team_id
											)D
											group by partner_id,customer_code,outlet_type,product_id,uom_id,city,township,street,branch_id,frequency_id,
											class_id,sales_channel,delivery_team_id
										)current_rec on (month1_rec.partner_id=current_rec.partner_id and month1_rec.product_id=current_rec.product_id)
									)AA
									group by partner_id,customer_code,outlet_type,city,township,street,branch_id,frequency_id,class_id,
									sales_channel,delivery_team_id,product_id,uom_id
								)BB
							)CC
						)DD
					)EE
				)	
				select ROW_NUMBER () OVER (ORDER BY partner_id) id,partner_id,product_id,uom_id,ach_qty,COALESCE(target_qty,0) as target_qty,COALESCE(gap_qty,0) as gap_qty,
				month1_sale,month2_sale,month3_sale,ams_total,round(ams_buget_total,0) ams_buget_total,round(month_out_todate::numeric,0) month_out_todate,
				round((ams_buget_total-month_out_todate)::numeric,0) ams_balance	
				from 
				(
					select *,
					(select ROUND(COALESCE((tt.ams_value),0),0) from target_line tt where tt.partner_id=tl.partner_id limit 1) ams_total,
					case when (select ROUND(COALESCE((tt.ams_value),0),0) from target_line tt where tt.partner_id=tl.partner_id limit 1) * 0.05 > 50000 then 50000
					else (select ROUND(COALESCE((tt.ams_value),0),0) from target_line tt where tt.partner_id=tl.partner_id limit 1) * 0.05 
					end as ams_buget_total,
					(select COALESCE(sum(trans.total_value),0) from product_trans trans where trans.partner_id=tl.partner_id) month_out_todate 
					from target_line tl		
				)AAA';
	
  BEGIN	    
		
	Return query execute sql;   
    
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;