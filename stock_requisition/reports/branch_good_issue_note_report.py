from openerp.osv import fields, osv
from openerp.tools.sql import drop_view_if_exists

class report_branch_good_issue_note(osv.osv):
    _name = "report.branch.good.issue.note"
    _description = "Branch Good Issue Note Report"
    _auto = False
    
    _columns = {
        'issue_date':fields.date('Date for Issue', readonly=True),               
        'state': fields.selection([
            ('pending', 'Pending'),
            ('approve', 'Approved'),
            ('issue', 'Issued'),
            ('partial_receive', 'Partial Received'),
            ('receive', 'Received'),
            ('cancel', 'Cancel'),
            ('reversed','Reversed'),        
            ], 'Status', readonly=True, select=True), 
        'request_id':fields.many2one('branch.stock.requisition', 'RFI Ref', readonly=True),
        'to_location_id':fields.many2one('stock.location', 'Requesting Location', readonly=True),
        'from_location_id':fields.many2one('stock.location', 'Request Warehouse', readonly=True),
        'name': fields.char('GIN Ref', readonly=True),
        'receiver':fields.char("Receiver"),
        'issue_by':fields.char("Issuer"),
        'request_by':fields.many2one('res.users', "Requested By"),
        'approve_by':fields.many2one('res.users', "Approved By"),  
        'reverse_user_id':fields.many2one('res.users', "Reverse User"),     
         'branch_id':fields.many2one('res.branch', "Branch"),     
         'eta_date':fields.date ('ETA Date') ,
 
    }

    def init(self, cr):
        drop_view_if_exists(cr, 'report_branch_good_issue_note')
        cr.execute("""
            create or replace view report_branch_good_issue_note as (
                select min(bgin.id)as id,issue_date,state,request_id,to_location_id,
                from_location_id,name,receiver,issue_by,request_by,approve_by,reverse_user_id,branch_id,eta_date
                from branch_good_issue_note bgin                
                group by issue_date,state,request_id,to_location_id,from_location_id,
                name,receiver,issue_by,request_by,approve_by,reverse_user_id,branch_id,eta_date
                order by id desc
            )""")
