from odoo import models, fields, Command

class EstateModel(models.Model):
    _inherit = 'estate.model'

    def action_sold(self):
        for order in self:
            invoice_vals = order._prepare_invoice()

            self.env['account.move'].create(invoice_vals)

        return super().action_sold()

    def _prepare_invoice(self):
        invoice_vals = {
            'partner_id': self.buyer_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': [
                Command.create({
                    "name": self.name,
                    "quantity": 1,
                    "price_unit": (self.selling_price * 0.06) + 100
                })
            ]
        }
        return invoice_vals