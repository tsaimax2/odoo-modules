# -*- coding:utf-8 -*-
"""Church Collections consists of all church weekly or monthly collections."""
from odoo.addons.ng_church.models.helper import parish
from odoo.http import request
from odoo import api, fields, models
from odoo.exceptions import AccessError,\
    MissingError, UserError, ValidationError


class Collection(models.Model):
    """Ng Church Collection Model."""

    _name = 'ng_church.collection'
    _description = "NG Church Collection"

    name = fields.Char(string="Name")


class Donation(models.Model):
    """Donation Model.

    Church Donation is cetain sum of money that is given
    to a church as charity.
    """

    _name = 'ng_church.donation'
    _description = "NG Church Donation"

    name = fields.Many2one('project.project', 'Project', required=True)
    start_date = fields.Date(related='name.x_date', string='Start Date')
    notes = fields.Text(string='Note')
    church_id = fields.Many2one('res.company', default=parish)
    donation_line_ids = fields.One2many('ng_church.donation_line',
                                        'donation_id', srting='Donations')


class DonationLine(models.Model):
    """Donation Line Model.

    Church Donation is cetain sum of money that is
    given to a church as charity.
    """

    _name = 'ng_church.donation_line'
    _description = "NG Church Donation Line"

    donation_id = fields.Many2one('ng_church.donation', string='Donation')
    name = fields.Char(string='Date')
    date = fields.Date(string='Date', required=True)
    donor_id = fields.Many2one('res.partner', string='Donor')
    amount = fields.Float(string='Donated Amount', required=True)
    is_invoiced = fields.Boolean(string='Invoiced', readonly=True)
    notes = fields.Char(related='donation_id.name.name')
    church_id = fields.Many2one('res.company', default=parish)

    @api.constrains('amount')
    def _check_valid_amount(self):
        for donation_l in self:
            if donation_l.amount < 1:
                raise ValidationError('Please enter a valid amount of'
                                      ' money {} can\'t be'
                                      ' deposited'.format(self.amount))

    @api.onchange('date')
    def _onchange_name(self):
        if self.date:
            self.name = self.date.strftime("%B %d, %Y")

    def _prepare_account_voucher(self):
        """Generate Account Voucher."""
        company = self.env.user and self.env.user.company_id or False
        voucher = self.env['account.payment'].create({
            # 'company_id': company and company.id or False,
            'partner_id': self.donor_id.id,
            'partner_type' : 'customer',
            # 'pay_now': 'pay_now',
            # 'account_id': company and company.transit_account and
            # company.transit_account.id or False,
            'payment_method_id' : self.env.ref("account.account_payment_method_manual_in").id,
            'journal_id': company and company.donation_journal and
            company.donation_journal.id or False,
            # 'name': '{} Donation'.format(self.donor_id.name or 'Anonymous'),
            'payment_type': 'inbound',
            'amount' : self.amount

        })
        return voucher

    # def _prepare_account_voucher_line(self, voucher_id):
    #     payload = self.env['account.move.line'].create({
    #         'name': self.notes,
    #         # Quantity is intentionally hard coded to be int: 1.
    #         'quantity': 1,
    #         'price_unit': self.amount,
    #         'voucher_id': voucher_id and voucher_id.id or False,
    #         # credit account
    #         'account_id': self.env.user.company_id and \
    #         self.env.user.company_id.donation_account and \
    #         self.env.user.company_id.donation_account.id or False
    #     })
    #     return payload

    def generate_donation_voucher(self):
        """User Interface button call this method."""
        voucher_id = self._prepare_account_voucher()
        # self._prepare_account_voucher_line(voucher_id)
        self.is_invoiced = True


