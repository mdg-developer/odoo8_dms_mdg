from openerp import models,fields,api,_
import logging

_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = 'res.users'

    device_ids = fields.One2many(comodel_name="one_signal_notification.users_device_ids",
                                 inverse_name="user_id", string="Device Ids", required=False, )


class OneSignalDeviceIDs(models.Model):
    _name = 'one_signal_notification.users_device_ids'
    _rec_name = 'name'
    _description = 'one signal notification users device ids'
    _order = "active desc, company_id, user_id"

    @api.model
    def _get_company(self):
        return self.env.user.company_id

    name = fields.Char(string="Name", required=False, help="One Signal-Id for the device")
    user_id = fields.Many2one(comodel_name="res.users", string="User", required=False, )
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True, default=_get_company)
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def create(self, values):
        name = values.get("name")
        user_id = values.get("user_id")
        company_id = values.get("company_id")
        search_condition = [
            '|',
            ("name", "=", name),
            ("user_id", "=", user_id),
            ("company_id", "=", company_id),
            ("active", "=", True)
        ]
        old_record_sets = self.search(search_condition)
        for old_record in old_record_sets:
            old_record.write({'active': False})
        return super(OneSignalDeviceIDs, self).create(values)

    @api.model
    def update_one_signal_device(self, dictionary):
        """
        This method is using in the Java APIs
        Update the one signal device id for user
        :param dictionary: dictionary
        :return: Json object
        a.	Input Request
            i.	denali_model = "one_signal_notification.users_device_ids"
            ii.	denali_method = "update_one_signal_device"
            iii.	denali_parameters = [{ 'device_id': '78', 'operation': "login"}]
            Note:  operation must be ['login', 'logout']
        b.	Response:
            i.	On- Success: {'active': False, 'user_id': 601, 'id': 5, 'device_id': '78'}
            ii.	On-Failure:  -1 --> In-sufficient Data
                             -2 --> Exception Raised


        """
        _logger.info("Update the One signal device for users and Input" + str(dictionary))
        return_result = -1  # In-sufficient data
        device_id = dictionary.get('device_id', False)
        operation = dictionary.get('operation', False)
        if device_id and operation:
            try:
                if operation == "login":
                    current_dictionary = {
                        'name': device_id,
                        'user_id': self.env.uid,
                        'company_id': self.env.user.company_id.id}
                    current_record = self.sudo().create(current_dictionary)
                    return_result = {
                        'id': current_record.id,
                        'device_id': current_record.name,
                        'user_id': current_record.user_id.id,
                        'active': current_record.active
                    }
                elif operation == "logout":
                    search_condition = [
                        ("name", "=", device_id),
                        ("company_id", "=", self.env.user.company_id.id),
                        ("active", "=", True)]
                    record_set = self.sudo().search(search_condition)
                    for current_record in record_set:
                        current_record.sudo().write({"active": False})
                        return_result = {
                            'id': current_record.id,
                            'device_id': current_record.name,
                            'user_id': current_record.user_id.id,
                            'active': current_record.active
                        }
            except Exception, e:
                _logger.info("\n Exception raised one_signal_notification --> models --> "
                             "res_users.py update_one_signal_device()" + str(e))
                return_result = -2  # Exception Raised
        return return_result

