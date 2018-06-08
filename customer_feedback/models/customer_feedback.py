from openerp.osv import fields, osv


class sync_log(osv.osv):
    _name = "customer.feedback"
    _description = "Customer Feedback"

    _columns = {      
                'date':fields.date('Date'),
                'sale_team_id':fields.many2one('crm.case.section', 'Sale Team'),
                'branch_id':fields.many2one('res.branch', 'Branch'),
                'customer_id':fields.many2one('res.partner', 'Customer'),
                'customer_code':fields.text('Customer Code',readonly=True),
                'feedback_type':fields.text('Feedback Type',readonly=True),
                'maingroup_id':fields.many2one('product.maingroup','Main Group'),
                'contents':fields.text('Contents',readonly=True),
                'm_status':fields.selection([('draft', 'Draft'),
                                                      ('open', 'Open'),('resolve','Resolved')], string='Status'),
                'assignby':fields.text('Assigned By'),
                'assignto':fields.many2one('res.users','Assign To'),
  }
    _defaults = {
        'm_status' : 'draft',     
    } 
    
    def action_assign(self, cr, uid, ids, context=None):
        
        return self.write(cr, uid, ids, {'m_status':'open',})  

    def action_done(self, cr, uid, ids, context=None):
        
        return self.write(cr, uid, ids, {'m_status':'resolve',})  