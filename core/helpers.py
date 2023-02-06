import uuid
import os
import datetime
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site

from django.utils.deconstruct import deconstructible

@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = "cidb-qlassic/" + sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        # filename_ = datetime.datetime.utcnow().strftime("%s") + uuid.uuid4().hex
        filename_ = str(datetime.datetime.utcnow().timestamp()).split('.', 1)[0] + uuid.uuid4().hex
        filename = '{}.{}'.format(filename_, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)

from django.core.exceptions import ValidationError

def file_size_validator(value): # add this to some file where you can import it from
    limit = 3 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 3 MiB.')

from django.core.mail import send_mail
from django.template.loader import render_to_string
from core.settings import skip_email

def send_email_default(subject, to, context, template):
    skip = skip_email
    print(skip)
    if skip == 0:
        message = render_to_string(
            template,
            context
        )
        send_mail(subject, message, None, to, fail_silently=False)
    else:
        print('Send email: ' + subject)

from mimetypes import guess_type
from os.path import basename
def send_email_with_attachment(subject, to, context, template, attachments):
    message = render_to_string(
        template,
        context
    )
    email = EmailMessage(subject, message, None, to)
    for attachment in attachments:
        f = attachment
        f.open()
        # msg.attach(filename, content, mimetype)
        email.attach(basename(f.name), f.read(), guess_type(f.name)[0])
        f.close()
        # email.attach_file(attachment)
    email.send()

# State Choice in Malaysia
STATE_CHOICES = [
    ('MELAKA','MELAKA'),
    ('JOHOR','JOHOR'),
    ('NEGERI SEMBILAN','NEGERI SEMBILAN'),
    ('PAHANG','PAHANG'),
    ('TERENGGANU','TERENGGANU'),
    ('KELANTAN','KELANTAN'),
    ('PERAK','PERAK'),
    ('PERLIS','PERLIS'),
    ('KEDAH','KEDAH'),
    ('SELANGOR','SELANGOR'),
    ('WILAYAH PERSEKUTUAN KUALA LUMPUR','WP KUALA LUMPUR'),
    ('WILAYAH PERSEKUTUAN LABUAN','WP LABUAN'),
    ('WILAYAH PERSEKUTUAN PUTRAJAYA','WP PUTRAJAYA'),
    ('SABAH','SABAH'),
    ('SARAWAK','SARAWAK'),
    ('PULAU PINANG','PULAU PINANG'),
]

def get_state_code(state):
    code = ''
    if state == 'MELAKA':
        code = 'ML'
    elif state == 'JOHOR':
        code = 'JH'
    elif state == 'NEGERI SEMBILAN':
        code = 'NS'
    elif state == 'PAHANG':
        code = 'PH'
    elif state == 'TERENGGANU':
        code = 'TR'
    elif state == 'KELANTAN':
        code = 'KN'
    elif state == 'PERAK':
        code = 'PR'
    elif state == 'PERLIS':
        code = 'PL'
    elif state == 'KEDAH':
        code = 'KD'
    elif state == 'SELANGOR':
        code = 'SL'
    elif state == 'WILAYAH PERSEKUTUAN KUALA LUMPUR':
        code = 'WP'
    elif state == 'SABAH':
        code = 'SB'
    elif state == 'SARAWAK':
        code = 'SR'
    elif state == 'PULAU PINANG':
        code = 'PP'
    else:
        code = ''
    return code

def get_sector_code(sector):
    code = ''
    if sector == 'GOVERNMENT':
        code = 'G'
    elif sector == 'PRIVATE':
        code = 'P'
    else:
        code = ''
    return code

def translate_malay_date(date):
    #str_date = str(date)
    #str_date = translate_month(str_date)
    #str_date = translate_day(str_date)
    return date

def standard_date(date):
    return date.strftime("%d %B %Y")

def translate_month(str_date):
    str_date = str_date.replace('January','Januari')
    str_date = str_date.replace('February','Februari')
    str_date = str_date.replace('March','Mac')
    str_date = str_date.replace('April','April')
    str_date = str_date.replace('May','Mei')
    str_date = str_date.replace('June','Jun')
    str_date = str_date.replace('July','Julai')
    str_date = str_date.replace('August','Ogos')
    str_date = str_date.replace('September','September')
    str_date = str_date.replace('October','Oktober')
    str_date = str_date.replace('November','November')
    str_date = str_date.replace('December','Disember')
    
    return str_date

def translate_day(str_date):
    str_date = str_date.replace('Sunday','Ahad')
    str_date = str_date.replace('Monday','Isnin')
    str_date = str_date.replace('Tuesday','Selesa')
    str_date = str_date.replace('Wednesday','Rabu')
    str_date = str_date.replace('Thursday','Khamis')
    str_date = str_date.replace('Friday','Jumaat')
    str_date = str_date.replace('Saturday','Sabtu')

    return str_date
    
import qrcode, io
from core import settings

def generate_and_save_qr(url, file):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=0,
    )
    qr.add_data(url)
    img_content = io.BytesIO(b'')
    
    # the following line "saves" to a bytearray
    qr.make_image().save(img_content, format='png')
    print(type(img_content.seek(0)))
    # saves to the FileField
    file.save("qr_code.png", img_content)

def get_domain(request):
    current_site = get_current_site(request)
    if request.is_secure():
        return 'https://' + current_site.domain
    else:
        return 'http://' + current_site.domain

import base64
from django.core.files.base import ContentFile

def convert_string_to_file(string_64, name):
    extension, imgstr = string_64.split(';base64,')
    ext = extension.split('/')[-1]

    data = ContentFile(base64.b64decode(imgstr))  
    full_name = name + '.' + ext
    return data, full_name
