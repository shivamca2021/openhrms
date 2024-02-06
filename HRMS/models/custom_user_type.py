from datetime import datetime
from odoo import api, models, fields, _



class customUserType(models.Model):
    _name = 'custom.usertype'
    _description = 'Custom User Type'

    name = fields.Char(string="Name")
    type = fields.Char(string="Type")