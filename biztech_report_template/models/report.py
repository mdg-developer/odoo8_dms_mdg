# -*- coding: utf-8 -*-
from openerp import fields, models,api,_

class Report(models.Model):
    _inherit = 'report'
    
    @api.v7
    def get_html(self, cr, uid, ids, report_name, data=None, context=None):
        res = super(Report, self).get_html(cr, uid, ids, report_name, data=data, context=context)
        invoice_obj = self.pool.get('account.invoice')
        if 'template' in report_name:
            for invoice in invoice_obj.browse(cr, uid, ids, context=context):
                report = self._get_report_from_name(cr, uid, invoice.report_template_id and invoice.report_template_id.report_name or invoice.partner_id and invoice.partner_id.report_template_id and invoice.partner_id.report_template_id.report_name or invoice.company_id and invoice.company_id.report_template_id and invoice.company_id.report_template_id.report_name)
                report_obj = self.pool[report.model]
                docs = report_obj.browse(cr, uid, ids, context=context)
                docargs = {
                    'doc_ids': ids,
                    'doc_model': report.model,
                    'docs': docs,
                }
                return self.render(cr, uid, [], report.report_name, docargs, context=context)
        return res
