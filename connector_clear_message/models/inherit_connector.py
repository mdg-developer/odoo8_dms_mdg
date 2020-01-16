# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from datetime import datetime, timedelta

from openerp import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)

class QueueJob(models.Model):
    
    _inherit='queue.job'
    
    @api.multi
    def clear_message(self):
        result = _('')
        for job in self:
            self.env.cr.execute("update queue_job set result =%s where id =%s",(result,job.id,))
        return True    
    
QueueJob()