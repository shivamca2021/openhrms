# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime
import pytz
from odoo.addons.web.controllers.session import Session


class HrmsCheckoutWizard(models.Model):
    _name = 'hrms.checkout.wiz'
    _description = 'HRMS Checkout Wizard'

    name = fields.Char(string='Name')
    # name = fields.Char(string='Name')
    project_id = fields.Many2one('project.project', string='Project')
    description = fields.Text(string='Description')
    hours_worked = fields.Float(string='Hours Worked')
    role = fields.Selection(
        [('coding', 'Coding'), ('ui_design', 'UI Design'), ('ui_html', 'UI HTML'), ('testing', 'Testing'),
         ('others', 'Others')], default="coding", string='Project Role')

    attendance_checkout_ids = fields.One2many(
        'attendance.checkout.line', 'checkout_wiz_id', string='Check Out')

    @api.model
    def default_get(self, fields):
        res = super(HrmsCheckoutWizard, self).default_get(fields)
        # Get the Indian timezone
        indian_timezone = pytz.timezone('Asia/Kolkata')
        if self._context.get('last_day') == 'yes':
            last_day_attendance = self.env['attendance.record'].search(
                [('employee', '=', self.env.user.employee_id.id)], order='id desc', limit=1)
            res['name'] = last_day_attendance.checkin_time.strftime("%m/%d/%Y, %H:%M:%S")
        # Get the current date and time as a string in the desired format in the Indian timezone
        else:
            res['name'] = datetime.now(indian_timezone).strftime("%m/%d/%Y, %H:%M:%S")
        return res

    @api.model_create_multi
    def create(self, vals_list):
        leads = super(HrmsCheckoutWizard, self).create(vals_list)
        return leads

    def checkout_today(self):
        self.env.user.user_login_today = False
        if self._context.get('last_day') == 'yes':
            self.env.user.action_id = False
            last_day_attendance = self.env['attendance.record'].search(
                [('employee', '=', self.env.user.employee_id.id)], order='id desc', limit=1)
            last_day_attendance.checkout_time = datetime.now()
        self.env['hr.employee'].sudo().browse(self.env.user.employee_id.id).attendance_manual(
            'hr_attendance.hr_attendance_action_my_attendances')
        Session.logout(self)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class AttendanceCheckoutLine(models.Model):
    _name = 'attendance.checkout.line'

    checkout_wiz_id = fields.Many2one('hrms.checkout.wiz', string='Checkout Wizard ID')
    project_id = fields.Many2one('project.project', string='Project')
    description = fields.Text(string='Description')
    hours_worked = fields.Float(string='Hours Worked')
    role = fields.Selection(
        [('coding', 'Coding'), ('ui_design', 'UI Design'), ('ui_html', 'UI HTML'), ('testing', 'Testing'),
         ('others', 'Others')], default="coding", string='Project Role')

    @api.model
    def default_get(self, fields):
        res = super(AttendanceCheckoutLine, self).default_get(fields)
        # res['hours_worked'] = 2.3
        # res['description'] = "somethings"
        print(res)
        return res
