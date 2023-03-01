# -*- coding:utf-8 -*-
"""Church followership."""
from datetime import date
from odoo import api, fields, models, SUPERUSER_ID

AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Low'),
    ('2', 'High'),
    ('3', 'Very High'),
]


class MemberFollowUp(models.Model):
    """Manage church first timer untill they become full member."""

    def _default_stage(self):
        stages = self.env['ng_church.member_stage'].search([])
        return stages[0].id

    _name = 'ng_church.followup_member'
    _description = "NG Church Followup Member"
    # add domain by max, refer to database: membership_status_id
    name = fields.Many2one('res.partner', string='Member', domain=[('membership_status_id','=',2)])
    email = fields.Char(related='name.email', string='Email')
    phone = fields.Char(related='name.phone', string='Phone')
    next_activity_id = fields.Many2one('mail.activity.type', string='Activity')
    stage_id = fields.Many2one('ng_church.member_stage', string='Stage',
                               index=True, track_visibility='onchange',
                               group_expand='_read_group_stage_ids',
                               default=_default_stage)
    priority = fields.Selection(AVAILABLE_PRIORITIES, string='Priority',
                                default='0')
    date_action = fields.Date('Next Activity Date', index=True)
    color = fields.Integer('Color Index', default=0)
    kanban_state = fields.Selection(
        [('grey', 'No next activity planned'),
         ('red', 'Next activity late'),
         ('green', 'Next activity is planned')],
        string='Activity State', compute='_compute_kanban_state')

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """Read group stage method.

        Read group customization in order to display all the
        stages in the kanban view, even if they are empty.
        """
        stage_ids = stages._search(
            [], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    def _compute_kanban_state(self):
        today = date.today()
        for follow_ups in self:
            print('follow_ups.data_action 1:', follow_ups.date_action)
            if follow_ups.date_action:
                follow_ups.kanban_state = 'grey'
                followup_date = fields.Date.from_string(follow_ups.date_action)
                if followup_date >= today:
                    follow_ups.kanban_state = 'green'
                else:
                    follow_ups.kanban_state = 'red'


class FirstTimerFollowUp(models.Model):
    """Manage church first timer untill they become full member."""

    def _default_stage(self):
        stages = self.env['ng_church.first_timer_stage'].search([])
        print('stages=', stages)
        return stages[0].id

    _name = 'ng_church.followup_first_timer'
    _description = "NG Church Followup First Timer"
    # domain changed by max
    name = fields.Many2one('res.partner', string='First Timer', domain=[('membership_status_id','=',1)])
    email = fields.Char(related='name.email', string='Email')
    phone = fields.Char(related='name.phone', string='Phone')
    next_activity_id = fields.Many2one('mail.activity.type', string='Activity')
    stage_id = fields.Many2one('ng_church.first_timer_stage', string='Stage',
                               index=True, track_visibility='onchange',
                               group_expand='_read_group_stage_ids',
                               default=_default_stage)
    print('stage_id', stage_id)
    priority = fields.Selection(AVAILABLE_PRIORITIES, string='Priority',
                                default='0')
    date_action = fields.Date('Next Activity Date', index=True)
    color = fields.Integer('Color Index', default=0)
    print('I am here')
    kanban_state = fields.Selection(
        [('grey', 'No next activity planned'),
         ('red', 'Next activity late'),
         ('green', 'Next activity is planned')],
        string='Activity State', compute='_compute_kanban_state')

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """Read Group Statge method.

        Read group customization in order to display all the stages in
        the kanban view, even if they are empty.
        """
        stage_ids = stages._search(
            [], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    def _compute_kanban_state(self):
        today = date.today()
        #print('self=', self)
        for follow_ups in self:
            print('follow_ups.data_action 2:', follow_ups.date_action)
            if follow_ups.date_action:
                follow_ups.kanban_state = 'grey'
                followup_date = fields.Date.from_string(follow_ups.date_action)
                if followup_date >= today:
                    follow_ups.kanban_state = 'green'
                else:
                    follow_ups.kanban_state = 'red'


class FirstTimerStage(models.Model):
    """Model for case stages."""

    _name = "ng_church.first_timer_stage"
    _description = "Stage of case"
    _rec_name = 'name'
    _order = "sequence, name, id"

    name = fields.Char('Stage Name', required=True)
    sequence = fields.Integer('Sequence', default=1,
                              help="Used to order stages. Lower is better.")
    fold = fields.Boolean(string='Folded in Pipeline',
                          help='This stage is folded in the kanban'
                          ' view when there are no records in that'
                          ' stage to display.')


class MemberStage(models.Model):
    """Model for case stages."""

    _name = "ng_church.member_stage"
    _description = "Stage of case"
    _rec_name = 'name'
    _order = "sequence, name, id"

    name = fields.Char('Stage Name', required=True)
    sequence = fields.Integer('Sequence', default=1,
                              help="Used to order stages. Lower is better.")
    fold = fields.Boolean(string='Folded in Pipeline',
                          help='This stage is folded in the kanban'
                          ' view when there are no records in'
                          ' that stage to display.')
