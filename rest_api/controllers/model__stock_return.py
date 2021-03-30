# -*- coding: utf-8 -*-
from .main import *

_logger = logging.getLogger(__name__)


# List of REST resources in current file:
#   (url prefix)               (method)     (action)
# /api/stock.return                GET     - Read all (with optional filters, offset, limit, order, exclude_fields, include_fields)
# /api/stock.return/<id>           GET     - Read one (with optional exclude_fields, include_fields)
# /api/stock.return                POST    - Create one
# /api/stock.return/<id>           PUT     - Update one
# /api/stock.return/<id>           DELETE  - Delete one
# /api/stock.return/<id>/<method>  PUT     - Call method (with optional parameters)


# List of IN/OUT data (json data and HTTP-headers) for each REST resource:

# /api/stock.return  GET  - Read all (with optional filters, offset, limit, order, exclude_fields, include_fields)
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
OUT__stock_return__read_all__SUCCESS_CODE = 200       # editable
#   Possible ERROR CODES:
#       401 'invalid_token'
#       400 'no_access_token'
#   JSON:
#       {
#           "count":   XXX,     # number of returned records
#           "results": [
OUT__stock_return__read_all__SCHEMA = (                 # editable
    'id',
    'name',
    ('sale_team_id', (  # will return dictionary of inner fields
        'id',
        'name',
    )),
    ('from_location', (  # will return dictionary of inner fields
        'id',
        'complete_name',
    )),
    ('to_location', (  # will return dictionary of inner fields
        'id',
        'complete_name',
    )),
    'return_date',
    ('branch_id', (  # will return dictionary of inner fields
        'id',
        'name',
    )),
    'to_return_date',
    'issue_from_optional_location',
    'returner',
    'wh_receiver',
    ('vehicle_id', (  # will return dictionary of inner fields
        'id',
        'name',
    )),
    ('p_line', [(
        'id',
        ('product_id', (  # will return dictionary of inner fields
            'id',
            'name',
        )),
        ('from_location_id', (  # will return dictionary of inner fields
            'id',
            'name',
        )),
        ('to_location_id', (  # will return dictionary of inner fields
            'id',
            'name',
        )),
        ('product_uom', (  # will return dictionary of inner fields
            'id',
            'name',
        )),
        'status',
        'opening_stock_qty',
        'in_stock_qty',
        'assembly_qty',
        'sale_quantity',
        'exchange_qty',
        'return_quantity',
        'onground_quantity',
        'actual_return_quantity',
        'closing_stock_qty',
        'different_qty',
        'miss_qty',
        'expiry_date',
        'remark',
    )]),
)
#           ]
#       }

# /api/stock.return/<id>  GET  - Read one (with optional exclude_fields, include_fields)
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
OUT__stock_return__read_one__SUCCESS_CODE = 200       # editable
#   Possible ERROR CODES:
#       401 'invalid_token'
#       400 'no_access_token'
#       400 'invalid_object_id'
#       404 'not_found_object_in_odoo'
OUT__stock_return__read_one__SCHEMA = (                 # editable
    # (The order of fields of different types can be arbitrary)
    # simple fields (non relational):
    'id',
    'name',
    ('sale_team_id', (  # will return dictionary of inner fields
        'id',
        'name',
    )),
    ('from_location', (  # will return dictionary of inner fields
        'id',
        'complete_name',
    )),
    ('to_location', (  # will return dictionary of inner fields
        'id',
        'complete_name',
    )),
    'return_date',
    ('branch_id', (  # will return dictionary of inner fields
        'id',
        'name',
    )),
    'to_return_date',
    'issue_from_optional_location',
    'returner',
    'wh_receiver',
    ('vehicle_id', (  # will return dictionary of inner fields
        'id',
        'name',
    )),
    ('p_line', [(
        'id',
        ('product_id', (  # will return dictionary of inner fields
            'id',
            'name',
        )),
        ('from_location_id', (  # will return dictionary of inner fields
            'id',
            'name',
        )),
        ('to_location_id', (  # will return dictionary of inner fields
            'id',
            'name',
        )),
        ('product_uom', (  # will return dictionary of inner fields
            'id',
            'name',
        )),
        'status',
        'opening_stock_qty',
        'in_stock_qty',
        'assembly_qty',
        'sale_quantity',
        'exchange_qty',
        'return_quantity',
        'onground_quantity',
        'actual_return_quantity',
        'closing_stock_qty',
        'different_qty',
        'miss_qty',
        'expiry_date',
        'remark',
    )]),
)

