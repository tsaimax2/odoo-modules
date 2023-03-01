# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2021-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#
#    Author: AVINASH NK(<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

import json
import pytz
from datetime import datetime, time

from odoo import fields, http
from odoo.http import request


class cafeBookingWeb(http.Controller):

    @http.route('/page/cafe_details', csrf=False, type="http",
                methods=['POST', 'GET'], auth="public", website=True)
    def cafe_details(self, **kwargs):
        name = kwargs['name']
        date = kwargs['date']
        time = kwargs['time']
        phone = kwargs['phone']
        email = kwargs['email']
        table = kwargs['table']
        j = 0
        snack_list = []
        while j < (int(kwargs['number'])):
            item = "list_snack["+str(j)+"][i]"
            snack_list.append(int(kwargs[item]))
            j += 1
        cafe_snack_obj = request.env['cafe.snack'].search([
            ('id', 'in', snack_list)])
        dates_time = date+" "+time+":00"
        date_and_time = pytz.timezone(request.env.user.tz).localize(
            datetime.strptime(dates_time, '%m/%d/%Y %H:%M:%S')).astimezone(
            pytz.UTC).replace(tzinfo=None)
        cafe_booking = request.env['cafe.booking']
        booking_data = {
            'name': name,
            'phone': phone,
            'time': date_and_time,
            'email': email,
            'table_id': table,
            'snack_ids': [(6, 0, [x.id for x in cafe_snack_obj])],
        }
        cafe_booking.create(booking_data)
        return json.dumps({'result': True})

    @http.route('/page/cafe_check_date', type='json', auth="public",
                website=True)
    def cafe_check(self, **kwargs):
        day = int(kwargs.get('check_date')[3:5])
        month = int(kwargs.get('check_date')[0:2])
        year = int(kwargs.get('check_date')[6:10])
        date_start = pytz.timezone(request.env.user.tz).localize(
            datetime(year, month, day, 0, 0, 0)).astimezone(
            pytz.UTC).replace(tzinfo=None)
        date_end = pytz.timezone(request.env.user.tz).localize(
            datetime(year, month, day, 23, 59, 59)).astimezone(
            pytz.UTC).replace(tzinfo=None)
        order_obj = request.env['cafe.order'].search(
            [('table_id.active_booking_tables', '=', True),
             ('stage_id', 'in', [1, 2, 3]), ('start_time', '>=', date_start),
             ('start_time', '<=', date_end)])
        order_details = {}
        for order in order_obj:
            data = {
                'number': order.id,
                'start_time_only': fields.Datetime.to_string(pytz.UTC.localize(
                    order.start_time).astimezone(pytz.timezone(
                        request.env.user.tz)).replace(tzinfo=None))[11:16],
                'end_time_only': fields.Datetime.to_string(pytz.UTC.localize(
                    order.end_time).astimezone(pytz.timezone(
                        request.env.user.tz)).replace(tzinfo=None))[11:16],
            }
            if order.table_id.id not in order_details:
                order_details[order.table_id.id] = {
                    'name': order.table_id.name,
                    'orders': [data],
                }
            else:
                order_details[order.table_id.id]['orders'].append(data)
        return order_details

    @http.route('/page/cafe_management/cafe_booking_thank_you', type='http',
                auth="public", website=True)
    def thank_you(self, **post):
        return request.render('cafe_management.cafe_booking_thank_you', {})

    @http.route('/page/cafe_management/cafe_booking_form', type='http',
                auth="public", website=True)
    def table_info(self, **post):
        cafe_snack_obj = request.env['cafe.snack'].search([])
        cafe_working_hours_obj = request.env['cafe.working.hours'].search([])
        cafe_holiday_obj = request.env['cafe.holiday'].search(
            [('holiday', '=', True)])
        date_check = fields.Date.context_today(request)
        date_start = pytz.timezone(request.env.user.tz).localize(
            datetime.combine(date_check, time(0, 0, 0))).astimezone(
            pytz.UTC).replace(tzinfo=None)
        date_end = pytz.timezone(request.env.user.tz).localize(
            datetime.combine(date_check, time(23, 59, 59))).astimezone(
            pytz.UTC).replace(tzinfo=None)
        table_obj = request.env['cafe.table'].search(
            [('active_booking_tables', '=', True)])
        order_obj = request.env['cafe.order'].search(
            [('table_id.active_booking_tables', '=', True),
             ('stage_id', 'in', [1, 2, 3]), ('start_time', '>=', date_start),
             ('start_time', '<=', date_end)])
        return request.render(
            'cafe_management.cafe_booking_form', {
                'table_details': table_obj,
                'order_details': order_obj,
                'cafe_snacks': cafe_snack_obj,
                'date_search': date_check,
                'holiday': cafe_holiday_obj,
                'working_time': cafe_working_hours_obj,
            })
