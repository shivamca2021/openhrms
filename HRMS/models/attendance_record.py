 # -*- coding: utf-8 -*-

from datetime import datetime
import random

from odoo import api, models, fields, _
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.tools import text_from_html
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo.tools.translate import html_translate


class EvonAttendance(models.Model):

    _name = 'attendance.record'

    checkin_time = fields.Datetime(string='Check-in Time')
    checkout_time = fields.Datetime(string='Check-out Time')
    employee = fields.Many2one("hr.employee", string='Employee')
    total_hours = fields.Float(string='Total Hours', compute='compute_total_worked_hours')
    today = fields.Char(string="Today's Date")

    @api.depends('checkin_time', 'checkout_time')
    def compute_total_worked_hours(self):
        for rec in self:
            if rec.checkin_time and rec.checkout_time:
                total_time_delta = rec.checkout_time - rec.checkin_time
                total_hours = total_time_delta.total_seconds() / 3600  # 3600 seconds in an hour
                hours_and_minutes = round(total_hours, 2)
                rec.total_hours = hours_and_minutes
            else:
                total_time_delta = datetime.now() - rec.checkin_time
                total_hours = total_time_delta.total_seconds() / 3600  # 3600 seconds in an hour
                hours_and_minutes = round(total_hours, 2)
                rec.total_hours = hours_and_minutes
                # rec.total_hours = 0
