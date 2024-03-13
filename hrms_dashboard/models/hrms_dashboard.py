# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
import pandas as pd
from pytz import utc
from odoo import models, fields, api, _
from odoo.http import request
from odoo.tools import float_utils

ROUNDING_FACTOR = 16


class HrLeave(models.Model):
    _inherit = 'hr.leave'
    duration_display = fields.Char('Requested (Days/Hours)',
                                   compute='_compute_duration_display',
                                   store=True,
                                   help="Field allowing to see the leave request duration"
                                        " in days or hours depending on the leave_type_request_unit")


class Employee(models.Model):
    _inherit = 'hr.employee'

    birthday = fields.Date('Date of Birth', groups="base.group_user",
                           help="Birthday")
    
    approval_boolean = fields.Boolean(string="Leave Approver")
    
    accessories_bool = fields.Boolean(string="Accessories")

    laptop = fields.Char(string="Laptop")
    laptop_spec = fields.Html(string='Laptop Specification')
    provided_date = fields.Date(string="Provided On")
    returned_on = fields.Date(string="Return On")
    other_accessories = fields.Char(string='Other Accessories')

    # @api.onchange('accessories_bool')
    def get_allpl_from_leave_alloc(self):
        pl_alloc_ids = self.env['hr.leave.allocation'].search([])
        for rec in pl_alloc_ids:
            if rec.holiday_status_id.name == 'Privileged Leave (PL)':
                varx1 = rec.number_of_days_display + float(1)
                varx2 = rec.number_of_days + float(1)
                rec.write({'number_of_days_display':varx1,
                           'number_of_days': varx2})
                
                
    @api.model
    def create(self, vals):
        res = super(Employee ,self).create(vals)
        if res.id:
            hol_clsl_id = self.env['hr.leave.type'].search([('id','=',177)])
            hol_pl_id = self.env['hr.leave.type'].search([('id','=',172)])
            val_slcl = {
                    'name':"{}'s Casual / Sick Leave ( CL/SL )".format(res.name),
                    'holiday_status_id': hol_clsl_id.id,
                    'allocation_type': 'regular',
                    'date_from':date.today(),
                    'number_of_days': float(12.00),
                    'number_of_days_display': float(12.00),
                    'holiday_type': 'employee',
                    'employee_id': res.id,
                    'multi_employee' : False,
                    'employee_ids': res.ids,
                }
            val_pl = {
                    'name':"{}'s Paid Time Off ( PL )".format(res.name),
                    'holiday_status_id': hol_pl_id.id,
                    'allocation_type': 'regular',
                    'date_from':date.today(),
                    'number_of_days': float(1.00),
                    'number_of_days_display': float(1.00),
                    'holiday_type': 'employee',
                    'employee_id': res.id,
                    'multi_employee' : False,
                    'employee_ids': res.ids,
                }
            self.env['hr.leave.allocation'].create(val_slcl)
            self.env['hr.leave.allocation'].create(val_pl)
        return res


    @api.model
    def check_user_group(self):
        uid = request.session.uid
        user = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        if user.has_group('hr.group_hr_manager'):
            return True
        else:
            return False

    @api.model
    def get_user_employee_details(self):
        uid = request.session.uid
        employee = self.env['hr.employee'].sudo().search_read(
            [('user_id', '=', uid)], limit=1)
        leaves_to_approve = self.env['hr.leave'].sudo().search_count(
            [('state', 'in', ['confirm', 'validate1'])])
        leaves = self.env['hr.leave'].sudo().search(
            [('state', 'in', ['confirm', 'validate1']),('user_id', '!=', self.env.user.id)])
        user_leavz = self.env['hr.leave'].sudo().search([('user_id', '=', self.env.user.id)])
        print("\n"*5,user_leavz, "\n"*5)
        
        leaves_to_notify = [{'id': leave.id, 
                            'employee_name': leave.employee_id.name, 
                            'holiday_status':leave.holiday_status_id.name, 
                            'request_from':leave.request_date_from,
                            'request_to': leave.request_date_to } for leave in leaves]
        
        user_leavz_notify = [{'id': leave.id,
                            'employee_name': leave.employee_id.name, 
                            'holiday_status':leave.holiday_status_id.name, 
                            'request_from':leave.request_date_from,
                            'request_to': leave.request_date_to } for leave in user_leavz]
        # for leave in leaves:
        #     notify_data = {'employee_name': leave.employee_id.name, }
        #     leaves_to_notify.append(notify_data)
        today = datetime.strftime(datetime.today(), '%Y-%m-%d')
        query = """
        select count(id)
        from hr_leave
        WHERE (hr_leave.date_from::DATE,hr_leave.date_to::DATE) OVERLAPS ('%s', '%s') and
        state='validate'""" % (today, today)
        cr = self._cr
        cr.execute(query)
        leaves_today = cr.fetchall()
        first_day = date.today().replace(day=1)
        last_day = (date.today() + relativedelta(months=1, day=1)) - timedelta(
            1)
        query = """
                select count(id)
                from hr_leave
                WHERE (hr_leave.date_from::DATE,hr_leave.date_to::DATE) OVERLAPS ('%s', '%s')
                and  state='validate'""" % (first_day, last_day)
        cr = self._cr
        cr.execute(query)
        leaves_this_month = cr.fetchall()
        print("leaves_this_month",leaves_this_month)
        leaves_alloc_req = self.env['hr.leave.allocation'].sudo().search_count(
            [('state', 'in', ['confirm', 'validate1'])])
        timesheet_count = self.env['account.analytic.line'].sudo().search_count(
            [('project_id', '!=', False), ('user_id', '=', uid)])
        timesheet_view_id = self.env.ref(
            'hr_timesheet.hr_timesheet_line_search')
        job_applications = self.env['hr.applicant'].sudo().search_count([])
        if employee:
            sql = """select broad_factor from hr_employee_broad_factor where id =%s"""
            self.env.cr.execute(sql, (employee[0]['id'],))
            result = self.env.cr.dictfetchall()
            broad_factor = result[0]['broad_factor']
            if employee[0]['birthday']:
                diff = relativedelta(datetime.today(), employee[0]['birthday'])
                age = diff.years
            else:
                age = False
            if employee[0]['joining_date']:
                diff = relativedelta(datetime.today(),
                                     employee[0]['joining_date'])
                years = diff.years
                months = diff.months
                days = diff.days
                experience = '{} years {} months {} days'.format(years, months,
                                                                 days)
            else:
                experience = False
            # my code
            import pytz
            indian_timezone = pytz.timezone('Asia/Kolkata')
            user_employee = self.env.user.employee_id
            attendances = self.env['hr.attendance'].search([('employee_id', '=', user_employee.id)])
            worked_hours = 0
            for rec in attendances:
                if int(rec.check_in.strftime("%d")) == int(datetime.today().strftime("%d")):
                    worked_hours += rec.worked_hours
                    if not rec.check_out:
                        till_now_time = datetime.now() - rec.check_in
                        # Convert timedelta to single floating-point hours and minutes
                        total_hours = till_now_time.total_seconds() / 3600  # 3600 seconds in an hour
                        hours_and_minutes = round(total_hours, 2)
                        worked_hours += hours_and_minutes  # Round to two decimal places
                        # print(till_now_time)
            # ends            
            if employee:
                data = {
                    'broad_factor': broad_factor if broad_factor else 0,
                    'leaves_to_approve': leaves_to_approve,
                    'leaves_today': leaves_today,
                    'leaves_this_month': leaves_this_month,
                    'leaves_alloc_req': leaves_alloc_req,
                    'emp_timesheets': timesheet_count,
                    'job_applications': job_applications,
                    'timesheet_view_id': timesheet_view_id,
                    'experience': experience,
                    'age': age
                }
                employee[0].update(data)
            # my code
            # attendance_record = self.env['attendance.record'].search([], order='id desc', limit=7)
            attendance_record = self.env['hr.attendance'].search([('user_id','=', self.env.user.id)], order='id desc', limit=7)

            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            attendance_data = []
            attendance_date = []
            
            varx = self.env['hr.leave'].search([('user_id','=',self.env.user.id)])
            # print("VARX",varx)
            tommo = date.today() + timedelta(days=1)
            yesterday = date.today() - timedelta(days=1)
            day_b4 = date.today() - timedelta(days=2)
            day_b41 = date.today() - timedelta(days=3)
            day_b42 = date.today() - timedelta(days=4)
            day_b43 = date.today() - timedelta(days=5)
            leave_list = [day_b43, day_b42, day_b41, day_b4, yesterday, date.today(), tommo]
            
            print("LEAVE_LIST :",leave_list)
            
            for line in varx:
                if line.date_from.date() in leave_list:
                    attendance_data.append({
                                                'day': 'Leave',
                                                'check_in': line.date_from.strftime("%d-%m-%y"),
                                                'check_out': " ",
                                                'hours':" ",
                                            })
            print("ATTENDANCE_REC",attendance_record)

            for rec in attendance_record:
                day_of_week = rec.check_in.weekday()
                print("PART-1",days[day_of_week])
                attendance_data.append({
                    'day': days[day_of_week],
                    'check_in': rec.check_in.strftime("%d-%m-%y %H:%M"),
                    'check_out': rec.check_out.strftime("%d-%m-%y %H:%M") if rec.check_out else ' ',
                    'hours': round(rec.worked_hours,2), 
                })
                attendance_date.append(rec.check_in.strftime("%d-%m-%y"))
            print("ATTENDANCE_DATE",attendance_date)
            
            for i in range(0, len(attendance_record)-1):
                current_date = attendance_record[i].check_in
                while current_date > attendance_record[i+1].check_in:
                    current_date -= timedelta(days=1)
                    if current_date.strftime("%d-%m-%y") not in attendance_date:
                        day_of_week = current_date.weekday()
                        attendance_data.append({
                            'day': days[day_of_week],
                            'check_in': current_date.strftime("%d-%m-%y"),
                            'check_out': ' ',
                            'hours': 0,
                        })
            print("attendance_data","==============",attendance_data)
            
            sorted_data = sorted(attendance_data, key=lambda x: x['check_in'])
            print("Sorted_data : ", sorted_data)
            final_data = sorted_data[::-1][0:7]
            print("final_data : ", final_data)
            # nml_days = []
            # wkd_days = []
            # newlist = []
            # for rec in sorted_data:
            #     if rec['day'] == 'Sunday':
            #         wkd_days.append(rec)
            #     else:
            #         nml_days.append(rec)
            # k = 0
            # if len(wkd_days) >= 2 :
            #     for res in wkd_days:
            #         if k == res['check_in']:
            #             del res
            #         else:
            #             k = res['check_in']
            #             newlist.append(res)
 
            # final_data1 = nml_days + newlist
            # print("final_data1 : ", final_data1)
            # post_sorted = sorted(final_data1, key=lambda x: x['check_in'])
            # print("post_sorted : ", post_sorted)

            # final_lst = []
            # for line in post_sorted:
            #     cut = '-23'
            #     supvar1 = line['check_in'].split(cut)[0]
            #     stripped = supvar1+'-2023'
            #     supvar2 = datetime.strptime(stripped, '%d-%m-%Y').date()
            #     if supvar2 in leave_list:
            #         final_lst.append(line)
            # print("final_lst : ", final_lst)

            if attendance_data:
                employee[0]['last_7_days'] = final_data[::-1]
            if attendances:
                employee[0]['attendance_count'] = len(attendances)
            if self.env.user.has_group('base.group_system'):
                employee[0]['is_admin'] = True
            if round(worked_hours, 2) or worked_hours == 0:
                employee[0]['login_hours'] = round(worked_hours, 2)
            if len(leaves_to_notify) != 0:
                employee[0]['leaves_to_notify'] = leaves_to_notify
            if len(user_leavz_notify) != 0:
                employee[0]['user_leavz_notify'] = user_leavz_notify
            # ends
            # print("leaves_to_notify", employee[0].get('leaves_to_notify'))
            # print("user_leavz_notify", employee[0].get('user_leavz_notify'))
            return employee
        else:
            return False

    @api.model
    def get_upcoming(self):
        cr = self._cr
        uid = request.session.uid
        employee = self.env['hr.employee'].search([('user_id', '=', uid)],
                                                  limit=1)

        cr.execute("""select *,
        (to_char(dob,'ddd')::int-to_char(now(),'ddd')::int+total_days)%total_days as dif
        from (select he.id, he.name, to_char(he.birthday, 'Month dd') as birthday,
        hj.name as job_id , he.birthday as dob,
        (to_char((to_char(now(),'yyyy')||'-12-31')::date,'ddd')::int) as total_days
        FROM hr_employee he
        join hr_job hj
        on hj.id = he.job_id
        ) birth
        where (to_char(dob,'ddd')::int-to_char(now(),'DDD')::int+total_days)%total_days between 0 and 15
        order by dif;""")
        birthday = cr.fetchall()
        # v16:added lang as key for fetching from jsonb;changed query :
        # retrieve the JSON object field by key
        lang = f"'{self.env.context['lang']}'"
        # print("current_language:",self.env.context['lang'])
        cr.execute("""select  e.name ->>lang as name, e.date_begin, e.date_end,rp.name as location
        from event_event e
        inner join res_partner rp
        on e.address_id = rp.id
        and (e.date_begin >= now())
        order by e.date_begin""")
        event = cr.fetchall()
        announcement = []
        if employee:
            department = employee.department_id
            job_id = employee.job_id
            sql = """select ha.name, ha.announcement_reason
            from hr_announcement ha
            left join hr_employee_announcements hea
            on hea.announcement = ha.id
            left join hr_department_announcements hda
            on hda.announcement = ha.id
            left join hr_job_position_announcements hpa
            on hpa.announcement = ha.id
            where ha.state = 'approved' and
            ha.date_start <= now()::date and
            ha.date_end >= now()::date and
            (ha.is_announcement = True or
            (ha.is_announcement = False
            and ha.announcement_type = 'employee'
            and hea.employee = %s)""" % employee.id
            if department:
                sql += """ or
                (ha.is_announcement = False and
                ha.announcement_type = 'department'
                and hda.department = %s)""" % department.id
            if job_id:
                sql += """ or
                (ha.is_announcement = False and
                ha.announcement_type = 'job_position'
                and hpa.job_position = %s)""" % job_id.id
            sql += ')'
            cr.execute(sql)
            announcement = cr.fetchall()
        return {
            'birthday': birthday,
            'event': event,
            'announcement': announcement
        }

    @api.model
    def get_dept_employee(self):
        cr = self._cr
        cr.execute("""select department_id, hr_department.name,count(*)
                    from hr_employee join hr_department on hr_department.id=hr_employee.department_id
                    group by hr_employee.department_id,hr_department.name""")
        dat = cr.fetchall()
        data = []
        for i in range(0, len(dat)):
            data.append({'label': dat[i][1], 'value': dat[i][2]})
        return data

    @api.model
    def get_department_leave(self):
        month_list = []
        graph_result = []
        for i in range(5, -1, -1):
            last_month = datetime.now() - relativedelta(months=i)
            text = format(last_month, '%B %Y')
            month_list.append(text)
        self.env.cr.execute(
            """select id, name from hr_department where active=True """)
        departments = self.env.cr.dictfetchall()
        department_list = [x['name'] for x in departments]
        for month in month_list:
            leave = {}
            for dept in departments:
                leave[dept['name']] = 0
            vals = {
                'l_month': month,
                'leave': leave
            }
            graph_result.append(vals)
        sql = """
        SELECT h.id, h.employee_id,h.department_id
             , extract('month' FROM y)::int AS leave_month
             , to_char(y, 'Month YYYY') as month_year
             , GREATEST(y                    , h.date_from) AS date_from
             , LEAST   (y + interval '1 month', h.date_to)   AS date_to
        FROM  (select * from hr_leave where state = 'validate') h
             , generate_series(date_trunc('month', date_from::timestamp)
                             , date_trunc('month', date_to::timestamp)
                             , interval '1 month') y
        where date_trunc('month', GREATEST(y , h.date_from)) >= date_trunc('month', now()) - interval '6 month' and
        date_trunc('month', GREATEST(y , h.date_from)) <= date_trunc('month', now())
        and h.department_id is not null
        """
        self.env.cr.execute(sql)
        results = self.env.cr.dictfetchall()
        leave_lines = []
        for line in results:
            employee = self.browse(line['employee_id'])
            from_dt = fields.Datetime.from_string(line['date_from'])
            to_dt = fields.Datetime.from_string(line['date_to'])
            days = employee.get_work_days_dashboard(from_dt, to_dt)
            line['days'] = days
            vals = {
                'department': line['department_id'],
                'l_month': line['month_year'],
                'days': days
            }
            leave_lines.append(vals)
        if leave_lines:
            df = pd.DataFrame(leave_lines)
            rf = df.groupby(['l_month', 'department']).sum()
            result_lines = rf.to_dict('index')
            for month in month_list:
                for line in result_lines:
                    if month.replace(' ', '') == line[0].replace(' ', ''):
                        match = list(filter(lambda d: d['l_month'] in [month],
                                            graph_result))[0]['leave']
                        dept_name = self.env['hr.department'].browse(
                            line[1]).name
                        if match:
                            match[dept_name] = result_lines[line]['days']
        for result in graph_result:
            result['l_month'] = result['l_month'].split(' ')[:1][0].strip()[
                                :3] + " " + \
                                result['l_month'].split(' ')[1:2][0]

        return graph_result, department_list

    def get_work_days_dashboard(self, from_datetime, to_datetime,
                                compute_leaves=False, calendar=None,
                                domain=None):
        resource = self.resource_id
        calendar = calendar or self.resource_calendar_id

        if not from_datetime.tzinfo:
            from_datetime = from_datetime.replace(tzinfo=utc)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(tzinfo=utc)
        from_full = from_datetime - timedelta(days=1)
        to_full = to_datetime + timedelta(days=1)
        intervals = calendar._attendance_intervals_batch(from_full, to_full,
                                                         resource)
        day_total = defaultdict(float)
        for start, stop, meta in intervals[resource.id]:
            day_total[start.date()] += (stop - start).total_seconds() / 3600
        if compute_leaves:
            intervals = calendar._work_intervals_batch(from_datetime,
                                                       to_datetime, resource,
                                                       domain)
        else:
            intervals = calendar._attendance_intervals_batch(from_datetime,
                                                             to_datetime,
                                                             resource)
        day_hours = defaultdict(float)
        for start, stop, meta in intervals[resource.id]:
            day_hours[start.date()] += (stop - start).total_seconds() / 3600
        days = sum(
            float_utils.round(ROUNDING_FACTOR * day_hours[day] / day_total[
                day]) / ROUNDING_FACTOR
            for day in day_hours
        )
        return days

    @api.model
    def employee_leave_trend(self):
        leave_lines = []
        month_list = []
        graph_result = []
        for i in range(5, -1, -1):
            last_month = datetime.now() - relativedelta(months=i)
            text = format(last_month, '%B %Y')
            month_list.append(text)
        uid = request.session.uid
        employee = self.env['hr.employee'].sudo().search_read(
            [('user_id', '=', uid)], limit=1)
        for month in month_list:
            vals = {
                'l_month': month,
                'leave': 0
            }
            graph_result.append(vals)
        sql = """
                SELECT h.id, h.employee_id
                     , extract('month' FROM y)::int AS leave_month
                     , to_char(y, 'Month YYYY') as month_year
                     , GREATEST(y                    , h.date_from) AS date_from
                     , LEAST   (y + interval '1 month', h.date_to)   AS date_to
                FROM  (select * from hr_leave where state = 'validate') h
                     , generate_series(date_trunc('month', date_from::timestamp)
                                     , date_trunc('month', date_to::timestamp)
                                     , interval '1 month') y
                where date_trunc('month', GREATEST(y , h.date_from)) >= date_trunc('month', now()) - interval '6 month' and
                date_trunc('month', GREATEST(y , h.date_from)) <= date_trunc('month', now())
                and h.employee_id = %s
                """
        self.env.cr.execute(sql, (employee[0]['id'],))
        results = self.env.cr.dictfetchall()
        for line in results:
            employee = self.browse(line['employee_id'])
            from_dt = fields.Datetime.from_string(line['date_from'])
            to_dt = fields.Datetime.from_string(line['date_to'])
            days = employee.get_work_days_dashboard(from_dt, to_dt)
            line['days'] = days
            vals = {
                'l_month': line['month_year'],
                'days': days
            }
            leave_lines.append(vals)
        if leave_lines:
            df = pd.DataFrame(leave_lines)
            rf = df.groupby(['l_month']).sum()
            result_lines = rf.to_dict('index')
            for line in result_lines:
                match = list(filter(
                    lambda d: d['l_month'].replace(' ', '') == line.replace(' ',
                                                                            ''),
                    graph_result))
                if match:
                    match[0]['leave'] = result_lines[line]['days']
        for result in graph_result:
            result['l_month'] = result['l_month'].split(' ')[:1][0].strip()[
                                :3] + " " + \
                                result['l_month'].split(' ')[1:2][0]
        return graph_result

    @api.model
    def join_resign_trends(self):
        cr = self._cr
        month_list = []
        join_trend = []
        resign_trend = []
        for i in range(11, -1, -1):
            last_month = datetime.now() - relativedelta(months=i)
            text = format(last_month, '%B %Y')
            month_list.append(text)
        for month in month_list:
            vals = {
                'l_month': month,
                'count': 0
            }
            join_trend.append(vals)
        for month in month_list:
            vals = {
                'l_month': month,
                'count': 0
            }
            resign_trend.append(vals)
        cr.execute('''select to_char(joining_date, 'Month YYYY') as l_month, count(id) from hr_employee
        WHERE joining_date BETWEEN CURRENT_DATE - INTERVAL '12 months'
        AND CURRENT_DATE + interval '1 month - 1 day'
        group by l_month''')
        join_data = cr.fetchall()
        cr.execute('''select to_char(resign_date, 'Month YYYY') as l_month, count(id) from hr_employee
        WHERE resign_date BETWEEN CURRENT_DATE - INTERVAL '12 months'
        AND CURRENT_DATE + interval '1 month - 1 day'
        group by l_month;''')
        resign_data = cr.fetchall()

        for line in join_data:
            match = list(filter(
                lambda d: d['l_month'].replace(' ', '') == line[0].replace(' ',
                                                                           ''),
                join_trend))
            if match:
                match[0]['count'] = line[1]
        for line in resign_data:
            match = list(filter(
                lambda d: d['l_month'].replace(' ', '') == line[0].replace(' ',
                                                                           ''),
                resign_trend))
            if match:
                match[0]['count'] = line[1]
        for join in join_trend:
            join['l_month'] = join['l_month'].split(' ')[:1][0].strip()[:3]
        for resign in resign_trend:
            resign['l_month'] = resign['l_month'].split(' ')[:1][0].strip()[:3]
        graph_result = [{
            'name': 'Join',
            'values': join_trend
        }, {
            'name': 'Resign',
            'values': resign_trend
        }]

        return graph_result

    @api.model
    def get_attrition_rate(self):

        month_attrition = []
        monthly_join_resign = self.join_resign_trends()
        month_join = monthly_join_resign[0]['values']
        month_resign = monthly_join_resign[1]['values']
        sql = """
        SELECT (date_trunc('month', CURRENT_DATE))::date - interval '1' month * s.a AS month_start
        FROM generate_series(0,11,1) AS s(a);"""
        self._cr.execute(sql)
        month_start_list = self._cr.fetchall()
        for month_date in month_start_list:
            self._cr.execute("""select count(id), to_char(date '%s', 'Month YYYY') as l_month from hr_employee
            where resign_date> date '%s' or resign_date is null and joining_date < date '%s'
            """ % (month_date[0], month_date[0], month_date[0],))
            month_emp = self._cr.fetchone()
            # month_emp = (month_emp[0], month_emp[1].split(' ')[:1][0].strip()[:3])
            match_join = \
                list(filter(
                    lambda d: d['l_month'] == month_emp[1].split(' ')[:1][
                                                  0].strip()[:3], month_join))[
                    0][
                    'count']
            match_resign = \
                list(filter(
                    lambda d: d['l_month'] == month_emp[1].split(' ')[:1][
                                                  0].strip()[:3],
                    month_resign))[0][
                    'count']
            month_avg = (month_emp[0] + match_join - match_resign + month_emp[
                0]) / 2
            attrition_rate = (
                                     match_resign / month_avg) * 100 if month_avg != 0 else 0
            vals = {
                # 'month': month_emp[1].split(' ')[:1][0].strip()[:3] + ' ' + month_emp[1].split(' ')[-1:][0],
                'month': month_emp[1].split(' ')[:1][0].strip()[:3],
                'attrition_rate': round(float(attrition_rate), 2)
            }
            month_attrition.append(vals)

        return month_attrition


class BroadFactor(models.Model):
    _inherit = 'hr.leave.type'

    emp_broad_factor = fields.Boolean(string="Broad Factor",
                                      help="If check it will display in broad factor type")
    suprem_leaves_id = fields.Many2one('hr.leave', string="Supp REM")

    def delete_duplicate_timeOffTypes(self):
        print("||||||||||||||||||||| delete_duplicate_timeOffTypes |||||||||||||||||")
        varx = self.env['hr.leave.type'].search([])
        print(varx)
        for rec in varx:
            # if rec.id not in [3,8,1,4,12,2,5,11,12,13,14,15,6,19]:
            if rec.id not in [177, 172, 173, 174, 175, 176, 178, 179, 180, 181, 182, 183, 184]:
                print(rec)
                rec.unlink()
                
class HrleaveNotebook(models.Model):
    _name = 'hr.leave.notebook'

    notebook_id = fields.Many2one('hr.leave', string=" Notebook ID")

    display_name = fields.Char(string="Display Name")
    remaining_leaves = fields.Float(string="Remaining Leaves")
    leaves_taken = fields.Float(string="Leaves Taken")
