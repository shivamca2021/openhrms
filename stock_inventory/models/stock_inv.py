# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError
from datetime import date


class StockInventoryApp(models.Model):
    _name = 'stock.inventory'
    _description = 'Stock Inventory'

    name = fields.Char(string="Make Model")
    assets = fields.Selection([('desktop', 'Desktop'),
                              ('laptop','Laptop'),
                              ('monitor', 'Monitor'), 
                              ('keyboard', 'Keyboard'), 
                              ('headphone', 'HeadPhone'),
                              ('webcam', 'WebCam'),
                              ('wifi', 'Wifi Receiver'),
                              ('mobile', 'Mobile Phone'),
                              ('ups', 'UPS'),
                              ('dongle', 'Internet Dongle'),
                              ('ram', 'RAM'),
                              ('ssd', 'SSD'),
                              ('hdd', 'HDD'),
                              ('router', 'Router'),
                              ('switches', 'Switches'),
                              ('printer', 'Printer'),
                              ('cctv_cam', 'CCTV Camera'),
                              ('grpahic_card', 'Graphic Card'),
                              ('ups_battery', 'UPS Battery'),
                              ('accessories', 'Accessories'),], string="Assets")
                              
    processor = fields.Char(string="Processor")
    motherboard = fields.Char(string="Motherboard")
    hdd = fields.Char(string="HDD")
    ram = fields.Char(string="RAM")
    os = fields.Char(string="OS")
    graphic_card = fields.Char(string="Graphic Card")
    serial_number = fields.Char(string="Serial Number")

    model_number = fields.Char(string="Model Number")
    bag = fields.Char(string="Bag")
    charger = fields.Char(string="Charger")

    size = fields.Char(string="Size")
    type = fields.Char(string="Type")

    laptop_Desktop = fields.Char(string="Laptop/Desktop")
    frequency = fields.Char(string="Frequency DDR3/DDR4")

    sata_m2 = fields.Char(string="SATA/M.2")
    company_name = fields.Char(string="Company Name")

    wifi_access = fields.Char(string="WiFi (Access point)")

    in_gb = fields.Selection([('2','2 GB'),('4','4 GB'),('6','6 GB')], string="In GB?")

    description = fields.Char(string="Description")
    seats = fields.Integer(string="Seats")
    state = fields.Selection([('live', 'Live'),('damaged','Damaged'),('all', 'All'), ('deleted', 'Deleted'), ('scrap', 'Scrap')], default='live', string="State")

    assigned_employee_id = fields.Many2one('hr.employee',string='Assigned to')
    

    def get_default_date():
        return date.today()
    assigned_date = fields.Date(string="Assigned Date", default=get_default_date())


    # Confirm buttom mechanism Code 
    def action_confirm(self):
        for rec in self:
            self.state = 'confirmed'

    # Approve buttom mechanism Code 
    def action_approve(self):
        for rec in self:
            self.state = 'done'

    @api.model_create_multi
    def create(self,vals):
        if self.user_has_groups('stock_inventory.group_customuser_HR'):
            raise UserError('You are Not Authorised to Create/Update/Delete')
        return super(StockInventoryApp, self).create(vals)
    
    def write(self,vals):
        if self.user_has_groups('stock_inventory.group_customuser_HR'):
            raise UserError('You are Not Authorised to Create/Update/Delete')
        return super(StockInventoryApp, self).write(vals)
    
    def unlink(self):
        if self.user_has_groups('stock_inventory.group_customuser_HR'):
            raise UserError('You are Not Authorised to Create/Update/Delete')
        return super(StockInventoryApp, self).unlink()