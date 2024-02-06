odoo.define('HRMS.hrms_dashboard_new', function(require) {
"use strict";

/**
 * The purpose of this widget is to shows a toggle button on depreciation and
 * installment lines for posted/unposted line. When clicked, it calls the method
 * create_move on the object account.asset.depreciation.line.
 * Note that this widget can only work on the account.asset.depreciation.line
 * model as some of its fields are harcoded.
 */

var AbstractField = require('web.AbstractField');
var core = require('web.core');
var registry = require('web.field_registry');
var hrms_dashboard = require('hrms_dashboard.DashboardRewrite');

var _t = core._t;

    hrms_dashboard.include({
        events: _.extend({}, hrms_dashboard.prototype.events, {
//            'click': '_onClick',user_checkout
            'click .user_checkout': 'user_checkout_action',
            'click .login_attendance': 'show_attendance_view',
            'click .login_broad_factor': 'employee_attendance_view',
        }),

        init: function(parent, context) {

            this._super(parent, context);

        },

        start: function() {

            var self = this;
            return this._super().then(function() {
                console.log('here');
            });
        },

        async update_attendance(ev) {
            var self = this;
            if (self.login_employee.attendance_state == 'checked_out'){
                await this._super(...arguments);
            }
            if (ev.currentTarget.classList.contains('user_checkout') == true){
                this.user_checkout_action(ev);
            }
        },

        user_checkout_action: function(ev){
            var self = this;
            ev.preventDefault();
//            var $action = $(ev.currentTarget);


            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };

            this.do_action({
                name: _t("Check Out"),
                type: 'ir.actions.act_window',
                res_model: 'hrms.checkout.wiz',
                domain: [],
                context: {},
                views: [[false, 'form']],
                view_mode: 'form',
                target: 'new'
            }, options);
            ev.stopPropagation();

        },

        show_attendance_view: function(ev){
            var self = this;
//            ev.stopPropagation();
            ev.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            this.do_action({
                name: _t("Attendance"),
                type: 'ir.actions.act_window',
                res_model: 'hrms.checkout.wiz',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                context: {
    //                'search_default_month': true,
                },
                domain: [],
                target: 'current'
            }, options)

        },

        employee_attendance_view: function(ev){
            var self = this;
//            ev.stopPropagation();
            ev.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            this.do_action({
                name: _t("Attendance"),
                type: 'ir.actions.act_window',
                res_model: 'attendance.record',
                view_mode: 'tree,form',
                views: [[false, 'list'], [false, 'form']],
                context: {
    //                'search_default_month': true,
                },
                domain: [],
                target: 'current'
            }, options)

        },
});
    return hrms_dashboard;

});
