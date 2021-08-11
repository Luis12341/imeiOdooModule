# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)



class AddImeisWizards(models.TransientModel):
    _name = "product.imei.wz"

    product_id = fields.Many2one('product.template')
    imeis = fields.One2many("product.imei.add.wz", "registerId")
    numberOfImeisWithoutAdd = fields.Integer(string="IMEI Sin registrar")
    numberOfImeisForAdd = fields.Integer(string="IMEI para Agregar")
    passed = fields.Boolean(string='passed',default=True)

    @api.model
    def default_get(self, fields_list):
        res = super(AddImeisWizards, self).default_get(fields_list)
        act_ids = self._context.get("active_ids")
        ids = self.env['product.template'].browse(act_ids)
        return res

    @api.onchange('product_id', 'imeis')
    def change_product(self):
        company = self.env.company.id
        id_product = self._context['active_id']
        product = self.env['product.template'].search([('id', '=', id_product)], limit=1)
        records = self.env['product.imei'].search_count([('product_id', '=', id_product), ('sale_order_line_id', '=', False), ('account_order_line_id', '=', False), ('company_id','=',company)])
        count = 0
        for r in self.imeis:
            count += 1

        if not self.product_id.id:
            self.product_id = id_product

        self.numberOfImeisForAdd = count

        if count > 0:
            name = self.imeis[count-1]
            imeiRegistered = self.env['product.imei'].search_count([('name', '=', name.name),('company_id','=',company)])
            imeiRegisteredOnWz = self.imeis.filtered(lambda r: r.name == name.name and r.id != name.id)
            # _logger.info(len(imeiRegisteredOnWz))
            if imeiRegistered > 0:
                self.imeis = self.imeis.filtered(lambda r: r != name)
                self.numberOfImeisForAdd = count - 1
                return {'warning': {
                    'title': "Error",
                    'message': "No se puede agregar este IMEI a el producto, ya esta registrado",
                    'type': 'ir.actions.act_window_close',
                    }
                }
            elif len(imeiRegisteredOnWz) > 0: 
                self.imeis = self.imeis.filtered(lambda r: r != name)
                self.numberOfImeisForAdd = count - 1
                return {'warning': {
                    'title': "Error",
                    'message': "Este IMEI ya esta registrado",
                    'type': 'ir.actions.act_window_close',
                    }
                }

        self.numberOfImeisWithoutAdd = (int(product.qty_available) - records) if (product.qty_available > records) else 0

        self.passed = False if count > self.numberOfImeisWithoutAdd else True

    def create_imeis(self):   
        company = self.env.company.id
        if not self.passed:
            # _logger.info('holas')
            return {'type': 'ir.actions.do_nothing'}
        else:
            colleccion = []
            for r in self.imeis:
                colleccion.append({'product_id': self._context['active_id'], 'name': r.name, 'company_id': company })

            if len(colleccion) > 0:
                self.env['product.imei'].create(colleccion)


class ImeisWizards(models.TransientModel):
    _name = "product.imei.add.wz"

    registerId = fields.Many2one('product.imei.wz')
    name = fields.Char(string="IMEI")

    @api.model
    def default_get(self, fields_list):
        res = super(ImeisWizards, self).default_get(fields_list)
        act_ids = self._context.get("active_ids")
        ids = self.env['product.imei.wz'].browse(act_ids)
        return res

class ImeiProductExtend(models.Model):
    _inherit = "product.template"
    imeis = fields.One2many('product.imei', 'product_id',"[('sale_order_line_id','=',False), ('account_order_line_id','=',False),('company_id','=',allowed_company_ids[0])]")


class ImeiSaleExtend(models.Model):
    _inherit = 'sale.order.line'
    imeisProduct = fields.One2many('product.imei', 'sale_order_line_id', string='IMEI')
    product_product_id = fields.Many2one('product.template')

    @api.onchange('imeisProduct', 'product_id')
    def change_imeis(self):
        self.product_uom_qty = len(self.imeisProduct) if len(self.imeisProduct) > 0 else 1
        if self.product_id:
            self.product_product_id = self.product_id.product_tmpl_id
        # _logger.info(self.product_product_id)
        # _logger.info(self.product_id.product_tmpl_id)

    def _prepare_invoice_line(self):

        self.ensure_one()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'analytic_account_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
            'imeisProduct': self.imeisProduct.ids
        }
        if self.display_type:
            res['account_id'] = False
        return res


class ImeiAccountMovement(models.Model):
    _inherit = 'account.move.line'
    imeisProduct = fields.One2many('product.imei', 'account_order_line_id')

class ImeiOfCompany(models.Model):
    _inherit = 'res.company'
    imeisCompany = fields.One2many('product.imei', 'company_id')


class ImeiModel(models.Model):
    _name = 'product.imei'

    name = fields.Char(string="IMEI", required=True)
    product_id = fields.Many2one('product.template', required=True)
    sale_order_line_id = fields.Many2one('sale.order.line')
    check = fields.Boolean(string="check", default=True)
    account_order_line_id = fields.Many2one('account.move.line')
    company_id = fields.Many2one('res.company')

    @api.onchange("product_id")
    def change_product(self):
        company = self.env.company.id
        self.company_id = company
        records = self.search_count([('product_id', '=', self.product_id.id), (
            'sale_order_line_id', '=', False), ('account_order_line_id', '=', False)])
        numberProducts = self.env['product.template'].search([('id', '=', self.product_id.id)],limit=1)
        if numberProducts.qty_available == 0:
            self.check = True
        elif records == numberProducts:
            self.check = True
            return {'warning': {
                'title': "Error",
                'message': "No se puede agregar IMEI a este producto, ya estan registrados"
            }
            }
        elif numberProducts.qty_available != 0:
            self.check = False

    _sql_constraints = [
        ('imei_unique_with_name',
         'UNIQUE(name,company_id)',
         "El IMEI ya esta registrado en el sistema"),
    ]
