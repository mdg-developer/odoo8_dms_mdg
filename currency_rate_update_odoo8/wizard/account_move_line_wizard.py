# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

#import time
import base64, StringIO, csv
from openerp.osv import orm, fields,osv
from openerp.tools.translate import _
from xlrd import open_workbook
from datetime import datetime
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class account_move_line(osv.osv):
    _inherit = 'account.move.line'
    _columns = {
               'currency_rate':fields.float('Currency Rate',digits_compute=dp.get_precision('Account')),
              
               }