class Tithe(models.Model):
    """Tithe Model.

    One tenth of produce or earnings, formerly taken as a tax for
    the support of the church and clergy.
    """

    _name = 'ng_church.tithe'
    _description = "NG Church Tithe"

    def _compute_default_collection(self):
        category = self.env['ng_church.collection'].name_search(
            'Tithes', limit=1)
        if category:
            # Remove the item at the given position in the list,
            # and unpack the tupple
            category_id, category_name = category.pop(0)
            return category_id
        else:
            self.env['ng_church.collection'].create({'name': 'Tithes'})
            category = self.env['ng_church.collection'].name_search(
                'Tithes', limit=1)
            category_id, category_name = category.pop(0)
            return category_id
            

    name = fields.Many2one('ng_church.collection', string='Collection',
                           default=_compute_default_collection)
    section_id = fields.Many2one(
        'church.sections', string="Church Section", required=True)
    service_id = fields.Many2one('ng_church.program', string="Church Service")
    pastor_id = fields.Many2one('ng_church.pastor', string='Minister\'s Name')
    church_id = fields.Many2one(
        'res.company', string='Church\'s Tithe', default=parish)
    is_pastor_tithe = fields.Boolean(string='Minister\'s Tithe')
    tithe_line_ids = fields.One2many(
        'ng_church.tithe_lines', 'tithe_id', string='Tithes')


class TitheLine(models.Model):
    """TitheLine Model.

    One tenth of produce or earnings,
    formerly taken as a tax for the support of the church and clergy.
    """

    _name = 'ng_church.tithe_lines'
    _description = "NG Church Tithe Lines"

    date = fields.Date(string='Date', required=True)
    name = fields.Char(string='Name')
    tithe_type = fields.Selection(
        selection=[('members', 'Members'), ('pastor', 'Pastor'),
                   ('minister', 'Minister')], string='Category',
        default='members')
    # changed by max
    tither = fields.Many2one('res.partner', string='Tither Name', domain=[('membership_status_id','=',2)])
    is_invoiced = fields.Boolean(string='Invoiced', readonly=True)
    tithe_id = fields.Many2one('ng_church.tithe', string='Tithe')
    amount = fields.Float('Amount', required=True)
    church_id = fields.Many2one('res.company', default=parish)

    @api.constrains('amount')
    def _check_valid_amount(self):
        for tithe_l in self:
            if tithe_l.amount < 1:
                raise ValidationError('Please enter a valid amount of'
                                      ' money {} can\'t be'
                                      ' deposited'.format(tithe_l.amount))

    @api.onchange('date')
    def _onchange_name(self):
        if self.date:
            self.name = self.date.strftime("%B %d, %Y")

    def _prepare_account_voucher(self):
        """Generate Account Voucher."""
        # sudo is edited by max, to create a line in account_payment db
        company = self.env.user and self.env.user.company_id or False
        #print('partner_id:',self.tither.id)
        #print('payment_method_id',self.env.ref("account.account_payment_method_manual_in").id)
        #print('journal_id', company.tithe_journal.id)
        #print('amount', self.amount)
        voucher_val={
            # paymentMethod, Date journal, are required, some of it are done by hard coding to facilitate
            # 'company_id': company and company.id or False,
            'partner_id': self.tither.id,
            'partner_type' : 'customer',
            # 'pay_now': 'pay_now',
            # 'account_id': company and company.transit_account and
            # company.transit_account.id or False,
            'payment_method_id' : self.env.ref("account.account_payment_method_manual_in").id,
            #'payment_method_id' : 1,
            'create_date': self.date,
            #'journal_id': company.tithe_journal.id,
            'journal_id': 7,
            # 'name': '{} Donation'.format(self.donor_id.name or 'Anonymous'),
            'payment_type': 'inbound',
            'amount' : self.amount
        }  
        #print('voucher_val=', voucher_val)
        #voucher = self.env['account.payment'].sudo().create({
        voucher_id = request.env['account.payment'].sudo().create(voucher_val)
        #print('voucher=','5')
        return voucher_id, voucher_val

        # company = self.env.user.company_id
        # payload = {
        #     'company_id': company.id,
        #     'partner_id': self.env.user.partner_id.id,
        #     'pay_now': 'pay_now',
        #     'account_id': company.transit_account.id,
        #     'journal_id': company.tithe_journal.id,
        #     'name': '{} Tithe'.format(self.tithe_type.capitalize()),
        #     'voucher_type': 'sale'

        # }
        # voucher = voucher.create(payload)
        # return voucher

    # def _prepare_account_voucher_line(self, voucher_id):
    #     payload = {
    #         'name': 'Tithe',
    #         # Quantity is intentionally hard coded to be int: 1.
    #         'quantity': 1,
    #         'price_unit': self.amount,
    #         'voucher_id': voucher_id.id,
    #         # credit account
    #         'account_id': self.env.user.company_id.tithe_account.id
    #     }
    #     return voucher_line.create(payload)

    def generate_tithe_voucher(self):
        """User Interface button call this method."""
        voucher_id, voucher = self._prepare_account_voucher()
        print('voucher_id=', voucher_id)
        # self._prepare_account_voucher_line(voucher_id)
        self.is_invoiced = True
        # added by max
        # this action_report_appointment located in the report directory and report.xml file
        data={
                # form_data is data we input in the wizard, it is a list form, so we need to get the first value [0]
                # the first value [0] is a dictionary!
                'form_data': self.read()[0],
                'voucher': voucher
            }
        print('data=',data)    
        return self.env.ref('ng_church.church_tithe_voucher').report_action(self, data=data) 


