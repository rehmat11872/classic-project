from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404

# XHTML2PDF
# from app.xhtml2pdf import link_callback
# from xhtml2pdf import pisa 
# from django.template.loader import get_template
# from projects.models import ProjectInfo
# from django.conf import settings
# from .docx2pdf import convert_to

from portal.models import LetterTemplate

# Helpers
from app.helpers.helpers import docx_to_pdf_stream

def doc_test(request):
    letter_template = LetterTemplate.objects.all()[0]
    context = { 'company_name' : "World company" }
    response = docx_to_pdf_stream(letter_template, context)

    return response

# def report_edit(request, report_type):
#     template_path = get_report_template(report_type)
    
#     urls = get_url_data(request)
#     context = {
#         'urls': urls,
#     }

#     return render(request, template_path, context)

# def report_generate(request, report_type):
#     template_path = ''
#     template_path = get_report_template(report_type)

#     urls = get_url_data(request)
#     context = {
#         'urls': urls,
#     }
#     # Create a Django response object, and specify content_type as pdf
#     response = HttpResponse(content_type='application/pdf')
#     # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
#     response['Content-Disposition'] = 'inline; filename="report.pdf"'
#     # find the template and render it.
#     template = get_template(template_path)
#     html = template.render(context)

#     # create a pdf
#     pisa_status = pisa.CreatePDF(
#        html, dest=response, link_callback=link_callback)
#     # if error then show some funy view
#     if pisa_status.err:
#        return HttpResponse('We had some errors <pre>' + html + '</pre>')
#     return response

# def get_report_template(report_type):
#     key = {'slug':[]}
#     template_path = ''
#     if report_type == 'score_letter':
#         template_path = 'pdf/score_letter.html'
#     elif report_type == 'qlassic_report':
#         template_path = 'pdf/qlassic_report.html'
#     elif report_type == 'qlassic_certificate':
#         template_path = 'pdf/qlassic_certificate.html'
#     else:
#         raise Http404
#     return template_path

# def get_url_data(request):
    # qr_url = request.build_absolute_uri()
    # host_url = request.scheme+'://'+request.META['HTTP_HOST'] 
    # url_data = {
    #     'qr_url': qr_url,
    #     'host_url': host_url,
    # }
    # return url_data