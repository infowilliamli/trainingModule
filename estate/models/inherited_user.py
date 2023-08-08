from odoo import models, fields

class InheritedUser(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many('estate.model', 'seller_id', string='Users')
