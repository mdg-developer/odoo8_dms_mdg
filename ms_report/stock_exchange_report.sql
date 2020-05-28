select ''::character varying account,''::character varying account_des,total_value,rb.name branch,
branch_region.name branch_region,categ.name product_category,ccs.name sales_team,
channel.name channel,city.name city,rp.name customer,country_state.name customer_state,
st.date::date date,st.name sen_no,st.transaction_id,exchange_type,description item_description,
outlet_type.name outlet_type,pm.name principal,name_template product,product_qty qty,uom.name uom,
case when trans_type = 'In' and uom.id=pt.uom_id then product_qty 
else product_qty*(select floor(round(1/factor,2)) from product_uom where id=uom.id) end as small_in_quantity,
case when trans_type = 'In' and uom.id=pt.uom_id 
then round(product_qty/(select floor(round(1/factor,2)) from product_uom where id=uom.id),0)
else product_qty end as bigger_in_quantity,
case when trans_type = 'Out' and uom.id=pt.uom_id then product_qty 
else product_qty*(select floor(round(1/factor,2)) from product_uom where id=uom.id)end as small_out_quantity,
case when trans_type = 'Out' and uom.id=pt.uom_id 
then round(product_qty/(select floor(round(1/factor,2)) from product_uom where id=uom.id),0)
else product_qty end as bigger_out_quantity,
township.name township,location_type,line.exp_date expired_date,batchno,line.note
from product_transactions st,product_transactions_line line,product_product pp,
crm_case_section ccs,res_branch rb,res_partner rp,product_uom uom,res_branch_region branch_region,
product_template pt,product_category categ,sale_channel channel,res_city city,
res_country_state country_state,outlettype_outlettype outlet_type,product_maingroup pm,
res_township township
where st.id=line.transaction_id
and line.product_id=pp.id 
and st.team_id=ccs.id
and st.branch_id=rb.id 
and st.customer_id=rp.id
and uom.id =line.uom_id
and rb.branch_region_id=branch_region.id
and pp.product_tmpl_id=pt.id
and pt.categ_id=categ.id
and rp.sales_channel=channel.id
and rp.city=city.id
and rp.state_id=country_state.id
and rp.outlet_type=outlet_type.id
and pt.main_group=pm.id
and rp.township=township.id