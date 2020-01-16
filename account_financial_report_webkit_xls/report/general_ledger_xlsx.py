# -*- coding: utf-8 -*-
# Copyright 2017 RGB Consulting S.L. (http://www.rgbconsulting.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

try:
    from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    ReportXlsx = object
from openerp.report import report_sxw
import xlwt
from openerp.addons.report_xlsx.report.utils import rowcol_to_cell
from datetime import datetime
from openerp import _
from openerp.addons.account_financial_report_webkit.report.general_ledger import GeneralLedgerWebkit


class JournalEntriesXlsx(ReportXlsx):
    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(ReportXlsx, self).__init__(
            name, table, rml, parser, header, store)

        self.sheet = None
        self.row_pos = None

        self.format_title = None
        self.format_border_top = None

    def _define_formats(self, workbook):
        """ Add cell formats to current workbook.
        Available formats:
         * format_title
         * format_header
         * format_header_right
         * format_header_italic
         * format_border_top
        """
        self.format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'bg_color': '#46C646',
            'border': True
        })
        self.format_header = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFFCC',
            'border': True
        })
        self.format_header_right = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFFCC',
            'border': True,
            'align': 'right'
        })
        self.format_header_center = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFFCC',
            'border': True,
            'align': 'center'
        })
        self.format_header_italic = workbook.add_format({
            'bold': True,
            'bg_color': '#FFFFCC',
            'border': True,
            'italic': True
        })
        self.format_border_top = workbook.add_format({
            'top': 1,
            'align': 'center'
        })
        self.format_header_one = workbook.add_format({
            'align': 'center',
            'border': True,
        })

    def _write_report_title(self, title):
        self.sheet.merge_range(
            self.row_pos, 0, self.row_pos, 7, title, self.format_title
        )
        self.row_pos += 2
        
    def _set_headers_top(self,data,_p):
        # Entry
        self.sheet.write_string(self.row_pos, 0, _('Chart of Account'), self.format_header_center)
        # Date
        self.sheet.write_string(self.row_pos, 1, _('Fiscal Year'), self.format_header_center)
        # Period
        self.sheet.write_string(self.row_pos, 2, _p.filter_form(data) =='filter_date' and _('Dates Filter') or _('Periods Filter'), self.format_header_center)        
        # Journal
        self.sheet.write_string(self.row_pos, 3, _('Accounts Filter'), self.format_header_center)
        # Partner
        self.sheet.write_string(self.row_pos, 4, _('Target Moves'), self.format_header_center)
        # Account
        self.sheet.write_string(self.row_pos, 5, _('Initial Balance'), self.format_header_center)
        self.row_pos += 1
       

    def _generate_header_data(self, data,_p):
            initial_balance_text = {'initial_balance': _('Computed'),
                                'opening_balance': _('Opening Entries'),
                                False: _('No')}
            df = _('From') + ': '
            if _p.filter_form(data) == 'filter_date':
                df += _p.start_date if _p.start_date else u''
            else:
                df += _p.start_period.name if _p.start_period else u''
            df += ' ' + _('To') + ': '
            if _p.filter_form(data) == 'filter_date':
                df += _p.stop_date if _p.stop_date else u''
            else:
                df += _p.stop_period.name if _p.stop_period else u''

            # Entry
            self.sheet.write_string(self.row_pos, 0, _p.chart_account.name or '', self.format_border_top)
            self.sheet.set_column(0, 0, 20)
            # Fiscal Year
            self.sheet.write_string(self.row_pos, 1, _p.fiscalyear.name if _p.fiscalyear else '-' or '', self.format_border_top)
            self.sheet.set_column(1, 1, 20)            
            # Date
            self.sheet.write_string(self.row_pos, 2, df or '', self.format_border_top)
            self.sheet.set_column(2, 2, 30)
            # Period
            self.sheet.write_string(self.row_pos, 3, _p.accounts(data) and ', '.join([account.code for account in _p.accounts(data)]) or _('All'), self.format_border_top)
            self.sheet.set_column(3, 3, 30)
            # Journal
            self.sheet.write_string(self.row_pos, 4, _p.display_target_move(data) or '', self.format_border_top)
            self.sheet.set_column(4, 4, 30)
            # Partner
            self.sheet.write_string(self.row_pos, 5, initial_balance_text[_p.initial_balance_mode] or '', self.format_border_top)
            self.sheet.set_column(5, 5, 20)            
            self.row_pos += 2

    def _set_headers(self,data,_p):
        # Entry
        self.sheet.write_string(self.row_pos, 0, _('Date'), self.format_header_center)
        # Date
        self.sheet.write_string(self.row_pos, 1, _('Period'), self.format_header_center)
        # Period
        self.sheet.write_string(self.row_pos, 2, _('Entry'), self.format_header_center)        
        # Journal
        self.sheet.write_string(self.row_pos, 3, _('Journal'), self.format_header_center)
        # Partner
        self.sheet.write_string(self.row_pos, 4, _('Account'), self.format_header_center)
        # Account
        self.sheet.write_string(self.row_pos, 5, _('Analytic Account'), self.format_header_center)
        # Analytic Account
        self.sheet.write_string(self.row_pos, 6, _('Partner'), self.format_header_center)
        # Account name
        self.sheet.write_string(self.row_pos, 7, _('Reference'), self.format_header_center)
        # Reference
        self.sheet.write_string(self.row_pos, 8, _('Label'), self.format_header_center)
        # Description
        self.sheet.write_string(self.row_pos, 9, _('Counterpart'), self.format_header_center)
        # Debit
        self.sheet.write_string(self.row_pos, 10, _('Debit'), self.format_header_right)
        # Credit
        self.sheet.write_string(self.row_pos, 11, _('Credit'), self.format_header_right) 
        # 'Cumul. Bal.'
        self.sheet.write_string(self.row_pos, 12, _('Cumul. Bal.'), self.format_header_right) 
        
        self.row_pos += 1

    def _generate_report_content(self, data,_p,objects):
        cnt = 0
        for account in objects:

            display_initial_balance = _p['init_balance'][account.id] and \
                (_p['init_balance'][account.id].get(
                    'debit', 0.0) != 0.0 or
                    _p['init_balance'][account.id].get('credit', 0.0)
                    != 0.0)
            display_ledger_lines = _p['ledger_lines'][account.id]

            if _p.display_account_raw(data) == 'all' or \
                    (display_ledger_lines or display_initial_balance):
                # TO DO : replace cumul amounts by xls formulas
                cnt += 1
                cumul_debit = 0.0
                cumul_credit = 0.0
                cumul_balance = 0.0
                cumul_balance_curr = 0.0

                self.sheet.write_string(self.row_pos, 0, ' - '.join([account.code, account.name]) or '', self.format_border_top)
                self.sheet.set_column(0, 0, 20)
                self.row_pos += 1

                if display_initial_balance:
                    init_balance = _p['init_balance'][account.id]
                    cumul_debit = init_balance.get('debit') or 0.0
                    cumul_credit = init_balance.get('credit') or 0.0
                    cumul_balance = init_balance.get('init_balance') or 0.0
                    cumul_balance_curr = init_balance.get(
                        'init_balance_currency') or 0.0
                    c_specs = [('empty%s' % x, 1, 0, 'text', None)
                               for x in range(6)]
                    
