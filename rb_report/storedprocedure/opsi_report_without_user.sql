-- Table: opsi_temp

-- DROP TABLE opsi_temp;

CREATE TABLE opsi_temp
(
  month character varying,
  order_value numeric,
  sale_order_value numeric,
  purchase_order_value numeric,
  inventory_value numeric,
  inventory_day numeric,
  product_id integer,
  product_name character varying,
  id serial NOT NULL,
  CONSTRAINT report_temp3_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

-- Function: opsi_report_without_user(character varying)

-- DROP FUNCTION opsi_report_without_user(character varying);

CREATE OR REPLACE FUNCTION opsi_report_without_user(IN param_year character varying)
  RETURNS TABLE(r_month character varying, r_order_value numeric, r_sale_order_value numeric, r_purchase_order_value numeric, r_inventory_value numeric, r_inventory_day numeric, p_id integer, p_name character varying) AS
$BODY$

	DECLARE
	proudct_data record;
	month_data record;
	inven_day numeric;
	inven_value numeric;
	po_qty numeric;
	so_qty numeric;
	div_qty numeric;
	order_qty numeric;
	_qty numeric;
	BEGIN

	RAISE NOTICE 'Starting Store Procedure.......';

	--Deleting Temp Table
	
	DELETE FROM opsi_temp;
    
	  
	FOR proudct_data 
		IN
		select id,name_template from product_product
	
	LOOP 
	for month_name in 1..12 
		LOOP

			
			--get order "O" data
			select sum(sol.product_uom_qty) into order_qty 
			from sale_order so ,sale_order_line sol
			where so.state = 'draft'
			and so.id = sol.order_id
			and sol.product_id = proudct_data.id
			and sol.product_id = proudct_data.id
			and extract('year' from so.date_order::date)::character varying = param_year
			and extract('month' from so.date_order::date) = month_name
			group by so.date_order::date,sol.product_id;

			--get sale order "S" data
			select sum(sol.product_uom_qty) into so_qty 
			from sale_order so ,sale_order_line sol
			where so.state not in ('draft','cancel')
			and so.id = sol.order_id
			and sol.product_id = proudct_data.id
			and extract('year' from so.date_order::date)::character varying = param_year
			and extract('month' from so.date_order::date) = month_name
			group by so.date_order::date,sol.product_id;

			--get po data
			select  sum(pol.product_qty) into po_qty 
			from purchase_order po ,purchase_order_line pol
			where po.state not in ('draft','cancel')
			and po.id = pol.order_id
			and extract('year' from po.date_order::date)::character varying = param_year
			and extract('month' from po.date_order::date) = month_name
			and pol.product_id = proudct_data.id
			group by po.date_order::date,pol.product_id;
			
			--get inventory value data
			inven_value = coalesce(po_qty, 0)- coalesce(so_qty, 0);
			_qty = coalesce(so_qty, 0)/30 ;
			
			INSERT INTO opsi_temp(product_name,product_id,month,order_value,sale_order_value,purchase_order_value,
			inventory_value,inventory_day)
			VALUES (proudct_data.name_template,proudct_data.id,month_name,order_qty,so_qty,po_qty,inven_value,
			--inven_value/(so_qty/30));
			CASE WHEN _qty::int =0 THEN inven_value
			ELSE    
				
				CASE WHEN (inven_value/ _qty::int ) <0 THEN (inven_value/ _qty::int) * -1
				ELSE inven_value/ _qty::int
				END
				  
			END  );

			

		END LOOP;
	END LOOP;		
	

	RAISE NOTICE 'Ending Store Procedure.......';

	RETURN QUERY select month r_month,COALESCE(order_value,0) r_order_value,COALESCE(sale_order_value,0) r_sale_order_value,
			COALESCE(purchase_order_value,0) r_purchase_order_value,
			COALESCE(inventory_value,0) r_inventory_value,COALESCE(floor(inventory_day),0) r_inventory_day,
			product_id p_id,product_name  p_name from opsi_temp
			 order by month::integer asc;	

			-- order by month::integer asc;			
	

	END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;