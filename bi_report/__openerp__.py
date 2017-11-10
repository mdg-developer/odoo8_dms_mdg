# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    'name' : 'BI Report',
    'version' : '1.0',
    'author': 'seventh computing',
    'website': 'http://www.7thcomputing.com',
    'category' : 'Reporting',
    'depends' : ["base","sale","ms_mobile_sale"],
    'description': """
    Product for OpenERP
    = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    Features:
    1. Business Intelligent Report

    """,
    'data': [
        'views/mobile_report_view.xml',
         'views/customer_visit_report_view.xml',
         'views/stock_history_view.xml',
         'views/sku_by_customer_view.xml',
         'views/sku_by_category_view.xml',
      #   'views/stock_different_report_view.xml',
         'views/invoice_report_view.xml',
         'views/sale_report_veiw.xml'

                ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: