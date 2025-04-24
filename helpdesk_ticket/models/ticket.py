from datetime import timedelta

from odoo import models, fields, api
from odoo.cli.scaffold import template
from odoo.exceptions import ValidationError

class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _description = 'Ticket d’assistance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Référence', required=True, copy=False, readonly=True, default='Nouveau')
    subject = fields.Char(string='Sujet', required=True, tracking=True)
    description = fields.Text(string='Description')
    partner_id = fields.Many2one('res.partner', string='Client', tracking=True)
    user_id = fields.Many2one('res.users', string='Assigné à', tracking=True)
    priority = fields.Selection([
        ('0', 'Basse'),
        ('1', 'Normale'),
        ('2', 'Haute'),
        ('3', 'Urgente')
    ], string='Priorité', default='1', tracking=True)

    state = fields.Selection([
        ('new', 'Nouveau'),
        ('in_progress', 'En cours'),
        ('waiting', 'En attente'),
        ('solved', 'Résolu'),
        ('closed', 'Fermé')
    ], string='État', default='new', tracking=True)

    date_open = fields.Datetime(string='Date ouverture', default=fields.Datetime.now, readonly=True)
    date_close = fields.Datetime(string='Date de fermeture', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('helpdesk.ticket') or 'Nouveau'
        ticket = super().create(vals)
        template = self.env.ref('helpdesk_ticket.ticket_mail_created')
        if template and ticket.partner_id and ticket.partner_id.email:
            template.send_mail(ticket.id, force_send=True)
        return ticket

    # --- Méthodes de transition d'états ---
    def action_set_in_progress(self):
        for record in self:
            if record.state not in ['new', 'waiting']:
                raise ValidationError("Le ticket doit être dans l'état 'Nouveau' ou 'En attente' pour être mis en cours.")
        record.state = 'in_progress'
        template = self.env.ref('helpdesk_ticket.ticket_mail_started')
        if template and record.user_id and record.user_id.email:
            template.send_mail(record.id, force_send=True)

        # Notification dans le chatter
        record.message_post(
            body=f"<b>Le ticket est maintenant en cours</b><br/>Assigné à : {record.user_id.name}",
            message_type='notification',
            partner_ids=[record.user_id.partner_id.id]
        )

        # Activité planifiée
        record.activity_schedule(
            'mail.mail_activity_data_todo',
            user_id=record.user_id.id,
            note='Suivre le ticket nouvellement mis en cours.',
            date_deadline=fields.Date.today() + timedelta(days=1)
        )

    def action_set_waiting(self):
        for record in self:
            #verification de l'utilisateur assigné
            if record.user_id != self.env.user:
                raise ValidationError("Seul l'employé assigné peut mettre le ticket en attente.")
            if record.state != 'in_progress':
                raise ValidationError("Le ticket doit être dans l'état 'En cours' pour être mis en attente.")
        record.state = 'waiting'

        #notification au chef support (créateur du ticket)
        if record.create_uid:
            record.message_post(
                body=f"<b>Notification :</b> Le ticket {record.name} a été mis en attente par {record.user_id.name}."
                     f"nous attendons la validation du client. {record.partner_id.name}",
                message_type='notification',
                partner_ids=[record.create_uid.partner_id.id] if record.create_uid.partner_id else []
            )

    def action_set_solved(self):
        for record in self:
            #verification de l'utilisateur en cours
            if record.user_id != self.env.user:
                raise ValidationError("Seul l'employé assigné peut marquer le ticket comme résolu.")
            if record.state not in ['in_progress', 'waiting']:
                raise ValidationError("Le ticket doit être dans l'état 'En cours' ou 'En attente' pour être marqué comme résolu.")
        record.state = 'solved'
        template = self.env.ref('helpdesk_ticket.ticket_mail_resolved')
        if template and record.partner_id and record.partner_id.email:
            template.send_mail(record.id, force_send=True)

        # Notification au chef support (créateur du ticket)
        if record.create_uid:
            record.message_post(
                body=f"<b>Notification :</b> Le ticket {record.name} a été résolu par {record.user_id.name}.",
                message_type='notification',
                partner_ids=[record.create_uid.partner_id.id] if record.create_uid.partner_id else []
            )



    def action_set_closed(self):
        for record in self:
            if record.state not in ['solved', 'waiting']:
                raise ValidationError("Le ticket doit être dans l'état 'Résolu' ou 'En attente' pour être fermé.")
            record.state = 'closed'
        template = self.env.ref('helpdesk_ticket.ticket_mail_closed')
        if template and record.partner_id and record.partner_id.email:
            template.send_mail(record.id, force_send=True)
            record.date_close = fields.Datetime.now()

    def action_reset_to_new(self):
        for record in self:
            if record.state != 'closed':
                raise ValidationError("Le ticket doit être dans l'état 'Clôturé' pour revenir à l'état 'Nouveau'.")
            record.state = 'new'

    # Exemple de déclenchement d'activité interne :
    def action_notify_assignee(self):
        for record in self:
            if record.user_id:
                record.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=record.user_id.id,
                    note='Nouveau ticket assigné : %s' % record.subject
                )
    #methode qui rappel un ticket non resolu depuis 7 jours
    def notify_unresolved_ticket(self):
        # calculer la date limite (7 jours avant aujourd'hui)
        date_limit = fields.Datetime.now() - timedelta(days=7)
        # rechercher les tickets non résolus
        tickets = self.search([
            ('state', 'not in', ['closed', 'solved']),
            ('create_date', '<=', 'date_limit')
        ])
        for ticket in tickets :
            # envoyer un email de notification
            template = self.env.ref('helpdesk_ticket.ticket_mail_unresolved')
            if template and ticket.partner_id and ticket.partner_id.email:
                template.send_mail(ticket.id, force_send=True)
                ticket.message_post(
                    body=f"<b>Notification :</b> Le ticket {ticket.name} est non résolu depuis 7 jours.",
                    message_type='notification',
                    partner_ids=[ticket.user_id.partner_id.id] if ticket.user_id.partner_id else []
                )
            # notification dans le chatter
            ticket.message_post(
                body=f"<b>Notification :</b> Le ticket {ticket.name} est non résolu depuis 7 jours.",
                message_type='notification',
                partner_ids=[ticket.user_id.partner_id.id] if ticket.user_id.partner_id else []
            )
    def print_ticket_pdf(self):
        return self.env.ref('helpdesk_ticket.action_report_ticket').report_action(self)