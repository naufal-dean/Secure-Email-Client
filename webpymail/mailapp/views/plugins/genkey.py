# Global Imports
import base64
import os
import zipfile
from io import BytesIO
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
from mailapp.forms import GenerateEccKeyForm

# Other
import hlimap

# Plugin Imports
from tools.ec import Point, ECC


@login_required
def generate_ecc_key(request):
    error_message = None
    if request.method == 'POST':
        print(request.POST)
        if 'cancel' in request.POST:
            return HttpResponseRedirect('/')

        form = GenerateEccKeyForm(request.POST)
        if form.is_valid():
            # Read the posted data
            form_data = form.cleaned_data
            print(form_data)

            # get curve parameters
            a = form_data['curve_param_a']
            b = form_data['curve_param_b']
            p = form_data['curve_param_p']
            # get optional input
            Gx = form_data['curve_base_Gx']
            Gy = form_data['curve_base_Gy']
            n = form_data['curve_order_n']
            # get generated input
            d = form_data['pri_key_d']
            Qx = form_data['pub_key_Qx']
            Qy = form_data['pub_key_Qy']

            # download as file
            if 'download' in request.POST:
                if all([el is not None for el in [a, b, p, Gx, Gy, n, d, Qx, Qy]]):
                    return get_zipped_key_response(a, b, p, Gx, Gy, n, d, Qx, Qy)
                else:
                    error_message = 'Failed to download key, form is not all filled'
                    return render(request, 'mail/plugins/generate_ecc_key.html', {
                        'form': form,
                        'error_message': error_message,
                        })
                    return HttpResponse('Failed to Download, form is not all filled')

            # generate ecc key
            new_data = form_data.copy()
            try:
                if Gx and Gy and n:
                    # G and n supplied no need to generate group, then manually generate key after G and n assigned
                    ecc = ECC(a, b, p, auto_gen_group=False, auto_gen_key=False)
                    G = Point(Gx, Gy)
                    ecc.G = G
                    ecc.n = n
                    ecc.generate_key()
                else:
                    # G and n not supplied
                    ecc = ECC(a, b, p)

                print(ecc)
            except Exception as e:
                print('Generate Key Failed')
                error_message = 'Generate Key Failed. Error: ' + str(e)
            else:
                # update if needed (when G and n not supplied, else the value will be the same)
                new_data['curve_base_Gx'] = ecc.G.x
                new_data['curve_base_Gy'] = ecc.G.y
                new_data['curve_order_n'] = ecc.n
                # generated
                new_data['pri_key_d'] = ecc.d
                new_data['pub_key_Qx'] = ecc.Q.x
                new_data['pub_key_Qy'] = ecc.Q.y
                # show in form
                print(new_data)
                form = GenerateEccKeyForm(new_data)
    else:
        form = GenerateEccKeyForm()
    return render(request, 'mail/plugins/generate_ecc_key.html', {
        'form': form,
        'error_message': error_message,
        })


def get_zipped_key_response(a, b, p, Gx, Gy, n, d, Qx, Qy):
    assert all([el is not None for el in [a, b, p, Gx, Gy, n, d, Qx, Qy]])

    # create ecc instance
    ecc = ECC(a, b, p, auto_gen_group=False, auto_gen_key=False)
    ecc.n = n
    ecc.G = Point(Gx, Gy)
    ecc.d = d
    ecc.Q = Point(Qx, Qy)
    print(ecc)

    # save key to temporary file
    folder_path = os.path.join('mailapp', 'savedkeys')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    ecc.save_file(os.path.join(folder_path, 'key'))

    # add path of public and private key file to be downloaded
    pri_key_path = os.path.join(folder_path, 'key.pri')
    pub_key_path = os.path.join(folder_path, 'key.pub')
    key_path = [pri_key_path, pub_key_path]

    # create in memory zipfile of public and private key
    bytesIO = BytesIO()
    zf = zipfile.ZipFile(bytesIO, "w")
    for kp in key_path:
        _, filename = os.path.split(kp)
        zf.write(kp, filename)
    zf.close()

    # return response with content disposition so it will be downloaded
    response = HttpResponse(bytesIO.getvalue(), content_type="application/x-zip-compressed")
    response['Content-Disposition'] = 'attachment; filename=key.zip'
    return response