class Offering(models.Model):
    """Church Offering Model."""

    _name = 'ng_church.offering'
    _description = "NG Church Offering"

    def _compute_default_collection(self):
        category = self.env['ng_church.collection'].name_search(
            'Offering', limit=1)
        if category:
            # Remove the item at the given position in the list,
            # and unpack the tupple
            category_id, category_name = category.pop(0)
            return category_id
        else:
            self.env['ng_church.collection'].create({'name': 'Offering'})
            category = self.env['ng_church.collection'].name_search(
                'Offering', limit=1)
            category_id, category_name = category.pop(0)
            return category_id

    name = fields.Many2one('ng_church.collection', string='Collection Source',
                           default=_compute_default_collection)
    section_id = fields.Many2one('church.sections', string="Church Section",
                                 required=True)
    service_id = fields.Many2one('ng_church.program', string="Church Service")
    church_id = fields.Many2one('res.company', default=parish)
    offering_line_ids = fields.One2many('ng_church.offering_line',
                                        'offering_id', string='Offering')


class OfferingLine(models.Model):
    """Church Offering lines model."""

    _name = 'ng_church.offering_line'
    _description = "NG Church Offering Line"

    date = fields.Date(string='Date', required=True)
    name = fields.Char(string='Date')
    is_invoiced = fields.Boolean(string='Invoiced')
    offeror_id = fields.Many2one('res.partner', string='Offeror')
    amount = fields.Float(string='Amount')
    offering_id = fields.Many2one('ng_church.offering', string='Offering')
    church_id = fields.Many2one('res.company', default=parish)

    @api.constrains('amount')
    def _check_valid_amount(self):
        for offering_l in self:
            if offering_l.amount < 1:
                raise ValidationError('Please enter a valid amount of'
                                      ' money {} can\'t be'
                                      ' deposited'.format(offering_l.amount))

    @api.onchange('date')
    def _onchange_name(self):
        if self.date:
            self.name = self.date.strftime("%B %d, %Y")

    def _prepare_account_voucher(self):
        """Generate Account Voucher."""

        company = self.env.user and self.env.user.company_id or False
        voucher = self.env['account.payment'].create({
            # 'company_id': company and company.id or False,
            'partner_id': self.offeror_id.id,
            'partner_type' : 'customer',
            # 'pay_now': 'pay_now',
            # 'account_id': company and company.transit_account and
            # company.transit_account.id or False,
            'payment_method_id' : self.env.ref("account.account_payment_method_manual_in").id,
            'journal_id': company.tithe_journal.id,
            # 'name': '{} Donation'.format(self.donor_id.name or 'Anonymous'),
            'payment_type': 'inbound',
            'amount' : self.amount

        })
        return voucher

    

    # def _prepare_account_voucher_line(self, voucher_id):
    #     payload = {
    #         'name': 'Offering',
    #         # Quantity is intentionally hard coded to be int: 1.
    #         'quantity': 1,
    #         'price_unit': self.amount,
    #         'voucher_id': voucher_id and voucher_id.id or False,
    #         # credit account
    #         'account_id': self.env.user and \
    #         self.env.user.company_id and \
    #         self.env.user.company_id.offering_account and \
    #         self.env.user.company_id.offering_account.id or False
    #     }
    #     return voucher_line.create(payload)

    def generate_offering_voucher(self):
        """User Interface button call this method."""
        # if self._uid != self.write_uid.id:
        #     raise AccessError(
        #         'You don\'t have the permission to Draft this invoice')
        #     return False
        voucher_id = self._prepare_account_voucher()
        # voucher_line_id = self._prepare_account_voucher_line(voucher_id)
        self.is_invoiced = True
        # return voucher_line_id

