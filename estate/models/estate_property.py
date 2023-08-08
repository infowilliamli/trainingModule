from odoo import models, fields, api, exceptions
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateModel(models.Model):
    _name = 'estate.model'
    _description = 'Estate Property'
    _order = 'id desc'

    name = fields.Char(string="name", required=True)
    description = fields.Text(string="description")
    postcode = fields.Char(string="postcode")
    date_availability = fields.Date(string="date_availability", copy=False, default=fields.Date.add(fields.Date.today(), months=3))
    expected_price = fields.Float(string="expected_price", required=True)
    selling_price = fields.Float(string="selling_price", readonly=True, copy=False)
    bedrooms = fields.Integer(string="bedrooms", default=2)
    living_area = fields.Integer(string="living_areas")
    facades = fields.Integer(string="facades")
    garage = fields.Boolean(string="garage?")
    garden = fields.Boolean(string="garden?")
    garden_area = fields.Integer(string="garden_area")
    garden_orientation = fields.Selection([('north', 'North'),
                                           ('south', 'South'),
                                           ('east', 'East'),
                                           ('west', 'West')
                                           ], string="garden_orientation")
    active = fields.Boolean(string="active", default=True)
    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled')
    ], string='Status', required=True, copy=False, default='new')
    property_type_id = fields.Many2one("estate.type.model", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    seller_id = fields.Many2one('res.users', string="Seller", default=lambda self: self.env.user)
    tags_id = fields.Many2many('estate.tag.model', string='Tags')
    offer_ids = fields.One2many('estate.offer.model', 'property_id', string='Offers')
    total_area = fields.Float(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for area in self:
            area.total_area = area.living_area + area.garden_area

    @api.depends('offer_ids')
    def _compute_best_price(self):
        for price in self:
            prices = price.offer_ids.mapped('price')
            if prices:
                price.best_price = max(prices)
                #if price.state != 'offer_accepted' and price.state != 'sold':
                    #price.state = 'offer_received'
            else:
                price.best_price = 0

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    def action_sold(self):
        for props in self:
            if props.state == 'canceled':
                raise exceptions.UserError('This property has already been canceled, you can not sell.')
            else:
                props.state = 'sold'
        return True

    def action_cancel(self):
        for props in self:
            if props.state == 'sold':
                raise exceptions.UserError('This property has already been sold, you can not cancel.')
            else:
                props.state = 'canceled'
        return True

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 'The expected price should be strictly positive.'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'The selling price must be positive')]

    @api.constrains('selling_price', 'expected_price')
    def check_selling_price(self):
        for price in self:
            if float_is_zero(price.selling_price, 2) is False and float_compare(self.selling_price, self.expected_price*0.9, 2) < 0:
                raise exceptions.ValidationError('The offer must be at least 90% of the expected price!')

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        for link in self:
            if link.state != 'new' and link.state != 'canceled':
                raise exceptions.UserError("Can only delete new or canceled")

    def check_offer(self, price):
        curr_offers = []
        for offers in self:
            for offer in offers.offer_ids:
                curr_offers.append(offer.price)
            if curr_offers:
                if price < min(curr_offers):
                    raise exceptions.UserError("New offer can not be lower than other offers")
            offers.state = 'offer_received'
