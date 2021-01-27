# -*- coding: utf-8 -*-
from .main import *

_logger = logging.getLogger(__name__)


# List of REST resources in current file:
#   (url prefix)               (method)     (action)
# /api/weekly.noti                GET     - Read all (with optional filters, offset, limit, order, exclude_fields, include_fields)
# /api/weekly.noti/<id>           GET     - Read one (with optional exclude_fields, include_fields)
# /api/weekly.noti                POST    - Create one
# /api/weekly.noti/<id>           PUT     - Update one
# /api/weekly.noti/<id>           DELETE  - Delete one
# /api/weekly.noti/<id>/<method>  PUT     - Call method (with optional parameters)


# List of IN/OUT data (json data and HTTP-headers) for each REST resource:

# /api/weekly.noti  GET  - Read all (with optional filters, offset, limit, order, exclude_fields, include_fields)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (optional filters (Odoo domain), offset, limit, order, exclude_fields, include_fields)
#           {                                       # editable
#               "filters": [('some_field_1', '=', some_value_1), ('some_field_2', '!=', some_value_2), ...],
#               "offset":  XXX,
#               "limit":   XXX,
#               "order":   "list_of_fields",  # default 'name asc'
#               "exclude_fields": ["some_field_1", "some_field_2", ...],
#                                   # "__all_fields__" excludes all fields from predefined schema
#               "include_fields": ["some_field_1", "some_field_2", ...]
#           }
# OUT data:
OUT__weekly_noti__read_all__SUCCESS_CODE = 200       # editable
#   Possible ERROR CODES:
#       401 'invalid_token'
#       400 'no_access_token'
#   JSON:
#       {
#           "count":   XXX,     # number of returned records
#           "results": [
OUT__weekly_noti__read_all__SCHEMA = (                 # editable
    'id',
    ('partner_id', (
        'id',
        'name',
    )),
    ('notified_days_ids', [(
        'id',
        'name',
    )]),
    'message'                                  
)
#           ]
#       }

# /api/weekly.noti/<id>  GET  - Read one (with optional exclude_fields, include_fields)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (optional search_field, exclude_fields, include_fields)
#           {                                       # editable
#               "search_field": "some_field_name" # for searching object not by 'id' field
#               "exclude_fields": ["some_field_1", "some_field_2", ...],
#                                   # "__all_fields__" excludes all fields from predefined schema
#               "include_fields": ["some_field_1", "some_field_2", ...]
#           }
# OUT data:
OUT__weekly_noti__read_one__SUCCESS_CODE = 200       # editable
#   Possible ERROR CODES:
#       401 'invalid_token'
#       400 'no_access_token'
#       400 'invalid_object_id'
#       404 'not_found_object_in_odoo'
OUT__weekly_noti__read_one__SCHEMA = (                 # editable
    # (The order of fields of different types can be arbitrary)
    # simple fields (non relational):
    'id',
    ('partner_id', (
        'id',
        'name',
    )),
    ('notified_days_ids', [(
        'id',
        'name',
    )]),
    'message'  
)

# /api/weekly.noti  POST  - Create one
# IN data:
#   HEADERS:
#       'access_token'
#   DEFAULTS:
#       (optional default values of fields)
DEFAULTS__weekly_noti__create_one__JSON = {          # editable
            #"some_field_1": some_value_1,
            #"some_field_2": some_value_2,
            #...
}
#   JSON:
#       (fields and its values of created object;
#        don't forget about model's mandatory fields!)
#           ...                                     # editable
# OUT data:
OUT__weekly_noti__create_one__SUCCESS_CODE = 200     # editable
#   Possible ERROR CODES:
#       401 'invalid_token'
#       400 'no_access_token'
#       409 'not_created_object_in_odoo'
OUT__weekly_noti__create_one__SCHEMA = (               # editable
    'id',
)

# /api/weekly.noti/<id>  PUT  - Update one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (fields and new values of updated object)   # editable
#           ...
# OUT data:
OUT__weekly_noti__update_one__SUCCESS_CODE = 200     # editable
#   Possible ERROR CODES:
#       401 'invalid_token'
#       400 'no_access_token'
#       400 'invalid_object_id'
#       409 'not_updated_object_in_odoo'

# /api/weekly.noti/<id>  DELETE  - Delete one
# IN data:
#   HEADERS:
#       'access_token'
# OUT data:
OUT__weekly_noti__delete_one__SUCCESS_CODE = 200     # editable
#   Possible ERROR CODES:
#       401 'invalid_token'
#       400 'no_access_token'
#       400 'invalid_object_id'
#       409 'not_deleted_object_in_odoo'

# /api/weekly.noti/<id>/<method>  PUT  - Call method (with optional parameters)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (named parameters of method)                # editable
#           ...
# OUT data:
OUT__weekly_noti__call_method__SUCCESS_CODE = 200    # editable
#   Possible ERROR CODES:
#       401 'invalid_token'
#       400 'no_access_token'
#       400 'invalid_object_id'
#       501 'method_not_exist_in_odoo'
#       409 'not_called_method_in_odoo'


# HTTP controller of REST resources:

class ControllerREST(http.Controller):
    
    # Read all (with optional filters, offset, limit, order, exclude_fields, include_fields):
    @http.route('/api/weekly.noti', methods=['GET'], type='http', auth='none')
    @check_permissions
    def api__weekly_noti__GET(self, **kw):
        return wrap__resource__read_all(
            modelname = 'weekly.noti',
            default_domain = [],
            success_code = OUT__weekly_noti__read_all__SUCCESS_CODE,
            OUT_fields = OUT__weekly_noti__read_all__SCHEMA
        )
    
    # Read one (with optional exclude_fields, include_fields):
    @http.route('/api/weekly.noti/<id>', methods=['GET'], type='http', auth='none')
    @check_permissions
    def api__weekly_noti__id_GET(self, id, **kw):
        return wrap__resource__read_one(
            modelname = 'weekly.noti',
            id = id,
            success_code = OUT__weekly_noti__read_one__SUCCESS_CODE,
            OUT_fields = OUT__weekly_noti__read_one__SCHEMA
        )
    
    # Create one:
    @http.route('/api/weekly.noti', methods=['POST'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__weekly_noti__POST(self, **kw):
        return wrap__resource__create_one(
            modelname = 'weekly.noti',
            default_vals = DEFAULTS__weekly_noti__create_one__JSON,
            success_code = OUT__weekly_noti__create_one__SUCCESS_CODE,
            OUT_fields = OUT__weekly_noti__create_one__SCHEMA
        )
    
    # Update one:
    @http.route('/api/weekly.noti/<id>', methods=['PUT'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__weekly_noti__id_PUT(self, id, **kw):
        return wrap__resource__update_one(
            modelname = 'weekly.noti',
            id = id,
            success_code = OUT__weekly_noti__update_one__SUCCESS_CODE
        )
    
    # Delete one:
    @http.route('/api/weekly.noti/<id>', methods=['DELETE'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__weekly_noti__id_DELETE(self, id, **kw):
        return wrap__resource__delete_one(
            modelname = 'weekly.noti',
            id = id,
            success_code = OUT__weekly_noti__delete_one__SUCCESS_CODE
        )
    
    # Call method (with optional parameters):
    @http.route('/api/weekly.noti/<id>/<method>', methods=['PUT'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__weekly_noti__id__method_PUT(self, id, method, **kw):
        return wrap__resource__call_method(
            modelname = 'weekly.noti',
            id = id,
            method = method,
            success_code = OUT__weekly_noti__call_method__SUCCESS_CODE
        )
