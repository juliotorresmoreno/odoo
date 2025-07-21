from odoo import http
from odoo.http import Response

class OnnasoftAdmin(http.Controller):
  @http.route('/onnasoft_admin/ping', type='http', auth='none', csrf=False)
  def ping(self, **kwargs):
    return Response(
        '{"status":"ok"}',
        content_type='application/json',
        status=200
    )
