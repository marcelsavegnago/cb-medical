from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from random import choice
from string import digits


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _default_personal_identifier(self):
        pid = None
        while not pid or self.env['hr.employee'].search(
                [('personal_identifier', '=', pid)]):
            pid = "".join(choice(digits) for i in range(8))
        return pid

    partner_id = fields.Many2one(
        'res.partner',
        required=True,
        readonly=True,
        store=True,
        string='Related partner'
    )
    name = fields.Char(
        compute=False,
        related='partner_id.name',
        readonly=True,
    )
    firstname = fields.Char(
        related='partner_id.firstname'
    )
    lastname = fields.Char(
        related='partner_id.lastname'
    )
    lastname2 = fields.Char(
        related='partner_id.lastname2'
    )

    identification_id_expiration = fields.Date(
        string="Identification No Expire Date"
    )
    user_id = fields.Many2one(
        readonly=True,
        compute='_compute_user',
        store=True,
    )
    personal_identifier = fields.Char(
        string='Personal ID',
        default=lambda r: r._default_personal_identifier(),
        readonly=True,
        copy=False
    )
    personal_email = fields.Char(related='partner_id.email')
    personal_phone = fields.Char(related='partner_id.mobile')
    personal_mobile = fields.Char(related='partner_id.phone')

    show_info = fields.Boolean('Able to see Private Info',
                               compute='_compute_show_info')

    parent_id = fields.Many2one(
        related='department_id.manager_id',
        readonly=True
    )
    company_id = fields.Many2one(
        related='contract_id.company_id',
        readonly=True
    )
    working_hours_type = fields.Selection(
        string='Working Hours Type',
        selection=[('full', 'Full Time'),
                   ('part', 'Part time'),
                   ('reduced', 'Reduced')],
        related='contract_id.working_hours_type',
        readonly=True
    )

    percentage_of_reduction = fields.Integer(
        string='Percentage of reduction',
        related='contract_id.percentage_of_reduction',
        readonly=True
    )

    locker = fields.Char(string='Locker')

    address_id = fields.Many2one(
        related='company_id.partner_id',
        readonly=True
    )
    manager = fields.Boolean(compute='_compute_is_manager', readonly=True)

    # groups
    address_home_id = fields.Many2one(groups="base.group_user")
    country_id = fields.Many2one(groups="base.group_user")
    gender = fields.Selection(groups="base.group_user")
    marital = fields.Selection(groups="base.group_user")
    birthday = fields.Date(groups="base.group_user")
    ssnid = fields.Char(groups="base.group_user")
    sinid = fields.Char(groups="base.group_user")
    identification_id = fields.Char(groups="base.group_user")
    passport_id = fields.Char(groups="base.group_user")
    permit_no = fields.Char(groups="base.group_user")
    visa_no = fields.Char(groups="base.group_user")
    visa_expire = fields.Date(groups="base.group_user")
    children = fields.Integer(
        groups="base.group_user",
        compute='_compute_children_count',
        store=True
    )

    @api.multi
    def toggle_active(self):
        for record in self:
            record.active = not record.active
            if record.partner_id:
                record.partner_id.write({'active': record.active})

    @api.depends('fam_children_ids')
    def _compute_children_count(self):
        for record in self:
            record.children = len(record.fam_children_ids)

    @api.depends('partner_id.user_ids')
    def _compute_user(self):
        for record in self:
            record.user_id = record.partner_id.user_ids[1:]

    @api.multi
    def action_open_related_partner(self):
        action = self.env.ref('cb_hr_views.action_open_related_partner')
        result = action.read()[0]
        result['views'] = [(False, 'form')]
        result['res_id'] = self.partner_id.id
        return result

    @api.multi
    def _compute_show_leaves(self):
        for employee in self:
            employee.show_leaves = employee.show_info

    @api.multi
    def _compute_show_info(self):
        is_manager = self.env['res.users'].has_group(
            'hr.group_hr_manager')
        is_officer = self.env['res.users'].has_group(
            'hr.group_hr_user')
        for employee in self:
            if is_manager or employee.user_id == self.env.user:
                employee.show_info = True
            elif is_officer and employee.parent_id.user_id == self.env.user:
                employee.show_info = True
            else:
                employee.show_info = False

    @api.multi
    def _compute_is_manager(self):
        managers = self.env['hr.department'].search([]).mapped('manager_id')
        for record in self:
            record.manager = record.id in managers.ids

    @api.constrains('partner_id.is_practitioner')
    def _check_practitioner(self):
        for record in self:
            if record.partner_id.is_practitioner:
                raise ValidationError(_(
                    'All employees must be practitioners'
                ))