# -*- coding: utf-8 -*-

from datetime import datetime
import random

from odoo import api, models, fields, _
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.tools import text_from_html
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo.tools.translate import html_translate
import pytz


class HrmsEmployee(models.Model):
    _inherit = "hr.employee"

    def get_current_uid(self):
        if self.env.context.get('uid', False):
            self.current_user_id = self.env['res.users'].browse(self.env.context.get('uid', False))
        else:
            self.current_user_id = False

    def compute_hr_admin(self):
        # current_user_id = self.env['res.users'].browse(self.env.context.get('uid', False))
        if self.env.user.has_group('hr.group_hr_manager') or self.address_home_id.id == self.env.user.partner_id.id:
            self.is_hr_admin = True
        else:
            self.is_hr_admin = False

    employee_login_state = fields.Boolean(string='Login-out')
    pan_number = fields.Char(string='PAN Number')
    adhar_number = fields.Char(string='Adhar Number')
    skype_id = fields.Char(string='Skype ID')
    career_start_date = fields.Date(string='Career Start Date')
    relevant_experience = fields.Float(string='Relevant Experience')
    current_user_id = fields.Many2one('res.users', compute='get_current_uid', string='Employee ID Computed')
    is_hr_admin = fields.Boolean(compute='compute_hr_admin', string='Employee HR Admin Computed')

    father_husband_name = fields.Selection([
        ('father', 'Father'),
        ('husband', 'Husband'),],string="Father/Husband Name")
    primary_contact_no = fields.Char(string="Primary Contact Number")
    emergency_contact_no = fields.Char(string="Emergency Contact No.")
    emergency_contact_name = fields.Char(string="Emergency Contact Name.")
    rel_type = fields.Char(string="Relation")
    current_address = fields.Char(string="Current Address")
    current_city = fields.Char(string="City")
    current_state = fields.Char(String="State")
    permanent_address = fields.Char(string="Permanent Address")
    personal_mailid = fields.Char(string="Personal Email")
    official_mailid = fields.Char(string="Official Email")
    custom_pan = fields.Char(string="PAN")
    c_adhaarnumber = fields.Char(string="Adhaar Number")
    c_dob = fields.Date(string="Date Of Birth")
    c_blood_grp = fields.Char(string="Blood Group")
    c_emp_doj = fields.Date(string="Date of Joining")
    c_emp_code = fields.Char(string="Employee Code")
    c_relevant_exp = fields.Char(string="Relevant Experience in Years")
    c_marital_status = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),],string="Marital Status")
    c_type_vehicle = fields.Selection([
        ('two wheeler', 'Two Wheeler'),
        ('four wheeler', 'Four Wheeler'),
        ('both', 'Both'),
        ('none', 'None'),],string="Type Of Vehicle")
    c_registration_no = fields.Char(string="Vehicle Registration Number")
    c_HR_mailid = fields.Char(string="Prev Co.HR Email ID")
    c_HR_contact_no = fields.Char(string="Prev Co.HR Contact No")
    upload_image = fields.Binary(string="Upload your picture")
    upload_image_char = fields.Char()



    @api.model
    def update_attendance_today(self):
        self.env.user.user_login_today = False

    def attendance_manual(self, next_action, entered_pin=None):
        defaults = super(HrmsEmployee, self).attendance_manual(next_action, entered_pin)
        if self.attendance_state == 'checked_in':
            vals = {
                'checkin_time': datetime.now(),
                'employee': self.id,
                'today': datetime.now().strftime("%d")

            }
            attendance_rec = self.env['attendance.record'].search(
                [('today', '=', datetime.now().strftime("%d")),
                 ('employee', '=', self.env.user.employee_id.id)])
            if len(attendance_rec) == 0:
                last_day_attendance = self.env['attendance.record'].search([('employee', '=', self.env.user.employee_id.id)], order='id desc', limit=1)
                if not last_day_attendance.checkout_time:
                    last_day_attendance.checkout_time = datetime.now()
                self.env['attendance.record'].create(vals)
            else:
                pass
        elif self.attendance_state == 'checked_out':
            attendance_rec = self.env['attendance.record'].search(
                [('today', '=', datetime.now().strftime("%d"))], limit=1)
            attendance_rec.checkout_time = datetime.now()
        return defaults


