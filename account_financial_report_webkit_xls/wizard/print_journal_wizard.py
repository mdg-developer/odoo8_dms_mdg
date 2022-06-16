from openerp.osv import fields, orm
import time

class PrintJournalWizard(orm.TransientModel):        
    _inherit = "print.journal.webkit"   
    
    def pre_print_report(self, cr, uid, ids, data, context=None):
        data = super(PrintJournalWizard, self).\
            pre_print_report(cr, uid, ids, data, context)
        # will be used to attach the report on the main account
        data['ids'] = [data['form']['chart_account_id']]
        vals = self.read(cr, uid, ids,
                         ['amount_currency',
                          'display_account',
                          'journal_ids'],
                         context=context)[0]
        data['form'].update(vals)
        return data
         
    def xls_export(self, cr, uid, ids, context=None):
        return self.check_report(cr, uid, ids, context=context)

    def _print_report(self, cr, uid, ids, data, context=None):
        context = context or {}
        if context.get('xls_export'):
            # we update form with display account value
            data = self.pre_print_report(cr, uid, ids, data, context=context)
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'account.account_report_print_journal_xlsx',
                    'datas': data}
        else:
            return super(PrintJournalWizard, self)._print_report(
                cr, uid, ids, data, context=context)

