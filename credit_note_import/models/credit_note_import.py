from openerp.osv import orm
from openerp.osv import fields, osv
import xlrd
from xlrd import open_workbook
from openerp.tools.translate import _
import datetime
import base64
import logging
from __builtin__ import True

_logger = logging.getLogger(__name__)

header_fields = ['Customer Code','Customer Name','Program','Principal','Type','Description','Terms and Conditions','Amount','Remark','Create Date','Branch','Customer Branch','From Date','To Date']

class credit_note_import(osv.osv):
    _name = 'credit.note.import'
    
    _columns = {
                'name':fields.char('Description'),
                'import_date':fields.date('Import Date', readonly=True),
                'import_fname': fields.char('Filename', size=128),
                'import_file':fields.binary('File', required=True),
                'note':fields.text('Log'),
                'state':fields.selection([
                  ('draft', 'Draft'),
                  ('completed', 'Completed'),
                  ('error', 'Error'),
                ], 'States'),
            }
    
    _defaults = {
                    'state':'draft',
                    'import_date':datetime.date.today(),
                }
    
    def _check_file_ext(self, cursor, user, ids):
        for import_file in self.browse(cursor, user, ids):
            if '.xls' in import_file.import_fname:return True
            else: return False
        return True
     
    _constraints = [(_check_file_ext, "Please import Excel file!", ['import_fname'])]
    
    def import_credit_note(self, cr, uid, ids, context=None):
        
        credit_note_obj = self.pool.get('account.creditnote')
        program_obj = self.pool.get('program.form.design')
        partner_obj = self.pool.get('res.partner')
        principal_obj = self.pool.get('product.maingroup')
        branch_obj = self.pool.get('res.branch')
        data = self.browse(cr, uid, ids)[0]
        import_file = data.import_file
        err_log = ''
        header_line = False
        lines = base64.decodestring(import_file)
        wb = open_workbook(file_contents=lines)
        excel_rows = []
        for s in wb.sheets():
            # header
            headers = []
            header_row = 0
            for hcol in range(0, s.ncols):
                headers.append(s.cell(header_row, hcol).value)
            # add header
            excel_rows.append(headers)
            for row in range(header_row + 1, s.nrows):
                values = []
                for col in range(0, s.ncols):
                    values.append(s.cell(row, col).value)
                excel_rows.append(values)
        con_ls = []
        amls = []
        count = val = head_count = 0
        
        for ln in excel_rows:
            # ln = [str(x).strip() for x in ln]
            if not ln or ln and ln in ['', '#']:
                continue
            # process header line
            if not header_line:
                for x in ln:
                    x = str(x).strip()
                    if x in header_fields:
                        con_ls.append(x)
                        head_count = head_count + 1
                if head_count < 3:
                    head_count = 0
                    con_ls = []
                else:
                    if ln:
                        b3 = set(header_fields).difference(con_ls)
                        # check the columns without contained the header fields
                        if b3:
                            for l in b3:
                                ln.append(str(l))
                            val = len(b3)
                    header_line = True
                    customer_code_i = customer_name_i = program_i = principal_i = type_i = description_i = terms_and_conditions_i = amount_i = remark_i = create_date_i = branch_i = customer_branch_i = from_date_i = to_date_i = None
                    column_cnt = len(ln)
                    for i in range(column_cnt):
                        # header fields
                        header_field = ln[i].strip()
                        if header_field not in header_fields:
                            err_log += '\n' + _("Invalid Excel File, Header Field '%s' is not supported !") % ln[i]
                        # required header fields : account, debit, credit
                        elif header_field == 'Customer Code':
                            customer_code_i = i
                        elif header_field == 'Customer Name':
                            customer_name_i = i
                        elif header_field == 'Program':
                            program_i = i
                        elif header_field == 'Principal':
                            principal_i = i
                        elif header_field == 'Type':
                            type_i = i
                        elif header_field == 'Description':
                            description_i = i
                        elif header_field == 'Terms and Conditions':
                            terms_and_conditions_i = i
                        elif header_field == 'Amount':
                            amount_i = i
                        elif header_field == 'Remark':
                            remark_i = i
                        elif header_field == 'Create Date':
                            create_date_i = i
                        elif header_field == 'Branch':
                            branch_i = i
                        elif header_field == 'Customer Branch':
                            customer_branch_i = i
                        elif header_field == 'From Date':
                            from_date_i = i
                        elif header_field == 'To Date':
                            to_date_i = i
                    for f in [(customer_code_i, 'Customer Code'), (customer_name_i, 'Customer Name'), (program_i, 'Program'), (principal_i, 'Principal'), (type_i, 'Type'), (description_i, 'Description'), (terms_and_conditions_i, 'Terms and Conditions'), (amount_i, 'Amount'), (remark_i, 'Remark'), (create_date_i, 'Create Date'), (branch_i, 'Branch'), (customer_branch_i, 'Customer Branch'), (from_date_i, 'From Date'), (to_date_i, 'To Date')]:
                        if not isinstance(f[0], int):
                            err_log += '\n' + _("Invalid Excel file, Header '%s' is missing !") % f[1]
                
                # process data lines           
            else:
                # add the without value for without header fields columns
                for i in range(0, val):
                    ln.append('')
                
                if ln and ln[0] and ln[0][0] not in ['#', '']:
                    import_vals = {}
                    import_vals['customer_code'] = ln[customer_code_i]
                    import_vals['customer_name'] = ln[customer_name_i]
                    import_vals['program'] = ln[program_i]
                    import_vals['principal'] = ln[principal_i]
                    import_vals['type'] = ln[type_i]
                    import_vals['description'] = ln[description_i]
                    import_vals['terms_and_conditions'] = ln[terms_and_conditions_i]
                    import_vals['amount'] = ln[amount_i]
                    import_vals['remark'] = ln[remark_i]
                    import_vals['create_date'] = ln[create_date_i]
                    import_vals['branch'] = ln[branch_i]
                    import_vals['customer_branch'] = ln[customer_branch_i]
                    import_vals['from_date'] = ln[from_date_i]
                    import_vals['to_date'] = ln[to_date_i]
                    amls.append(import_vals)
        
        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            self.write(cr, uid, ids[0], {'state': 'error'})
        if amls or err_log:
            try:
            
                for aml in amls:
                    partner_id = customer_code = program_id = principal_id = description = terms_and_conditions = remark = customer_branch_id = None
                    data = None
                    amount = 0
                     
                    if aml['customer_code']:
                        partner = partner_obj.search(cr, uid, [('customer_code', '=',  aml['customer_code'])],context=None)
                        if not partner:
                            raise osv.except_osv(_('Error!'), _('Customer code %s doesn\'t exist!') % (aml['customer_code'],))
                        else:
                            partner_data = partner_obj.browse(cr, uid, partner)[0]
                            partner_id = partner_data.id 
                            customer_code = aml['customer_code'] 
                            
                    if aml['program']:
                        program = program_obj.search(cr, uid, [('name', '=',  aml['program'])],context=None)
                        if not program:
                            raise osv.except_osv(_('Error!'), _('Program %s doesn\'t exist!') % (aml['program'],))
                        else:
                            program_data = program_obj.browse(cr, uid, program)[0]
                            program_id = program_data.id 
                            
                    if aml['principal']:
                        principal = principal_obj.search(cr, uid, [('name', '=',  aml['principal'])],context=None)
                        if not principal:
                            raise osv.except_osv(_('Error!'), _('Principal %s doesn\'t exist!') % (aml['principal'],))
                        else:
                            principal_data = principal_obj.browse(cr, uid, principal)[0]
                            principal_id = principal_data.id 
                            
                    if aml['type']:
                        if 'offset' in aml['type'].lower():
                            type = 'invoice_offset'
                        if 'cash' in aml['type'].lower():
                            type = 'cash'
                            
                    if aml['description']:
                        description = aml['description']
                        
                    if aml['terms_and_conditions']:
                        terms_and_conditions = aml['terms_and_conditions']
                        
                    if aml['amount']:
                        amount = aml['amount']
                        
                    if aml['remark']:
                        remark = aml['remark']
                          
                    value = {
                                'customer_id': partner_id,
                                'customer_code': customer_code,
                                'program_id': program_id,
                                'principle_id': principal_id,    
                                'type': type,   
                                'description': description,
                                'terms_and_conditions': terms_and_conditions,
                                'amount': amount,  
                                'remark': remark,                
                            }
                    credit_note_id = credit_note_obj.create(cr, uid, value, context=context)
                    
            except Exception, e:
                raise osv.except_osv(_('Warning!'), _('Something wrong with this %s .') % (e))                        
            self.write(cr, uid, ids, {'state':'completed'}, context=context)                       
