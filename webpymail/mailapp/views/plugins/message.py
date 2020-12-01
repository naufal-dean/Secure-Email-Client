# Global Imports
import base64
# Django:
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

# Local
from .utils import get_text_plain, check_digital_signature
from ..mail_utils import serverLogin
from themesapp.shortcuts import render
from utils.config import WebpymailConfig
from .. import msgactions
from mailapp.forms import ProcessEmailForm

# Other
import hlimap

# Plugin Imports
from tools.cipher import STRAIT, Mode


@login_required
def message_process(request, folder, uid):
    if request.method == 'POST':
        form = ProcessEmailForm(request.POST)
        if form.is_valid():
            # get form data
            form_data = form.cleaned_data

            # get message object
            config = WebpymailConfig(request)
            folder_name = base64.urlsafe_b64decode(str(folder))
            M = serverLogin(request)
            folder = M[folder_name]
            message = folder[int(uid)]

            # Get text/plain part
            text_plain = get_text_plain(message)

            # decryption plugin
            use_decryption = form_data['use_decryption']
            message_text_dec = None
            decryption_error = None
            if use_decryption:
                try:
                    # decrypt
                    # decryption_key = 'ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEF'
                    decryption_key = form_data['decryption_key'].ljust(32, '0')[:32]
                    text_plain = base64.b64decode(text_plain)
                    cipher = STRAIT(decryption_key, Mode.CBC)
                    iv, message_text_enc = text_plain[:8].decode('utf-8'), text_plain[8:]
                    message_text_dec = cipher.decrypt(message_text_enc, iv).decode('utf-8', 'ignore')
                    text_to_validate = message_text_dec
                except Exception as e:
                    decryption_error = 'Failed to decrypt email content: ' + str(e)
                    text_to_validate = ''
            else:
                text_to_validate = text_plain

            # validation plugin
            use_validation = form_data['use_validation']
            validation = None
            validation_error = None
            if use_validation:
                try:
                    # validate
                    a = form_data['validation_pub_key_a']
                    b = form_data['validation_pub_key_b']
                    p = form_data['validation_pub_key_p']
                    Qx = form_data['validation_pub_key_Qx']
                    Qy = form_data['validation_pub_key_Qy']
                    print(a, b, p, Qx, Qy)
                    print(type(a), type(b), type(p), type(Qx), type(Qy))
                    # TODO: change check_digital_signature implementation
                    validation = check_digital_signature(text_to_validate)
                except Exception as e:
                    validation_error = 'Failed to validate signature: ' + str(e)

            # Check the query string
            try:
                external_images = config.getboolean('message', 'external_images')
                external_images = request.GET.get('external_images', external_images)
                external_images = bool(int(external_images))
            except ValueError:
                external_images = config.getboolean('message', 'external_images')

            return render(request, 'mail/plugins/message_process.html', {
                'folder': folder,
                'message': message,
                'show_images_inline': config.getboolean('message',
                                                        'show_images_inline'),
                'show_html': config.getboolean('message', 'show_html'),
                'external_images': external_images,
                'use_validation': use_validation,
                'validation': validation,
                'validation_error': validation_error,
                'use_decryption': use_decryption,
                'message_text_dec': message_text_dec,
                'decryption_error': decryption_error,
                })
                
    else:
        form = ProcessEmailForm()

    return render(request, 'mail/plugins/message_process_form.html', {
        'folder': folder,
        'uid': uid,
        'form': form,
        })
