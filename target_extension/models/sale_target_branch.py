from openerp import models, fields, api, _
from openerp.osv.orm import except_orm

class SalesTargetBranch(models.Model):    
    _inherit = "sales.target.branch"
    
    @api.one
    @api.constrains('target_line')
    def check_target_line(self):
        
        for line in self.target_line:
            target_lines = self.env["sales.target.branch.line"].search([('sale_ids', '=', self.id), 
                                                                        ('product_id', '=', line.product_id.id)])
            if target_lines and len(target_lines) > 1:
                raise except_orm(_('UserError'), _("%s is duplicated!") % (line.product_id.name_template,))