from openerp.osv import fields, osv

class branch_good_issue_note(osv.osv):    
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = "branch.good.issue.note"
    
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
        'total_tcl': fields.float('Total TCL'),
        'total_value': fields.float('Total Value'),
        'transit_location':fields.many2one('stock.location', "Transit Location"),
        'tcl_value':fields.float("TCL / Value (%)"),
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
    
    def onchange_total_tcl_calculate(self, cr, uid, ids,transport_cost, labor_cost,total_tcl ,context=None):
        labor_cost = float(labor_cost)
        transport_cost= float(transport_cost)
        total_tcl=float(total_tcl)
        return {'value' : {'total_tcl' :(labor_cost+transport_cost),}}
 
    
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