# /api/stock.return  POST  - Create one
# IN data:
#   HEADERS:
#       'access_token'
#   DEFAULTS:
#       (optional default values of fields)
DEFAULTS__stock_return__create_one__JSON = {          # editable
            #"some_field_1": some_value_1,
            #"some_field_2": some_value_2,
            #...
}
#   JSON:
#       (fields and its values of created object;
#        don't forget about model's mandatory fields!)
#           ...                                     # editable
# OUT data:
OUT__stock_return__create_one__SUCCESS_CODE = 200     # editable
#   Possible ERROR CODES:
#       401 'invalid_token'
#       400 'no_access_token'
#       409 'not_created_object_in_odoo'
OUT__stock_return__create_one__SCHEMA = (               # editable
    'id',
)

# /api/stock.return/<id>  PUT  - Update one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (fields and new values of updated object)   # editable
#           ...
# OUT data:
OUT__stock_return__update_one__SUCCESS_CODE = 200     # editable
#   Possible ERROR CODES:
#       401 'invalid_token'
#       400 'no_access_token'
#       400 'invalid_object_id'
#       409 'not_updated_object_in_odoo'

# /api/stock.return/<id>  DELETE  - Delete one
# IN data:
#   HEADERS:
#       'access_token'
# OUT data:
OUT__stock_return__delete_one__SUCCESS_CODE = 200     # editable
#   Possible ERROR CODES:
#       401 'invalid_token'
#       400 'no_access_token'
#       400 'invalid_object_id'
#       409 'not_deleted_object_in_odoo'

# /api/stock.return/<id>/<method>  PUT  - Call method (with optional parameters)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (named parameters of method)                # editable
#           ...
# OUT data:
OUT__stock_return__call_method__SUCCESS_CODE = 200    # editable
#   Possible ERROR CODES:
#       401 'invalid_token'
#       400 'no_access_token'
#       400 'invalid_object_id'
#       501 'method_not_exist_in_odoo'
#       409 'not_called_method_in_odoo'


# HTTP controller of REST resources:

class ControllerREST(http.Controller):
    
    # Read all (with optional filters, offset, limit, order, exclude_fields, include_fields):
    @http.route('/api/stock.return', methods=['GET'], type='http', auth='none')
    @check_permissions
    def api__stock_return__GET(self, **kw):
        return wrap__resource__read_all(
            modelname = 'stock.return',
            default_domain = [],
            success_code = OUT__stock_return__read_all__SUCCESS_CODE,
            OUT_fields = OUT__stock_return__read_all__SCHEMA
        )
    
    # Read one (with optional exclude_fields, include_fields):
    @http.route('/api/stock.return/<id>', methods=['GET'], type='http', auth='none')
    @check_permissions
    def api__stock_return__id_GET(self, id, **kw):
        return wrap__resource__read_one(
            modelname = 'stock.return',
            id = id,
            success_code = OUT__stock_return__read_one__SUCCESS_CODE,
            OUT_fields = OUT__stock_return__read_one__SCHEMA
        )
    
    # Create one:
    @http.route('/api/stock.return', methods=['POST'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__stock_return__POST(self, **kw):
        return wrap__resource__create_one(
            modelname = 'stock.return',
            default_vals = DEFAULTS__stock_return__create_one__JSON,
            success_code = OUT__stock_return__create_one__SUCCESS_CODE,
            OUT_fields = OUT__stock_return__create_one__SCHEMA
        )
    
    # Update one:
    @http.route('/api/stock.return/<id>', methods=['PUT'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__stock_return__id_PUT(self, id, **kw):
        return wrap__resource__update_one(
            modelname = 'stock.return',
            id = id,
            success_code = OUT__stock_return__update_one__SUCCESS_CODE
        )
    
    # Delete one:
    @http.route('/api/stock.return/<id>', methods=['DELETE'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__stock_return__id_DELETE(self, id, **kw):
        return wrap__resource__delete_one(
            modelname = 'stock.return',
            id = id,
            success_code = OUT__stock_return__delete_one__SUCCESS_CODE
        )
    
    # Call method (with optional parameters):
    @http.route('/api/stock.return/<id>/<method>', methods=['PUT'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__stock_return__id__method_PUT(self, id, method, **kw):
        return wrap__resource__call_method(
            modelname = 'stock.return',
            id = id,
            method = method,
            success_code = OUT__stock_return__call_method__SUCCESS_CODE
        )
