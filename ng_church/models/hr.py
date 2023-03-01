# -*- coding: utf-8 -*-
##############################################################################
# hr.employee
#    Odoo, Open Source Management Solution
#    Copyright (C) 2013-Today Mattobell (<http://www.mattobell.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from odoo import fields, models


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    related_member_id = fields.Many2one('res.partner', string="Related Member")

