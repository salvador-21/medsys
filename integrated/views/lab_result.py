from typing import final
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from datetime import date, datetime, timedelta
from django.template import loader
from django.template.loader import get_template, render_to_string
from django.conf import settings
from requests.api import head
from fpdf import FPDF, HTMLMixin
import requests
import json
import io
import xlwt
from requests.exceptions import ConnectionError
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm, inch
from reportlab.lib import colors

from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.rl_config import defaultPageSize
from reportlab.platypus import Paragraph, Table, TableStyle, PageBreak, BaseDocTemplate,Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from num2words import num2words
from storages.backends.ftp import FTPStorage
from django.contrib import messages
from datetime import date, datetime, timedelta
# from datetime import datetime
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import (ParagraphStyle, getSampleStyleSheet)
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib import colors




static_root = "http://173.10.7.2/medsys-static-files"
# root = "http://173.10.2.108:9092/"
root = "http://172.22.10.11:9091/"
all_patients_api = root + "api/enc/getAllEncounter"
patient_search_api = root + "api/patients/patient-search"

# enccod-order_id
get_lab_request = root + "api/doctor/doctorsOrderList"

doctorsOrderPatient=root+"api/doctor/doctorsOrderPatientList"
update_status=root+"api/laboratory/updateOrderStatus"

getLab_modality=root+"api/laboratory/getLabOrderByModality"

get_latest_control=root+"api/laboratory/getLatestControlNo"
save_new_control_no=root+"api/laboratory/addControlNo"

put_orderDetails=root+"api/doctor/receivedLabOrder"
accept_allOder=root+"api/laboratory/updateAcceptAllOrder"

#FECALYSIS
#order_id
get_fecalysis=root+"api/laboratory/getFecalysisResult"
fecalysisResult=root+"api/laboratory/fecalysisResult"

# RESULTING API###

get_urinalysis=root+"api/laboratory/getUrinalysisResult"
adduptdate_urinalysis=root+"api/laboratory/UrinalysisResult"
get_rapid_result=root+"api/laboratory/getRapidResult"
get_age=root+"api/patients/age"

