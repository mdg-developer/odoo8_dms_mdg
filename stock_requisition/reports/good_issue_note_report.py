from openerp.osv import fields, osv
from openerp.tools.sql import drop_view_if_exists

class report_good_issue_note(osv.osv):
    _name = "report.good.issue.note"
    _description = "Good Issue Note Report"
    _auto = False
    
    _columns = {
        'issue_date':fields.char('Date for Issue', readonly=True),     
        'sub_d_customer_id': fields.many2one('sub.d.customer', 'Sub-D Customer', readonly=True, select=True),  
        'state': fields.selection([
            ('draft', 'Pending'),
            ('approve', 'Approved'),
            ('issue','Issued'),
            ('cancel', 'Cancel'),
            ('reversed', 'Reversed'),            
            ], 'Status', readonly=True, select=True), 
        'request_id':fields.many2one('stock.requisition', 'RFI Ref', readonly=True),
        'to_location_id':fields.many2one('stock.location', 'Requesting Location', readonly=True),
        'from_location_id':fields.many2one('stock.location', 'Request Warehouse', readonly=True),
        'name': fields.char('GIN Ref', readonly=True),
        'receiver':fields.char("Receiver"),
        'issue_by':fields.char("Issuer"),
        'request_by':fields.many2one('res.users', "Requested By"),
        'approve_by':fields.many2one('res.users', "Approved By"),
        'reverse_user_id':fields.many2one('res.users', "Reverse User", readonly=True),
    }

    def init(self, cr):
        drop_view_if_exists(cr, 'report_good_issue_note')
        cr.execute("""
            create or replace view report_good_issue_note as (
                select min(gin.id)as id,issue_date,sub_d_customer_id,state,request_id,to_location_id,
                from_location_id,name,receiver,issue_by,request_by,approve_by,reverse_user_id
                from good_issue_note gin                
                group by issue_date,sub_d_customer_id,state,request_id,to_location_id,from_location_id,
                name,receiver,issue_by,request_by,approve_by,reverse_user_id
                order by id desc
            )""")
