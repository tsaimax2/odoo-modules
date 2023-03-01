# -*- coding: utf-8 -*-
"""Church offering report wizard."""

import datetime
from odoo import api, fields, models
from odoo.exceptions import MissingError, UserError


class ChurchOfferingLineAbstractModel(models.AbstractModel):
    """Church OfferingLine Abstract Model."""

    _name = 'report.ng_church.church_offering_report'
    _description = "Report NG Church Church Offering Report"

    def offering_caculator(self, model):
        """offering_caculator."""
        return sum(offering.amount for offering in model)

    # @api.model
    # def render_html(self, docids, data=None):
    #     """."""
    #     name = 'ng_church.church_offering_report'
    #     report_obj = self.env['report']
    #     report = report_obj._get_report_from_name(name)
    #     docargs = {
    #         'doc_ids': docids,
    #         'doc_model': report.model,
    #         'docs': self.env['ng_church.offering_line'].browse(docids),
    #         'offering_caculator': self.offering_caculator
    #     }
    #     return report_obj.render(name, docargs)

    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     if data:
    #         data.update(self.env.company._check_hash_integrity())
    #     else:
    #         data = self.env.company._check_hash_integrity()
    #     return {
    #         'doc_ids' : docids,
    #         'doc_model' : self.env['res.company'],
    #         'data' : data,
    #         'docs' : self.env['res.company'].browse(self.env.company.id),
    #     }

    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     report = self.env['ir.actions.report']._get_report_from_name('base.report_irmodulereference')
    #     selected_modules = self.env['ir.module.module'].browse(docids)
    #     return {
    #         'doc_ids': docids,
    #         'doc_model': "ng_church.offering",
    #         'docs': selected_modules,
    #         'findobj': self._object_find,
    #         'findfields': self._fields_find,
    #     }

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['ng_church.offering'].browse(docids)
        return {
        'doc_ids': docs.ids,
        'doc_model': 'ng_church.offering',
        'docs': self.env['ng_church.offering_line'].browse(docids),
        'offering_caculator': self.offering_caculator
        }

        
class OfferingReportWizard(models.Model):
    """."""

    _name = 'ng_church.offering_wizard'
    _description = "NG Church Offering Wizard"

    date_from = fields.Date(string='Date from')
    date_to = fields.Date(
        string='Date to',
        default=lambda self: datetime.datetime.now().strftime('%Y-%m-%d'))
    offering = fields.Many2one('ng_church.program', required=True)

    def _report_range(self, model, after, before):
        if after > before:
            raise UserError('Date from is ahead of date to')
        if after and before:
            model = model.filtered(lambda r: r.date >= after)
            model = model.filtered(lambda r: r.date <= before)
            return model
        elif after:
            model = model.filtered(lambda r: r.date >= after)
            return model
        model = model.filtered(lambda r: r.date <= before)
        return model

    def check_report(self):
        """."""
        """ query = self.offering
        church = ('church_id', '=', self.env.user.company_id.id)
        services = self.env['ng_church.offering'].search([
            ('service_id', '=', query.id), church])
        offering_line = self.env['ng_church.offering_line']
        for offering in services:
            offering_line += offering_line.search(
                [('offering_id', '=', offering.id), church])
        offerings = self._report_range(
            offering_line, self.date_from, self.date_to)
        if len(offerings) > 0:
            return self.env['report'].\
                get_action(offerings, 'ng_church.church_offering_report')
        raise MissingError('Record not found')
 """
        
        domain=[]
        
        query = self.offering

        #church = [('church_id', '=', self.env.user.company_id.id)]
        # dig out how many lines we have for the serivce(ie prayer1) we want to check 
        services = self.env['ng_church.offering'].search([
            ('service_id', '=', query.id)])
        
        print('services', services)
        """ if offering in services:
            domain += [('offering_id','=',offering.id)] """
        
        date_from = self.date_from
        if date_from:
            domain += [('date','>=',date_from)]

        date_to = self.date_to
        if date_to:
            domain += [('date','<=',date_to)]
        
        print('domain=', domain)
        for offering in services:
            # the offering.id is from the wizard form input
            domain += [('offering_id','=',offering.id)]
            # fetch values from two model
            offerings=self.env['ng_church.offering_line'].search_read(domain)
        print('self',self.read())
        data={
                # form_data is data we input in the wizard, it is a list form, so we need to get the first value [0]
                # the first value [0] is a dictionary!
                'form_data': self.read()[0],
                'offerings': offerings
            }
        print('data=',data)
        # this action_report_appointment located in the report directory and report.xml file (first line)
        return self.env.ref('ng_church.church_offering_report').report_action(self, data=data)  

