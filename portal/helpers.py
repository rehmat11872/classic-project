from django.contrib import messages

# Models


TEMPLATE_TYPE = [
    # To follow SRS
    ('qlassic_score_letter','QLASSIC Score letter'),
    ('qlassic_certificate','QLASSIC Certificate'),
    ('qlassic_report','QLASSIC Report'),
    ('attendance_sheet','Attendance Sheet'),
    # ('training_certificate','Training Certificate'),
    ('trainer_interview_letter','Trainer Interview Letter'),
    ('trainer_reject_letter','Trainer Rejection Letter'),
    ('trainer_accreditation_letter','Trainer Accreditation Letter'),
    ('qca_interview_letter','QCA Interview Letter'),
    ('qca_reject_letter','QCA Rejection Letter'),
    ('qca_accreditation_letter','QCA Accreditation Letter'),
    ('qca_accreditation_certificate','QCA Accreditation Certificate'),
    ('qia_accreditation_certificate','QIA Accreditation Certificate'),
]