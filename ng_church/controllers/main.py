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

from collections import OrderedDict
from odoo import api, fields, models, _
# for portal purpuse, we need following
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.addons.account.controllers.portal import PortalAccount
from odoo.addons.website_event.controllers.main import WebsiteEventController

class ChurchDevotionWeb(http.Controller):
    # go to cafe_details page and create booking data package, where is cafe_details page?
    @http.route('/page/devotion_details', csrf=False, type="http",
                methods=['POST', 'GET'], auth="public", website=True)
    def devotion_details(self, **kwargs):
        name = kwargs['name']
        phone = kwargs['phone']
        email = kwargs['email']
        amount = kwargs['amount']
        type_value = kwargs['type_value']
        note = kwargs['note']
        
        date_and_time = datetime.now(pytz.timezone('Asia/Taipei')).strftime("%Y-%m-%d")
        #print('I am back in controller')        
        
        
        if type_value == '1':
            tithe_rec = request.env['ng_church.tithe']
            # doing the mapping to the ChurchCollection.py
            devotion_data = {
                'name': type_value,
                'section_id': 3,
            #    'service_id': '祷告会',
                'tithe_line_ids':[(0,0,{'date': date_and_time,
                                        'tither': request.env.user.partner_id.id,
                                        'tithe_type': 'members', 
            #                           'phone': phone,
            #                           'email': email,
                                        'amount': amount,
            #                           'type_value': type_value,
            #                           'note': note            
                                    })]    
            }
            print('type_value',type_value,'tithe_lines=',devotion_data)
            tithe_rec.sudo().create(devotion_data)
        
        elif type_value == '2':
            offering_rec = request.env['ng_church.offering']
            offering_data = {
                'name': type_value,
                'section_id': 3,
            #    'service_id': '祷告会',
                'offering_line_ids':[(0,0,{'date': date_and_time,
            #                            'tither': request.env.user.partner_id.id,
            #                            'tithe_type': 'members', 
            #                           'phone': phone,
            #                           'email': email,
                                        'amount': amount,
            #                           'type_value': type_value,
            #                           'note': note            
                                    })]    
            }
            print('type_value',type_value,'offering_lines=', offering_data)
            offering_rec.sudo().create(offering_data)
        
        #print('tithe_rec', tithe_rec)
        
        return json.dumps({'result': True})
    
    """ @http.route('/page/cafe_check_date', type='json', auth="public",
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
        return order_details """

    @http.route('/page/ng_church/church_devotion_thank_you', type='http',
                auth="public", website=True)
    def thank_you(self, **post):
        return request.render('ng_church.church_devotion_thank_you', {})

    """  @http.route('/page/cafe_management/cafe_booking_form', type='http',
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
            }) """
    
    # send some specific data to church_devotion_form, url to get template_id, template_id to get controller to render 
    @http.route('/page/ng_church/church_devotion_form', type="http", auth="public", website=True)
    def devotion_info(self, **post):
        # send data to church_devotion_form
        church_collections = request.env['ng_church.collection'].search([])
        #devotion_note = fields.Text(String='Notes')
        #print("Execution Here.........................")
        #doctor_rec = request.env['hospital.doctor'].sudo().search([])
        #print("doctor_rec...", doctor_rec)
        # Odoo Mates Test 123 can be replaced by current login user, together with the t-att in view.xml
        # render will search for create_patient template in web..xml, om_hospital is it's directory
        # for doctor case, the doctor_rec db will be invoked and to be called in web xml with name of 'doctor_rec'
        return http.request.render('ng_church.church_devotion_form', {'name': 'Odoo Mates Test 123',
                                                                      'church_collections': church_collections})
class WalletCustomerPortal(PortalAccount):
    # counters are connected from count_appointment in templates.xml
    # we need pass a variable into this route to trigger another render!
    @http.route(['/my/wallet', '/my/wallet/<sum>'], type='http', auth="user", website=True)
    def display_wallet(self):
        balance = self.portal_my_wallet()
        #return '<h1>{}</h1>'.format(sum)
        #sums={'sum':sum}
        #balance = fields.Monetary(string="My Balance", compute=self.portal_my_wallet())
        #print('balance', sum)
        return http.request.render('ng_church.wallet_balance', {'balance': balance})

    def portal_my_wallet(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        AccountInvoice = request.env['account.move']

        domain = self._get_invoices_domain()

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'invoice_date desc'},
            'duedate': {'label': _('Due Date'), 'order': 'invoice_date_due desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'invoices': {'label': _('Invoices'), 'domain': [('move_type', '=', ('out_invoice', 'out_refund'))]},
            'bills': {'label': _('Bills'), 'domain': [('move_type', '=', ('in_invoice', 'in_refund'))]},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        invoice_count = AccountInvoice.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/invoices",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=invoice_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        invoices = AccountInvoice.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_invoices_history'] = invoices.ids[:100]

        values.update({
            'date': date_begin,
            'invoices': invoices,
            'page_name': 'invoice',
            'pager': pager,
            'default_url': '/my/invoices',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby':filterby,
        })

        balance=0
        for invoice in invoices:
            if invoice.move_type == 'out_invoice': 
                amount=-invoice.amount_residual
                print('invoice=',amount)
            else:
                amount=invoice.amount_residual
                print('invoice_normal', amount)
            balance += amount
        print('sum=',balance)
        return balance
        #return http.request.render('om_hospital.wallet_balance', {'sum':sum})

