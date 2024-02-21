from odoo import models, fields, api, _
from odoo.http import request
from odoo.exceptions import ValidationError,UserError
from collections import namedtuple, defaultdict
from odoo.addons.resource.models.resource import float_to_time

class CustomHrLeave(models.Model):
    _inherit = 'hr.leave'

    rel_type_approver = fields.Many2many('res.users', 'leave_user_new_table', string="Approver")

    report_field_id = fields.Many2many('res.partner', string="Res Approver")
    supp_approval_id = fields.Many2many('hr.employee', 'hr_leave_employee_tabletwo', string="Notified To")
    # approved_by_id = fields.Many2one('hr.employee', string='Approved By')
    # emp_remaining_leaves_ids = fields.One2many('hr.leave.type','suprem_leaves_id', string="Remaining Leaves")
    emp_remaining_leaves_ids = fields.One2many('hr.leave.allocation','remain_leaves_id', string="Remaining Leaves")
    
    check_leave_from = fields.Char(string="Check Leave From", store=True, compute='compute_leave_from_to')
    check_leave_to = fields.Char(string="Check Leave To", store=True, compute='compute_leave_from_to')

    @api.depends('request_date_from', 'request_date_to')
    def compute_leave_from_to(self):
        for rec in self:
            rec.check_leave_from = rec.request_date_from.strftime('%Y-%m-%d')
            rec.check_leave_to = rec.request_date_to.strftime('%Y-%m-%d')

    # @api.onchange('name')
    @api.onchange('emp_remaining_leaves_ids')
    def get_emp_remaining_leaves_ids(self):
        varx = self.env['hr.leave.allocation'].search([('create_uid','=',self.env.user.id)])
        print("VARX",varx)
        if varx:        
            self.write({'emp_remaining_leaves_ids': [(5, 0, 0)]})        
            self.write({'emp_remaining_leaves_ids': [(0,0,{
                        'name' : rec.name,
                        'duration_display' : rec.duration_display,
                        'leaves_taken' : rec.number_of_days,}) for rec in varx ]})


    @api.onchange('supp_approval_id')
    def get_supp_approval_id(self):
        varc = []
        for rec in self.supp_approval_id.ids:
            supp = self.env['hr.employee'].browse(rec)
            res_parter = self.env['res.partner'].search([('id','=',supp.work_contact_id.id)])
            varc.append(res_parter)
            self.report_field_id = [(4, reh.id) for reh in varc] 

    
    @api.onchange('holiday_status_id')
    def get_rel_type_approver(self):
        self.supp_approval_id = self.employee_id.parent_id.ids
        if self.holiday_status_id.id in (16,19,25,27,28,29):
            self.rel_type_approver = self.holiday_status_id.responsible_id.ids
        if self.holiday_status_id.id in (18,26):    
            hr = self.env['res.users'].browse(18)
            botx = []
            botx.append(hr)
            botx.append(self.employee_id.leave_manager_id)
            self.rel_type_approver = [(4, reh.id) for reh in botx]
        if self.holiday_status_id.id in (17,22,15):
            self.rel_type_approver = self.employee_id.leave_manager_id.ids

    
    def custom_add_follower(self, employee_id):
        print("KINI",self.supp_approval_id.ids)
        if self.supp_approval_id.ids:
            varc = []
            for rec in self.supp_approval_id.ids:
                supp = self.env['hr.employee'].browse(rec)
                res_parter = self.env['res.partner'].search([('id','=',supp.work_contact_id.id)])
                varc.append(res_parter)
            # print("---------------","VARC",varc,type(varc),"------------------")
        employee = self.env['hr.employee'].browse(employee_id)
        if employee.user_id:
            self.message_subscribe(partner_ids = self.report_field_id.ids)


    def action_approve(self):
        res = super(CustomHrLeave, self).action_approve()
        print("PrinTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
        user = self.env.user
        if user.id not in self.rel_type_approver.ids:
            raise UserError("You are Not Authorised to approve leaves.")
        return res
    
    
    @api.model_create_multi
    def create(self, vals_list):
        print("vals_list1",vals_list)
        leave_date_employees = defaultdict(list)
        employee_ids = []
        for values in vals_list:
            if values.get('employee_id'):
                employee_ids.append(values['employee_id'])
                if values.get('date_from') and values.get('date_to'):
                    date_from = fields.Datetime.to_datetime(values['date_from'])
                    date_to = fields.Datetime.to_datetime(values['date_to'])
                    if values['employee_id'] not in leave_date_employees[(date_from, date_to)]:
                        leave_date_employees[(date_from, date_to)].append(values['employee_id'])
        employees = self.env['hr.employee'].browse(employee_ids)
        if self._context.get('leave_compute_date_from_to') and employees:
            employee_leave_date_duration = defaultdict(dict)
            for (date_from, date_to), employee_ids in leave_date_employees.items():
                employee_leave_date_duration[(date_from, date_to)] = self._get_number_of_days_batch(date_from, date_to, employee_ids)
            for values in vals_list:
                employee_id = values.get('employee_id')
                if employee_id and values.get('date_from') and values.get('date_to'):
                    date_from = values.get('date_from')
                    date_to = values.get('date_to')
                    employee = employees.filtered(lambda emp: emp.id == employee_id)
                    attendance_from, attendance_to = self._get_attendances(employee, date_from.date(), date_to.date())
                    hour_from = float_to_time(attendance_from.hour_from)
                    hour_to = float_to_time(attendance_to.hour_to)
                    hour_from = hour_from.hour + hour_from.minute / 60
                    hour_to = hour_to.hour + hour_to.minute / 60

                    values['date_from'] = self._get_start_or_end_from_attendance(hour_from, date_from.date(), employee)
                    values['date_to'] = self._get_start_or_end_from_attendance(hour_to, date_to.date(), employee)
                    values['request_date_from'], values['request_date_to'] = values['date_from'].date(), values['date_to'].date()
                    values['number_of_days'] = employee_leave_date_duration[(date_from, date_to)][values['employee_id']]['days']

        """ Override to avoid automatic logging of creation """
        if not self._context.get('leave_fast_create'):
            leave_types = self.env['hr.leave.type'].browse([values.get('holiday_status_id') for values in vals_list if values.get('holiday_status_id')])
            mapped_validation_type = {leave_type.id: leave_type.leave_validation_type for leave_type in leave_types}

            for values in vals_list:
                employee_id = values.get('employee_id', False)
                leave_type_id = values.get('holiday_status_id')
                # Handle automatic department_id
                if not values.get('department_id'):
                    values.update({'department_id': employees.filtered(lambda emp: emp.id == employee_id).department_id.id})

                # Handle no_validation
                if mapped_validation_type[leave_type_id] == 'no_validation':
                    values.update({'state': 'confirm'})

                if 'state' not in values:
                    # To mimic the behavior of compute_state that was always triggered, as the field was readonly
                    values['state'] = 'confirm' if mapped_validation_type[leave_type_id] != 'no_validation' else 'draft'

                # Handle double validation
                if mapped_validation_type[leave_type_id] == 'both':
                    self._check_double_validation_rules(employee_id, values.get('state', False))
        
        holidays = super(CustomHrLeave, self.with_context(mail_create_nosubscribe=True)).create(vals_list)
        print("holidays : ",holidays)

        for holiday in holidays:
            if not self._context.get('leave_fast_create'):
                # Everything that is done here must be done using sudo because we might
                # have different create and write rights
                # eg : holidays_user can create a leave request with validation_type = 'manager' for someone else
                # but they can only write on it if they are leave_manager_id
                holiday_sudo = holiday.sudo()
                print("created from here1")
                holiday_sudo.custom_add_follower(employee_id)
                if holiday.validation_type == 'manager':
                    holiday_sudo.message_subscribe(partner_ids=holiday.employee_id.leave_manager_id.partner_id.ids)
                if holiday.validation_type == 'no_validation':
                    # Automatic validation should be done in sudo, because user might not have the rights to do it by himself
                    holiday_sudo.action_validate()
                    holiday_sudo.message_subscribe(partner_ids=[holiday._get_responsible_for_approval().partner_id.id])
                    holiday_sudo.message_post(body=_("The time off has been automatically approved"), subtype_xmlid="mail.mt_comment") # Message from OdooBot (sudo)
                elif not self._context.get('import_file'):
                    holiday_sudo.activity_update()
        print("Return holidays : ",holidays)

        #CODE for mail to Approver
        # user = self.env.user
        # force_send = not(self.env.context.get('import_file', False))
        # print(vals_list[0].get('rel_type_approver')[0][-1])
        # mailto = self.env['res.users'].browse(vals_list[0].get('rel_type_approver')[0][-1])
        # email_values = {
        #     'email_to': mailto.self.email,
        #     'email_cc': False,
        #     'auto_delete': True,
        #     'recipient_ids': [],
        #     'partner_ids': [],
        #     'scheduled_date': False,
        # }
        # template = self.env.ref('hrms_dashboard.leave_approval_mail_template').sudo()
        # print("Template   :", template)
        # template.send_mail(user.id, force_send=force_send, raise_exception=True, email_values=email_values)
        # print("Mail Sent.","\n"*10)

        return holidays