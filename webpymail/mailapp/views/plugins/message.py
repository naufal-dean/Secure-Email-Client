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

import hlimap


@login_required
def message_validate(request, folder, uid):
    if request.method == 'POST':
        # get message object
        config = WebpymailConfig(request)
        folder_name = base64.urlsafe_b64decode(str(folder))
        M = serverLogin(request)
        folder = M[folder_name]
        message = folder[int(uid)]

        # validate
        # TODO: change check_digital_signature implementation
        text = get_text_plain(message)
        validation = check_digital_signature(text)

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
            'validation': validation,
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
