from odoo import api, fields, models, _

class Employee(models.Model):
    _inherit = 'hr.employee'
    
    ssb_no = fields.Char("SSB No")
    ssb_effective_date = fields.Date("SSB Effective Date")
    fingerprint_id = fields.Char("FingerPrint ID") 
