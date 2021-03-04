# -*- coding: utf-8 -*-
# from odoo import http


# class Imei-product-extend(http.Controller):
#     @http.route('/imei-product-extend/imei-product-extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/imei-product-extend/imei-product-extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('imei-product-extend.listing', {
#             'root': '/imei-product-extend/imei-product-extend',
#             'objects': http.request.env['imei-product-extend.imei-product-extend'].search([]),
#         })

#     @http.route('/imei-product-extend/imei-product-extend/objects/<model("imei-product-extend.imei-product-extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('imei-product-extend.object', {
#             'object': obj
#         })
