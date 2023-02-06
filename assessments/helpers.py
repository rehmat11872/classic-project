def calculate_sample(qaa):
    sample = 0
    gfa = qaa.pi.gfa
    gfa_per = 70
    min = 30
    max = 700
    building_type = qaa.building_type
    if building_type == 'A':
        gfa_per = 70
        min = 30
        max = 700
    if building_type == 'B':
        gfa_per =  70
        min = 30
        max = 600
    if building_type == 'C':
        gfa_per = 500
        min = 30
        max = 150
    if building_type == 'D':
        gfa_per = 500
        min = 30
        max = 100

    sample = gfa / gfa_per
    if sample < min:
        sample = min
    elif sample > max:
        sample = max

    return sample

def get_qaa_sd_name(name):
    if name == 'sd_1':
        return 'SURAT PENGESAHAN PEMILIKAN KOSONG ATAU VACANT(VP) OLEH PEMILIK PROJEK/KLIEN'
    if name == 'sd_2':
        return 'SURAT PERAKUAN SIAP KERJA OLEH ARKITEK'
    if name == 'sd_3':
        return 'SURAT PENGESAHAN OLEH ARKITEK'
    if name == 'sd_4':
        return 'SALINAN SURAT TAWARAN PROJEK/PROJECTS LETTER OF AWARD'
    if name == 'sd_5':
        return 'SALINAN PELAN LOKASI TAPAK/SITE LOCATION MAP'
    if name == 'sd_6':
        return 'SALINAN PROJECT LAYOUT'
    if name == 'sd_7':
        return 'SALINAN FLOOR PLAN'
    if name == 'sd_8':
        return 'SALINAN EXTERNAL WORKS LAYOUT PLAN'
    if name == 'sd_9':
        return 'SURAT PERAKUAN'
    return name