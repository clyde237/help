# -*- coding: utf-8 -*-
# from odoo import http


# class HelpdeskTicket(http.Controller):
#     @http.route('/helpdesk_ticket/helpdesk_ticket', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/helpdesk_ticket/helpdesk_ticket/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('helpdesk_ticket.listing', {
#             'root': '/helpdesk_ticket/helpdesk_ticket',
#             'objects': http.request.env['helpdesk_ticket.helpdesk_ticket'].search([]),
#         })

#     @http.route('/helpdesk_ticket/helpdesk_ticket/objects/<model("helpdesk_ticket.helpdesk_ticket"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('helpdesk_ticket.object', {
#             'object': obj
#         })

