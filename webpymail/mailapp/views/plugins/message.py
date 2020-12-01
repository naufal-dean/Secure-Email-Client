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

# Other
import hlimap

# Plugin Imports
from tools.cipher import STRAIT, Mode


@login_required
def message_validate(request, folder, uid):
    if request.method == 'POST':
        # get message object
        config = WebpymailConfig(request)
        folder_name = base64.urlsafe_b64decode(str(folder))
        M = serverLogin(request)
        folder = M[folder_name]
        message = folder[int(uid)]

        # Get text/plain part
        text_plain = get_text_plain(message)

        # TODO: retrieve use_decryption from forms
        use_decryption = True
        message_text_dec = None
        if use_decryption:
            # decrypt
            # TODO: retrieve key from forms
            key = 'ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEF'

            text_plain = base64.b64decode(text_plain)
            cipher = STRAIT(key, Mode.CBC)
            iv, message_text_enc = text_plain[:8].decode('utf-8'), text_plain[8:]
            message_text_dec = cipher.decrypt(message_text_enc, iv).decode('utf-8')
            text_to_validate = message_text_dec
        else:
            text_to_validate = text_plain

        # TODO: retrieve use_validation from forms
        use_validation = True
        validation = None
        if use_validation:
            # validate
            # TODO: change check_digital_signature implementation
            validation = check_digital_signature(text_to_validate)

        # Check the query string
        try:
            external_images = config.getboolean('message', 'external_images')
            external_images = request.GET.get('external_images', external_images)
            external_images = bool(int(external_images))
        except ValueError:
            external_images = config.getboolean('message', 'external_images')

        return render(request, 'mail/plugins/message_validate.html', {
            'folder': folder,
            'message': message,
            'show_images_inline': config.getboolean('message',
                                                    'show_images_inline'),
            'show_html': config.getboolean('message', 'show_html'),
            'external_images': external_images,
            'use_validation': use_validation,
            'validation': validation,
            'use_decryption': use_decryption,
            'message_text_dec': message_text_dec,
            })

    elif request.method == 'GET':
        return redirect('mailapp_message_validate_form', folder=folder, uid=uid)


@login_required
def message_validate_form(request, folder, uid):
    if request.method == 'GET':
        return render(request, 'mail/plugins/message_validate_form.html', {
            'folder': folder,
            'uid': uid,
            })
