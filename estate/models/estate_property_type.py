from odoo import models, fields, api


class EstateTypeModel(models.Model):
    _name = 'estate.type.model'
    _description = 'Different Estate Types'
    _order = "sequence, name asc"

    name = fields.Char(string="Type", required=True)
    property_ids = fields.One2many('estate.model', 'property_type_id', string="Properties")
    sequence = fields.Integer(string='Sequence', default=1)
    offer_ids = fields.One2many('estate.model', 'property_type_id', string="Offers")
    offer_count = fields.Integer(string='Number of offers', compute="_compute_offers")

    _sql_constraints = [('check_type_unique', 'unique(name)', 'Type must be unique')]

    @api.depends('offer_ids')
    def _compute_offers(self):
        for offers in self:
            offers.offer_count = len(offers.offer_ids.offer_ids)
