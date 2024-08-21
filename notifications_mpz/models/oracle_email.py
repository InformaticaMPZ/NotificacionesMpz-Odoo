from odoo import models, fields, api
import oci
import os
import base64

class OracleEmail(models.Model):
    _name = "notifications_mpz.oracle_email"
    _description = "Oracle Email"
    _rec_name = "id"

    user_id = fields.Char(string="User Identification")
    fingerprint = fields.Char(string="Fingerprint")
    tenancy = fields.Char(string="Tenancy")
    region = fields.Char(string="Region Server")
    compartment_id = fields.Char(string="Compartment Identification")
    key_file = fields.Binary(string="Private Key File", attachment=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], string='State', default='inactive', readonly=False)

    @api.model
    def create(self, vals):
        record = super(OracleEmail, self).create(vals)
        record._save_key_file()
        return record

    def write(self, vals):
        res = super(OracleEmail, self).write(vals)
        self._save_key_file()
        return res

    def _save_key_file(self):
        key_file_path = os.path.expanduser("mnt/extra-addons/notifications_mpz/security/key_private.pem")
        if self.key_file:
            key_file_content = base64.b64decode(self.key_file)
            with open(key_file_path, 'wb') as f:
                f.write(key_file_content)

    def send_notification_email(self, to, subject,plate_number, remaining_time):
        last_record = self.search([], order="id desc", limit=1)
        if not last_record:
            return

        if last_record.state == 'inactive':
            return

        key_file_path = os.path.expanduser("mnt/extra-addons/notifications_mpz/security/key_private.pem")
        config = {
            "user": last_record.user_id,
            "key_file": key_file_path,
            "fingerprint": last_record.fingerprint,
            "tenancy": last_record.tenancy,
            "region": last_record.region,
        }
        
        template = self.env.ref('notifications_mpz.notification_time_report')
    
        if not template:
            return
        
        context = {
            'plate_number': plate_number,
            'remaining_time':remaining_time
        }

        body_rendered = self.env['ir.qweb']._render(template.id, context)
       
        try:
            email_client = oci.email_data_plane.EmailDPClient(config)
            email_details = oci.email_data_plane.models.SubmitEmailDetails(
                sender=oci.email_data_plane.models.Sender(
                    sender_address=oci.email_data_plane.models.EmailAddress(
                        email="notificaciones@mpz.go.cr", name="Municipalidad de Pérez Zeledón"
                    ),
                    compartment_id=last_record.compartment_id,
                ),
                recipients=oci.email_data_plane.models.Recipients(
                    to=[
                        oci.email_data_plane.models.EmailAddress(
                            email=to, name="Nombre del destinatario"
                        )
                    ],
                    cc=[],
                    bcc=[],
                ),
                subject=subject,
                body_html = body_rendered if body_rendered != "" else "Gracias por utilizar nuestros servicios en línea",
            )

            email_client.submit_email(email_details)

        except oci.exceptions.ServiceError as e:
            print(f"Error del servicio OCI: {e.message}")
        except Exception as e:
            print(f"Error al enviar el correo: {str(e)}")
