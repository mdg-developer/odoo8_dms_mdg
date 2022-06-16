import time
from openerp.osv import fields, osv
import xlwt
from xlsxwriter.workbook import Workbook
import xlsxwriter
from cStringIO import StringIO
import base64
from openerp import _
import  logging

class ReportStockbyDateWizard(osv.osv):

    """Will launch stock by date report and pass required args"""

    _name = "stock.by.date.wizard"
    _description = "Stock by Date Report"

    _columns = {
        'branch_ids': fields.many2many(
            'res.branch', string='Branch'),
        'warehouse_id': fields.many2one(
            'stock.warehouse', string='Warehouse'),
        'location_ids': fields.many2many(
            'stock.location', string='Locations',
            ),        
        'from_date': fields.date('From Date'),
        'to_date': fields.date('To Date'),
        'product_ids': fields.many2many(
            'product.product', string='Products'),
    }

    def generate_excel_report(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids, context=context)
        print 'data.from_date',data.from_date
        filename = 'filename.xls'
        workbook = xlwt.Workbook(encoding="UTF-8")
        worksheet = workbook.add_sheet('Sheet 1')
        style = xlwt.easyxf('font: bold True, name Arial;')

        self.row_pos = 0

        company_id = self.pool.get('res.company').search(cr, uid, [], limit=1, context=context)
        company_obj = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
        worksheet.write_merge(self.row_pos, 0, self.row_pos, 10, company_obj.name, style)
        self.row_pos += 2

        worksheet.write(self.row_pos, 0, _('Prduct Name'), style)
        worksheet.write(self.row_pos, 1, _('Date'), style)
        worksheet.write(self.row_pos, 2, _('Ref'), style)
        worksheet.write(self.row_pos, 3, _('Location'), style)
        worksheet.write(self.row_pos, 4, _('Source'), style)
        worksheet.write(self.row_pos, 5, _('From/To'), style)
        worksheet.write(self.row_pos, 6, _('Opening'), style)
        worksheet.write(self.row_pos, 7, _('Purchase'), style)
        worksheet.write(self.row_pos, 8, _('Transfer In'), style)
        worksheet.write(self.row_pos, 9, _('Transfer Out'), style)
        worksheet.write(self.row_pos, 10, _('Sales'), style)
        worksheet.write(self.row_pos, 11, _('Adjustment'), style)
        worksheet.write(self.row_pos, 12, _('Closing'), style)
        self.row_pos += 1

        param_product = str(data.product_ids.ids).replace("[","").replace("]","")
        print 'self product ids',str(data.product_ids.ids).replace("[","").replace("]","")
        print 'self location ids', str(data.location_ids.id)
        print 'self branch ids', str(data.branch_ids.id)
        print 'ttt',data.branch_ids.id
        cr.execute("""select *,
                case when f.x_move_type in ('sale_out','sale_return') then f.x_qty end as sales,
                case when f.x_move_type in ('purchase_in','purchase_return') then f.x_qty end as purchase,
                case when f.x_move_type in ('transfer_in','sale_return_in') then f.x_qty end as transfer_in,
                case when f.x_move_type='transfer_out' then f.x_qty end as transfer_out,
                case when f.x_move_type like %s then f.x_qty end as adjustment
                from
                (
                select m.x_id,
                w.name as x_warehouse,
                ((m.x_date at time zone 'utc') at time zone 'asia/rangoon') as time,
                ((m.x_date at time zone 'utc') at time zone 'asia/rangoon')::date as date,
                ll.complete_name as x_location,
                ll.id as x_location_id,
                ll.branch_id as x_branch,
                pp.name as x_product,
                pp.id as x_product_id,
                m.x_source,    
                (select * from get_reference(m.x_source,m.x_id)) as x_ref,
                case when m.x_from is null then m.x_to
                when m.x_to is null then m.x_from
                end as x_team,
                case when m.x_move_in_type is null then m.x_move_out_type
                when m.x_move_out_type is null then m.x_move_in_type
                end as x_move_type,
                d.opening as x_opening,
                d.qty as x_qty,
                d.closing as x_closing
                from stock_movement_data(%s,%s,%s,%s,%s) m
                left join
                (
                select t.name,p.default_code,p.id
                from product_product p,
                product_template t
                where p.product_tmpl_id=t.id
                and p.active=true
                and t.active=true
                )pp on m.x_product_id=pp.id
                left join
                (
                select sl.name as complete_name,sl.id,sl.branch_id
                from stock_location sl where active=true
                and branch_id in (%s)
                )ll on m.x_location_id=ll.id
                left join
                stock_warehouse as w on w.lot_stock_id=m.x_location_id
                left join
                (
                SELECT x_id,x_location_id, x_product_id, x_date
                   , sum(x_balance) OVER (PARTITION BY x_location_id, x_product_id ORDER BY x_date,x_uom) - x_balance as opening,
                   x_balance as qty, sum(x_balance) OVER (PARTITION BY x_location_id, x_product_id ORDER BY x_date,x_uom) as closing
                FROM   stock_movement_data(%s,%s,%s,%s,%s)
                ORDER  BY x_product_id, x_location_id, x_date
                ) d on m.x_location_id=d.x_location_id and m.x_product_id=d.x_product_id  and m.x_date=d.x_date and m.x_id = d.x_id
                order by m.x_location_id,m.x_product_id,m.x_date,m.x_uom
                )f
                where date between %s and %s
                and x_branch in (%s)
                and x_location_id in (%s);""",
                ('%adjustment%',data.from_date,data.to_date,param_product,str(data.location_ids.id),str(data.branch_ids.id),
                 data.branch_ids.id,
                 data.from_date,data.to_date,param_product,str(data.location_ids.id),str(data.branch_ids.id),
                 data.from_date,data.to_date,data.branch_ids.id,data.location_ids.id,))
        report_data = cr.fetchall()
        logging.warning("report_data: %s", report_data)
        for result in report_data:
            worksheet.write(self.row_pos, 0, result[7], style)
            worksheet.write(self.row_pos, 1, result[3], style)
            worksheet.write(self.row_pos, 2, result[10], style)
            worksheet.write(self.row_pos, 3, result[4], style)
            worksheet.write(self.row_pos, 4, result[9], style)
            worksheet.write(self.row_pos, 5, result[11], style)
            worksheet.write(self.row_pos, 6, result[13], style)
            worksheet.write(self.row_pos, 7, result[17], style)
            worksheet.write(self.row_pos, 8, result[18], style)
            worksheet.write(self.row_pos, 9, result[19], style)
            worksheet.write(self.row_pos, 10, result[16], style)
            worksheet.write(self.row_pos, 11, result[20], style)
            worksheet.write(self.row_pos, 12, result[15], style)
            self.row_pos += 1
        fp = StringIO()
        workbook.save(fp)

        record_id = self.pool.get('wizard.excel.report').create(cr, uid, {'excel_file': base64.encodestring(fp.getvalue()),
                                                            'file_name': filename}, context=None)
        fp.close()
        return {'view_mode': 'form',
                'res_id': record_id,
                'res_model': 'wizard.excel.report',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'context': context,
                'target': 'new',
                }

class wizard_excel_report(osv.osv):
    _name= "wizard.excel.report"

    _columns = {
        'excel_file': fields.binary('excel file'),
        'file_name': fields.char('Excel File', size=64)
    }