#                     self.sheet.write_string(self.row_pos, 0,_('Initial Balance') or '' , self.format_border_top)
#                     self.sheet.set_column(0, 0, 20)
#                     
#                     self.sheet.write_string(self.row_pos, 0, '' , self.format_border_top)
#                     self.sheet.set_column(0, 0, 20)
                
                    self.sheet.write_number(self.row_pos, 0, cumul_debit or 0.0 , self.format_border_top)
                    self.sheet.set_column(9, 9, 20)
                
                    self.sheet.write_number(self.row_pos, 0, cumul_credit or 0.0 , self.format_border_top)
                    self.sheet.set_column(10, 10, 20)
                
                    self.sheet.write_number(self.row_pos, 0, cumul_balance or 0.0 , self.format_border_top)
                    self.sheet.set_column(11, 11, 20)
                  
                    if _p.amount_currency(data):
                        self.sheet.write_number(self.row_pos, 0, cumul_balance_curr or '', self.format_border_top)
                        self.sheet.set_column(12,12, 20)

                for line in _p['ledger_lines'][account.id]:

                    cumul_debit += line.get('debit') or 0.0
                    cumul_credit += line.get('credit') or 0.0
                    cumul_balance_curr += line.get('amount_currency') or 0.0
                    cumul_balance += line.get('balance') or 0.0
                    label_elements = [line.get('lname') or '']
                    if line.get('invoice_number'):
                        label_elements.append(
                            "(%s)" % (line['invoice_number'],))
                    label = ' '.join(label_elements)

                    self.sheet.write_string(self.row_pos, 0,line.get('period_code') or '' , self.format_border_top)
                    self.sheet.set_column(1, 1, 20)
                
                    self.sheet.write_string(self.row_pos, 0,line.get('move_name') or '' , self.format_border_top)
                    self.sheet.set_column(2, 2, 20)
                    
                    self.sheet.write_string(self.row_pos, 0,line.get('jcode') or '' , self.format_border_top)
                    self.sheet.set_column(3, 3, 20)
                    
                    self.sheet.write_string(self.row_pos, 0, account.code or '' , self.format_border_top)
                    self.sheet.set_column(4,4, 20)
                
                    self.sheet.write_string(self.row_pos, 0,line.get('partner_name') or '' , self.format_border_top)
                    self.sheet.set_column(5, 5, 20)
                    
                    self.sheet.write_string(self.row_pos, 0,line.get('lref') or '' , self.format_border_top)
                    self.sheet.set_column(6, 6, 20)
                    
                    self.sheet.write_string(self.row_pos, 0,label or '' , self.format_border_top)
                    self.sheet.set_column(7, 7, 20)
                    
                    self.sheet.write_string(self.row_pos, 0,line.get('counterparts') or '' , self.format_border_top)
                    self.sheet.set_column(8, 8, 20)
                
                    self.sheet.write_number(self.row_pos, 0, line.get('debit', 0.0) or 0.0 , self.format_border_top)
                    self.sheet.set_column(9, 9, 20)
                
                    self.sheet.write_number(self.row_pos, 0, line.get('credit', 0.0) or 0.0 , self.format_border_top)
                    self.sheet.set_column(10, 10, 20)
                
                    self.sheet.write_number(self.row_pos, 0, cumul_balance or 0.0 , self.format_border_top)
                    self.sheet.set_column(11, 11, 20)
                    
                    self.row_pos += 1

                    if _p.amount_currency(data):
                        self.sheet.write_number(self.row_pos, 0, line.get('amount_currency') or 0.0 , self.format_border_top)
                        self.sheet.set_column(12, 12, 20)
                        self.sheet.write_number(self.row_pos, 1, line.get('currency_code') or 0.0 , self.format_border_top)
                        self.sheet.set_column(13, 13, 20)
                        self.row_pos += 1

  
