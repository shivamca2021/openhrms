# -- coding: utf-8 --
from odoo import fields, api, models, _
from odoo.exceptions import ValidationError,UserError
from datetime import date

class Service(models.Model):

    _name = 'service.request'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "service_name"

    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.id

    service_name = fields.Char( string="Description", help="Service name")
    employee_id = fields.Many2one('hr.employee', string="Employee", default=_get_employee_id, readonly=True, help="Employee")
    service_date = fields.Datetime(string="Date", default=date.today() ,help="Service date")
    state = fields.Selection([('draft', 'Draft'),
                              ('requested', 'Requested'),
                              ('assign', 'Assigned'),
                              ('check', 'Checked'),
                              ('reject', 'Rejected'),
                              ('approved', 'Approved')], default='draft', tracking=True, help="State")
    service_executer = fields.Many2one('hr.employee', string='Service Executer', help="Service executer")
    read_only = fields.Boolean(string="check field", compute='get_user')
    tester = fields.One2many('service.execute', 'test', string='tester', help="Tester")
    internal_note = fields.Text(string="internal notes", help="Internal Notes")
    service_type = fields.Selection([('reimbursement', 'Reimbursement'),
                                     ('infra_issue', 'Infra issues'),
                                     ('other_Request', 'Other Request')],
                                    string='Type', help="Type for the service request")
    service_product = fields.Many2one('product.product', string='Item For Service', help="Product you want to service")
    name = fields.Char(string='Reference', copy=False, readonly=True,
                       default=lambda self: _('New'))
    
    attach_service = fields.Binary(string="Upload Attachments for Request")
    upload_service = fields.Char(string="Upload Attachments for Request")

    @api.onchange('service_type')
    def onchange_service_type(self):
        for rec in self:
            if rec.service_type == 'reimbursement':
                rec.service_executer = 45

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('service.request')
        return super(Service, self).create(vals)

    @api.depends('read_only')
    def get_user(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('project.group_project_manager'):
            self.read_only = True
        else:
            self.read_only = False

    def submit_reg(self):
        self.ensure_one()
        self.sudo().write({
            'state': 'requested'
        })
        return

    def assign_executer(self):
        self.ensure_one()
        if not self.service_executer:
            raise ValidationError(_("Select Executer For the Requested Service"))
        self.write({
            'state': 'assign'
        })
        vals = {
            'issue': self.service_name,
            'executer': self.service_executer.id,
            'client': self.employee_id.id,
            'executer_product': self.service_product.name,
            'type_service': self.service_type,
            'execute_date': self.service_date,
            'state_execute': self.state,
            'notes': self.internal_note,
            'test': self.id,
        }
        approve = self.env['service.execute'].sudo().create(vals)
        return
    
    def service_approval(self):
        for record in self:
            record.tester.sudo().state_execute = 'approved'
            record.write({
                'state': 'approved'
            })
        return
    
    def service_rejection(self):
        self.write({
            'state': 'reject'
        })
        return


class Executer(models.Model):

    _name = 'service.execute'
    _rec_name = 'issue'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'issue'

    client = fields.Many2one('hr.employee', string="Client", help="Client")
    executer = fields.Many2one('hr.employee', string='Executer', help="Executer")
    issue = fields.Char(string="Issue", help="Issue")
    execute_date = fields.Datetime(string="Date Of Reporting", help="Date of reporting")
    state_execute = fields.Selection([('draft', 'Draft'), ('requested', 'Requested'), ('assign', 'Assigned')
                                 , ('check', 'Checked'), ('reject', 'Rejected'),
                              ('approved', 'Approved')], tracking=True,)
    test = fields.Many2one('service.request', string='test', help="Test")
    notes = fields.Text(string="Internal notes", help="Internal Notes")
    executer_product = fields.Char(string='Service Item', help="service item")
    type_service = fields.Char(string='Service Type', help="Service type")

    def service_check(self):
        self.test.sudo().state = 'check'
        if self.test.service_type == 'reimbursement' and self.user_has_groups('stock_inventory.group_customuser_HR'):
            self.write({
                'state_execute': 'check'
            })
        elif self.test.service_type == 'infra_issue' and self.user_has_groups('stock_inventory.group_customuser_Infra'):
             self.write({
                'state_execute': 'check'
            })
        elif self.test.service_type == 'other_Request' and self.user_has_groups('stock_inventory.group_customuser_HR') or self.user_has_groups('stock_inventory.group_customuser_HR'):
             self.write({
                'state_execute': 'check'
            })  
        else:
            raise UserError('You are Not Authorised to check the service')
