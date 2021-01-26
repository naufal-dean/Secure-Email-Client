# Secure Email Client
# Penerapan Elliptic Curve Cryptography dan SHA-3 untuk Menandatangani Surel pada Perangkat Mobile

## Description
Secure Email Client is an email client based on [webpymail](https://gitlab.com/hgg/webpymail). This web app adds digital signature and encryption features. The digital signature is generated using Elliptic Curve Digital Signature Algorithm (ECDSA). The encryption is done using custom block cipher algorithm (STRAIT cipher).

## Identitas
Muhammad Zunan Alfikri (13518019)\
Annisa Ayu Pramesti (13518085)\
Naufal Dean Anugrah (13518123)

## Python version
`$ python --version`\
`Python 3.8.5`

## How to run
1. Install all python dependencies in `requirements.txt` and `requirements-plugins.txt` (`requirements-optional.txt` is not needed). Use command below:
    ```
    pip install -r requirements.txt
    pip install -r requirements-plugins.txt
    ```
2. Fix Django 2.2.9 bug in `boundfield.py`. See **Notes Bug Fix** below for reference.
3. Run `./prepare.sh` to generate database used by the application.
4. Run `./server.sh` to start mail client server.
5. Access the url showed by Django (by default it is `http://127.0.0.1:8000/`) via browser in your mobile phone or desktop.
6. On login page select `Google Gmail` for the `Imap Server`.
7. Login to the mail client using your Gmail account. To setup IMAP access on Gmail and turn on Less Secure Apps see articles on **Notes to Setup Gmail Account** below.

## Notes Bug Fix
In `lib/python<version>/site-packages/django/forms/boundfield.py`, remove line `renderer` params in widget.render call.

See code below for reference
```
return widget.render(
    name=self.html_initial_name if only_initial else self.html_name,
    value=self.value(),
    attrs=attrs,
)
# renderer=self.form.renderer,
```

Source: [render() got unexpected keyword renderer](https://github.com/froala/django-froala-editor/issues/55)

## Notes to Setup Gmail Account
1. [Setup Gmail IMAP Access](https://support.google.com/mail/answer/7126229?hl=en)
2. [Turn On Gmail Less Secure Apps](https://hotter.io/docs/email-accounts/secure-app-gmail/)