#                 debit_formula = 'SUM(' + '0' + ':' + '0' + ')'         
#                 credit_formula = 'SUM(' + '0' + ':' + '0' + ')'       
#                 balance_formula = '0' + '-' + '0'
#                 
#                 self.sheet.write_string(self.row_pos, 0,' - '.join([account.code, account.name]) or '' , self.format_border_top)
#                 self.sheet.set_column(0, 0, 20)
#                 
#                 self.sheet.write_string(self.row_pos, 0,_('Cumulated Balance on Account') or '' , self.format_border_top)
#                 self.sheet.set_column(0, 0, 20)
#                 
#                 self.sheet.write_string(self.row_pos, 0, debit_formula or 0.0 , self.format_border_top)
#                 self.sheet.set_column(8, 8, 20)
#                 
#                 self.sheet.write_string(self.row_pos, 0, credit_formula or 0.0 , self.format_border_top)
#                 self.sheet.set_column(9, 9, 20)
#                 
#                 self.sheet.write_string(self.row_pos, 0, balance_formula or 0.0 , self.format_border_top)
#                 self.sheet.set_column(10, 10, 20)

                if _p.amount_currency(data):
                    if account.currency_id:
                        self.sheet.write_number(self.row_pos, 0, cumul_balance_curr or '', self.format_border_top)                        
                        self.sheet.set_column(11,11, 20)
                        self.row_pos += 1
                

    def generate_xlsx_report(self, workbook,data, _p, objects):
        if data:
            period_ids = data['form']['period_to']
            journal_ids = data['form']['journal_ids']
        else:  # pragma: no cover
            journal_ids = []
            period_ids = []
            for jp in objects:
                journal_ids.append(jp.journal_id.id)
                period_ids.append(jp.period_id.id)

        # Initial row
        self.row_pos = 0

        # Load formats to workbook
        self._define_formats(workbook)

        # Set report name
        report_name = ' - '.join([_p.report_name.upper(),
                                 _p.company.partner_id.name,
                                 _p.company.currency_id.name])
        self.sheet = workbook.add_worksheet(report_name[:31])
        self._write_report_title(report_name)
     
        # Set headers Top
        self._set_headers_top(data,_p)

        # Generate data
        self._generate_header_data(data,_p)

        cnt = 0
        for account in objects:

            display_initial_balance = _p['init_balance'][account.id] and \
                (_p['init_balance'][account.id].get(
                    'debit', 0.0) != 0.0 or
                    _p['init_balance'][account.id].get('credit', 0.0)
                    != 0.0)
            display_ledger_lines = _p['ledger_lines'][account.id]

            if _p.display_account_raw(data) == 'all' or \
                    (display_ledger_lines or display_initial_balance):
                # TO DO : replace cumul amounts by xls formulas
                cnt += 1
                cumul_debit = 0.0
                cumul_credit = 0.0
                cumul_balance = 0.0
                cumul_balance_curr = 0.0

                self.sheet.write_string(self.row_pos, 0, ' - '.join([account.code, account.name]) or '', self.format_header_one)
                self.sheet.set_column(0, 0, 30)
                self.row_pos += 1
                
                # Set headers
                self._set_headers(data,_p)
                row_start = self.row_pos

                if display_initial_balance:
                    init_balance = _p['init_balance'][account.id]
                    cumul_debit = init_balance.get('debit') or 0.0
                    cumul_credit = init_balance.get('credit') or 0.0
                    cumul_balance = init_balance.get('init_balance') or 0.0
                    cumul_balance_curr = init_balance.get(
                        'init_balance_currency') or 0.0
                    
