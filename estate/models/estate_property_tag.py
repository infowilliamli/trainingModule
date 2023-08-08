from odoo import models, fields


class EstateModel(models.Model):
    _name = 'estate.tag.model'
    _description = 'Estate property tags'
    _order = 'name asc'

    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color')

    _sql_constraints = [('check_tag_unique', 'unique(name)', 'Tag must be unique')]