class Pledge(models.Model):
    """."""

    _name = 'ng_church.pledge'
    _description = "NG Church Pledge"

    name = fields.Many2one('project.project', string='Project', required=True)
    date = fields.Date(related='name.x_date', string='Date')
    church_id = fields.Many2one('res.company', default=parish)
    pledge_line_ids = fields.One2many('ng_church.pledge_line', 'pledge_id',
                                      string='Pledges')


    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['ng_church.pledge'].browse(docids)
        return {
        'doc_ids': docs.ids,
        'doc_model': 'ng_church.pledge',
        'docs': self.env['ng_church.pledge_line'].browse(docids),
        'presenter': self.reports_presenter
        }

class PledgeLine(models.Model):
    """."""

    _name = 'ng_church.pledge_line'
    _description = "NG Church Pledge Line"

    name = fields.Char(string='Name', related='pledge_id.name.name')
    date = fields.Date(string='Pledged Date', required=True)
    # replace ng_church.associate model with res.partner

    pledger = fields.Many2one('res.partner', string='Pledger')
    
    # pledger = fields.Many2one('ng_church.associate', string='Pledger')
    amount = fields.Float(string='Pledged Amount')
    balance = fields.Float(string='Balance',
                           compute='_compute_balance', store=True)
    paid = fields.Float(string='Paid', compute='_compute_total_paid',
                        store=True)
    is_invoiced = fields.Char(string='Invoiced', default=False)
    state = fields.Selection(selection=[('active', 'Active'),
                                        ('fulfilled', 'Fulfilled')],
                             default='active')
    pledge_id = fields.Many2one('ng_church.pledge', string='Pledge')
    pledge_line_payment_ids = fields.One2many('ng_church.pledge_line_payment',
                                              'pledge_line_id',
                                              string='Pledge Payment')

    @api.constrains('amount')
    def _check_valid_amount(self):
        for pledge_l in self:
            if pledge_l.amount < 1:
                raise ValidationError('Please enter a valid amount of'
                                      ' money {} can\'t be'
                                      ' pledged'.format(pledge_l.amount))

    @api.depends('pledge_line_payment_ids')
    def _compute_total_paid(self):
        for pledge_l in self:
            total = 0
            for pledge_line_id in self.pledge_line_payment_ids:
                for pledge in pledge_line_id:
                    total += pledge.amount
            pledge_l.paid = total

    @api.depends('paid')
    def _compute_balance(self):
        for pledge_l in self:
            if pledge_l.paid >= pledge_l.amount:
                pledge_l.write({'state': 'fulfilled'})
            else:
                pledge_l.write({'state': 'active'})
            pledge_l.balance = 0.0 if (pledge_l.amount - pledge_l.paid) < 1 \
                else (pledge_l.amount - pledge_l.paid)

    def send_by_email(self):
        """Send report via email."""
        # ir_model_data = self.env['ir.model.data']
        # try:
        #     template_id = ir_model_data.get_object_reference(
        #         'ng_church', 'ng_church_pledge_payment_email_template')[1]
        #     print("::::;template_id",template_id)
        # except ValueError:
        #     template_id = False
        # try:
        #     compose_form_id = ir_model_data.get_object_reference(
        #         'mail', 'email_compose_message_wizard_form')[1]
        #     print("::::;compose_form_id",compose_form_id, self.id)
        # except ValueError:
        #     compose_form_id = False
        # ctx = {
        #     'default_model': 'ng_church.pledge_line',
        #     'default_res_id': self._ids[0],
        #     'default_use_template': bool(template_id),
        #     'default_template_id': template_id,
        #     'default_composition_mode': 'comment',
        # }

        """ template_id = self.env['ir.model.data'].get_object_reference(
                'ng_church',
                'ng_church_pledge_payment_email_template')[1] 
        template_rec = self.env['mail.template'].browse(template_id)
        template_rec.send_mail(self.id, force_send=True) """
        
        # attempt by max
       
        template= self.env.ref('ng_church.ng_church_pledge_payment_email_template')
        
        for rec in self:
            if rec.pledger.email:
            # we can use the following to overwrite what in mail template
                email_values= {'subject': 'Pledge Notification'}             
                template.send_mail(rec.id, force_send=True, email_values=email_values)  
        
        
        # return {      
        #      'type': 'ir.actions.act_window',  
        #      'view_type': 'form',          
        #      'view_mode': 'form',       
        #      'res_model': 'mail.compose.message',   
        #      'views': [(compose_form_id, 'form')],   
        #      'view_id': compose_form_id,        
        #      'target': 'new',          
        #      'context': ctx,    
        #      }

        # return {
        #     'name': 'Compose Email',
        #     'type': 'ir.actions.act_window',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'mail.compose.message',
        #     'views': [(compose_form_id, 'form')],
        #     'view_id': compose_form_id,
        #     'target': 'new',
        #     'context': ctx,
        # }

    # @api.model
    # def message_get_reply_to(self, res_id, default=None):
    #     """message_get_reply_to."""
    #     if self.env.user.company_id.email is False:
    #         raise MissingError('Set church email address')
    #     return {res_id[0]: self.env.user.company_id.email}


    
    @api.model
    def print_report(self, docids, data=None):
        print("::::;docs",docids)
        docs = self.env['ng_church.pledge_line'].browse(docids)
        return self.env.ref('ng_church.pledge_report_reg').report_action([], data=data)

        # return {
        # 'doc_ids': docs.ids,
        # 'doc_model': 'ng_church.pledge',
        # 'docs': self.env['ng_church.pledge_line'].browse(docids),
        # }
        # datas = {'ids': self.env.context.get('active_ids', [])}
        

    # def print_report(self):
    #     """Direct Report printing."""
    #     return self.env['ir.actions.report'].report_action(self,
    #                                          'ng_church.print_pledge_report')

    def _prepare_account_voucher(self):
        """Generate Account Voucher."""

        company = self.env.user and self.env.user.company_id or False
        voucher = self.env['account.payment'].create({
            # 'company_id': company and company.id or False,
            'partner_id': self.pledger.id,
            'partner_type' : 'customer',
            # 'pay_now': 'pay_now',
            # 'account_id': company and company.transit_account and
            # company.transit_account.id or False,
            'payment_method_id' : self.env.ref("account.account_payment_method_manual_in").id,
            'journal_id': company.pledge_journal.id,
            # 'name': '{} Donation'.format(self.donor_id.name or 'Anonymous'),
            'payment_type': 'inbound',
            'amount' : self.amount

        })
        return voucher



    # def _prepare_account_voucher(self):
    #     """Generate Account Invoice."""
    #     company = self.env.user.company_id
    #     voucher = voucher.create({
    #         'partner_id': company.partner_id.id,
    #         'pay_now': 'pay_now',
    #         'account_id': company.transit_account.id,
    #         'journal_id': company.pledge_journal.id,
    #         'name': '{} Pledge'.format(self.name),
    #         'voucher_type': 'sale'

    #     })

        # return voucher

    # def _prepare_account_voucher_line(self, voucher_id):
    #     company = self.env.user.company_id
    #     payload = {
    #         'name': voucher_id.name,
    #         # Quantity is intentionally hard coded to be int: 1.
    #         'quantity': 1,
    #         'price_unit': self.paid,
    #         'voucher_id': voucher_id.id,
    #         'account_id': company.pledge_account.id
    #     }
    #     return voucher_line.create(payload)

    def generate_pledge_voucher(self):
        """User Interface button call this method."""
        if not self.is_invoiced:
            voucher_id = self._prepare_account_voucher()
            # voucher_line_id = self._prepare_account_voucher_line(voucher_id)
            self.is_invoiced = True
            # return voucher_line_id
        # raise UserError('Voucher already existed')


class PledgeLinePayment(models.Model):
    """Ng Church Pledge Line Payment."""

    _name = 'ng_church.pledge_line_payment'
    _description = "NG Church Pledge Line Payment"

    date = fields.Date(string='Date', required=True)
    amount = fields.Float(string='Amount')
    pledge_line_id = fields.Many2one('ng_church.pledge_line')

    @api.constrains('amount')
    def _check_valid_amount(self):
        for pledge_l in self:
            if pledge_l.amount < 1:
                raise ValidationError('Please enter a valid amount of'
                                      ' money {} can\'t be'
                                      ' deposited'.format(pledge_l.amount))
