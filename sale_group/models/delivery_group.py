import itertools
import math
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

import logging

_logger = logging.getLogger(__name__)


class delivery_group(models.Model):
    _name = "delivery.group"
    description = "Delivery Group"

    name = fields.Char(string='Delivery Group Name', index=True)
    active = fields.Boolean(string='Active',
                            default=True)
    delivery_line = fields.One2many('delivery.group.line', 'delivery_id', string='Delivery Lines',
                                    copy=True)

    @api.multi
    def action_retrive(self):
        for line in self.delivery_line:
            line.unlink()

        self.env.cr.execute("""select s.id as state_id,s.name as state_name,c.id as city_id,c.name as city_name,t.id as township_id,t.name as township_name 
        from res_country_state s,
        res_city c, res_township t
        where s.id=c.state_id and t.city=c.id
        order by s.name,c.name,t.name""")
        result = self.env.cr.dictfetchall()
        g_vals = {}
        delivery_line = []
        g_vals['name'] = self.name
        g_vals['active'] = self.active
        g_vals['delivery_line'] = []
        for res in result:
            _logger.info("Result:%s", res)
            g_vals['delivery_line'].append([0, False, {
                'name': self.name or '',
                'delivery_id': self.id,
                'state_id': res['state_id'],
                'city_id': res['city_id'],
                'township_id': res['township_id']
            }])

        new_id = self.write(g_vals)
        _logger.info("Final Result:%s", g_vals['delivery_line'])
        return {'value': {'delivery_line': g_vals['delivery_line']}}


class delivery_group_line(models.Model):
    _name = "delivery.group.line"
    _description = "Delivery Line"

    name = fields.Text(string='Description', required=False)
    delivery_id = fields.Many2one('delivery.group', string='Delivery Reference')
    state_id = fields.Many2one('res.country.state', string='State')
    city_id = fields.Many2one('res.city', string='City')
    township_id = fields.Many2one('res.township', string='Township')
    delivery_team_id = fields.Many2one('crm.case.section', string='Delivery Team')