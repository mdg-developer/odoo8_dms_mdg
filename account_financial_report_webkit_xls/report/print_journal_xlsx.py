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
from openerp.addons.account_financial_report_webkit.report.print_journal import PrintJournalWebkit


class PrintJournalXlsx(ReportXlsx):
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
            'align': 'left',
            'bg_color': '#FFFFCC',
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
        self.format_header_left = workbook.add_format({
            'align': 'left',
            'border': True,
        })
        self.format_header_number_right = workbook.add_format({
            'align': 'right',
            'border': True,
        })
        
    def _write_report_title(self, title):
        self.sheet.merge_range(
            self.row_pos, 0, self.row_pos, 4, title, self.format_title
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
        self.sheet.write_string(self.row_pos, 3, _('Journal Filter'), self.format_header_center)
        # Target Move
        self.sheet.write_string(self.row_pos, 4, _('Target Moves'), self.format_header_center)        
        self.row_pos += 1       

    def _generate_header_data(self, data,_p):
        
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
        self.sheet.write_string(self.row_pos, 0, _p.chart_account.name or '', self.format_header_one)
        self.sheet.set_column(0, 0, 20)
        # Fiscal Year
        self.sheet.write_string(self.row_pos, 1, _p.fiscalyear.name if _p.fiscalyear else '-' or '', self.format_header_one)
        self.sheet.set_column(1, 1, 20)            
        # Period
        self.sheet.write_string(self.row_pos, 2, df or '', self.format_header_one)
        self.sheet.set_column(2, 2, 30)
        # Journal
        self.sheet.write_string(self.row_pos, 3, _p.journals(data) and ', '.join([journal.code + ' ' + journal.name for journal in _p.journals(data)]) or _('All'), self.format_header_one)
        self.sheet.set_column(3, 3, 30)
        # Target Move
        self.sheet.write_string(self.row_pos, 4, _p.display_target_move(data) or '', self.format_header_one)
        self.sheet.set_column(4, 4, 30)
        self.row_pos += 2

    def generate_xlsx_report(self, workbook,data, _p, objects):
         
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
        
        move_list = []
        if _p.moves:
            for move in _p.moves:   
                for move in _p.moves.get(move).ids:                    
                    move_list.append(move)      

        for period in _p.period_obj:            
            for journal in _p.journals(data):
                if _p.amount_currency(data):
                    self.sheet.merge_range(self.row_pos, 0, self.row_pos, 11, journal.name + '-' + period.code or '', self.format_title)
                else:
                    self.sheet.merge_range(self.row_pos, 0, self.row_pos, 9, journal.name + '-' + period.code or '', self.format_title)                
                self.row_pos += 1  
                self.sheet.write_string(self.row_pos, 0, 'Date' , self.format_header_one)
                self.sheet.set_column(0, 0, 30)
                self.sheet.write_string(self.row_pos, 1, 'Entry' , self.format_header_one)
                self.sheet.set_column(1, 1, 30)
                self.sheet.write_string(self.row_pos, 2, 'Account' , self.format_header_one)
                self.sheet.set_column(2, 2, 30)
                self.sheet.write_string(self.row_pos, 3, 'Account Description' , self.format_header_one)
                self.sheet.set_column(3, 3, 30)
                self.sheet.write_string(self.row_pos, 4, 'Due Date' , self.format_header_one)
                self.sheet.set_column(4, 4, 30)
                self.sheet.write_string(self.row_pos, 5, 'Partner' , self.format_header_one)
                self.sheet.set_column(5, 5, 30)
                self.sheet.write_string(self.row_pos, 6, 'Label' , self.format_header_one)
                self.sheet.set_column(6, 6, 30)
                self.sheet.write_string(self.row_pos, 7, 'Reference' , self.format_header_one)
                self.sheet.set_column(7, 7, 30)
                self.sheet.write_string(self.row_pos, 8, 'Debit' , self.format_header_one)
                self.sheet.set_column(8, 8, 30)
                self.sheet.write_string(self.row_pos, 9, 'Credit' , self.format_header_one)
                self.sheet.set_column(9, 9, 30)
                if _p.amount_currency(data):
                    self.sheet.write_string(self.row_pos, 10, 'Currency Balance' , self.format_header_one)
                    self.sheet.set_column(10, 10, 30)
                    self.sheet.write_string(self.row_pos, 11, 'Currency' , self.format_header_one)
                    self.sheet.set_column(11, 11, 30)
                self.row_pos += 1
                                
                move_ids = self.env['account.move.line'].search([('move_id', 'in', tuple(move_list)),
                                                                 ('journal_id', '=', journal.id),
                                                                 ('period_id', '=', period.id)])
                
                if move_ids:
                    total_debit = total_credit = 0 
                    for move in move_ids:                        
                                               
                        self.sheet.write_string(self.row_pos, 0, move.move_id.date or '', self.format_header_one)
                        self.sheet.set_column(0, 0, 30)
                        self.sheet.write_string(self.row_pos, 1, move.move_id.name or '', self.format_header_one)
                        self.sheet.set_column(1, 1, 30)
                        self.sheet.write_string(self.row_pos, 2, move.account_id.code or '', self.format_header_one)
                        self.sheet.set_column(2, 2, 30)
                        self.sheet.write_string(self.row_pos, 3, move.account_id.name or '', self.format_header_left)
                        self.sheet.set_column(3, 3, 30)
                        self.sheet.write_string(self.row_pos, 4, move.date_maturity or '', self.format_header_one)
                        self.sheet.set_column(4, 4, 30)
                        self.sheet.write_string(self.row_pos, 5, move.partner_id.name or '', self.format_header_left)
                        self.sheet.set_column(5, 5, 30)
                        self.sheet.write_string(self.row_pos, 6, move.name or '', self.format_header_left)
                        self.sheet.set_column(6, 6, 30)
                        self.sheet.write_string(self.row_pos, 7, move.move_id.ref or '', self.format_header_left)
                        self.sheet.set_column(7, 7, 30)
                        self.sheet.write_number(self.row_pos, 8, move.debit or 0.00, self.format_header_number_right)
                        self.sheet.set_column(8, 8, 30)
                        self.sheet.write_number(self.row_pos, 9, move.credit or 0.00, self.format_header_number_right)
                        self.sheet.set_column(9, 9, 30)   
                        if _p.amount_currency(data):  
                            self.sheet.write_number(self.row_pos, 10, move.amount_currency or 0.00, self.format_header_number_right)
                            self.sheet.set_column(10, 10, 30) 
                            self.sheet.write_string(self.row_pos, 11, move.currency_id.symbol or '', self.format_header_one)
                            self.sheet.set_column(11, 11, 30)                    
                        self.row_pos += 1
                        total_debit = total_debit + move.debit
                        total_credit = total_credit + move.credit
                        
                    self.sheet.write_number(self.row_pos, 8, total_debit or 0.00, self.format_header_number_right)
                    self.sheet.set_column(8, 8, 30)
                    self.sheet.write_number(self.row_pos, 9, total_credit or 0.00, self.format_header_number_right)
                    self.sheet.set_column(9, 9, 30)
                    self.row_pos += 1
                        
                self.row_pos += 1

if ReportXlsx != object:
    PrintJournalXlsx('report.account.account_report_print_journal_xlsx',
                   'account.account', parser=PrintJournalWebkit
    )