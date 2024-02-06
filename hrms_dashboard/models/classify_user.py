from odoo import models, fields, api, _
import time
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError,UserError
import calendar

class ClassifyUserType(models.Model):
    _inherit = 'res.users'

    classify_usertype = fields.Selection([('admin', 'Admin'),('hr', 'HR'),('employee','Employee'),('infra', 'Infra')],
        string='Type', default='employee')
    
class AttendanceUser(models.Model):
    _inherit = 'hr.attendance'

    user_id = fields.Many2one('res.users', related='employee_id.user_id')
    current_user = fields.Many2one('res.users', default=lambda self: self.env.user.id)

    check_in_sub = fields.Char(string="Check Present", store=True, compute='compute_check_in_sub')

    @api.depends('check_in')
    def compute_check_in_sub(self):
        for rec in self:
            rec.check_in_sub = rec.check_in.strftime('%Y-%m-%d')


class UserHolidaycompute(models.Model):
    _inherit = 'resource.calendar.leaves'

    check_in_sub = fields.Char(string="Check Present", store=True, compute='compute_check_in_sub')

    @api.depends('date_from')
    def compute_check_in_sub(self):
        for rec in self:
            rec.check_in_sub = rec.date_from.strftime('%Y-%m-%d')


class MonthlyAttendancedata(models.Model):
    _name = 'monthly.attendance.data'
    _description = 'Monthly Attendance Data'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    day_1 = fields.Char("1")
    day_2 = fields.Char("2")
    day_3 = fields.Char("3")
    day_4 = fields.Char("4")
    day_5 = fields.Char("5")
    day_6 = fields.Char("6")
    day_7 = fields.Char("7")
    day_8 = fields.Char("8")
    day_9 = fields.Char("9")
    day_10 = fields.Char("10")
    day_11 = fields.Char("11")
    day_12 = fields.Char("12")
    day_13 = fields.Char("13")
    day_14 = fields.Char("14")
    day_15 = fields.Char("15")
    day_16 = fields.Char("16")
    day_17 = fields.Char("17")
    day_18 = fields.Char("18")
    day_19 = fields.Char("19")
    day_20 = fields.Char("20")
    day_21 = fields.Char("21")
    day_22 = fields.Char("22")
    day_23 = fields.Char("23")
    day_24 = fields.Char("24")
    day_25 = fields.Char("25")
    day_26 = fields.Char("26")
    day_27 = fields.Char("27")
    day_28 = fields.Char("28")
    day_29 = fields.Char("29")
    day_30 = fields.Char("30")
    day_31 = fields.Char("31")

    def compute_data_attendance(self, eid, day, counter):
        print("eid, day, counter",self, eid, day, counter)
        
        varx = day+timedelta(days = counter)
        print("DAY :", varx, varx.weekday())
        
        check_present = self.env['hr.attendance'].search([('employee_id','=',eid),('check_in_sub','=',varx.strftime('%Y-%m-%d'))])
        # check_present = self.env['hr.attendance'].search([('employee_id','=',eid),
        #                                           ('create_date','<',(date.today()+relativedelta(months=1)).strftime('%Y-%m-01')), 
        #                                           ('create_date','>=',time.strftime('%Y-%m-01')), 
        #                                           ('check_in_sub','=',varx.strftime('%Y-%m-%d'))
        #                                           ])
        print("check_present :",check_present)

        check_leave = self.env['hr.leave'].search([('employee_id','=',eid), '|',
                                                  ('check_leave_from','=',varx.strftime('%Y-%m-%d')),
                                                  ('check_leave_to','=',varx.strftime('%Y-%m-%d'))
                                                  ])
        print("check_leave :",check_leave)

        check_holiday = self.env['resource.calendar.leaves'].search([('holiday_id','=', False),('resource_id','=',False),('check_in_sub','=',varx.strftime('%Y-%m-%d'))])
        print("check_holiday :",check_holiday)
        
        cur_date = date.today()
        next_date = cur_date + timedelta(days = 1)
        
        if varx.weekday() in [5,6]:
            return 'WO'
        elif check_holiday:
            return 'Holiday'
        elif check_leave:
            return 'Leave'
        elif check_present: 
            start = str(check_present[0].check_in).split()[-1][:-3]
            end = str(check_present[-1].check_out).split()[-1][:-3]
            login_time = start +'|'+ end
            return login_time
        else:
            return 'H'

    def view_monthly_attendance_data(self, p_month, p_year):
        if self.user_has_groups('stock_inventory.group_customuser_Infra') or self.user_has_groups('stock_inventory.group_customgroup_Employee'):
            raise UserError('You are Not Authorised to View Monthly Data')
        self.env['monthly.attendance.data'].search([]).unlink()
        # date_string = str(date.today())
        # year, month, day = map(int, date_string.split("-"))
        # num_days = calendar.monthrange(year, month)[1]
        month = int(p_month)
        year = int(p_year)
        
        st_date = datetime(year, month, 1)
        x_date = st_date.strftime("%Y-%m-%d")
        start_date = datetime.strptime(x_date,"%Y-%m-%d")
        
        context = self.env['hr.employee'].search([])

        counter = 0
        for rec in context:
            day = start_date.date()
            varx = day+timedelta(days = counter)
            vals = { 'employee_id': rec.id,
                    'day_1': self.compute_data_attendance(rec.id, day, 0),
                    'day_2': self.compute_data_attendance(rec.id, day, 1),
                    'day_3': self.compute_data_attendance(rec.id, day, 2),
                    'day_4': self.compute_data_attendance(rec.id, day, 3),
                    'day_5': self.compute_data_attendance(rec.id, day, 4),
                    'day_6': self.compute_data_attendance(rec.id, day, 5),
                    'day_7': self.compute_data_attendance(rec.id, day, 6),
                    'day_8': self.compute_data_attendance(rec.id, day, 7),
                    'day_9': self.compute_data_attendance(rec.id, day, 8),
                    'day_10': self.compute_data_attendance(rec.id, day, 9),
                    'day_11': self.compute_data_attendance(rec.id, day, 10),
                    'day_12': self.compute_data_attendance(rec.id, day, 11),
                    'day_13': self.compute_data_attendance(rec.id, day, 12),
                    'day_14': self.compute_data_attendance(rec.id, day, 13),
                    'day_15': self.compute_data_attendance(rec.id, day, 14),
                    'day_16': self.compute_data_attendance(rec.id, day, 15),
                    'day_17': self.compute_data_attendance(rec.id, day, 16),
                    'day_18': self.compute_data_attendance(rec.id, day, 17),
                    'day_19': self.compute_data_attendance(rec.id, day, 18),
                    'day_20': self.compute_data_attendance(rec.id, day, 19),
                    'day_21': self.compute_data_attendance(rec.id, day, 20),
                    'day_22': self.compute_data_attendance(rec.id, day, 21),
                    'day_23': self.compute_data_attendance(rec.id, day, 22),
                    'day_24': self.compute_data_attendance(rec.id, day, 23),
                    'day_25': self.compute_data_attendance(rec.id, day, 24),
                    'day_26': self.compute_data_attendance(rec.id, day, 25),
                    'day_27': self.compute_data_attendance(rec.id, day, 26),
                    'day_28': self.compute_data_attendance(rec.id, day, 27),
                    'day_29': self.compute_data_attendance(rec.id, day, 28),
                    'day_30': self.compute_data_attendance(rec.id, day, 29),
                    'day_31': self.compute_data_attendance(rec.id, day, 30)
                }
            counter = counter+1
            self.env['monthly.attendance.data'].create(vals)
        
        view_id = self.env.ref("hrms_dashboard.monthly_attendance_treeview").id,
        return {
            'name': ("Monthly Attendance Report"),
            'res_model': 'monthly.attendance.data',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'views':[[view_id,'tree']],
	    }