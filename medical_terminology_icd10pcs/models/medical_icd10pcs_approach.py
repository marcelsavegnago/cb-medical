# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalIcd10pcsApproach(models.Model):

    _name = "medical.icd10pcs.approach"
    _description = "Medical Icd10pcs Approach"

    code = fields.Char(required=True)
    name = fields.Char(translate=True)
    section_id = fields.Many2one("medical.icd10pcs.section", required=True)
