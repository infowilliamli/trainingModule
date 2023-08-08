from odoo import models, fields, api, exceptions
from datetime import datetime, timedelta


class EstateModel(models.Model):
    _name = 'estate.offer.model'
    _description = 'Estate Property offers'
    _order = 'price desc'

    price = fields.Float(string='Price')
    status = fields.Selection([('accepted', 'Accepted'), ('refused', 'Refused')], string='Status', copy=False)
    partner_id = fields.Many2one('res.partner', string='Buyer', required=True)
    property_id = fields.Many2one('estate.model', string='Property', required=True)
    validity = fields.Integer(string='Validity', default=7)
    date_deadline = fields.Date(string='Date Deadline', compute='_compute_deadline', inverse='_inverse_validity')
    property_type_id = fields.Char(related="property_id.property_type_id.name", store=True)

    @api.depends('create_date', 'validity')
    def _compute_deadline(self):
        for dates in self:
            if dates.create_date:
                dates.date_deadline = fields.Date.add(dates.create_date, days=dates.validity)
            else:
                dates.date_deadline = fields.Date.add(fields.Date.today(), days=dates.validity)

    def _inverse_validity(self):
        for dates in self:
            if not dates.create_date:
                dates.create_date = fields.Date.today()
            a = fields.Date.to_string(dates.create_date)
            a = a.split('-')
            b = fields.Date.to_string(dates.date_deadline)
            b = b.split('-')
            d1 = datetime(int(a[0]), int(a[1]), int(a[2]), 0, 0, 0)
            d2 = datetime(int(b[0]), int(b[1]), int(b[2]), 0, 0, 0)
            c = int((d2-d1) / timedelta(days=1))
            dates.validity = c

    def action_accept(self):
        for props in self:
            if props.property_id.selling_price == 0:
                props.status = 'accepted'
                props.property_id.buyer_id = props.partner_id
                props.property_id.selling_price = props.price
                props.property_id.state = 'offer_accepted'
            else:
                raise exceptions.UserError('This property has already been sold')
        return True

    def action_refuse(self):
        for props in self:
            props.status = 'refused'
        return True

    _sql_constraints = [('check_offer_price', 'CHECK(price > 0)', 'Offer price must be strictly positive')]

    @api.model
    def create(self, vals):
        new_price = vals['price']
        self.env['estate.model'].browse(vals['property_id']).check_offer(new_price)
        return super(EstateModel, self).create(vals)