def result_RDT(request,toecode,orderid,encc,prikey):
    # key orderid and encc
    getPatient=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid,'status':'COMPLETED'}).json()
    # print(getPatient)
    now=datetime.now()
    now=datetime.strftime(now,'%m-%d-%Y')
   
    for p in getPatient['details']:
        
        ptx=p['patlast']+', '+p['patfirst']+' '+p['patmiddle'][:1]+'.'
        dob=p['birthdate'][:8]
        address=p['patbplace']
        gender=p['patsex']
        if gender == 'M':
            gender='MALE'
        elif gender =='F':
            gender='FEMALE'
        stat=p['patcstat']
        if stat == 'S':
            stat='SINGLE'
        elif stat == 'M':
            stat ='MARRIED'
        else:
            stat =p['patcstat']
    getRapid=requests.post(get_rapid_result,data={'order_id':orderid,'enccode':encc}).json()
    # print(getRapid)
    for r in getRapid['data']:
  
        r['expiry_date'] = datetime.strptime(r['expiry_date'],"%Y-%m-%dT%H:%M:%S.%fZ")
        r['expiry_date']=datetime.strftime(r['expiry_date'], '%m/%d/%Y')
        # age=r['patage']
        # result=r['result']
        # hosno=r['hperco']
        # print(r['expiry_date'])

        logo = ImageReader(static_root + '/integrated/img/brghgmclogo.png')
        logo1 = ImageReader(static_root + '/integrated/img/dohlogo.png')
        padaba = ImageReader(static_root + '/integrated/img/pagpadaba.png')
        response = HttpResponse(content_type='application/pdf')
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setPageSize((8.27*inch, 5.85*inch))
        # p.setPageSize((A4))

        p.setFont('Helvetica',100, leading=None)
        p.rotate(20)
        p.setFillColorCMYK(0,0,0,0.08)
        p.drawString(1*inch,.5*inch,'BRGHGMC')
        p.rotate(-20)

        p.drawImage(logo, 0.5*inch, 5.05*inch, mask='auto', width=50, height=50)
        p.drawImage(logo1, 1.2*inch, 5.05*inch, mask='auto', width=50, height=50)

        # p.drawImage(logo, 0.5*inch, 0*inch, mask='auto', width=400, height=400)

        p.setFont("Times-Roman", 16, leading=None)
        p.setFillColor("green")
        p.drawString(1.9*inch, 5.52*inch, "Bicol Region General Hospital and Geriatric Medical Center")
        p.setFont("Times-Roman", 9, leading=None)
        p.drawString(3.2*inch, 5.37*inch, "(Formely BICOL SANITARIUM)")
        p.setFillColor("black")
        p.drawString(3.2*inch, 5.26*inch, "San Pedro, Cabusao Camarines Sur")
        p.setFont("Times-Roman", 8, leading=None)
        p.drawString(2.6*inch, 5.16*inch, "Telephone Nos.: (054) 473-2244, 472-4422, 881-1033, 881-1761")
        p.drawString(2.8*inch, 5.06*inch, "E-mail Address: bicolsan@gmail.com, brghgmc@gmail.com")
        # Header
        p.line(0, 5*inch, 1000, 5*inch) #(x1, y1, x2, y2)
        p.setFont("Times-Roman", 16, leading=None)
        p.drawString(2*inch, 4.75*inch, "RAPID ANTIGEN TEST for SARS-CoV-19")
        p.setLineWidth(0.1)
        p.setFont("Times-Roman", 10, leading=None)

        p.drawString(6.5*inch, 4.5*inch, "Date:")
        p.line(490, 4.45*inch, 555, 4.45*inch) #(x1, y1, x2, y2)
        p.drawString(6.9*inch, 4.52*inch, now)
        
        p.drawString(0.2*inch, 4.2*inch, "Name:")
        p.line(43, 4.2*inch, 200, 4.2*inch) #(x1, y1, x2, y2)
        p.drawString(0.6*inch, 4.22*inch,ptx)

        p.drawString(3*inch, 4.2*inch, "Age:")
        p.line(235, 4.2*inch, 280, 4.2*inch) #(x1, y1, x2, y2)
        p.drawString(3.5*inch, 4.22*inch, r['patage'])

        p.drawString(3.95*inch, 4.2*inch, "Sex:")
        p.line(300, 4.2*inch, 350, 4.2*inch) #(x1, y1, x2, y2)
        p.drawString(4.25*inch, 4.22*inch, gender)

        p.drawString(5.1*inch, 4.2*inch, "Ward:")
        p.line(395, 4.2*inch, 570, 4.2*inch) #(x1, y1, x2, y2)
        p.drawString(5.5*inch, 4.22*inch, toecode )

        # newline
        p.drawString(0.2*inch, 3.95*inch, "Hospital No.:")
        p.line(70, 3.95*inch, 200, 3.95*inch) #(x1, y1, x2, y2)
        p.drawString(1*inch, 3.98*inch, r['hpercode'])

        p.drawString(3*inch, 3.95*inch, "Physician:")
        p.line(260, 3.95*inch, 390, 3.95*inch) #(x1, y1, x2, y2)
        p.drawString(3.6*inch, 3.98*inch, r['physician'])

        p.drawString(5.5*inch, 3.95*inch, "Classification:")
        p.line(455, 3.95*inch, 570, 3.95*inch) #(x1, y1, x2, y2)
        p.drawString(6.5*inch, 3.98*inch, "SERVICE")

        p.drawString(0.2*inch, 3.7*inch, "Civil Status:")
        p.line(70, 3.68*inch, 125, 3.68*inch) #(x1, y1, x2, y2)
        p.drawString(1*inch, 3.7*inch, stat)

        p.drawString(1.8*inch, 3.7*inch, "DATE OF BIRTH(MM/DD/YYYY):")
        p.line(280, 3.68*inch, 370, 3.68*inch) #(x1, y1, x2, y2)
        p.drawString(4*inch, 3.7*inch, dob)

        p.drawString(5.2*inch, 3.7*inch, "NATIONALITY:")
        p.line(450, 3.68*inch, 570, 3.68*inch) #(x1, y1, x2, y2)
        p.drawString(6.5*inch, 3.7*inch, "--")


        p.drawString(0.2*inch, 3.4*inch, "ADDRESS:")
        p.line(65, 3.4*inch, 300, 3.4*inch) #(x1, y1, x2, y2)
        p.drawString(1*inch, 3.45*inch, address)

        p.drawString(4.3*inch, 3.4*inch, "CONTACT NO.:")
        p.line(390, 3.4*inch, 570, 3.4*inch) #(x1, y1, x2, y2)
        p.drawString(5.4*inch, 3.45*inch, "###")


        

        p.setFillColor('white')# Amount
        p.rect(0.25*inch,2.8*inch,7.75*inch,0.25*inch,fill=0)
        p.setFillColor("black")# AMOUNT :
        p.setFont("Times-Bold", 12, leading=None)
        p.drawString(5.8*inch, 2.85*inch, "RESULT")

        p.setFillColor('GRAY')# Amount
        p.rect(0.25*inch,2.1*inch,4*inch,0.70*inch,fill=1)
        p.setFillColor("white")# AMOUNT :
        p.setFont("Times-Bold", 16, leading=None)
        p.drawString(0.9*inch, 2.4*inch, "Panbio CoVid-19 Ag Rapid Test")

        p.setFillColor('BLACK')# Amount
        p.rect(4.25*inch,2.1*inch,3.75*inch,0.70*inch,fill=1)
        p.setFillColor("white")# AMOUNT :
        p.setFont("Times-Bold", 18, leading=None)
        p.drawString(5.5*inch, 2.4*inch, r['result'])

        # p.setFillColor('NONE')# Amount
        # p.rect(0.25*inch,1.5*inch,7.75*inch,0.5*inch,fill=0)
        # p.line(18, 1.8*inch, 577, 1.8*inch) #(x1, y1, x2, y2)

        p.rect(0.25*inch,1.6*inch,1*inch,0.35*inch,fill=0)
        p.rect(1.25*inch,1.6*inch,1.25*inch,0.35*inch,fill=0)
        p.rect(2.5*inch,1.6*inch,1.25*inch,0.35*inch,fill=0)
        p.rect(3.75*inch,1.6*inch,1.5*inch,0.35*inch,fill=0)
        p.rect(5.25*inch,1.6*inch,1.5*inch,0.35*inch,fill=0)
        p.rect(6.75*inch,1.6*inch,1.25*inch,0.35*inch,fill=0)
        p.setFillColor('BLACK')# Amount
        p.setFont("Times-Bold", 12, leading=None)
        p.drawString(0.35*inch, 1.7*inch, "KIT USED:")
        p.setFont("Times-Bold", 8, leading=None)
        p.drawString(1.35*inch, 1.8*inch, "Abott-Pabio Covid-19")
        p.drawString(1.5*inch, 1.7*inch, "Ag Rapid Test")
        p.setFont("Times-Bold", 12, leading=None)
        p.drawString(2.75*inch, 1.7*inch, "LOT NO.:")
        p.drawString(4*inch, 1.7*inch, r['lot_no'])
        p.drawString(5.35*inch, 1.7*inch, "EXPIRY DATE:")
        p.drawString(6.8*inch, 1.7*inch,r['expiry_date'])


        p.rect(0.25*inch,1.35*inch,1*inch,0.25*inch,fill=0)
        p.rect(1.25*inch,1.35*inch,6.75*inch,0.25*inch,fill=0)
        p.setFont("Times-Bold", 11, leading=None)
        p.drawString(1.5*inch, 1.4*inch, r['remarks'])
        p.drawString(0.35*inch, 1.4*inch, "REMARKS:")
    
        p.setFillColor('BLACK')# Amount
        p.setFont("Times-Roman", 10, leading=None)
        p.drawString(0.2*inch, 1*inch, "Perform by:")
        p.drawString(0.2*inch, 0.60*inch, "_______________________________")
        p.drawString(0.75*inch, 0.75*inch, r['perform_by'])
        p.setFont("Times-Italic", 10, leading=None)
        p.setFillColor('GRAY')# Amount
        p.drawString(0.9*inch, .6*inch, "Lic #######")
        p.setFillColor('BLACK')# Amount
        p.setFont("Times-Roman", 10, leading=None)
        p.drawString(0.75*inch, 0.45*inch, "Medical Technologist")


        p.setFont("Times-Roman", 10, leading=None)
        p.drawString(2.75*inch, 1.1*inch, "Verify by:")
        p.drawString(3*inch, 0.60*inch, "_______________________________")
        p.drawString(3.25*inch, 0.75*inch, r['verified_by'])
        p.setFont("Times-Italic", 10, leading=None)
        p.setFillColor('GRAY')# Amount
        p.drawString(3.5*inch, .6*inch, "Lic #######")
        p.setFillColor('BLACK')# Amount
        p.setFont("Times-Roman", 10, leading=None)
        p.drawString(3.25*inch, 0.45*inch, "Medical Technologist")

        p.setFont("Times-Roman", 10, leading=None)
        p.drawString(5.5*inch, 1.1*inch, "Approved by:")
        p.drawString(5.75*inch, 0.60*inch, "_______________________________")
        p.drawString(5.75*inch, 0.75*inch,"RAYMUNDO B. IBARRIENTOS,MD")
        p.setFont("Times-Italic", 10, leading=None)
        p.setFillColor('GRAY')# Amount
        p.drawString(6.5*inch, .6*inch, "Lic #0078995")
        p.setFillColor('BLACK')# Amount
        p.setFont("Times-Roman", 10, leading=None)
        p.drawString(6.5*inch, 0.45*inch, "Pathologist")


    p.line(0, 0.2*inch, 1000, 0.30*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Italic", 7, leading=None)
    p.drawString(0.1*inch, 0.1*inch, "BRGHGMC-F-AS-BIL-006")
    p.drawString(3*inch, 0.1*inch, "Rev 2")
    p.drawString(4.5*inch, 0.1*inch, "Effectivity Date: January 6, 2020")
    p.drawImage(padaba, 7*inch, 0.05*inch, mask='auto', width=80, height=10)
    p.setTitle("RDT_RESULT")
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response



# /////////////// HEMA
def result_hematology(request):
    logo = ImageReader(static_root + '/integrated/img/brghgmclogo.png')
    logo1 = ImageReader(static_root + '/integrated/img/dohlogo.png')
    padaba = ImageReader(static_root + '/integrated/img/pagpadaba.png')
    # bg = ImageReader(static_root + '/integrated/img/lab-bg.png')
   
    response = HttpResponse(content_type='application/pdf')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setPageSize((5.85*inch, 8.27*inch)) 
    # p.setPageSize((A4))
    p.setFont('Helvetica',100, leading=None)
    p.rotate(45)
    p.setFillColorCMYK(0,0,0,0.08)
    p.drawString(1.5*inch,.5*inch,'BRGHGMC')
    p.rotate(-45)

    p.drawImage(logo, 0.1*inch, 7.63*inch, mask='auto', width=35, height=35)
    p.drawImage(logo1, 0.65*inch, 7.63*inch, mask='auto', width=35, height=35)
    
    # p.drawImage(logo, 0.5*inch, 0*inch, mask='auto', width=400, height=400)

    p.setFont("Times-Bold", 12, leading=None)
    p.setFillColor("green")
    p.drawString(1.2*inch, 8*inch, "Bicol Region General Hospital and Geriatric Medical Center")
    p.setFont("Times-Roman", 9, leading=None)
    p.drawString(2.3*inch, 7.85*inch, "(Formely BICOL SANITARIUM)")
    p.setFillColor("black")
    p.drawString(2.25*inch, 7.75*inch, "San Pedro, Cabusao Camarines Sur")
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(1.65*inch, 7.65*inch, "Telephone Nos.: (054) 473-2244, 472-4422, 881-1033, 881-1761")
    p.drawString(1.75*inch, 7.55*inch, "E-mail Address: bicolsan@gmail.com, brghgmc@gmail.com")
    # Header
    p.line(0, 7.52*inch, 1000, 7.52*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 14, leading=None)
    p.drawString(2.18*inch, 7.3*inch, "HEMATOLOGY")
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(2.6*inch, 7.18*inch, "(FORM A)")
    p.setLineWidth(0.1)
    p.setFont("Times-Roman", 9, leading=None)

    p.drawString(4.5*inch, 7.2*inch, "Date.:")
    p.line(345, 7.19*inch, 410, 7.19*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 9, leading=None)
    p.drawString(4.8*inch, 7.2*inch, '')
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(4.2*inch, 7*inch, "Control No.:")
    p.line(345, 7*inch, 410, 7*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 9, leading=None)
    p.drawString(4.8*inch, 7.02*inch,'INP23-0000021')

    
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(0.2*inch, 6.7*inch, "Name:")
    p.line(43, 6.7*inch, 220, 6.7*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(0.6*inch, 6.72*inch, 'JUAN DELA CRUZ')

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(3.2*inch, 6.7*inch, "Age:")
    p.line(250, 6.7*inch, 310, 6.7*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(3.6*inch, 6.72*inch,'21' )

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(4.4*inch, 6.7*inch, "Sex:")
    p.line(330, 6.7*inch, 410, 6.7*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(5*inch, 6.72*inch, 'MALE')

    # newline
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(0.2*inch, 6.5*inch, "Ward:")
    p.line(40, 6.5*inch, 100,6.5*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(0.6*inch, 6.52*inch, 'OPD')

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(1.5*inch, 6.5*inch, "Hospital No.:")
    p.line(155, 6.5*inch, 250,6.5*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(2.3*inch, 6.52*inch, '0000000000123')

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(3.6*inch, 6.5*inch, "Classification:")
    p.line(310, 6.5*inch, 410,6.5*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(4.8*inch, 6.52*inch, "SERIVCES")

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(0.2*inch, 6.3*inch, "Requesting Physician:")
    p.line(85, 6.3*inch, 410, 6.3*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(1.2*inch, 6.35*inch, 'DR. BADONG')
    

    # ############################
    mdata=  [
            ['','RESULT (SI UNITS)','NORMAL VALUE (SI UNITS)'],
            ['Hemoglobin:','----------','120-140 g/l'],
            ['Hematocrit:','----------','0.37 - 0.45'],
            ['RBC Count:','----------','4.5-5.5 X 10 12/l'],
            ['MVC:','----------','80 - 96 fl'],
            ['MCH','----------','27-32 pg'],
            ['MCHC:','----------','32-36 g/dl'],
            ['WBC Count:','----------','5.0-10 X 10 12/l'],
            ['Differential Count:','----------',''],
            ['Poly Neutrophils:','----------',''],
            ['      \tNeutrophil','----------','0.04-12.0'],
            ['      \tLymphocytes:','----------','0.15-0.45µ'],
            ['      \tMonocytes:','----------','0.04-12.0'],
            ['      \tEosinophil:','----------','0.05-0.07'],
            ['      \tBasophils:','----------','0.0-0.02'],
            ['Platelet Count:','----------','150-400 X 10 9/L'],
            ['','',''],
            ['Blood Group:','----------',''],
            ['Reticulocyte:','----------','0.5-1.5%'],
            ['NOTES:','----------'],
           
        ]
    
    # mt = Table(mdata, colWidths=[ 1.8*inch,1.9*inch,1.9*inch],rowHeights=[0.2*inch,.70*inch,0.2*inch])
    mt = Table(mdata, colWidths=[ 1.8*inch,1.9*inch,1.9*inch])
    mt.setStyle(TableStyle([
            
            ('BOX', (0, 0), (-1, -1), 0.2, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.05, colors.gray),
            ('VALIGN', (-1, -1), (-1, -1), 'MIDDLE'),
            ('VALIGN', (0, -2), (-1, -1), 'BOTTOM'),
            
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            # ('BACKGROUND',(-1,-1),(0,0),colors.gray),
            ('ALIGN',(0,-2),(0,-2),'LEFT'),
            ('ALIGN',(0,-3),(0,-3),'LEFT'),
            ('ALIGN',(0,-4),(0,-4),'LEFT'),
            ('ALIGN',(0,-5),(0,-5),'LEFT'),
            ('ALIGN',(0,-6),(0,-6),'LEFT'),
            ('ALIGN',(0,-7),(0,-7),'LEFT'),
            ('ALIGN',(0,-8),(0,-8),'LEFT'),
            ('ALIGN',(0,-9),(0,-9),'LEFT'),
            ('ALIGN',(0,-10),(0,-10),'LEFT'),
            ('ALIGN',(0,-11),(0,-11),'LEFT'),
            ('ALIGN',(0,-12),(0,-12),'LEFT'),
            ('ALIGN',(0,-13),(0,-13),'LEFT'),
            ('ALIGN',(0,-14),(0,-14),'LEFT'),
            ('ALIGN',(0,-15),(0,-15),'LEFT'),
            ('ALIGN',(0,-16),(0,-16),'LEFT'),
            ('ALIGN',(0,-17),(0,-17),'LEFT'),
            ('ALIGN',(0,-18),(0,-18),'LEFT'),
            ('ALIGN',(0,-19),(0,-19),'LEFT'),
            ('ALIGN',(0,-20),(0,-20),'LEFT'),
            # ('BACKGROUND',(0,-20),(0,-20),colors.black),
            # ('TEXTCOLOR',(0,-20),(0,-20),colors.white),
            
            ('ALIGN',(0,-1),(-1,-1),'CENTER'),
            
            ('FONT', (0, 0), (-1, -1), 'Times-Bold', 9),
            # ('FONT', (0, -1), (-1, -1), 'Times-Italic', 8)

        ]))
    mt.wrapOn(p, 0, 0)
    
    mt.drawOn(p, 0.1*inch, 1.6*inch)


    ############################
    
    pb=Paragraph('performBy')
    vb=Paragraph('verifyBy')
    ab=Paragraph('RAYMUNDO B IBARRIENTOS, MD. ')
   
    pbb='SALVADOR B. CECILIO \n Lic #0070511'
    vbb='SALVADOR B. CECILIO \n Lic #0070511'
    abb='RAYMUNDO B. IBARRIENTOS,MD \n Lic #0078995'
    
    
    mdata=  [
            ['Performed By:','Verified By:','Approved By:'],
            [pbb,vbb,abb],
            ['Medical Technologist:','Medical Technologist:','Pathologisit'],
           
        ]
    
    mt = Table(mdata, colWidths=[ 1.8*inch,1.9*inch,1.9*inch],rowHeights=[0.2*inch,.70*inch,0.2*inch])
    mt.setStyle(TableStyle([
            
            ('BOX', (0, 0), (-1, -1), 0.2, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.05, colors.gray),
            ('VALIGN', (-1, -1), (-1, -1), 'MIDDLE'),
            ('VALIGN', (0, -2), (-1, -1), 'BOTTOM'),
            
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN',(0,-2),(-1,-1),'CENTER'),
            ('ALIGN',(0,-1),(-1,-1),'CENTER'),
            ('FONT', (0, -2), (-1, -1), 'Times-Italic', 8),
            ('FONT', (0, 0), (-1, -1), 'Times-Italic', 8),
            ('FONT', (0, -1), (-1, -1), 'Times-Italic', 8)

        ]))
    mt.wrapOn(p, 0, 0)
    
    mt.drawOn(p, 0.1*inch, .45*inch)
    
        


    p.line(0, 0.2*inch, 1000, 0.30*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Italic", 7, leading=None)
    p.drawString(0.1*inch, 0.1*inch, "BRGHGMC-F-MS-LAB-005")
    p.drawString(1.5*inch, 0.1*inch, "Rev 2")
    p.drawString(2.5*inch, 0.1*inch, "Effectivity Date: May 2, 2023")
    p.drawImage(padaba, 4.5*inch, 0.05*inch, mask='auto', width=80, height=10)

    p.setTitle("HEMATOLOGY-FORM-A")
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

################### COAGULATION 

def result_coagulation(request):

    logo = ImageReader(static_root + '/integrated/img/brghgmclogo.png')
    logo1 = ImageReader(static_root + '/integrated/img/dohlogo.png')
    padaba = ImageReader(static_root + '/integrated/img/pagpadaba.png')
    # bg = ImageReader(static_root + '/integrated/img/lab-bg.png')
    response = HttpResponse(content_type='application/pdf')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setPageSize((5.85*inch, 8.27*inch)) 
    # p.setPageSize((A4))
    p.setFont('Helvetica',100, leading=None)
    p.rotate(45)
    p.setFillColorCMYK(0,0,0,0.08)
    p.drawString(1.5*inch,.5*inch,'BRGHGMC')
    p.rotate(-45)

    p.drawImage(logo, 0.1*inch, 7.63*inch, mask='auto', width=35, height=35)
    p.drawImage(logo1, 0.65*inch, 7.63*inch, mask='auto', width=35, height=35)

    # p.drawImage(logo, 0.5*inch, 0*inch, mask='auto', width=400, height=400)

    p.setFont("Times-Bold", 12, leading=None)
    p.setFillColor("green")
    p.drawString(1.2*inch, 8*inch, "Bicol Region General Hospital and Geriatric Medical Center")
    p.setFont("Times-Roman", 9, leading=None)
    p.drawString(2.3*inch, 7.85*inch, "(Formely BICOL SANITARIUM)")
    p.setFillColor("black")
    p.drawString(2.25*inch, 7.75*inch, "San Pedro, Cabusao Camarines Sur")
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(1.65*inch, 7.65*inch, "Telephone Nos.: (054) 473-2244, 472-4422, 881-1033, 881-1761")
    p.drawString(1.75*inch, 7.55*inch, "E-mail Address: bicolsan@gmail.com, brghgmc@gmail.com")
    # Header
    p.line(0, 7.52*inch, 1000, 7.52*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 14, leading=None)
    p.drawString(2.18*inch, 7.3*inch, "COAGULATION")
    p.setFont("Times-Roman", 8, leading=None)
    # p.drawString(2.6*inch, 7.18*inch, "(FORM A)")
    p.setLineWidth(0.1)
    p.setFont("Times-Roman", 9, leading=None)

    p.drawString(4.5*inch, 7.2*inch, "Date.:")
    p.line(345, 7.19*inch, 410, 7.19*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 9, leading=None)
    p.drawString(4.8*inch, 7.2*inch, '')
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(4.2*inch, 7*inch, "Control No.:")
    p.line(345, 7*inch, 410, 7*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 9, leading=None)
    p.drawString(4.8*inch, 7.02*inch,'INP23-0000021')

    
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(0.2*inch, 6.7*inch, "Name:")
    p.line(43, 6.7*inch, 220, 6.7*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(0.6*inch, 6.72*inch, 'JUAN DELA CRUZ')

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(3.2*inch, 6.7*inch, "Age:")
    p.line(250, 6.7*inch, 310, 6.7*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(3.6*inch, 6.72*inch,'21' )

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(4.4*inch, 6.7*inch, "Sex:")
    p.line(330, 6.7*inch, 410, 6.7*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(5*inch, 6.72*inch, 'MALE')

    # newline
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(0.2*inch, 6.5*inch, "Ward:")
    p.line(40, 6.5*inch, 100,6.5*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(0.6*inch, 6.52*inch, 'OPD')

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(1.5*inch, 6.5*inch, "Hospital No.:")
    p.line(155, 6.5*inch, 250,6.5*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(2.3*inch, 6.52*inch, '0000000000123')

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(3.6*inch, 6.5*inch, "Classification:")
    p.line(310, 6.5*inch, 410,6.5*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(4.8*inch, 6.52*inch, "SERIVCES")

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(0.2*inch, 6.3*inch, "Requesting Physician:")
    p.line(85, 6.3*inch, 410, 6.3*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(1.2*inch, 6.35*inch, 'DR. BADONG')
    

    # ############################
    mdata=  [
            ['','RESULT (SI UNITS)','NORMAL VALUE (SI UNITS)'],
            ['PROTHROMBIN TIME','--------  sec.','11.8 - 15.1 sec'],
            ['        \t INR','----------','0.37 - 0.45'],
            ['        \t %','----------','4.5-5.5 X 10 12/l'],
            ['ACTIVATE PARTIAL\nTHROMBIN TIME','----------','80 - 96 fl'],
            ['','',''],
            ['FIBRINOGEN','----------','32-36 g/dl'],
            ['','',''],
            ['D-DIMER','----------',''],
            ['','',''],
            ['CLOTTING TIME','----------','0.04-12.0'],
            ['BLEEDING TIME','----------','0.15-0.45'],
            ['','',''],
            ['ESR','----------','0.05-0.07'],
            ['        \t MALE','----------','0.0-0.02'],
            ['        \t FEMALE','----------','150-400 X 10 9/L'],
            ['NOTES:','----------'],
           
        ]
    
    # mt = Table(mdata, colWidths=[ 1.8*inch,1.9*inch,1.9*inch],rowHeights=[0.2*inch,.70*inch,0.2*inch])
    mt = Table(mdata, colWidths=[ 1.8*inch,1.8*inch,1.9*inch])
    mt.setStyle(TableStyle([
            
            ('BOX', (0, 0), (-1, -1), 0.2, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.05, colors.gray),
            ('VALIGN', (-1, -1), (-1, -1), 'MIDDLE'),
            ('VALIGN', (0, -2), (-1, -1), 'BOTTOM'),
            
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            # ('BACKGROUND',(-1,-1),(0,0),colors.gray),
            ('ALIGN',(0,-2),(0,-2),'LEFT'),
            ('ALIGN',(0,-3),(0,-3),'LEFT'),
            ('ALIGN',(0,-4),(0,-4),'LEFT'),
            ('ALIGN',(0,-5),(0,-5),'LEFT'),
            ('ALIGN',(0,-6),(0,-6),'LEFT'),
            ('ALIGN',(0,-7),(0,-7),'LEFT'),
            ('ALIGN',(0,-8),(0,-8),'LEFT'),
            ('ALIGN',(0,-9),(0,-9),'LEFT'),
            ('ALIGN',(0,-10),(0,-10),'LEFT'),
            ('ALIGN',(0,-11),(0,-11),'LEFT'),
            ('ALIGN',(0,-12),(0,-12),'LEFT'),
            ('ALIGN',(0,-13),(0,-13),'LEFT'),
            ('ALIGN',(0,-14),(0,-14),'LEFT'),
            ('ALIGN',(0,-15),(0,-15),'LEFT'),
            ('ALIGN',(0,-16),(0,-16),'LEFT'),
            ('ALIGN',(0,-17),(0,-17),'LEFT'),
            ('ALIGN',(0,-18),(0,-18),'LEFT'),
            ('ALIGN',(0,-19),(0,-19),'LEFT'),
            ('ALIGN',(0,-20),(0,-20),'LEFT'),
            # ('BACKGROUND',(0,-20),(0,-20),colors.black),
            # ('TEXTCOLOR',(0,-20),(0,-20),colors.white),
            ('ALIGN',(0,-1),(-1,-1),'CENTER'),
            
            ('FONT', (0, 0), (-1, -1), 'Times-Bold', 9),
            # ('FONT', (0, -1), (-1, -1), 'Times-Italic', 8)

        ]))
    mt.wrapOn(p, 0, 0)
    
    mt.drawOn(p, 0.2*inch, 2*inch)


    ############################
    
    pb=Paragraph('performBy')
    vb=Paragraph('verifyBy')
    ab=Paragraph('RAYMUNDO B IBARRIENTOS, MD. ')
   
    pbb='SALVADOR B. CECILIO \n Lic #0070511'
    vbb='SALVADOR B. CECILIO \n Lic #0070511'
    abb='RAYMUNDO B. IBARRIENTOS,MD \n Lic #0078995'
    
    
    mdata=  [
            ['Performed By:','Verified By:','Approved By:'],
            [pbb,vbb,abb],
            ['Medical Technologist:','Medical Technologist:','Pathologisit'],
           
        ]
    
    mt = Table(mdata, colWidths=[ 1.8*inch,1.8*inch,1.9*inch],rowHeights=[0.2*inch,.70*inch,0.2*inch])
    mt.setStyle(TableStyle([
            
            ('BOX', (0, 0), (-1, -1), 0.2, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.05, colors.gray),
            ('VALIGN', (-1, -1), (-1, -1), 'MIDDLE'),
            ('VALIGN', (0, -2), (-1, -1), 'BOTTOM'),
            
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN',(0,-2),(-1,-1),'CENTER'),
            ('ALIGN',(0,-1),(-1,-1),'CENTER'),
            ('FONT', (0, -2), (-1, -1), 'Times-Italic', 8),
            ('FONT', (0, 0), (-1, -1), 'Times-Italic', 8),
            ('FONT', (0, -1), (-1, -1), 'Times-Italic', 8)

        ]))
    mt.wrapOn(p, 0, 0)
    
    mt.drawOn(p, 0.2*inch, .58*inch)
    
        


    p.line(0, 0.35*inch, 1000, 0.35*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Italic", 7, leading=None)
    p.drawString(0.1*inch, 0.15*inch, "BRGHGMC-F-MS-LAB-005")
    p.drawString(1.5*inch, 0.15*inch, "Rev 2")
    p.drawString(2.5*inch, 0.15*inch, "Effectivity Date: May 2, 2023")
    p.drawImage(padaba, 4.5*inch, 0.13*inch, mask='auto', width=80, height=10)

    p.setTitle("HEMATOLOGY-FORM-A")
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def result_obf_hematology(request):

    logo = ImageReader(static_root + '/integrated/img/brghgmclogo.png')
    logo1 = ImageReader(static_root + '/integrated/img/dohlogo.png')
    padaba = ImageReader(static_root + '/integrated/img/pagpadaba.png')
    # bg = ImageReader(static_root + '/integrated/img/lab-bg.png')
    response = HttpResponse(content_type='application/pdf')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setPageSize((5.85*inch, 8.27*inch)) 
    # p.setPageSize((A4))
    p.setFont('Helvetica',100, leading=None)
    p.rotate(45)
    p.setFillColorCMYK(0,0,0,0.08)
    p.drawString(1.5*inch,.5*inch,'BRGHGMC')
    p.rotate(-45)

    p.drawImage(logo, 0.1*inch, 7.63*inch, mask='auto', width=35, height=35)
    p.drawImage(logo1, 0.65*inch, 7.63*inch, mask='auto', width=35, height=35)

    # p.drawImage(logo, 0.5*inch, 0*inch, mask='auto', width=400, height=400)

    p.setFont("Times-Bold", 12, leading=None)
    p.setFillColor("green")
    p.drawString(1.2*inch, 8*inch, "Bicol Region General Hospital and Geriatric Medical Center")
    p.setFont("Times-Roman", 9, leading=None)
    p.drawString(2.3*inch, 7.85*inch, "(Formely BICOL SANITARIUM)")
    p.setFillColor("black")
    p.drawString(2.25*inch, 7.75*inch, "San Pedro, Cabusao Camarines Sur")
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(1.65*inch, 7.65*inch, "Telephone Nos.: (054) 473-2244, 472-4422, 881-1033, 881-1761")
    p.drawString(1.75*inch, 7.55*inch, "E-mail Address: bicolsan@gmail.com, brghgmc@gmail.com")
    # Header
    p.line(0, 7.52*inch, 1000, 7.52*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 14, leading=None)
    p.drawString(1.8*inch, 7.3*inch, "OTHER BODY FLUIDS")
    p.setFont("Times-Roman", 14, leading=None)
    p.drawString(2.1*inch, 7.1*inch, "(HEMATOLOGY)")
    p.setLineWidth(0.1)
    p.setFont("Times-Roman", 9, leading=None)

    p.drawString(4.5*inch, 7.2*inch, "Date.:")
    p.line(345, 7.19*inch, 410, 7.19*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 9, leading=None)
    p.drawString(4.8*inch, 7.2*inch, '')
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(4.2*inch, 7*inch, "Control No.:")
    p.line(345, 7*inch, 410, 7*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 9, leading=None)
    p.drawString(4.8*inch, 7.02*inch,'INP23-0000021')

    
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(0.2*inch, 6.7*inch, "Name:")
    p.line(43, 6.7*inch, 220, 6.7*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(0.6*inch, 6.72*inch, 'JUAN DELA CRUZ')

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(3.2*inch, 6.7*inch, "Age:")
    p.line(250, 6.7*inch, 310, 6.7*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(3.6*inch, 6.72*inch,'21' )

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(4.4*inch, 6.7*inch, "Sex:")
    p.line(330, 6.7*inch, 410, 6.7*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(5*inch, 6.72*inch, 'MALE')

    # newline
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(0.2*inch, 6.5*inch, "Ward:")
    p.line(40, 6.5*inch, 100,6.5*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(0.6*inch, 6.52*inch, 'OPD')

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(1.5*inch, 6.5*inch, "Hospital No.:")
    p.line(155, 6.5*inch, 250,6.5*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(2.3*inch, 6.52*inch, '0000000000123')

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(3.6*inch, 6.5*inch, "Classification:")
    p.line(310, 6.5*inch, 410,6.5*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(4.8*inch, 6.52*inch, "SERIVCES")

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(0.2*inch, 6.3*inch, "Requesting Physician:")
    p.line(85, 6.3*inch, 410, 6.3*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(1.2*inch, 6.35*inch, 'DR. BADONG')
    

    # ############################
    mdata=  [
            ['WBC DIFFERENTIAL COUNT'],
            ['Macroscopic Findings'],
            ['Color:','----------'],
            ['Transparency','----------'],
            ['Volume:','----------'],
            ['','',''],
            ['Microscopic Findings'],
            ['RBC:','----------','/HPF'],
            ['Pus Cells:','----------','/HPF'],
            ['','',''],
            ['WBC','-------','5-10 12/L'],
            ['','',''],
            ['Differential Count'],
            ['Segmenters:','----------','%'],
            ['Lymphocytes:','----------','%'],
            ['Monocytes:','----------','%'],
            ['Eosinophil:','----------','%'],
            ['Stab:','----------','%'],
            ['NOTES:','----------'],
           
        ]
    
    # mt = Table(mdata, colWidths=[ 1.8*inch,1.9*inch,1.9*inch],rowHeights=[0.2*inch,.70*inch,0.2*inch])
    mt = Table(mdata, colWidths=[ 1.8*inch,1.85*inch])
    mt.setStyle(TableStyle([
            
            ('BOX', (0, 0), (-1, -1), 0.2, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.05, colors.gray),
            ('VALIGN', (-1, -1), (-1, -1), 'MIDDLE'),
            ('VALIGN', (0, -2), (-1, -1), 'BOTTOM'),
            
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            # # ('BACKGROUND',(0,-17),(2,-17),colors.gray),
            # ('SPAN',(0,-20),(2,-20)),
            # ('ALIGN',(0,-20),(2,-20),'CENTER'),
            # # ('TEXTCOLOR',(0,-17),(2,-17),colors.red),
            # ('FONT',(0,-20),(0,-20),'Times-Bold',14),
            
            ('SPAN',(0,-19),(2,-19)),
            ('ALIGN',(0,-19),(2,-19),'CENTER'),
            ('FONT',(0,-19),(0,-19),'Times-Bold',14),

            ('SPAN',(0,-18),(2,-18)),
            ('ALIGN',(0,-18),(2,-18),'CENTER'),
            ('FONT',(0,-18),(0,-18),'Times-Bold',12),

            # ('BACKGROUND',(1,-1),(2,-1),colors.gray),
            ('SPAN',(1,-17),(2,-17)),
            ('SPAN',(1,-16),(2,-16)),
            ('SPAN',(1,-15),(2,-15)),
            ('SPAN',(0,-14),(2,-14)),
            ('SPAN',(0,-13),(2,-13)),

            ('SPAN',(0,-10),(2,-10)),
            ('SPAN',(1,-1),(2,-1)),

            ('ALIGN',(0,-13),(2,-13),'CENTER'),
            ('FONT',(0,-13),(0,-13),'Times-Bold',12),

            ('SPAN',(0,-7),(2,-7)),
            ('ALIGN',(0,-7),(2,-7),'CENTER'),
            ('FONT',(0,-7),(0,-7),'Times-Bold',12),

            ('ALIGN',(0,-2),(0,-2),'LEFT'),
            ('FONT', (0, -2), (0, -2), 'Times-Bold', 9),
            ('ALIGN',(0,-3),(0,-3),'LEFT'),
            ('FONT', (0, -3), (0, -3), 'Times-Bold', 9),
            ('ALIGN',(0,-4),(0,-4),'LEFT'),
            ('FONT', (0, -4), (0, -4), 'Times-Bold', 9),
            ('ALIGN',(0,-5),(0,-5),'LEFT'),
            ('FONT', (0, -5), (0, -5), 'Times-Bold', 9),
            ('ALIGN',(0,-6),(0,-6),'LEFT'),
            ('FONT', (0, -6), (0, -6), 'Times-Bold', 9),
            # ('ALIGN',(0,-7),(0,-7),'LEFT'),
            # ('FONT', (0, -7), (0, -7), 'Times-Bold', 9),
            ('ALIGN',(0,-8),(0,-8),'LEFT'),
            ('FONT', (0, -8), (0, -8), 'Times-Bold', 9),
            ('ALIGN',(0,-9),(0,-9),'LEFT'),
            ('FONT', (0, -9), (0, -9), 'Times-Bold', 9),
            ('ALIGN',(0,-10),(0,-10),'LEFT'),
            ('FONT', (0, -10), (0, -10), 'Times-Bold', 6),
            ('ALIGN',(0,-11),(0,-11),'LEFT'),
            ('FONT', (0, -11), (0, -11), 'Times-Bold', 9),
            ('ALIGN',(0,-12),(0,-12),'LEFT'),
            ('FONT', (0, -12), (0, -12), 'Times-Bold', 9),
            # ('ALIGN',(0,-13),(0,-13),'LEFT'),
            ('ALIGN',(0,-14),(0,-14),'LEFT'),
            ('FONT', (0, -14), (0, -14), 'Times-Bold', 9),
            ('ALIGN',(0,-15),(0,-15),'LEFT'),
            ('FONT', (0, -15), (0, -15), 'Times-Bold', 9),
            ('ALIGN',(0,-16),(0,-16),'LEFT'),
            ('FONT', (0, -16), (0, -16), 'Times-Bold', 9),
            ('ALIGN',(0,-17),(0,-17),'LEFT'),
            ('FONT', (0, -17), (0, -17), 'Times-Bold', 9),
            # ('ALIGN',(0,-18),(0,-18),'LEFT'),
            # ('ALIGN',(0,-19),(0,-19),'LEFT'),
            # ('ALIGN',(0,-20),(0,-20),'LEFT'),
            # ('BACKGROUND',(0,-20),(0,-20),colors.black),
            # ('TEXTCOLOR',(0,-20),(0,-20),colors.white),
            # ('ALIGN',(0,-1),(-1,-1),'CENTER'),
            
            ('FONT', (0, -2), (0, -2), 'Times-Bold', 9),
            # ('FONT', (0, -1), (-1, -1), 'Times-Italic', 8)

        ]))
    mt.wrapOn(p, 0, 0)
    
    mt.drawOn(p, 0.2*inch, 1.35*inch)


    ############################
    
    pb=Paragraph('performBy')
    vb=Paragraph('verifyBy')
    ab=Paragraph('RAYMUNDO B IBARRIENTOS, MD. ')
   
    pbb='SALVADOR B. CECILIO \n Lic #0070511'
    vbb='SALVADOR B. CECILIO \n Lic #0070511'
    abb='RAYMUNDO B. IBARRIENTOS,MD \n Lic #0078995'
    
    
    mdata=  [
            ['Performed By:','Verified By:','Approved By:'],
            [pbb,vbb,abb],
            ['Medical Technologist:','Medical Technologist:','Pathologisit'],
           
        ]
    
    mt = Table(mdata, colWidths=[ 1.8*inch,1.8*inch,1.9*inch],rowHeights=[0.2*inch,.55*inch,0.2*inch])
    mt.setStyle(TableStyle([
            
            ('BOX', (0, 0), (-1, -1), 0.2, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.05, colors.gray),
            ('VALIGN', (-1, -1), (-1, -1), 'MIDDLE'),
            ('VALIGN', (0, -2), (-1, -1), 'BOTTOM'),
            
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN',(0,-2),(-1,-1),'CENTER'),
            ('ALIGN',(0,-1),(-1,-1),'CENTER'),
            ('FONT', (0, -2), (-1, -1), 'Times-Italic', 8),
            ('FONT', (0, 0), (-1, -1), 'Times-Italic', 8),
            ('FONT', (0, -1), (-1, -1), 'Times-Italic', 8)

        ]))
    mt.wrapOn(p, 0, 0)
    
    mt.drawOn(p, 0.2*inch, .35*inch)
    
        


    p.line(0, 0.25*inch, 1000, 0.30*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Italic", 7, leading=None)
    p.drawString(0.1*inch, 0.15*inch, "BRGHGMC-F-MS-LAB-005")
    p.drawString(1.5*inch, 0.15*inch, "Rev 2")
    p.drawString(2.5*inch, 0.15*inch, "Effectivity Date: May 2, 2023")
    p.drawImage(padaba, 4.5*inch, 0.12*inch, mask='auto', width=80, height=10)

    p.setTitle("OBF-HEMATOLOGY")
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


####################################### URINALYSIS RESULT
def result_Urinalysis(request,encc,orderid):
    getuaresult=requests.post(get_urinalysis,data={'order_id':orderid}).json()
    ptx_req=requests.post(get_lab_request, data={'enccode':encc,'order_id':orderid}).json()

    # print(getuaresult)
    now=datetime.now()
    now=datetime.strftime(now,'%m-%d-%Y')
    # for i in getuaresult['data']:
    #         i['enccode'] = i['enccode'].replace("/", "-")
    #         if i['proccode'] == 'LABOR00076':
    #             color=i['urnvcolor']

    for ptx in ptx_req['details']:
        age=ptx['patage']
        gender=ptx['patsex']
        ptx['enccode'] = ptx['enccode'].replace("/", "-")
        try:
            wardname=ptx['wardname']
        except Exception as e:
            wardname=""
   
    logo = ImageReader(static_root + '/integrated/img/brghgmclogo.png')
    logo1 = ImageReader(static_root + '/integrated/img/dohlogo.png')
    padaba = ImageReader(static_root + '/integrated/img/pagpadaba.png')
    response = HttpResponse(content_type='application/pdf')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setPageSize((8.27*inch, 5.85*inch))
    # p.setPageSize((A4))

    p.setFont('Helvetica',100, leading=None)
    p.rotate(20)
    p.setFillColorCMYK(0,0,0,0.08)
    p.drawString(1*inch,.5*inch,'BRGHGMC')
    p.rotate(-20)
    p.drawImage(logo, 0.7*inch, 5.2*inch, mask='auto', width=40, height=40)
    p.drawImage(logo1, 1.3*inch, 5.2*inch, mask='auto', width=40, height=40)

    # p.drawImage(logo, 0.5*inch, 0*inch, mask='auto', width=400, height=400)
    color=''
    transparency=''
    reaction=''
    ph=''
    sg=''
    prot=''
    sugar=''
    ket=''
    nit=''
    bili=''
    bilin=''
    leu=''
    mlchon=''
    mlprot=''
    wbc=''
    rbc=''
    epi=''
    mucus=''
    bact=''
    cal=''
    uric=''
    amm=''
    fgc=''
    cgc=''
    hya=''
    wbccast=''
    rbccast=''
    others=''
    preg=''

    for u in getuaresult['data']:
        try:
            if(u['proccode'] == 'LABOR00076'):
                try:
                    ptxname=u['patlast']+", "+ u['patfirst']+"  "+u['patmiddle']
                    if u['urnvcolor'] == "":
                        color="------------------"
                    else:
                        color=u['urnvcolor']

                    if u['urnvchar'] == "":
                        transparency="------------------"
                    else:
                        transparency=u['urnvchar']
                    if u['urnvreac'] == "":
                        reaction="------------------"
                    else:
                        reaction=u['urnvreac']
                    if u['urnvph'] == "":
                        ph="------------------"
                    else:
                        ph=u['urnvph']
                    if u['urnvsg'] == "":
                        sg="------------------"
                    else:
                        sg=u['urnvsg']
                    if u['urnvprot'] == "":
                        prot="------------------"
                    else:
                        prot=u['urnvprot']

                    if u['urnvsugar'] == "":
                        sugar="------------------"
                    else:
                        sugar=u['urnvsugar']
                    if u['urnvket'] == "":
                        ket="------------------"
                    else:
                        ket=u['urnvket']
                    if u['urnvnit'] == "":
                        nit="------------------"
                    else:
                        nit=u['urnvnit']
                    if u['urnvbil'] == "":
                        bili="------------------"
                    else:
                        bili=u['urnvbil']
                    if u['urnvbilin'] == "":
                        bilin="------------------"
                    else:
                        bilin=u['urnvbilin']
                    if u['urnvleu'] == "":
                        leu="------------------"
                    else:
                        leu=u['urnvleu']
                    if u['urnvmlchon'] == "":
                        mlchon="------------------"
                    else:
                        mlchon=u['urnvmlchon']
                    if u['urnvmlprot'] == "":
                        mlprot="------------------"
                    else:
                        mlprot=u['urnvmlprot']
                    if u['urnvwbc'] == "":
                        wbc="----------/HPF"
                    else:
                        wbc=u['urnvwbc']+" /HPF"
                    if u['urnvrbc'] == "":
                        rbc="----------/HPF"
                    else:
                        rbc=u['urnvrbc']+" /HPF"
                    if u['urnvepi'] == "":
                        epi="------------------"
                    else:
                        epi=u['urnvepi']
                    if u['urnvmucus'] == "":
                        mucus="------------------"
                    else:
                        mucus=u['urnvmucus']
                    if u['urnvbact'] == "":
                        bact="------------------"
                    else:
                        bact=u['urnvbact']
                    if u['urnvval'] == "":
                        cal="------------------"
                    else:
                        cal=u['urnvval']
                    if u['urnvuric'] == "":
                        uric="------------------"
                    else:
                        uric=u['urnvuric']
                    if u['urnvamm'] == "":
                        amm="------------------"
                    else:
                        amm=u['urnvamm']
                    if u['urnvfgc'] == "":
                        fgc="----------/LPF"
                    else:
                        fgc=u['urnvfgc']+" /LPF"
                    if u['urnvcgc'] == "":
                        cgc="----------/LPF"
                    else:
                        cgc=u['urnvcgc']+" /LPF"
                    if u['urnvhya'] == "":
                        hya="----------/LPF"
                    else:
                        hya=u['urnvhya']+" /LPF"
                    if u['urnvwbccast'] == "":
                        wbccast="----------/LPF"
                    else:
                        wbccast=u['urnvwbccast']+" /LPF"
                    if u['urnvrbccast'] == "":
                        rbccast="----------/LPF"
                    else:
                        rbccast=u['urnvrbccast']+" /LPF"
                    if u['urnvothers'] == "":
                        others="----------"
                    else:
                        others=u['urnvothers']
                except Exception as e:
                    ptx_req=''
            elif(u['proccode'] == 'LABOR00081'):
                try:
                    ptxname=u['patlast']+", "+ u['patfirst']+"  "+u['patmiddle']
                    if u['urnvpreg'] is not None:
                       preg=u['urnvpreg']
                    else:
                       preg="----------"
                except Exception as e:
                    ptx_req=''


        except Exception as e:
                pt=''
    p.setFont("Times-Bold", 12, leading=None)
    p.setFillColor("green")
    p.drawString(2*inch, 5.65*inch, "Bicol Region General Hospital and Geriatric Medical Center")
    p.setFont("Times-Roman", 9, leading=None)
    p.drawString(3.2*inch, 5.5*inch, "(Formely BICOL SANITARIUM)")
    p.setFillColor("black")
    p.drawString(3.2*inch, 5.4*inch, "San Pedro, Cabusao Camarines Sur")
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(2.6*inch, 5.3*inch, "Telephone Nos.: (054) 473-2244, 472-4422, 881-1033, 881-1761")
    p.drawString(2.8*inch, 5.2*inch, "E-mail Address: bicolsan@gmail.com, brghgmc@gmail.com")
    p.line(0, 5.1*inch, 1000, 5.1*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 14, leading=None)
    p.drawString(3.5*inch, 4.9*inch, "URINALYSIS")
    p.setLineWidth(0.1)
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(6.5*inch, 4.9*inch, "Date:")
    p.line(490, 4.9*inch, 585, 4.9*inch) #(x1, y1, x2, y2)
    p.drawString(6.9*inch, 4.92*inch, now)
    p.drawString(0.2*inch, 4.7*inch, "Name:")
    p.line(43, 4.7*inch, 200, 4.7*inch) #(x1, y1, x2, y2)
    p.drawString(0.6*inch, 4.72*inch, ptxname)
    p.drawString(3*inch, 4.7*inch, "Age:")
    p.line(235, 4.7*inch, 280, 4.7*inch) #(x1, y1, x2, y2)
    p.drawString(3.5*inch, 4.72*inch, str(age))
    p.drawString(3.95*inch, 4.7*inch, "Sex:")
    p.line(300, 4.7*inch, 350, 4.7*inch) #(x1, y1, x2, y2)
    p.drawString(4.25*inch, 4.72*inch, gender)
    p.drawString(5.1*inch, 4.7*inch, "Ward:")
    p.line(395, 4.7*inch, 585, 4.7*inch) #(x1, y1, x2, y2)
    p.drawString(5.5*inch, 4.72*inch, ptx_req['toecode']+" - "+wardname)
    p.drawString(0.2*inch, 4.5*inch, "Hospital No.:")
    p.line(70, 4.5*inch, 200,4.5*inch) #(x1, y1, x2, y2)
    p.drawString(1*inch, 4.52*inch, u['hpercode'])
    p.drawString(3*inch, 4.5*inch, "Physician:")
    p.line(250, 4.5*inch, 390, 4.5*inch) #(x1, y1, x2, y2)
    p.drawString(3.6*inch, 4.52*inch, "---------")
    p.drawString(5.5*inch, 4.5*inch, "Classification:")
    p.line(455, 4.5*inch, 585, 4.5*inch) #(x1, y1, x2, y2)
    p.drawString(6.5*inch, 4.52*inch, "SERVICE")
    data=  [
                ['COLOR:','MICROSCOPIC FINDINGS'],
                ['TRANSPARENCY:', '                    WBC:'],
                ['REACTION:', '                    RBC:'],
                ['PH:', '                    EPITHELIAL CELLS:'],
                ['SPECIFIC GRAVITY', '                    MUCOS THREADS:'],
                ['CHEMICAL REACTIONS', '                    BACTERIA:'],
                ['           \t PROTIEN:', '                         \t Calcium Oxalate:'],
                ['           \t GLOCUSE:', '                         \t Amorphous Phosphate/Urates:'],
                ['           \t KETONE:', '                         \t Uric Acid'],
                ['           \t NITRITE:', '                         \t Ammonium Biurates:'],
                ['           \t BILIRUBIN:', '                    CAST:'],
                ['           \t UROBILINOGEN:', '                         \t Fine Granular Cast:'],
                ['           \t LEUKOCYTES:', '                         \t Coarse Granular Cast:'],
                ['', '                         \t Hyaline Cast:'],
                ['', '                         \t WBC Cast:'],
                ['MANUAL PROCEDURE', '                         \t RBC Cast:'],
                ['           \t URINE CHON:', 'OTHERS:'],
                ['           \t PROTIEN:', 'PREGNANCY TEST:'],
                ['NOTE:'],
                
            ]
        
        
        
    t = Table(data, colWidths=[ 4*inch,4*inch])
    t.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.05, colors.gray),
            ('VALIGN', (-1, -1), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONT', (0, 0), (-1, -1), 'Times-Bold', 6.2)
        ]))
    t.wrapOn(p, 0, 0)
        
    t.drawOn(p, 0.15*inch, 0.9*inch)

        # table value
        
            
    p.setFillColor('BLACK')# Amount
    p.setFont("Times-Bold", 10.5, leading=None)
    p.drawString(2*inch, 4.3*inch, color)
    p.drawString(2*inch, 4.13*inch, transparency)
    p.drawString(2*inch, 3.93*inch, reaction)
    p.drawString(2*inch, 3.74*inch, ph)
    p.drawString(2*inch, 3.54*inch, sg)
    p.drawString(2*inch, 3.18*inch, prot)
    p.drawString(2*inch, 2.99*inch, sugar)
    p.drawString(2*inch, 2.81*inch, ket)
    p.drawString(2*inch, 2.62*inch, nit)
    p.drawString(2*inch, 2.44*inch, bili)
    p.drawString(2*inch, 2.24*inch, bilin)
    p.drawString(2*inch, 2.06*inch, leu)
    p.drawString(2*inch, 1.32*inch, mlchon)
    p.drawString(2*inch, 1.13*inch, mlprot)
    p.drawString(6.5*inch, 4.12*inch, wbc)
    p.drawString(6.5*inch, 3.95*inch, rbc)
    p.drawString(6.5*inch, 3.74*inch, epi)
    p.drawString(6.5*inch, 3.55*inch, mucus)
    p.drawString(6.5*inch, 3.37*inch, bact)
    p.drawString(6.5*inch, 3.2*inch, cal)
    p.drawString(6.5*inch, 3*inch, "----------")
    p.drawString(6.5*inch, 2.81*inch, uric)
    p.drawString(6.5*inch, 2.62*inch, amm)
    p.drawString(6.5*inch, 2.26*inch, fgc)
    p.drawString(6.5*inch, 2.06*inch, cgc)
    p.drawString(6.5*inch, 1.88*inch,hya)
    p.drawString(6.5*inch, 1.7*inch, wbccast)
    p.drawString(6.5*inch, 1.5*inch, rbccast)
    p.setFillColor('RED')
    p.drawString(4.7*inch, 1.32*inch, others)
    p.setFillColor('BLACK')
    p.drawString(6.5*inch, 1.15*inch, preg)

        # /table value
        
            
    p.setFillColor('BLACK')# Amount
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(0.2*inch, 0.75*inch, "Perform by:")
    p.drawString(0.2*inch, 0.45*inch, "_______________________________")
    p.drawString(0.52*inch, 0.55*inch, u['perform_by'])
    p.setFont("Times-Italic", 8, leading=None)
    p.setFillColor('GRAY')# Amount
    p.drawString(0.9*inch, .45*inch, "Lic #0070511")
    p.setFillColor('BLACK')# Amount
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(0.75*inch, 0.3*inch, "Medical Technologist")


    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(2.75*inch, 0.75*inch, "Verify by:")
    p.drawString(3*inch, 0.45*inch, "_______________________________")
    p.drawString(3.25*inch, 0.55*inch, u['verified_by'])
    p.setFont("Times-Italic", 8, leading=None)
    p.setFillColor('GRAY')# Amount
    p.drawString(3.5*inch, .45*inch, "Lic #0070511")
    p.setFillColor('BLACK')# Amount
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(3.5*inch, 0.3*inch, "Medical Technologist")

    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(5.5*inch, 0.75*inch, "Approved by:")
    p.drawString(5.75*inch, 0.45*inch, "_______________________________")
    p.drawString(5.75*inch, 0.55*inch,"RAYMUNDO B. IBARRIENTOS,MD")
    p.setFont("Times-Italic", 8, leading=None)
    p.setFillColor('GRAY')# Amount
    p.drawString(6.5*inch, .45*inch, "Lic #0078995")
    p.setFillColor('BLACK')# Amount
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(6.5*inch, 0.3*inch, "Pathologist")


    p.line(0, 0.2*inch, 1000, 0.30*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Italic", 7, leading=None)
    p.drawString(0.1*inch, 0.1*inch, "BRGHGMC-F-AS-BIL-006")
    p.drawString(3*inch, 0.1*inch, "Rev 2")
    p.drawString(4.5*inch, 0.1*inch, "Effectivity Date: January 6, 2020")
    p.drawImage(padaba, 7*inch, 0.05*inch, mask='auto', width=80, height=10)
    p.setTitle("URINALYSIS - "+ ptxname)
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
