# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re

import odoo
from odoo import http
from odoo.http import dispatch_rpc, request, Response
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


DBNAME_PATTERN = '^[a-zA-Z0-9][a-zA-Z0-9_.-]+$'


class Onnasoft(http.Controller):
    
    @http.route('/onnasoft_admin/ping', type='http', auth='none', csrf=False)
    def ping(self, **kwargs):
        return Response(
            '{"status":"ok"}',
            content_type='application/json',
            status=200
        )
    
    @http.route('/onnasoft_admin/database/create', type='http', auth="none", methods=['POST'], csrf=False)
    def create(self, master_pwd, name, lang, password, **post):
        try:
            insecure = odoo.tools.config.verify_admin_password('admin')
            if insecure and master_pwd:
                dispatch_rpc('db', 'change_admin_password', ["admin", master_pwd])

            if not re.match(DBNAME_PATTERN, name):
                return self._json_error("Invalid database name. Use only letters, numbers, underscores, hyphens, or dots.")

            country_code = post.get('country_code') or False
            dispatch_rpc('db', 'create_database', [
                master_pwd,
                name,
                bool(post.get('demo')),
                lang,
                password,
                post['login'],
                country_code,
                post['phone']
            ])

            credential = {'login': post['login'], 'password': password, 'type': 'password'}
            request.session.authenticate(name, credential)
            request.session.db = name

            return Response(
                '{"status": "success", "message": "Database created", "db": "%s"}' % name,
                content_type='application/json',
                status=200
            )
        except Exception as e:
            _logger.exception("Database creation error.")
            return self._json_error(f"Database creation error: {str(e)}")

    def _json_error(self, message):
        return Response(
            '{"status": "error", "message": "%s"}' % message.replace('"', '\\"'),
            content_type='application/json',
            status=400
        )