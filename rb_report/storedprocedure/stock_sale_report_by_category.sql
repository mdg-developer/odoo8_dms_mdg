-- Function: stock_sale_report(date, date, integer)

-- DROP FUNCTION stock_sale_report(date, date, integer);

CREATE OR REPLACE FUNCTION stock_sale_report(IN param_from_date date, IN param_to_date date, IN param_categ_id integer)
  RETURNS TABLE(ser_no integer, p_default_code character varying, p_categ_name character varying, p_product_name character varying, p_uom character varying, p_open_qty numeric, p_open_amt numeric, p_receipt_qty numeric, p_receipt_amt numeric, p_sale_qty numeric, p_sale_amt numeric, p_foc_qty numeric, p_foc_amt numeric, short_qty numeric, short_amt numeric, p_close_qty numeric, p_close_amt numeric) AS
$BODY$
	DECLARE
		inform_data RECORD ;
	BEGIN
		DROP TABLE IF EXISTS sale_stock_temp;
		CREATE TEMPORARY TABLE sale_stock_temp AS
		(select pp.id as product_id,pp.default_code,pc.name as categ_name,pp.name_template as product_name,pu.name as uom,0.0 as open_qty,0.0 as open_amt,0.0 as receipt_qty,0.0 as receipt_amt,0.0 as sale_qty,0.0 as sale_amt,0.0 as foc_qty,0.0 as foc_amt,0.0 as short_qty,0.0 as short_amt
		 from product_category pc,product_product pp, product_template pt,product_uom pu
		where pp.product_tmpl_id=pt.id
			and pt.categ_id=pc.id
			 and pt.uom_po_id =pu.id
			 and pt.type='product'
			 order by product_name
			 );
			 
		FOR inform_data In
		

		      select B.product_id,null::character varying as location,null::character varying as location_complete,'opening_balance' as type,B.product_name,B.uom,B.category,B.default_code,sum(qty) as qty,sum(B.total_amt) as total_amt from 
		      (select product_id ,pp.name_template as product_name,pu.name as uom,pc.name as category,
		      pp.default_code,A.re_qty as qty,A.product_uom_qty*A.price_unit as total_amt from (

			select product_id,create_date::date,location_id,product_uom_qty as re_qty,product_uom_qty,price_unit ,'Receipts' as type from stock_move where picking_type_id in (select id from stock_picking_type where name ='Receipts') 
			UNION ALL
			select product_id ,create_date::date,location_id,-1*product_uom_qty as re_qty,product_uom_qty,-1*price_unit ,'delivery' as type from stock_move where picking_type_id in (select id from stock_picking_type where name like 'Delivery %s') 
			UNION ALL
			 select product_id,create_date::date,location_id,-1*product_uom_qty as re_qty,product_uom_qty,-1*price_unit,'loss' as type from stock_move where location_id in (select id from stock_location where name='Inventory loss') 
			UNION ALL
			 select product_id,create_date::date,location_id,-1*product_uom_qty as re_qty,product_uom_qty,-1*price_unit,'FOC' as type from stock_move where name ='FOC')A,product_product pp,product_uom pu,product_category pc ,product_template pt
			 where A.product_id=pp.id
			 and pp.product_tmpl_id=pt.id
			 and pt.categ_id=pc.id
			 and pt.uom_po_id =pu.id
			and A.create_date::date < param_from_date
			)B
			group by B.product_id,B.product_name,B.uom,B.category,B.default_code
			UNION ALL
			(select product_id,sl.name as location,sl.complete_name as location_complete,A.type,pp.name_template as product_name,pu.name as uom,pc.name as category,pp.default_code,sum(A.product_uom_qty) as qty,sum(A.product_uom_qty*A.price_unit) as total_amt from (
			select product_id,create_date::date,location_id,product_uom_qty,price_unit ,'Receipts' as type from stock_move where picking_type_id in (select id from stock_picking_type where name ='Receipts')
			UNION ALL
			select product_id ,create_date::date,location_id,product_uom_qty,price_unit ,'delivery' as type from stock_move where picking_type_id in (select id from stock_picking_type where name like 'Delivery %s')
			UNION ALL
			 select product_id,create_date::date,location_id,product_uom_qty,price_unit,'loss' as type from stock_move where location_id in (select id from stock_location where name='Inventory loss')
			UNION ALL
			 select product_id,create_date::date,location_id,product_uom_qty,price_unit,'FOC' as type from stock_move where name ='FOC')A,product_product pp,product_uom pu,product_category pc ,product_template pt,stock_location sl
			 where A.product_id=pp.id
			 and pp.product_tmpl_id=pt.id
			 and pt.categ_id=pc.id
			 and pt.uom_po_id =pu.id
			 and sl.id=A.location_id
			and A.create_date::date between param_from_date and param_to_date
			group by A.product_id,sl.name,A.type,pp.name_template,pu.name,pc.name,pp.default_code,sl.complete_name)
		LOOP 		
		
		       IF (inform_data.type ='opening_balance') THEN
		           Update sale_stock_temp set open_qty=inform_data.qty,open_amt=inform_data.total_amt where product_id=inform_data.product_id;
		       ELSEIF ( inform_data.type='Receipts') THEN
		           Update sale_stock_temp set receipt_qty=inform_data.qty,receipt_amt=inform_data.total_amt where product_id=inform_data.product_id;
			ELSEIF  (inform_data.type='delivery' ) THEN
		           Update sale_stock_temp set sale_qty=inform_data.qty,sale_amt=inform_data.total_amt where product_id=inform_data.product_id;		       
			ELSEIF  (inform_data.type='loss' and inform_data.total_amt is not null) THEN
		           Update sale_stock_temp set short_qty=inform_data.qty,short_amt=inform_data.total_amt where product_id=inform_data.product_id;			
		       ELSEIF  (inform_data.type='loss' and inform_data.total_amt is null) THEN
		           Update sale_stock_temp set short_qty=inform_data.qty,short_amt=0.0 where product_id=inform_data.product_id;			           		 
			ELSEIF  (inform_data.type='FOC' ) THEN
		           Update sale_stock_temp set foc_qty=inform_data.qty,foc_amt=inform_data.total_amt where product_id=inform_data.product_id;	
		        END IF;	

		END LOOP;
		IF param_categ_id is null THEN
		   RETURN QUERY select st.*,st.open_qty+st.receipt_qty-(st.sale_qty+st.foc_qty+st.short_qty) as close_qty,st.open_amt+st.receipt_amt-(st.sale_amt+st.foc_amt+st.short_amt) as close_amt from sale_stock_temp  st ;
               ELSE
 		   RETURN QUERY select st.*,st.open_qty+st.receipt_qty-(st.sale_qty+st.foc_qty+st.short_qty) as close_qty,st.open_amt+st.receipt_amt-(st.sale_amt+st.foc_amt+st.short_amt) as close_amt from sale_stock_temp  st,product_category pc
 		   where pc.name=st.categ_name
 		   and pc.id=param_categ_id;
		END IF;
              
 END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;