from openerp.osv import fields, osv

class branch_good_issue_note(osv.osv):    
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "branch.good.issue.note"
    
    def _get_tcl_value(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        tcl_value=0
        if context is None:
            context = {}
            
        for gin in self.browse(cr, uid, ids, context=context):
            gin_data = self.browse(cr, uid, gin.id, context=context)
            if gin_data:
                if  gin_data.total_value != 0:         
                    tcl_value = (gin_data.total_tcl / gin_data.total_value)*100
                                 
            res[gin_data.id] = tcl_value            
        return res     
    
    
    def _get_total_tcl(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        total_tcl=0.0
        if context is None:
            context = {}
            
        for gin in self.browse(cr, uid, ids, context=context):
            gin_data = self.browse(cr, uid, gin.id, context=context)
            if gin_data:         
                total_tcl=gin_data.labor_cost + gin_data.transport_cost
             
            res[gin_data.id] = total_tcl            
        return res     
                      
        
    def _get_total_value(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        total_value = 0.0
        if context is None:
            context = {}       
                        
        for gin in self.browse(cr, uid, ids, context=context):
            gin_data = self.browse(cr, uid, gin.id, context=context)
            if gin_data:
                for line in gin_data.p_line:
                    total_value = total_value + line.product_value
            res[gin_data.id] = total_value            
        return res   
    
    _columns = {
        'name': fields.char('GIN Ref', readonly=True),
        'branch_id':fields.many2one('res.branch', 'Branch',required=True),
        'to_location_id':fields.many2one('stock.location', 'Requesting Location',  readonly=True, required=True),
        'request_by':fields.many2one('res.users', "Requested By"),
        'issue_date':fields.date('Date for Issue',required=True),
        'request_id':fields.many2one('stock.requisition', 'RFI Ref', readonly=True),
        'from_location_id':fields.many2one('stock.location', 'Request Warehouse',  readonly=True,required=True),
        'supplier_id': fields.many2one('res.partner', 'Supplier'), 
        'vehicle_id': fields.many2one('fleet.vehicle', 'Vehicle'),
        'route_id': fields.many2one('transport.route', 'Route'),
        'max_weight': fields.float('Max Weight'),
        'max_cbm': fields.float('Max CBM'),
        'approve_by':fields.many2one('res.users', "Approved By"),
        'pricelist_id': fields.many2one('product.pricelist', 'Price list', required=True, readonly=True),
        'issue_by':fields.char("Issuer"),
        'receiver':fields.char("Receiver"),
        'loading_date' : fields.date('Loading Date'),
        'eta_date' : fields.date('ETA Date'),
        'variable_costing': fields.boolean('Is Variable Costing'),
        'transport_cost': fields.float('Transport Cost'),
        'labor_cost': fields.float('Labor Cost'),
        'total_value': fields.function(_get_total_value, type='float', string='Total Value'),
        'total_tcl': fields.function(_get_total_tcl, type='float', string='Total TCL'),          
        'transit_location':fields.many2one('stock.location', "Transit Location"),
        'total_tcl': fields.function(_get_total_tcl, type='float', string='Total TCL'),
        'tcl_value': fields.function(_get_tcl_value, type='float', string='TCL/Value(%)'),
        'p_line':fields.one2many('branch.good.issue.note.line', 'line_id', 'Product Lines',
                              copy=True),
        'state': fields.selection([
            ('pending', 'Pending'),
            ('approve', 'Approved'),
            ('issue', 'Issued'),
            ('receive', 'Received'),            
            ('cancel', 'Cancel'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
        }
    
    _defaults = {
         'state' : 'pending',         
         'request_date': fields.datetime.now,
         'request_by':lambda obj, cr, uid, context: uid,
         'pricelist_id':1,
         
    }
    
    def create(self, cursor, user, vals, context=None):       
        id_code = self.pool.get('ir.sequence').get(cursor, user,
                                                'branch.gin.code') or '/'
        vals['name'] = id_code       
        return super(branch_good_issue_note, self).create(cursor, user, vals, context=context)
    
    def onchange_vehicle(self, cr, uid,ids,vehicle_id,context=None):  
        if vehicle_id:
            vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id, context=context)                       
            route_id = self.pool.get('transport.route.line').search(cr, uid, [('vehicle_id', '=',vehicle_id)], context=context)
            route_obj= self.pool.get('transport.route.line').browse(cr, uid, route_id, context=context) 
            if route_id:                    
                return {'value' : {'max_weight' : vehicle.weight_viss,'max_cbm' : vehicle.vol_cbm,
                               'supplier_id':vehicle.supplier_id,'transport_cost' :route_obj.transport_cost,'labor_cost' : route_obj.labor_cost,}}
    
    def onchange_route(self, cr, uid,ids,route_id,context=None):
        domain={}

        if route_id:
            route_ids = self.pool.get('transport.route.line').search(cr, uid, [('line_id', '=',route_id)], context=context)
            route_list = str(tuple(route_ids))
            route_list = eval(route_list)
            cr.execute('SELECT vehicle_id  FROM transport_route_line where id in %s',(route_list,))
            vehicle_list = cr.fetchall()
            if vehicle_list:        
                domain = {'vehicle_id': [('id', 'in', vehicle_list)]}
        return {'domain':domain}           
      
class branch_good_issue_note_line(osv.osv):  
    _name = 'branch.good.issue.note.line'
    
    _columns = {                
        'line_id':fields.many2one('branch.good.issue.note', 'Line', ondelete='cascade', select=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),        
        'issue_quantity': fields.float(string='Issued (Qty)', digits=(16, 0)),
        'receive_quantity' : fields.float(string='Received (Qty)', digits=(16, 0)),
        'diff_quantity' : fields.float(string='Diff (Qty)', digits=(16, 0)),        
        'product_uom': fields.many2one('product.uom', ' UOM'),        
        'qty_on_hand':fields.float(string='Qty On Hand(S)', digits=(16, 0)),
        'sequence':fields.integer('Sequence'),
        'product_value' : fields.float(string='Value', digits=(16, 0)),
        'product_loss' : fields.boolean(string='Loose'),
        'product_viss' : fields.float(string='Viss', digits=(16, 0)),
        'product_cbm' : fields.float(string='CBM', digits=(16, 0)),
        'remark':fields.selection([
                ('predefined', 'Predefined'),
                ('other_reason', 'Other Reason'),                
            ], 'Remark'),        
    }
    