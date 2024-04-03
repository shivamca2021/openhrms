# -*- coding: utf-8 -*-

import re
import werkzeug
import itertools
import pytz
import babel.dates
from collections import OrderedDict

from odoo import http, fields, tools
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.http import request
from odoo.osv import expression
from odoo.tools import html2plaintext
from odoo.tools.misc import get_lang
from odoo.tools import sql
from odoo.addons.portal.controllers.web import Home
from odoo.addons.web.controllers.session import Session
from datetime import datetime,date


class HrmsHome(Home):

    # Force website=True + auth='public', required for login form layout
    @http.route(website=True, auth="public", sitemap=False)
    def web_login(self, *args, **kw):
        response = super().web_login(*args, **kw)
        print("Response_Status_Code : ",response.status_code)
        last_day_attendance = request.env['attendance.record'].sudo().search([('employee', '=', request.env.user.employee_id.id)],
                                                                   order='id desc', 
                                                                   limit=1)
        # if len(last_day_attendance) == 1 and not last_day_attendance.checkout_time:
        #     request.env.user.action_id = request.env.ref('HRMS.act_hrms_checkout').id
        #     last_day_attendance.checkout_time = datetime.now()
        
        if response.status_code == 303 and request.env.user.employee_id and not request.env.user.user_login_today:
            request.env.user.write({'user_login_today': True})
            request.env['hr.employee'].sudo().browse(request.env.user.employee_id.id).attendance_manual(
                'hr_attendance.hr_attendance_action_my_attendances')
        
        return response


class HrmsSession(Session):

    @http.route(type='http', auth="user")
    def logout(self, redirect='/web'):
        response = super().logout(redirect=redirect)
        return response
