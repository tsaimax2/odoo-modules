from datetime import date
from odoo import api, fields, models
from odoo.tools import image

class DemandCreator(models.Model):
    # table name for the table to be created in DB
    _name = 'demand.creator'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Create demand by press create'
    
    #abc = fields.Many2many('demand.tag', string="Tags_2")
    
    #@api.model
    #def get_demand(self):
    #    return self.env['demand.tag'].search([('type', 'in', 'demand')]).ids

class AddField(models.Model):
    # we need to tell which database we are goint to modify
    _inherit = "event.event"
    # to add a column into the event.event database
    service_id =  fields.Many2one('demand.tag', string="Service_Kinds", required=True)
    