#                     self.sheet.write_string(self.row_pos, 0,_('Initial Balance') or '' , self.format_border_top)
#                     self.sheet.set_column(0, 0, 20)
#                      
#                     self.sheet.write_string(self.row_pos, 7, '' , self.format_border_top)
#                     self.sheet.set_column(7, 7, 20)
#                 
#                     self.sheet.write_number(self.row_pos, 8, cumul_debit or 0.0 , self.format_border_top)
#                     self.sheet.set_column(8, 8, 20)
#                  
#                     self.sheet.write_number(self.row_pos, 9, cumul_credit or 0.0 , self.format_border_top)
#                     self.sheet.set_column(9, 9, 20)
#                  
#                     self.sheet.write_number(self.row_pos, 10, cumul_balance or 0.0 , self.format_border_top)
#                     self.sheet.set_column(10, 10, 20)
                   
#                     if _p.amount_currency(data):
#                         self.sheet.write_number(self.row_pos, 11, cumul_balance_curr or '', self.format_border_top)
#                         self.sheet.set_column(11,11, 20)

                for line in _p['ledger_lines'][account.id]:

                    cumul_debit += line.get('debit') or 0.0
                    cumul_credit += line.get('credit') or 0.0
                    cumul_balance_curr += line.get('amount_currency') or 0.0
                    cumul_balance += line.get('balance') or 0.0
                    label_elements = [line.get('lname') or '']
                    if line.get('invoice_number'):
                        label_elements.append(
                            "(%s)" % (line['invoice_number'],))
                    label = ' '.join(label_elements)
                    
                    if line.get('ldate'):
                        self.sheet.write_string(self.row_pos, 0, line.get('ldate') or '' , self.format_border_top)
                        self.sheet.set_column(0, 0, 30)
                    
                    self.sheet.write_string(self.row_pos, 1,line.get('period_code') or '' , self.format_border_top)
                    self.sheet.set_column(1, 1, 20)
                
                    self.sheet.write_string(self.row_pos, 2,line.get('move_name') or '' , self.format_border_top)
                    self.sheet.set_column(2, 2, 20)
                     
                    self.sheet.write_string(self.row_pos, 3,line.get('jcode') or '' , self.format_border_top)
                    self.sheet.set_column(3, 3, 20)
                     
                    self.sheet.write_string(self.row_pos, 4,account.code or '' , self.format_border_top)
                    self.sheet.set_column(4, 4, 20)
                    
                    self.sheet.write_string(self.row_pos, 5,line.get('analytic_account') or '' , self.format_border_top)
                    self.sheet.set_column(5, 5, 20)
                 
                    self.sheet.write_string(self.row_pos, 6,line.get('partner_name') or '' , self.format_border_top)
                    self.sheet.set_column(6, 6, 30)
                    
                    self.sheet.write_string(self.row_pos, 7,line.get('lref') or '' , self.format_border_top)
                    self.sheet.set_column(7, 7, 20)
                     
                    self.sheet.write_string(self.row_pos, 8,label or '' , self.format_border_top)
                    self.sheet.set_column(8, 8, 20)
                     
                    self.sheet.write_string(self.row_pos, 9,line.get('counterparts') or '' , self.format_border_top)
                    self.sheet.set_column(9, 9, 20)
                 
                    self.sheet.write_number(self.row_pos, 10, line.get('debit', 0.0) or 0.0 , self.format_border_top)
                    self.sheet.set_column(10, 10, 20)
                 
                    self.sheet.write_number(self.row_pos, 11, line.get('credit', 0.0) or 0.0 , self.format_border_top)
                    self.sheet.set_column(11, 11, 20)
                 
                    self.sheet.write_number(self.row_pos, 12, cumul_balance or 0.0 , self.format_border_top)
                    self.sheet.set_column(12, 12, 20)
                    
                    if _p.amount_currency(data):
                        self.sheet.write_number(self.row_pos, 13, line.get('amount_currency') or 0.0 , self.format_border_top)
                        self.sheet.set_column(13, 13, 20)
                        self.sheet.write_number(self.row_pos, 14, line.get('currency_code') or 0.0 , self.format_border_top)
                        self.sheet.set_column(14, 14, 20)
                    self.row_pos += 1
                    
                debit_start = rowcol_to_cell(row_start, 9)
                debit_end = rowcol_to_cell(self.row_pos - 1, 9)
                debit_formula = 'SUM(' + debit_start + ':' + debit_end + ')'
                credit_start = rowcol_to_cell(row_start, 10)
                credit_end = rowcol_to_cell(self.row_pos - 1, 10)
                credit_formula = 'SUM(' + credit_start + ':' + credit_end + ')'
                balance_debit = rowcol_to_cell(self.row_pos, 9)
                balance_credit = rowcol_to_cell(self.row_pos, 10)
                balance_formula = balance_debit + '-' + balance_credit
                 
                self.sheet.write_string(self.row_pos, 0,' - '.join([account.code, account.name]) or '' , self.format_header_center)
                self.sheet.set_column(0,0, 30)
                   
                self.sheet.write_string(self.row_pos,6,_('Cumulated Balance on Account') or '' , self.format_header_center)
                self.sheet.set_column(6,6, 20)
                   
                self.sheet.write_formula(self.row_pos, 10, debit_formula or 0.0 , self.format_header_center)
                self.sheet.set_column(10, 10, 20)
                   
                self.sheet.write_formula(self.row_pos,11, credit_formula or 0.0 , self.format_header_center)
                self.sheet.set_column(11, 11, 20)
                   
                self.sheet.write_formula(self.row_pos, 12, balance_formula or 0.0 , self.format_header_center)
                self.sheet.set_column(12, 12, 20)
                
                if _p.amount_currency(data):
                    if account.currency_id:
                        self.sheet.write_string(self.row_pos, 13, cumul_balance_curr or 0.0 , self.format_header_center)
                        self.sheet.set_column(13, 13, 20)
                self.row_pos += 2
        self.row_pos += 6

        # Generate data
        #self._generate_report_content(data,_p,objects)

if ReportXlsx != object:
    JournalEntriesXlsx('report.account.account_report_general_ledger_xlsx',
                   'account.account', parser=GeneralLedgerWebkit
    )