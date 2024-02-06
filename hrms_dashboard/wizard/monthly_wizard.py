# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime,date
import pytz


class MonthlyAttDataWizard(models.TransientModel):
    _name = 'monthly.attendance.wizard'
    _description = 'Monthly Attendance Wizard'

    def get_years():
        year_list = []
        for i in range(2020, (date.today().year)+1):
            year_list.append((str(i), str(i)))
        return year_list
    
    def get_default_year():
        return str(date.today().year)
    
    def get_default_month():
        return str(date.today().month)
    
    curr_month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), 
                        ('4', 'April'),('5', 'May'), ('6', 'June'), 
                        ('7', 'July'), ('8', 'August'), ('9', 'September'), 
                        ('10', 'October'), ('11', 'November'), ('12', 'December'),], 
                        default = get_default_month(),
                        string='Month')
    
    curr_year = fields.Selection(get_years(), default=get_default_year(), string='Year')

    def get_wizard_monthdata(self):
        return self.env['monthly.attendance.data'].view_monthly_attendance_data(self.curr_month, self.curr_year)
