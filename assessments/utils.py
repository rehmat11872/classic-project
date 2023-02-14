from datetime import datetime
from io import BytesIO

import xlwt
from django.http import HttpResponse

from assessments.models import QlassicAssessmentApplication


class CreateExcell(object):

    def excel_view(self, request):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=Assessments.xls'
        work_book = xlwt.Workbook()
        work_sheet = work_book.add_sheet('Students Info')
        style_head_row = xlwt.easyxf("""    
        font:
          name Arial,
          colour_index white,
          bold on,
          height 0xA0;
        pattern:
          pattern solid,
          fore-colour 0x19;
        """
                                     )
        style_data_row = xlwt.easyxf("""
        align:
          wrap on,
          vert center,
          horiz left;
        font:
          name Arial,
          bold off,
          height 0xA0;
        borders:
          left THIN,
          right THIN,
          top THIN,
          bottom THIN;
        """
                                     )
        work_sheet.write(0, 0, 'APPLICATION NUMBER', style_head_row)
        work_sheet.write(0, 1, 'PROJECT TITLE', style_head_row)
        work_sheet.write(0, 2, 'SECTOR', style_head_row)
        work_sheet.write(0, 3, 'PROJECT VALUE', style_head_row)
        work_sheet.write(0, 4, 'STATUS', style_head_row)
        work_sheet.write(0, 5, 'PAYMENT STATUS', style_head_row)
        work_sheet.write(0, 6, 'APPLICATION DATE', style_head_row)

        row = 1

        for data in QlassicAssessmentApplication.objects.all():
            work_sheet.write(row, 0, data.qaa_number)
            work_sheet.write(row, 1, data.pi.project_title)
            work_sheet.write(row, 2, str(data.pi.project_type))
            work_sheet.write(row, 3, data.pi.contract_value)
            work_sheet.write(row, 4, str(data.application_status))
            work_sheet.write(row, 5, data.payment_status)
            try:

                conv_date1 = datetime.strftime(data.created_date, "%m/%d/%y")
                work_sheet.write(row, 6, conv_date1)
            except Exception as e:
                pass
            row = row + 1

        output = BytesIO()
        work_book.save(output)
        output.seek(0)
        response.write(output.getvalue())
        return response