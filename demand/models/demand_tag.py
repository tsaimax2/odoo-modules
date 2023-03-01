from odoo import api, fields, models

class DemandTag(models.Model):
    _name = "demand.tag"
    _description = "Demand Tag"

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string="Active", default=True)
    color = fields.Integer(string="Color")