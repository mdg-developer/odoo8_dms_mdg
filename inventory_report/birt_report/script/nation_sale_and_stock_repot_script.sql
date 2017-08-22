-- Function: get_git(integer, date)

-- DROP FUNCTION get_git(integer, date);

CREATE OR REPLACE FUNCTION get_git(product_id integer, from_date date)
  RETURNS numeric AS
$BODY$
DECLARE
	get_git_opening numeric=0;
	p_id integer;	
	f_date date;
BEGIN
	p_id = product_id;	
	f_date = from_date;
	WITH get_bal AS (
		select A.create_date,A.product_id,sum(A.product_uom_qty) as qty from (
		select m.product_id,m.create_date::date,m.location_id,m.product_uom_qty from stock_move as m where picking_type_id in (select id from stock_picking_type where name ='Receipts')
		UNION ALL
		select m.product_id,m.create_date::date,m.location_id,m.product_uom_qty * (-1) as product_uom_qty from stock_move as m where picking_type_id in (select id from stock_picking_type where name like 'Delivery %s')
		UNION ALL
		 select m.product_id,m.create_date::date,m.location_id,m.product_uom_qty * (-1) as product_uom_qty from stock_move as m where location_id in (select id from stock_location where name='Inventory loss') --and date between ? and ?
		UNION ALL
		 select m.product_id,m.create_date::date,m.location_id,m.product_uom_qty * (-1) as product_uom_qty from stock_move as m where name ='FOC')A
		 
		 where A.product_id=p_id
		 		
		and A.create_date <= f_date-1 
		group by A.create_date,A.product_id
		
	)
	select qty into get_git_opening from get_bal as t ;

	RETURN get_git_opening;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION get_git(integer, date)
  OWNER TO openerp;

-----------------------------------------------------------------------------------------------------------------

-- Function: get_git_bywarehouse(integer, integer, date)

-- DROP FUNCTION get_git_bywarehouse(integer, integer, date);

CREATE OR REPLACE FUNCTION get_git_bywarehouse(product_id integer, warehouse_id integer, to_date date)
  RETURNS numeric AS
$BODY$
DECLARE
	get_git_opening numeric=0;
	p_id integer;
	w_id integer;
	t_date date;
BEGIN
	p_id = product_id;
	w_id = warehouse_id;
	t_date = to_date;
	WITH get_bal AS (
		select A.create_date,A.product_id,A.warehouse_id,sum(A.product_uom_qty) as qty from (
		select m.product_id,m.warehouse_id,m.create_date::date,m.location_id,m.product_uom_qty from stock_move as m where picking_type_id in (select id from stock_picking_type where name ='Receipts')
		UNION ALL
		select m.product_id,m.warehouse_id,m.create_date::date,m.location_id,m.product_uom_qty * (-1) as product_uom_qty from stock_move as m where picking_type_id in (select id from stock_picking_type where name like 'Delivery %s')
		UNION ALL
		 select m.product_id,m.warehouse_id,m.create_date::date,m.location_id,m.product_uom_qty * (-1) as product_uom_qty from stock_move as m where location_id in (select id from stock_location where name='Inventory loss') --and date between ? and ?
		UNION ALL
		 select m.product_id,m.warehouse_id,m.create_date::date,m.location_id,m.product_uom_qty * (-1) as product_uom_qty from stock_move as m where name ='FOC')A
		 
		 where A.product_id=p_id
		 and A.warehouse_id=w_id		
		and A.create_date <= t_date 
		group by A.create_date,A.product_id,A.warehouse_id
		
	)
	select qty into get_git_opening from get_bal as t ;

	RETURN get_git_opening;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION get_git_bywarehouse(integer, integer, date)
  OWNER TO openerp;

-------------------------------------------------------------------------------------------------------------------------------

-- Function: national_sale_stock_report(integer, date, date, integer)

-- DROP FUNCTION national_sale_stock_report(integer, date, date, integer);

CREATE OR REPLACE FUNCTION national_sale_stock_report(IN category_id integer, IN from_date date, IN to_date date, IN warehouse_id integer)
  RETURNS TABLE(product_id integer, warehouseid integer, stockid character varying, product character varying, pracking character varying, qty numeric, price_unit numeric, amt numeric, category character varying, branch character varying, git numeric, bal numeric) AS
$BODY$
    DECLARE
    f_date date = NULL;
    t_date date = NULL;
    
    sql text := ' select B.product_id,B.warehouseid,B.stockid,B.product,B.packing,B.qty,B.price_unit,B.qty * B.price_unit as amt,B.category,B.Branch,B.git,B.bal from
    (select d.product_id,h.warehouse_id as warehouseid,p.default_code as stockid,t.name as product,u.name as packing,sum(d.product_uos_qty) as qty,d.price_unit as price_unit,c.name as category,w.name as Branch,';
		
		

  BEGIN
		    --f_date = from_date;
		    --t_date = to_date;
		    
		    
		    IF from_date IS NOT NULL AND to_date IS NOT NULL THEN  
			f_date = from_date;
			t_date = to_date; 
			sql := sql || ' get_git(d.product_id,''' || f_date || ''') as git,get_git_bywarehouse(d.product_id,h.warehouse_id,''' || t_date || ''') as bal
				from sale_order h,sale_order_line d,product_template t,product_product p,product_uom u,product_category c,stock_warehouse w
				where h.id = d.order_id and h.warehouse_id=w.id and d.product_id = p.id and d.product_uom=u.id and p.product_tmpl_id=t.id and t.categ_id = c.id';			                     
	            END IF;		   
		    
		    IF f_date IS NOT NULL AND t_date IS NOT NULL THEN
			sql := sql || ' and h.date_order::date between ''' || f_date || ''' and ''' || t_date || ''' ';
	            END IF;	
	            	
		    IF category_id IS NOT NULL THEN
			sql := sql || ' and (c.id = ''' || category_id || ''' or c.parent_id =''' || category_id ||''') ';
			--sql := sql || ' and t.categ_id = ''' || category_id || ''' ';
		    END IF;
		    
		    IF warehouse_id IS NOT NULL THEN
                        
                        --sql := sql || ' and loc.complete_name like ' ||'''%'|| $4 ||'%''';
                        sql := sql || ' and h.warehouse_id= ''' || warehouse_id || '''';
	            END IF;
	            
		    RAISE NOTICE ' SQL 2(%)', sql;
		    sql := sql || ' group by d.product_id,h.warehouse_id,p.default_code,t.name,u.name,d.price_unit,c.name,w.name,git,bal)B';		
		    RAISE NOTICE ' SQL 3 (%)', sql;
    Return QUERY EXECUTE sql;			
    
  END;
  $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION national_sale_stock_report(integer, date, date, integer)
  OWNER TO openerp;
