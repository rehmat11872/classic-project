import os
import tempfile
from subprocess import  Popen

from django.conf import settings
from django.http import StreamingHttpResponse

TEMPLATE_TEMP_PATH = ''
if os.name == 'nt':
    TEMPLATE_TEMP_PATH = settings.BASE_DIR + settings.MEDIA_ROOT + '\\media\\tmp\\'
else:
    TEMPLATE_TEMP_PATH = settings.MEDIA_ROOT + '/cidb-qlassic/tmp/'

class StreamingConvertedPdf:

    def __init__(self, dock_obj, download=True):
        self.doc = dock_obj
        self.download = download
        self.tmp_path = TEMPLATE_TEMP_PATH

    def validate_document(self):
        if not self.doc.name.split('.')[-1] in ('doc', 'docm', 'docx'):
            raise Exception('The input file must have one format from this: doc, docm, docx')

    def check_tmp_folder(self):
        if not os.path.exists(self.tmp_path):
            os.makedirs(self.tmp_path)

    def convert_to_pdf(self):
        self.validate_document()
        self.check_tmp_folder()
        with tempfile.NamedTemporaryFile(prefix=self.tmp_path, delete=False) as tmp:
            tmp.write(self.doc.read())

            print("Name:"+tmp.name)
            print("PAth TMP:"+self.tmp_path)

            try:
                with open(tmp.name):
                    print('file_existttt')
            except Exception:
                print('nooooott_existttt')
            if os.name == 'nt':
                process = Popen(['C:\\Program Files\\LibreOffice\\program\\soffice', '--convert-to', 'pdf', tmp.name, '--outdir', self.tmp_path])
                process.wait()
            else:
                process = Popen(['soffice', '--convert-to', 'pdf', tmp.name, '--outdir', self.tmp_path])
                process.wait()
            # process = Popen(['soffice', '--convert-to', 'pdf', tmp.name, '--outdir', self.tmp_path])
            self.tmp_path = tmp.name + '.pdf'

    def get_file_name(self):
        return self.doc.name.split('.')[0] + '.pdf'

    def stream_content(self):
        self.convert_to_pdf()
        res = StreamingHttpResponse(open(self.tmp_path, 'rb'), content_type='application/pdf')
        if self.download:
            res['Content-Disposition'] = 'attachment; filename="{}"'.format(self.get_file_name())
        return res
    
    def file_content(self):
        self.convert_to_pdf()
        res = open(self.tmp_path, 'rb')
        return res

    def __del__(self):
        try:
            if os.path.exists(self.tmp_path):
                os.remove(self.tmp_path)
        except IOError:
            print('Error deleting file')


class ConvertFileModelField(StreamingConvertedPdf):

    def get_content(self):
        self.convert_to_pdf()
        print(type(self))
        return {'doc': self.doc, 'path': self.tmp_path, 'name': self.get_file_name()}

    def stream_content(self):
        pass