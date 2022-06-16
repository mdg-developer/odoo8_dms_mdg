# -*- coding: utf-8 -*-
from .main import *

_logger = logging.getLogger(__name__)


# List of REST resources in current file:
#   (url prefix)                (method)     (action)
# /api/point.history                GET     - Read all (with optional filters, offset, limit, order)
# /api/point.history/<id>           GET     - Read one
# /api/point.history                POST    - Create one
# /api/point.history/<id>           PUT     - Update one
# /api/point.history/<id>           DELETE  - Delete one
# /api/point.history/<id>/<method>  PUT     - Call method (with optional parameters)


# List of IN/OUT data (json data and HTTP-headers) for each REST resource:

# /api/point.history  GET  - Read all (with optional filters, offset, limit, order)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (optional filters (Odoo domain), offset, limit, order)
#           {                                       # editable
#               "filters": [('some_field_1', '=', some_value_1), ('some_field_2', '!=', some_value_2), ...],
#               "offset":  XXX,
#               "limit":   XXX,
#               "order":   "list_of_fields"  # default 'name asc'
#           }
# OUT data:
OUT__point_history__read_all__SUCCESS_CODE = 200      # editable
#   JSON:
#       {
#           "count":   XXX,     # number of returned records
#           "results": [
OUT__point_history__read_all__SCHEMA = (                # editable
    'id',
    'name',
    ('customer_id', (
        'id',
        'name',
    )),                          
)
#           ]
#       }

# /api/point.history/<id>  GET  - Read one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (optional parameter 'search_field' for search object not by 'id' field)
#           {"search_field": "some_field_name"}     # editable
# OUT data:
OUT__point_history__read_one__SUCCESS_CODE = 200      # editable
OUT__point_history__read_one__SCHEMA = (                # editable
    # (The order of fields of different types maybe arbitrary)
    # simple fields (non relational):
    'id',
    'name',
    ('customer_id', (
        'id',
        'name',
    )),     
)

# /api/point.history  POST  - Create one
# IN data:
#   HEADERS:
#       'access_token'
#   DEFAULTS:
#       (optional default values of fields)
DEFAULTS__point_history__create_one__JSON = {         # editable
            #"some_field_1": some_value_1,
            #"some_field_2": some_value_2,
            #...
}
#   JSON:
#       (fields and its values of created object;
#        don't forget about model's mandatory fields!)
#           ...                                     # editable
# OUT data:
OUT__point_history__create_one__SUCCESS_CODE = 200    # editable
OUT__point_history__create_one__SCHEMA = (              # editable
    'partner_id'
)

# /api/point.history/<id>  PUT  - Update one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (fields and new values of updated object)   # editable
#           ...
# OUT data:
OUT__point_history__update_one__SUCCESS_CODE = 200    # editable

# /api/point.history/<id>  DELETE  - Delete one
# IN data:
#   HEADERS:
#       'access_token'
# OUT data:
OUT__point_history__delete_one__SUCCESS_CODE = 200    # editable

# /api/point.history/<id>/<method>  PUT  - Call method (with optional parameters)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (named parameters of method)                # editable
#           ...
# OUT data:
OUT__point_history__call_method__SUCCESS_CODE = 200   # editable


# HTTP controller of REST resources:

class ControllerREST(http.Controller):
    
    # Read all (with optional filters, offset, limit, order):
    @http.route('/api/point.history', methods=['GET'], type='http', auth='none')
    @check_permissions
    def api__point_history__GET(self, **kw):
        return wrap__resource__read_all(
            modelname = 'point.history',
            default_domain = [],
            success_code = OUT__point_history__read_all__SUCCESS_CODE,
            OUT_fields = OUT__point_history__read_all__SCHEMA
        )
    
    # Read one:
    @http.route('/api/point.history/<id>', methods=['GET'], type='http', auth='none')
    @check_permissions
    def api__point_history__id_GET(self, id, **kw):
        return wrap__resource__read_one(
            modelname = 'point.history',
            id = id,
            success_code = OUT__point_history__read_one__SUCCESS_CODE,
            OUT_fields = OUT__point_history__read_one__SCHEMA
        )
    
    # Create one:
    @http.route('/api/point.history', methods=['POST'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__point_history__POST(self, **kw):
        return wrap__resource__create_one(
            modelname = 'point.history',
            default_vals = DEFAULTS__point_history__create_one__JSON,
            success_code = OUT__point_history__create_one__SUCCESS_CODE,
            OUT_fields = OUT__point_history__create_one__SCHEMA
        )
    
    # Update one:
    @http.route('/api/point.history/<id>', methods=['PUT'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__point_history__id_PUT(self, id, **kw):
        return wrap__resource__update_one(
            modelname = 'point.history',
            id = id,
            success_code = OUT__point_history__update_one__SUCCESS_CODE
        )
    
    # Delete one:
    @http.route('/api/point.history/<id>', methods=['DELETE'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__point_history__id_DELETE(self, id, **kw):
        return wrap__resource__delete_one(
            modelname = 'point.history',
            id = id,
            success_code = OUT__point_history__delete_one__SUCCESS_CODE
        )
    
    # Call method (with optional parameters):
    @http.route('/api/point.history/<id>/<method>', methods=['PUT'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__point_history__id__method_PUT(self, id, method, **kw):
        return wrap__resource__call_method(
            modelname = 'point.history',
            id = id,
            method = method,
            success_code = OUT__point_history__call_method__SUCCESS_CODE
        )
