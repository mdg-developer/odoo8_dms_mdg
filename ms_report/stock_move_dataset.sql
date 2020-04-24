select sm.name description,sp.name reference,sm.origin source,spt.name picking_type,
pt.name product,
case when uom.id=pt.uom_id then product_uom_qty 
	when uom.id=pt.big_uom_id then product_uom_qty*(select floor(round(1/factor,2)) from product_uom where id=pt.big_uom_id) 
end as smaller_quantity,
(select name from product_uom where id=pt.uom_id) smaller_uom,
case when uom.id=pt.big_uom_id then product_uom_qty 
	when uom.id=pt.uom_id then round(product_uom_qty/(select floor(round(1/factor,2)) from product_uom where id=pt.big_uom_id),0)
end as bigger_quantity,
(select name from product_uom where id=pt.big_uom_id) bigger_uom,
(select name from stock_location where id=sm.location_id) source_location,
(select name from stock_location where id=sm.location_dest_id) destination_location,
sm.date::date date,date_expected::date expected_date,sm.state status
from stock_move sm
left join stock_picking sp on (sm.picking_id=sp.id)
left join stock_picking_type spt on (sm.picking_type_id=spt.id)
left join product_product pp on (sm.product_id=pp.id)
left join product_template pt on (pp.product_tmpl_id=pt.id)
left join product_uom uom on (sm.product_uom=uom.id)