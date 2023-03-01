# -*- coding: utf-8 -*-
"""Church tithe report wizard."""

import datetime
from odoo import api, fields, models
from odoo.exceptions import MissingError, UserError


class ChurchTitheLineAbstractModel(models.AbstractModel):
    """Church TitheLine Abstract Model."""

    _name = 'report.ng_church.church_tithe_report'
    _description = "Report NG Church Tithe"

    def tithe_caculator(self, model):
        """tithe_caculator."""
        return sum(tithe.amount for tithe in model)

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['ng_church.tithe'].browse(docids)
        return {
        'doc_ids': docs.ids,
        'doc_model': 'ng_church.tithe',
        'docs': self.env['ng_church.tithe_lines'].browse(docids),
        'tithe_caculator': self.tithe_caculator
        }

    # @api.model
    # def render_html(self, docids, data=None):
    #     """."""
    #     name = 'ng_church.church_tithe_report'
    #     report_obj = self.env['report']
    #     report = report_obj._get_report_from_name(name)
    #     docargs = {
    #         'doc_ids': docids,
    #         'doc_model': report.model,
    #         'docs': self.env['ng_church.tithe_lines'].browse(docids),
    #         'tithe_caculator': self.tithe_caculator
    #     }
    #     return report_obj.render(name, docargs)


class TitheReportWizard(models.Model):
    """."""

    _name = 'ng_church.tithe_wizard'
    _description = "NG Church Tithe Wizard"

    date_from = fields.Date(string='Date from')
    date_to = fields.Date(string='Date to',
                          default=lambda self: datetime.datetime.now().
                          strftime('%Y-%m-%d'))
    tithe = fields.Selection(selection=[('all', 'All'), ('members', 'Members'),
                                        ('pastor', 'Pastor'),
                                        ('minister', 'Minister')],
                             string='Category', default='all',
                             required=True)

    """ def _report_range(self, model, after, before):
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
 """
    def check_report(self):
        """."""
        """ query = self.tithe
        church = ('church_id', '=', self.env.user.company_id.id)
        domain = [('tithe_type', '=', query),
                  church] if self.tithe != 'all' else [church]
        tithes = self._report_range(self.env['ng_church.tithe_lines'].search(
            domain), self.date_from, self.date_to)
        if len(tithes) > 0:
            return self.env['report'].\
                get_action(tithes, 'ng_church.church_tithe_report')
        raise MissingError('Record not found') """

        domain=[]
        
        query = self.tithe

        #church = [('church_id', '=', self.env.user.company_id.id)]
        # dig out how many lines we have for the serivce(ie prayer1) we want to check 
        if query != 'all':
            domain += [('tithe_type', '=', query)]
        
        #print('services', services)
        """ if offering in services:
            domain += [('offering_id','=',offering.id)] """
        
        date_from = self.date_from
        if date_from:
            domain += [('date','>=',date_from)]

        date_to = self.date_to
        if date_to:
            domain += [('date','<=',date_to)]
        
        print('domain=', domain)
        
            # fetch values from two model
        tithes=self.env['ng_church.tithe_lines'].search_read(domain)
        print('self',self.read())
        data={
                # form_data is data we input in the wizard, it is a list form, so we need to get the first value [0]
                # the first value [0] is a dictionary!
                'form_data': self.read()[0],
                'tithes': tithes
            }
        print('data=',data)
        # this action_report_appointment located in the report directory and report.xml file (first line)
        return self.env.ref('ng_church.church_tithe_report').report_action(self, data=data)  


