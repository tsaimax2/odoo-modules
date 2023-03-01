# -*- coding: utf-8 -*-
# We use This program to control events, and leave events alone!
from odoo import http
from odoo.http import request
from odoo.addons.website_event.controllers.main import WebsiteEventController
from odoo.addons.website_event_sale.controllers.main import WebsiteEventSaleController
import logging
_logger = logging.getLogger(__name__)

# class Select(WebsiteEventController,WebsiteEventSaleController):
#     def select_registration_confirm(self):
#         WebsiteEventController.registration_confirm(self, event, **post)
#         WebsiteEventSaleController.registration_confirm(self, event, **post)

class ShortCircuit(WebsiteEventController):
    
    @http.route()
    def registration_confirm(self, event, **post):
        
        #print('res_ticket', res_ticket)
        # this one 'registration_confirm' inherit from WebsiteEventController, will go cascade to salecontrol...
        #res = super(ShortCircuit, self).registration_confirm(event, **post)
        #print('res=', res)
        
        # this one 'registration_confirm' inherit from WebsiteSaleEventController, contain redirect
        # this will only trace back to top WebsiteEventController, skip WebsiteEventSaleController 
        # The VM ok, but server no good 
        _logger.debug("Debug message")
        import sys
        print(sys.version)
        print(self)
        print(type(self))
        print(isinstance(self, WebsiteEventSaleController))
        # no working 
        #res = WebsiteEventSaleController.registration_confirm(event, **post)
        res = super(WebsiteEventSaleController, self).registration_confirm(event, **post)
        # use the following:

        #print('res=', res)
        registrations = self._process_attendees_form(event, post)
        print('registration=', registrations)
        # we have at least one registration linked to a ticket -> sale mode activate
        #res_ticket= super(Short, self)._process_tickets_form(self, event)
        #print('ticket info', res_ticket)
        if any(info['event_ticket_id'] for info in registrations):
            order = request.website.sale_get_order(force_create=False)            
            if order.amount_total:
                pass                
                #return request.redirect("/shop/checkout")                
            # free tickets -> order with amount = 0: auto-confirm, no checkout
            elif order:
                #order.action_confirm()  # tde notsure: email sending ?
                #request.website.sale_reset()
                pass        
        return res
    
    @http.route(['/event/<model("event.event"):event>/registration/success'], type='http', auth="public", methods=['GET'], website=True, sitemap=False)
    def event_registration_success(self, event, registration_ids):
            # fetch the related registrations, make sure they belong to the correct visitor / event pair
        # we can find the ticket id from the registration_id informat
        print('resgistrion_id', registration_ids)
        visitor = request.env['website.visitor']._get_visitor_from_request()
        if not visitor:
            raise NotFound()
        attendees_sudo = request.env['event.registration'].sudo().search([
            ('id', 'in', [str(registration_id) for registration_id in registration_ids.split(',')]),
            ('event_id', '=', event.id),
            ('visitor_id', '=', visitor.id),
        ]) 
        
        ticket_id = request.env['event.registration'].sudo().search([
            ('id', '=', [str(registration_id) for registration_id in registration_ids.split(',')])
            ])
        print('ticket_id', ticket_id.event_ticket_id)
        
        # get the ticket value for the specific id which is 9 and look like  event.event.ticket(9,) in this case, need to add int!
        ticket = request.env['event.event.ticket'].sudo().search([
            ('id', '=', int(ticket_id.event_ticket_id))])
        
        # to fill the PO and SO, we need to do some format conversion!
        # this will give produc.product(4,), to link to the name, we need to add int( ) to convert
        so_po_product=ticket.product_id
        # this will give float value
        so_po_price=ticket.price
        print('product and price=', so_po_product, so_po_price)
        # we add this paragraph to create a purchase order 
        #tag = 'event.tag_ids'
        #print('Stop here')    
        tag= event.service_id['color']
        
        if tag == 10:
            partner_val={            
            'partner_id': visitor.id,
            'order_line': [(0, 0, {'product_id': int(so_po_product),
                                    'name': 'event_id',
                                    'qty_received': 1.0, 
                                    'price_unit': so_po_price})
                                                    ]}  
            request.env['purchase.order'].sudo().create(partner_val)
        elif tag ==9:
            partner_val={            
            'partner_id': visitor.id,
            'state': 'sale',
            'order_line': [(0, 0, {'product_id': int(so_po_product),
                                    'name': 'event_id',
                                    'price_unit': so_po_price})
                                                    ]}
        
            request.env['sale.order'].sudo().create(partner_val)

            # ###################################################
        
        return request.render("website_event.registration_complete",
            self._get_registration_confirm_values(event, attendees_sudo))

   
        #res = super(Event2Order, self).registration_confirm(event, **post)


# class OmOdooInheritence(http.Controller):
#     @http.route('/om_odoo_inheritence/om_odoo_inheritence', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/om_odoo_inheritence/om_odoo_inheritence/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('om_odoo_inheritence.listing', {
#             'root': '/om_odoo_inheritence/om_odoo_inheritence',
#             'objects': http.request.env['om_odoo_inheritence.om_odoo_inheritence'].search([]),
#         })

#     @http.route('/om_odoo_inheritence/om_odoo_inheritence/objects/<model("om_odoo_inheritence.om_odoo_inheritence"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('om_odoo_inheritence.object', {
#             'object': obj
#         })
