 # -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.tools import text_from_html
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo.tools.translate import html_translate


class ResUsers(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    hrms_employee_id = fields.Many2one('hr.employee', string='HRMS Employee')
    user_login_today = fields.Boolean(string='User Login for Today', default=False)
