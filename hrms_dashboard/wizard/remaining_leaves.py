# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime,date
import pytz


class GetRemainingLeavesonForm(models.Model):
    _name = 'remaining.leaves.wizard'
    _description = 'Remaining Leaves Wizard'

    wizard_emp_id = fields.Many2one('hr.employee',string='Employee ID')
    wizard_leave_ids = fields.One2many('hr.leave.allocation','wizard_leave_id',string=' Wizard Remaining Leaves' )
    
    display_name = fields.Char(string="Display Name")
    duration_display = fields.Char(string="Duration Display")
    leaves_taken = fields.Float(string="Leaves Taken")
    
    @api.onchange('wizard_leave_ids')
    def get_emp_remaining_leaves_ids(self):
        varx = self.env['hr.leave.allocation'].search([('employee_id', '=', self.wizard_emp_id.id)])
        print("VARX",varx)
        if varx:         
            self.write({'wizard_leave_ids': [(0,0,{
                                                    'display_name' : rec.name,
                                                    'duration_display' : rec.duration_display,
                                                    'leaves_taken' : rec.leaves_taken,}) for rec in varx ]})
