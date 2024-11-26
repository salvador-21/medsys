from typing import final
from django.shortcuts import render,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from datetime import date, datetime, timedelta
from django.template import loader
from django.template.loader import get_template, render_to_string
from django.conf import settings
from requests.api import head
from django.core.files import File
from fpdf import FPDF, HTMLMixin
import requests
import json
import ast
import re
import io
import xlwt
from requests.exceptions import ConnectionError
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm, inch
from reportlab.lib import colors
import os
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
import datetime,time
from django.utils import timezone
from django.utils.timezone import now
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
import base64
import imghdr
from django.core.files.base import ContentFile
from PIL import Image
import pytesseract
from django_xhtml2pdf.utils import generate_pdf
from django_xhtml2pdf.utils import pdf_decorator
from django.utils.timezone import localdate
from django.utils import dateparse




static_root = "http://173.10.7.2/medsys-static-files"
# live
root = "http://173.10.2.108:9092/"
# root = "http://172.22.10.11:9091/"

# static=173.10.7.2


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
get_age=root+"api/patients/age"
#CHEMISTRY API
save_chem=root+"api/laboratory/chemistryResult"
get_chem_result=root+"api/laboratory/getChemistryResult"

#HEMATHOLOGY
save_cbc_result=root+"api/laboratory/hemaResult"
get_cbc_result=root+"api/laboratory/getHemaResult"
#RAPID TEST
save_rapid_result=root+"api/laboratory/rapidResult"
get_rapid_result=root+"api/laboratory/getRapidResult"
#CHARGESLIP 

charge=root+"api/laboratory/charges"
get_charges=root+"api/laboratory/getPatientCharges"
releasing=root+"api/laboratory/releaseChargeSlip"
#orderid
get_released=root+"api/laboratory/getReleaseChargeSlip"

allkit=root+"api/laboratory/getkits"
getkit=root+"api/laboratory/getkit"
su_kit=root+"api/laboratory/kit"

# Immunology
su_immuno=root+"api/laboratory/immunoResult"
im_result=root+"api/laboratory/getImmunoResult"

# SEROLOGY
su_sero=root+"api/laboratory/serologyResult"
getsero_result=root+"api/laboratory/getSerologyResult"

#BACTERIOLOGY

su_microbio=root+"api/laboratory/bactiResult"
getbacti_result=root+"api/laboratory/getBactiResult"


#MACHINE_CHEM

machineAll=root+"api/laboratory/getAllMachineChem"

#machine_name,test_name,normal_values
su_machine=root+"api/laboratory/machineChem"




############################## REPORTS

def reports(request):

    return render(request,'integrated/laboratory/reports/index.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], })

@csrf_exempt
def load_request(request):
    rdata=[]

    request=requests.post(doctorsOrderPatient).json()
    for r in request['data']:
        get_test = requests.post(get_lab_request, data={'enccode':r['enccode'],'order_id':r['order_id']}).json()
        for p in get_test['details']:
            patient=p['patlast']+', '+p['patfirst']
            ward=p['wardname']
        for g in get_test['laboratory']:
            if g['status'] == 'RELEASED':
                dt1 = datetime.datetime.strptime(g['datemod'], "%Y-%m-%dT%H:%M:%S.%fZ")
                dt2 = datetime.datetime.strptime(g['dodate'], "%Y-%m-%dT%H:%M:%S.%fZ")
                dt1r=datetime.datetime.strftime(dt1, '%b %d, %y (%I:%M %p)')
                dt2r=datetime.datetime.strftime(dt2, '%b %d, %y (%I:%M %p)')
                interval = int(dt1.timestamp()) - int(dt2.timestamp())
                time_str = time.strftime("%H:%M", time.gmtime(interval))

                res={
                    'control_no':g['control_no'],
                    'received':dt2r,
                    'released':dt1r,
                    'interval':time_str,
                    'patient':patient,
                    'ward':ward,
                    'test':g['procdesc'],
                    'status':g['status']
                }
                rdata.append(res)
                # print(str(dt1r)+' - '+str(dt2r)+' - '+str(time_str))
         

    return JsonResponse({'data':rdata})

 
############################## HEMA MACHINE
@csrf_exempt
def hema_machine(request):
    machine_id=request.POST.get('machine_id')
    machine_name=request.POST.get('machine_name')
    test_name=request.POST.get('test_name')
    normal_values=request.POST.get('normal_values')
    modality=request.POST.get('machine_modality')
    
    if machine_id is None:
        addmachine=requests.post(su_machine,data={'machine_name':machine_name,'test_name':test_name,'normal_values':normal_values,'modality':modality}).json()
    else:
        addmachine=requests.post(su_machine,data={'machine_id':machine_id,'machine_name':machine_name,'test_name':test_name,'normal_values':normal_values,'modality':modality}).json()
    data=addmachine['status']
    return JsonResponse({'data':data})
############################## CHEM MACHINE
@csrf_exempt
def getAllMachine(request):
    machine=requests.post(machineAll).json()
    data=machine
    return JsonResponse({'data':data})

@csrf_exempt
def addMachine(request):
    machine_id=request.POST.get('machine_id')
    machine_name=request.POST.get('machine_name')
    test_name=request.POST.get('test_name')
    normal_values=request.POST.get('normal_values')
    modality=request.POST.get('machine_modality')
    if machine_id is None:
        addmachine=requests.post(su_machine,data={'machine_name':machine_name,'test_name':test_name,'normal_values':normal_values,'modality':modality}).json()
    else:
        addmachine=requests.post(su_machine,data={'machine_id':machine_id,'machine_name':machine_name,'test_name':test_name,'normal_values':normal_values,'modality':modality}).json()
    data=addmachine['status']
    return JsonResponse({'data':data})
############################## UPDATE CONTROL NUMBER

@csrf_exempt
def update_ctr(request):
    encc=request.POST.get('encc')
    orderid=request.POST.get('orderid')
    nctr=request.POST.get('nctr')
    try:
        update_ctr=requests.post(save_new_control_no,data={'enccode':encc,'order_id':orderid,'control_no':nctr}).json()
        data=update_ctr['status']
    except Exception as e:
        data=e

    return JsonResponse({'data':data})


############################### TO RELEASE RESULT
@csrf_exempt
def release_test(request):
    rtest=request.POST.getlist('test[]')
    sd=[]
    for t in rtest:
        clean_item = t.strip('[]')
        parts = clean_item.split('],[')
        record = {
        'prikey': parts[0],
        'encc': parts[1],
        'ordid': parts[2]
        }
        sd.append(record)
       
    for test in sd:
        get_test = requests.post(get_lab_request, data={'enccode':test['encc'],'order_id':test['ordid']}).json()
        for g in get_test['laboratory']:
            if g['prikey'] == test['prikey']:
                try:
                    recep_rel_res=requests.post(update_status, data={'key':test['prikey'], 'enccode': test['encc'],'order_id':test['ordid'],'receive':g['received_specimen'], 'status':'RELEASED','remarks':''}).json()
                    data=recep_rel_res['status']
                except Exception as e:
                    data=e


    return JsonResponse({'data':data})

############################### GET TO RELEASE TEST
def torealese_cnt(request):
    torel=[]
    micro=requests.post(getLab_modality,data={'modality':'MICRO','status':'COMPLETED'}).json()
    chemi=requests.post(getLab_modality,data={'modality':'CHEMI','status':'COMPLETED'}).json()
    hemat=requests.post(getLab_modality,data={'modality':'HEMAT','status':'COMPLETED'}).json()
    serol=requests.post(getLab_modality,data={'modality':'SEROL','status':'COMPLETED'}).json()
    bacti=requests.post(getLab_modality,data={'modality':'BACTI','status':'COMPLETED'}).json()
    immuno=requests.post(getLab_modality,data={'modality':'IMMUN','status':'COMPLETED'}).json()
    thyro=requests.post(getLab_modality,data={'modality':'THYRO','status':'COMPLETED'}).json()
    cardi=requests.post(getLab_modality,data={'modality':'CARDI','status':'COMPLETED'}).json()
    blgas=requests.post(getLab_modality,data={'modality':'BLGAS','status':'COMPLETED'}).json()
    tumor=requests.post(getLab_modality,data={'modality':'TUMOR','status':'COMPLETED'}).json()

    tmicro=[]
    for c in micro['data']:
        if c['toecode'] != 'OPD':
            tmicro.append(c['proccode'])

    tchemi=[]
    for c in chemi['data']:
        if c['toecode'] != 'OPD':
            tchemi.append(c['proccode'])

    themat=[]
    for c in hemat['data']:
        if c['toecode'] != 'OPD':
            themat.append(c['proccode'])
    
    tserol=[]
    for c in serol['data']:
        if c['toecode'] != 'OPD':
            tserol.append(c['proccode'])

    tbacti=[]
    for c in bacti['data']:
        if c['toecode'] != 'OPD':
            tbacti.append(c['proccode'])
    
    timmuno=[]
    for c in immuno['data']:
        if c['toecode'] != 'OPD':
            timmuno.append(c['proccode'])

    tthyro=[]
    for c in thyro['data']:
        if c['toecode'] != 'OPD':
            tthyro.append(c['proccode'])
    
    tcardi=[]
    for c in cardi['data']:
        if c['toecode'] != 'OPD':
            tcardi.append(c['proccode'])

    tblgas=[]
    for c in blgas['data']:
        if c['toecode'] != 'OPD':
            tblgas.append(c['proccode'])
    
    ttumor=[]
    for c in tumor['data']:
        if c['toecode'] != 'OPD':
            ttumor.append(c['proccode'])
   
    data=len(tmicro) + len(tchemi) + len(themat) + len(tserol) + len(tbacti) + len(timmuno) + len(tthyro) + len(tcardi) + len(tblgas) + len(ttumor)

    return JsonResponse({'data':data})

@csrf_exempt
def get_torelease(request):
    torel=[]
    ward=''
    get_micro=requests.post(getLab_modality,data={'modality':'MICRO','status':'COMPLETED'}).json()
    get_chemi=requests.post(getLab_modality,data={'modality':'CHEMI','status':'COMPLETED'}).json()
    get_hemat=requests.post(getLab_modality,data={'modality':'HEMAT','status':'COMPLETED'}).json()
    get_serol=requests.post(getLab_modality,data={'modality':'SEROL','status':'COMPLETED'}).json()
    get_bacti=requests.post(getLab_modality,data={'modality':'BACTI','status':'COMPLETED'}).json()
    get_immuno=requests.post(getLab_modality,data={'modality':'IMMUN','status':'COMPLETED'}).json()
    get_thyro=requests.post(getLab_modality,data={'modality':'THYRO','status':'COMPLETED'}).json()
    get_cardi=requests.post(getLab_modality,data={'modality':'CARDI','status':'COMPLETED'}).json()
    get_blgas=requests.post(getLab_modality,data={'modality':'BLGAS','status':'COMPLETED'}).json()
    get_tumor=requests.post(getLab_modality,data={'modality':'TUMOR','status':'COMPLETED'}).json()

  
    if len(get_chemi['data']) > 0:
       
        for c in get_chemi['data']:
            # print(c)
            c['dodate'] = datetime.datetime.strptime(c['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            c['dodate']=datetime.datetime.strftime(c['dodate'], '%b %d, %y (%I:%M %p)')
            cdata={
                'prikey':c['prikey'],
                'proccode':c['proccode'],
                'ctr':c['control_no'],
                'patient':c['patlast']+', '+c['patfirst'],
                'labtest':c['procdesc'],
                'ward':c['wardname'],
                'date':c['received_datetime'],
                'encc':c['enccode'],
                'orderid':c['lab_order_id'],
                'dodate':c['dodate'],
                'toecode':c['toecode']
                }
            torel.append(cdata)
    
    if len(get_micro['data']) > 0:
        for c in get_micro['data']:
            c['dodate'] = datetime.datetime.strptime(c['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            c['dodate']=datetime.datetime.strftime(c['dodate'], '%b %d, %y (%I:%M %p)')
            mdata={
                'prikey':c['prikey'],
                'proccode':c['proccode'],
                'ctr':c['control_no'],
                'patient':c['patlast']+', '+c['patfirst'],
                'labtest':c['procdesc'],
                'ward':c['wardname'],
                'date':c['received_datetime'],
                'encc':c['enccode'],
                'orderid':c['lab_order_id'],
                'dodate':c['dodate'],
                'toecode':c['toecode']
                }
            torel.append(mdata)

    if len(get_hemat['data']) > 0:
        for c in get_hemat['data']:
            c['dodate'] = datetime.datetime.strptime(c['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            c['dodate']=datetime.datetime.strftime(c['dodate'], '%b %d, %y (%I:%M %p)')
            hdata={
                'prikey':c['prikey'],
                'proccode':c['proccode'],
                'ctr':c['control_no'],
                'patient':c['patlast']+', '+c['patfirst'],
                'labtest':c['procdesc'],
                'ward':c['wardname'],
                'date':c['received_datetime'],
                'encc':c['enccode'],
                'orderid':c['lab_order_id'],
                'dodate':c['dodate'],
                'toecode':c['toecode']
                }
            torel.append(hdata)

    if len(get_serol['data']) > 0:
        for c in get_serol['data']:
            c['dodate'] = datetime.datetime.strptime(c['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            c['dodate']=datetime.datetime.strftime(c['dodate'], '%b %d, %y (%I:%M %p)')
            sdata={
                'prikey':c['prikey'],
                'proccode':c['proccode'],
                'ctr':c['control_no'],
                'patient':c['patlast']+', '+c['patfirst'],
                'labtest':c['procdesc'],
                'ward':c['wardname'],
                'date':c['received_datetime'],
                'encc':c['enccode'],
                'orderid':c['lab_order_id'],
                'dodate':c['dodate'],
                'toecode':c['toecode']
                }
            torel.append(sdata)

    if len(get_bacti['data']) > 0:
        for c in get_bacti['data']:
            c['dodate'] = datetime.datetime.strptime(c['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            c['dodate']=datetime.datetime.strftime(c['dodate'], '%b %d, %y (%I:%M %p)')
            bdata={
                'prikey':c['prikey'],
                'proccode':c['proccode'],
                'ctr':c['control_no'],
                'patient':c['patlast']+', '+c['patfirst'],
                'labtest':c['procdesc'],
                'ward':c['wardname'],
                'date':c['received_datetime'],
                'encc':c['enccode'],
                'orderid':c['lab_order_id'],
                'dodate':c['dodate'],
                'toecode':c['toecode']
                }
            torel.append(bdata)
    
    if len(get_immuno['data']) > 0:
        for c in get_immuno['data']:
            c['dodate'] = datetime.datetime.strptime(c['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            c['dodate']=datetime.datetime.strftime(c['dodate'], '%b %d, %y (%I:%M %p)')
            idata={
                'prikey':c['prikey'],
                'proccode':c['proccode'],
                'ctr':c['control_no'],
                'patient':c['patlast']+', '+c['patfirst'],
                'labtest':c['procdesc'],
                'ward':c['wardname'],
                'date':c['received_datetime'],
                'encc':c['enccode'],
                'orderid':c['lab_order_id'],
                'dodate':c['dodate'],
                'toecode':c['toecode']
                }
            torel.append(idata)

    if len(get_thyro['data']) > 0:
        for c in get_thyro['data']:
            c['dodate'] = datetime.datetime.strptime(c['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            c['dodate']=datetime.datetime.strftime(c['dodate'], '%b %d, %y (%I:%M %p)')
            tdata={
                'prikey':c['prikey'],
                'proccode':c['proccode'],
                'ctr':c['control_no'],
                'patient':c['patlast']+', '+c['patfirst'],
                'labtest':c['procdesc'],
                'ward':c['wardname'],
                'date':c['received_datetime'],
                'encc':c['enccode'],
                'orderid':c['lab_order_id'],
                'dodate':c['dodate'],
                'toecode':c['toecode']
                }
            torel.append(tdata)

    if len(get_cardi['data']) > 0:
        for c in get_cardi['data']:
            c['dodate'] = datetime.datetime.strptime(c['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            c['dodate']=datetime.datetime.strftime(c['dodate'], '%b %d, %y (%I:%M %p)')
            cdata={
                'prikey':c['prikey'],
                'proccode':c['proccode'],
                'ctr':c['control_no'],
                'patient':c['patlast']+', '+c['patfirst'],
                'labtest':c['procdesc'],
                'ward':c['wardname'],
                'date':c['received_datetime'],
                'encc':c['enccode'],
                'orderid':c['lab_order_id'],
                'dodate':c['dodate'],
                'toecode':c['toecode']
                }
            torel.append(cdata)

    if len(get_blgas['data']) > 0:
        for c in get_blgas['data']:
            c['dodate'] = datetime.datetime.strptime(c['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            c['dodate']=datetime.datetime.strftime(c['dodate'], '%b %d, %y (%I:%M %p)')
            bdata={
                'prikey':c['prikey'],
                'proccode':c['proccode'],
                'ctr':c['control_no'],
                'patient':c['patlast']+', '+c['patfirst'],
                'labtest':c['procdesc'],
                'ward':c['wardname'],
                'date':c['received_datetime'],
                'encc':c['enccode'],
                'orderid':c['lab_order_id'],
                'dodate':c['dodate'],
                'toecode':c['toecode']
                }
            torel.append(bdata)

    if len(get_tumor['data']) > 0:
        for c in get_tumor['data']:
            c['dodate'] = datetime.datetime.strptime(c['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            c['dodate']=datetime.datetime.strftime(c['dodate'], '%b %d, %y (%I:%M %p)')
            tdata={
                'prikey':c['prikey'],
                'proccode':c['proccode'],
                'ctr':c['control_no'],
                'patient':c['patlast']+', '+c['patfirst'],
                'labtest':c['procdesc'],
                'ward':c['wardname'],
                'date':c['received_datetime'],
                'encc':c['enccode'],
                'orderid':c['lab_order_id'],
                'dodate':c['dodate'],
                'toecode':c['toecode']
                }
            torel.append(tdata)

    
    return JsonResponse({'data':torel})

#################################### BACTERIOLOGY

def bacteriology_result(request,ward,physician,orderid,encc):
    
    get_examination = requests.post(get_lab_request, data={'enccode': encc,'order_id':orderid}).json()
    ptx=get_examination['details']
    bacti_res=requests.post(getbacti_result, data={'order_id': orderid}).json()
  
    # for i in sero_res['data']:
    #         i['verify_date'] = datetime.datetime.strptime(i['verify_date'],"%Y-%m-%dT%H:%M:%S.%fZ")
    #         i['verify_date']=datetime.datetime.strftime(i['verify_date'], '%b %d, %Y (%I:%M %p)')
    return render(request,'integrated/laboratory/result_form/bacteriology.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name'],'test':bacti_res['data'][0],'ptx':ptx[0],'ward':ward,'doctor':physician})

@csrf_exempt
def get_bactiResult(request):
    orderid=request.POST.get('orderid')
    bacti_res=requests.post(getbacti_result, data={'order_id': orderid}).json()
    return JsonResponse({'data':bacti_res['data']})


@csrf_exempt
def get_bactiview(request):
    encc=request.POST.get('encc')
    orderid=request.POST.get('orderid')
    procode=request.POST.get('procode')
    rtype=request.POST.get('rtype')
    gdata=[]
    try:
        get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
        for s in get_test['laboratory']:
            if s['modality'] == 'BACTI' and s['proccode'] != 'LABOR0051':
                # print(s['proccode']+'-'+s['procdesc'])
                if s['status'] == rtype:
                    gdata.append(s)
                    data = gdata
    except Exception as e:
        data='potaka'
    
    return JsonResponse({'data':data})


@csrf_exempt
def load_biology(request):
    stat=request.POST.get('type')
    get_sero=requests.post(getLab_modality,data={'modality':'BACTI','status':stat}).json()
    hdata=[]
    cc=0
    for i in get_sero['data']:
        if i['proccode'] != 'LABOR0051':
            cc=cc + 1
            i['enccode'] = i['enccode'].replace("/", "-")
            i['received_datetime'] = datetime.datetime.strptime(i['received_datetime'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['received_datetime']=datetime.datetime.strftime(i['received_datetime'], '%b %d, %y (%I:%M %p)')
            i['birthdate'] = datetime.datetime.strptime(i['birthdate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['birthdate']=datetime.datetime.strftime(i['birthdate'], '%b %d, %Y')
            # age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
            # i['uomcode']=age['data']
            hdata.append(i)
    return JsonResponse({'data':hdata})

@csrf_exempt
def bio_sentToProcess(request):
    modality=request.POST.get('modality')
    encc=request.POST.get('encc')
    ord=request.POST.get('orderid')
    key=request.POST.get('key')
    procode=request.POST.get('procode')
    # samplemodality=requests.post(update_status, data={'key':key, 'enccode': encc,'order_id':ord, 'status':'ONPROCESS'}).json()
    # data=samplemodality['status']
    data=procode
    if procode == 'LABOR00343' or procode == 'LABOR00338':
        get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':ord}).json()
        for g in get_test['laboratory']:
            if g['proccode'] == 'LABOR00343' or g['proccode'] == 'LABOR00338':
                samplemodality=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':ord, 'status':'ONPROCESS','receive':g['received_specimen']}).json()
                data=samplemodality['status']
                 
    else:
        samplemodality=requests.post(update_status, data={'key':key, 'enccode': encc,'order_id':ord, 'status':'ONPROCESS'}).json()
        data=samplemodality['status']
    # if procode == 'LABOR00343' or procode == 'LABOR00338':
    #     get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':ord}).json()
    #     for g in get_test['laboratory']:
    #         if g['proccode '] == 'LABOR00343' or g['proccode'] == 'LABOR00338':
    #                 try:
    #                     samplemodality=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':ord, 'status':'ONPROCESS','receive':g['received_specimen']}).json()
    #                     data=samplemodality['status']
    #                 except Exception as e:
    #                     data=e
    #                 print(data)
    # else:
    #     samplemodality=requests.post(update_status, data={'key':key, 'enccode': encc,'order_id':ord, 'status':'ONPROCESS'}).json()
    #     data=samplemodality['status']
    #     print(data)
   
    return JsonResponse({'data':data}) 

@csrf_exempt
def bacte_check_res(request):
    orderid=request.POST.get('orderid')
    bacti_res=requests.post(getbacti_result, data={'order_id': orderid}).json()
    return JsonResponse({'data':bacti_res['data']})


@csrf_exempt
def save_bio(request):
    action=request.POST.get('action')
    encc=request.POST.get('i_encc')
    orderid=request.POST.get('i_orderid')
    hosno=request.POST.get('i_hpercode')
    key=request.POST.get('i_key')
    ctr=request.POST.get('i_ctr')
    procode=request.POST.get('procode')
    # bacti_res=requests.post(getbacti_result, data={'order_id': orderid}).json()
    # for b in bacti_res['data']:
    #     print(b['salmogen_igg'])



    if action == 'insert':

        try:
            s_biology=requests.post(su_microbio,data={
            'enccode':request.POST.get('i_encc'),
            'order_id':request.POST.get('i_orderid'),
            'control_no':request.POST.get('i_ctr'),
            'salmogen_igg':request.POST.get('sal_igg'),
            'salmogen_igm':request.POST.get('sal_igm'),
            'dengue_igg':request.POST.get('dt_igg'),
            'dengue_igm':request.POST.get('dt_igm'),
            'dengue_ns1':request.POST.get('dt_ns1'),
            'malaria_pf':request.POST.get('mal_pf'),
            'malaria_pan':request.POST.get('mal_pan'),
            'gram_ep':request.POST.get('gram_ep'),
            'gram_negative':request.POST.get('gram_neg'),
            'gram_positive':request.POST.get('gram_pos'),
            'koh':request.POST.get('koh'),
            'acid_fast':request.POST.get('acid_fast'),
            'skin_slit':request.POST.get('slit_skin'),
            'bi':request.POST.get('bi'),
            'perform_by':request.session['employee_id'],
            'perform_date':datetime.datetime.strftime(datetime.datetime.now(), "%Y/%m/%d"),
            }).json()
            if s_biology['status'] == 'success':
                get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
                for g in get_test['laboratory']:
                    if g['modality'] == 'BACTI' and g['proccode'] != 'LABOR0051' and g['status'] == 'ONPROCESS':
                        if procode == 'LABOR00338' or procode == 'LABOR00343':
                            try:
                                samplemodality=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':orderid, 'status':'TOVERIFY','receive':g['received_specimen']}).json()
                                data=samplemodality['status']
                            except Exception as e:
                                data=e
                        else:
                            samplemodality=requests.post(update_status, data={'key':key, 'enccode': encc,'order_id':orderid, 'status':'TOVERIFY','receive':g['received_specimen']}).json()
                            data=samplemodality['status']

            else:
                data='error add Result'
        except Exception as e:
            data='failed'
    elif action == 'verify':
        # get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
        # for g in get_test['laboratory']:
        #     try:
        #         samplemodality=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':orderid, 'status':'PENDING','receive':g['received_specimen']}).json()
        #         data=samplemodality['status']
        #     except Exception as e:
        #         data=e
                   
        try:
            v_biology=requests.post(su_microbio,data={
            'enccode':request.POST.get('i_encc'),
            'order_id':request.POST.get('i_orderid'),
            'control_no':request.POST.get('i_ctr'),
            'salmogen_igg':request.POST.get('sal_igg'),
            'salmogen_igm':request.POST.get('sal_igm'),
            'dengue_igg':request.POST.get('dt_igg'),
            'dengue_igm':request.POST.get('dt_igm'),
            'dengue_ns1':request.POST.get('dt_ns1'),
            'malaria_pf':request.POST.get('mal_pf'),
            'malaria_pan':request.POST.get('mal_pan'),
            'gram_ep':request.POST.get('gram_ep'),
            'gram_negative':request.POST.get('gram_neg'),
            'gram_positive':request.POST.get('gram_pos'),
            'koh':request.POST.get('koh'),
            'acid_fast':request.POST.get('acid_fast'),
            'skin_slit':request.POST.get('slit_skin'),
            'bi':request.POST.get('bi'),
            'verified_by':request.session['employee_id'],
            'verify_date':datetime.datetime.strftime(datetime.datetime.now(), "%Y/%m/%d"),
            }).json()
            if v_biology['status'] == 'success':
                get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
                for g in get_test['laboratory']:
                    if g['modality'] == 'BACTI' and g['proccode'] != 'LABOR0051' and g['status'] == 'TOVERIFY':
                        if procode == 'LABOR00338' or procode == 'LABOR00343':
                            try:
                                samplemodality=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':orderid, 'status':'COMPLETED','receive':g['received_specimen']}).json()
                                data=samplemodality['status']
                            except Exception as e:
                                data=e
                        else:
                            samplemodality=requests.post(update_status, data={'key':key, 'enccode': encc,'order_id':orderid, 'status':'COMPLETED','receive':g['received_specimen']}).json()
                            data=samplemodality['status']
            else:
                data='error add Result'
        except Exception as e:
            data='failed'


    return JsonResponse({'data':data})

def lab_microbiology(request):

    return render(request,'integrated/laboratory/microbiology/index.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})
#################################### KIT
def lab_kit(request):

    return render(request,'integrated/laboratory/kit/index.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})

@csrf_exempt
def load_kit(request):
    kits=requests.post(allkit).json()
    return JsonResponse({'data':kits['data']})

#################################### BACTERIOLOGY

def bacte_result(request):

    return render(request,'integrated/laboratory/result_form/bacteriology.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})


##################################### SEROLOGY
@csrf_exempt
def load_sero(request):
    stat=request.POST.get('type')

    # pending=requests.post(getLab_modality,data={'modality':'SEROL','status':'PENDING'}).json()
    # onprocess=requests.post(getLab_modality,data={'modality':'SEROL','status':'ONPROCESS'}).json()
    # toverify=requests.post(getLab_modality,data={'modality':'SEROL','status':'TOVERIFY'}).json()
    # completed=requests.post(getLab_modality,data={'modality':'SEROL','status':'COMPLETED'}).json()
    # released=requests.post(getLab_modality,data={'modality':'SEROL','status':'RELEASED'}).json()

    # count={
    #     'pending':len(pending['data']),
    #     'onprocess':len(onprocess['data']),
    #     'toverify':len(toverify['data']),
    #     'completed':len(completed['data']),
    #     'released':len(released['data']),
    # }
    count=[]
    get_sero=requests.post(getLab_modality,data={'modality':'SEROL','status':stat}).json()
    hdata=[]
    test=0
    cc=0
    encc=''
    ntest=0
    for i in get_sero['data']:
        
        i['procdesc']=ntest
        if encc != i['enccode']:
            encc=i['enccode']
            cc=cc + 1
            test=1
            i['procdesc']=test
            i['enccode'] = i['enccode'].replace("/", "-")
            i['dodate'] = datetime.datetime.strptime(i['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['dodate']=datetime.datetime.strftime(i['dodate'], '%b %d, %Y (%I:%M %p)')

            i['received_datetime'] = datetime.datetime.strptime(i['received_datetime'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['received_datetime']=datetime.datetime.strftime(i['received_datetime'], '%b %d, %Y (%I:%M %p)')

            i['birthdate'] = datetime.datetime.strptime(i['birthdate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['birthdate']=datetime.datetime.strftime(i['birthdate'], '%b %d, %Y')

            # age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
            # i['uomcode']=age['data']
            hdata.append(i)
        else:
            test=test + 1            
    
    return JsonResponse({'data':hdata,'count':count})

@csrf_exempt
def get_seroview(request):
    encc=request.POST.get('encc')
    orderid=request.POST.get('orderid')
    gdata=[]
    try:
        get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
        for s in get_test['laboratory']:
            if s['modality'] == 'SEROL':
                gdata.append(s)
                data = gdata
    except Exception as e:
        data='potaka'
    return JsonResponse({'data':data})


@csrf_exempt
def sero_sentToProcess(request):
    encc=request.POST.get('encc')
    ord=request.POST.get('orderid')
    get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':ord}).json()
    for g in get_test['laboratory']:
        if g['modality'] == 'SEROL':
            try:
                samplemodality=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':ord, 'status':'ONPROCESS','receive':g['received_specimen']}).json()
                data=samplemodality['status']
            except Exception as e:
                data=e
        else:
            data=''
    return JsonResponse({'data':data}) 

def sero_result(request):

    return render(request,'integrated/laboratory/result_form/serology.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})

def lab_serology(request):
    try:
        serokit=requests.post(allkit).json()
        kits=[]
        for s in serokit['data']:
            if s['modality'] == 'SEROLOGY':
                s['expiry_date'] = datetime.datetime.strptime(s['expiry_date'],"%Y-%m-%dT%H:%M:%S.%fZ")
                s['expiry_date']=datetime.datetime.strftime(s['expiry_date'], '%Y-%m-%d')
                kits.append(s)
    except Exception as e:
        kits=''
    # print(kits)
    return render(request, 'integrated/laboratory/serology/index.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name'],'kit':kits})


@csrf_exempt
def save_sero(request):
    action=request.POST.get('action')
    encc=request.POST.get('i_encc')
    orderid=request.POST.get('i_orderid')
    hosno=request.POST.get('i_hpercode')
    key=request.POST.get('i_key')
    ctr=request.POST.get('i_ctr')

    if action == 'insert':
    # data=s_exp
        try:
            s_sero=requests.post(su_sero,data={
                'enccode':encc,
                'order_id':orderid,
                'control_no':ctr,
                'hbsag':request.POST.get('hbsag'),
                'hbsag_kit':request.POST.get('hbsag_kit'),
                'hbsag_lot':request.POST.get('hbsag_lotno'),
                'hbsag_exp':request.POST.get('hbsag_expiry'),
                'syph':request.POST.get('syp'),
                'syph_kit':request.POST.get('syp_kit'),
                'syph_lot':request.POST.get('syp_lotno'),
                'syph_exp':request.POST.get('syp_expiry'),
                'hav_igm':request.POST.get('hav_igm'),
                'hav_igm_kit':request.POST.get('hav_kit'),
                'hav_igm_lot':request.POST.get('hav_lotno'),
                'hav_igm_exp':request.POST.get('hav_expiry'),

                'hav_igg':request.POST.get('hav_igg'),
                'hav_igg_kit':request.POST.get('hav_kit'),
                'hav_igg_lot':request.POST.get('hav_lotno'),
                'hav_igg_exp':request.POST.get('hav_expiry'),

                'hbhs':request.POST.get('hbs'),
                'hbhs_kit':request.POST.get('hbs_kit'),
                'hbhs_lot':request.POST.get('hbs_lotno'),
                'hbhs_exp':request.POST.get('hbs_expiry'),

                'hcv':request.POST.get('hcv'),
                'hcv_kit':request.POST.get('hcv_kit'),
                'hcv_lot':request.POST.get('hcv_lotno'),
                'hcv_exp':request.POST.get('hcv_expiry'),
                'perform_by':request.session['employee_id'],
                'perform_date': datetime.datetime.strftime(datetime.datetime.now(), "%Y/%m/%d"),
                'verified_by':'',
                'verify_date':datetime.datetime.strftime(datetime.datetime.now(), "%Y/%m/%d")
            }).json()
            if s_sero['status'] == 'success':
                get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
                for g in get_test['laboratory']:
                    if g['modality'] == 'SEROL':
                        try:
                            samplemodality=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':orderid, 'status':'TOVERIFY','receive':g['received_specimen']}).json()
                            data=samplemodality['status']
                        except Exception as e:
                            print(e)
                            data='Failed Add Status'
                    else:
                        data='potaka'
            else:
                print(s_sero)
                data=s_sero

        except Exception as e:
            print(e)
            data=e
                

    elif action == 'verify':
        v_sero=requests.post(su_sero,data={
            'enccode':encc,
            'order_id':orderid,
            'control_no':ctr,
            'hbsag':request.POST.get('hbsag'),
            'hbsag_kit':request.POST.get('hbsag_kit'),
            'hbsag_lot':request.POST.get('hbsag_lotno'),
            'hbsag_exp':request.POST.get('hbsag_expiry'),
            'syph':request.POST.get('syp'),
            'syph_kit':request.POST.get('syp_kit'),
            'syph_lot':request.POST.get('syp_lotno'),
            'syph_exp':request.POST.get('syp_expiry'),
            'hav_igm':request.POST.get('hav_igm'),
            'hav_igm_kit':request.POST.get('hav_kit'),
            'hav_igm_lot':request.POST.get('hav_lotno'),
            'hav_igm_exp':request.POST.get('hav_expiry'),

            'hav_igg':request.POST.get('hav_igg'),
            'hav_igg_kit':request.POST.get('hav_kit'),
            'hav_igg_lot':request.POST.get('hav_lotno'),
            'hav_igg_exp':request.POST.get('hav_expiry'),

            'hbhs':request.POST.get('hbs'),
            'hbhs_kit':request.POST.get('hbs_kit'),
            'hbhs_lot':request.POST.get('hbs_lotno'),
            'hbhs_exp':request.POST.get('hbs_expiry'),

            'hcv':request.POST.get('hcv'),
            'hcv_kit':request.POST.get('hcv_kit'),
            'hcv_lot':request.POST.get('hcv_lotno'),
            'hcv_exp':request.POST.get('hcv_expiry'),
            'verified_by':request.session['employee_id'],
            'verify_date': datetime.datetime.strftime(datetime.datetime.now(), "%Y/%m/%d"),
        }).json()
        if v_sero['status'] == 'success':
            get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
            for g in get_test['laboratory']:
                if g['modality'] == 'SEROL':
                    try:
                        samplemodality=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':orderid, 'status':'COMPLETED','receive':g['received_specimen']}).json()
                        data=samplemodality['status']
                    except Exception as e:
                        data='Failed Verify Status'
                
                    

    
    return JsonResponse({'data':data}) 

@csrf_exempt
def get_seroResult(request):
    orderid=request.POST.get('orderid')
    sero_res=requests.post(getsero_result, data={'order_id': orderid}).json()
    

    return JsonResponse({'data':sero_res['data']})

def serology_result(request,ward,physician,orderid,encc):
    
    get_examination = requests.post(get_lab_request, data={'enccode': encc,'order_id':orderid}).json()
    ptx=get_examination['details']
    sero_res=requests.post(getsero_result, data={'order_id': orderid}).json()
    # print(sero_res)
    return render(request,'integrated/laboratory/result_form/serology.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name'],'test':sero_res['data'][0],'ptx':ptx[0],'ward':ward,'doctor':physician})


##################################### IMMUNOLOGY

@csrf_exempt
def immuno_ToProcess(request):
    encc=request.POST.get('encc')
    ord=request.POST.get('orderid')
    try:
        get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':ord}).json()
        for g in get_test['laboratory']:
            if g['status'] == 'PENDING':
                if g['modality'] == 'IMMUN' or g['modality'] == 'THYRO' or g['modality'] == 'CARDI' or g['modality'] == 'BLGAS' or g['modality'] == 'TUMOR':
                    try:
                        samplemodality=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':ord, 'status':'ONPROCESS','receive':g['received_specimen']}).json()
                        data=samplemodality['status']
                    except Exception as e:
                        data=e
            
    except Exception as e:
        data=e
    return JsonResponse({'data':data}) 


@csrf_exempt
def get_immunview(request):
    encc=request.POST.get('encc')
    orderid=request.POST.get('orderid')
    rtype=request.POST.get('rtype')
    n_values=[]
    gdata=[]
    print(encc)
    machine=requests.post(machineAll).json()
    for m in machine['data']:
        if m['modality'] == 'IMMUN':
            n_values.append(m)

    try:
        get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
        for s in get_test['laboratory']:
            if s['status'] == rtype:
                if s['modality'] == 'IMMUN' or s['modality'] == 'THYRO' or s['modality'] == 'CARDI' or s['modality'] == 'BLGAS' or s['modality'] == 'TUMOR':
                    gdata.append(s)
                    # print(s['proccode']+' - '+s['modality']+' - '+s['procdesc'])
                    data = gdata
    except Exception as e:
        data=e
    return JsonResponse({'data':data,'n_values':n_values})


def lab_immuno(request):

    return render(request,'integrated/laboratory/immuno/index.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})

@csrf_exempt
def get_immunores(request):
    encc=request.POST.get('encc')
    orderid=request.POST.get('orderid')
    rtype=request.POST.get('rtype')
    imres=[]
    n_values=[]
    immuno_res=requests.post(im_result, data={'order_id': orderid}).json()
    machine=requests.post(machineAll).json()
    for m in machine['data']:
        if m['modality'] == 'IMMUN':
            n_values.append(m)
    get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
    for s in get_test['laboratory']:
            if s['status'] == rtype:
                if s['modality'] == 'IMMUN' or s['modality'] == 'THYRO' or s['modality'] == 'CARDI' or s['modality'] == 'BLGAS' or s['modality'] == 'TUMOR':
                    imres.append(s)

    return JsonResponse({'data':imres,'n_values':n_values,'result':immuno_res['data']})

@csrf_exempt
def load_immuno(request):
    stat=request.POST.get('type')
    
    get_immun=requests.post(getLab_modality,data={'modality':'IMMUN','status':stat}).json()
    get_thyro=requests.post(getLab_modality,data={'modality':'THYRO','status':stat}).json()
    get_cardi=requests.post(getLab_modality,data={'modality':'CARDI','status':stat}).json()
    get_tumor=requests.post(getLab_modality,data={'modality':'TUMOR','status':stat}).json()
    # get_blgas=requests.post(getLab_modality,data={'modality':'TUMOR','status':stat}).json()
    hdata=[]
    display=[]
    test=0
    cc=0
    encc=''
    ctr=''
    ntest=0
    # print(get_immun['data'])
  
    for i in get_immun['data']:
        i['procdesc']=ntest
        if encc != i['enccode']:
            encc=i['enccode']
            cc=cc + 1
            test=1
            i['procdesc']=test
            i['enccode'] = i['enccode'].replace("/", "-")
            i['birthdate'] = datetime.datetime.strptime(i['birthdate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['birthdate']=datetime.datetime.strftime(i['birthdate'], '%b %d, %Y')
            i['received_datetime'] = datetime.datetime.strptime(i['received_datetime'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['received_datetime']=datetime.datetime.strftime(i['received_datetime'], '%b %d, %Y (%I:%M %p)')

            i['dodate'] = datetime.datetime.strptime(i['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['dodate']=datetime.datetime.strftime(i['dodate'], '%b %d, %Y (%I:%M %p)')

            # age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
            # i['uomcode']=age['data']
            hdata.append(i)
        else:
            test=test + 1  

    for i in get_thyro['data']:
        i['procdesc']=ntest
        if encc != i['enccode']:
            encc=i['enccode']
            cc=cc + 1
            test=1
            i['procdesc']=test
            i['enccode'] = i['enccode'].replace("/", "-")
            i['birthdate'] = datetime.datetime.strptime(i['birthdate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['birthdate']=datetime.datetime.strftime(i['birthdate'], '%b %d, %Y')

            i['received_datetime'] = datetime.datetime.strptime(i['received_datetime'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['received_datetime']=datetime.datetime.strftime(i['received_datetime'], '%b %d, %Y (%I:%M %p)')

            # age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
            # i['uomcode']=age['data']
            hdata.append(i)
        else:
            test=test + 1 
    for i in get_cardi['data']:
        i['procdesc']=ntest
        if encc != i['enccode']:
            encc=i['enccode']
            cc=cc + 1
            test=1
            i['procdesc']=test
            i['enccode'] = i['enccode'].replace("/", "-")
            i['birthdate'] = datetime.datetime.strptime(i['birthdate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['birthdate']=datetime.datetime.strftime(i['birthdate'], '%b %d, %Y')

            i['received_datetime'] = datetime.datetime.strptime(i['received_datetime'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['received_datetime']=datetime.datetime.strftime(i['received_datetime'], '%b %d, %Y (%I:%M %p)')

            # age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
            # i['uomcode']=age['data']
            hdata.append(i)
        else:
            test=test + 1 
    for i in get_tumor['data']:
        i['procdesc']=ntest
        if encc != i['enccode']:
            encc=i['enccode']
            cc=cc + 1
            test=1
            i['procdesc']=test
            i['enccode'] = i['enccode'].replace("/", "-")
            i['birthdate'] = datetime.datetime.strptime(i['birthdate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['birthdate']=datetime.datetime.strftime(i['birthdate'], '%b %d, %Y')

            i['received_datetime'] = datetime.datetime.strptime(i['received_datetime'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['received_datetime']=datetime.datetime.strftime(i['received_datetime'], '%b %d, %Y (%I:%M %p)')

            # age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
            # i['uomcode']=age['data']
            hdata.append(i)
        else:
            test=test + 1 

    # for i in get_blgas['data']:
    #     i['procdesc']=ntest
    #     if encc != i['enccode']:
    #         encc=i['enccode']
    #         cc=cc + 1
    #         test=1
    #         i['procdesc']=test
    #         i['enccode'] = i['enccode'].replace("/", "-")
    #         i['dodate'] = datetime.datetime.strptime(i['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
    #         i['dodate']=datetime.datetime.strftime(i['dodate'], '%b %d, %Y (%I:%M %p)')

    #         i['received_datetime'] = datetime.datetime.strptime(i['received_datetime'],"%Y-%m-%dT%H:%M:%S.%fZ")
    #         i['received_datetime']=datetime.datetime.strftime(i['received_datetime'], '%b %d, %Y (%I:%M %p)')

    #         # age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
    #         # i['uomcode']=age['data']
    #         hdata.append(i)
    #     else:
    #         test=test + 1 
    
    # for d in hdata:
    #     ctr=d['control_no']
    #     if ctr != d['control_no']:
    #         display.append(d)


        
    return JsonResponse({'data':hdata})

@csrf_exempt
def immuno_sentToProcess(request):
    modality=request.POST.get('modality')
    encc=request.POST.get('encc')
    ord=request.POST.get('orderid')
    key=request.POST.get('key')
    get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':ord}).json()
    for g in get_test['laboratory']:
        if g['prikey'] == key:
            try:
                samplemodality=requests.post(update_status, data={'key':key, 'enccode': encc,'order_id':ord, 'status':'ONPROCESS','receive':g['received_specimen']}).json()
                data=samplemodality['status']
            except Exception as e:
                data=e
        else:
            data=''
    return JsonResponse({'data':data}) 


@csrf_exempt
def save_immuno(request):
    action=request.POST.get('action')
    encc=request.POST.get('i_encc')
    orderid=request.POST.get('i_orderid')
    hosno=request.POST.get('i_hpercode')
    key=request.POST.get('i_key')

    

    rheu=str(request.POST.get('rheu'))+','+str(request.POST.get('rheu_nv'))
    aso=str(request.POST.get('aso'))+','+str(request.POST.get('aso_nv'))
    crp=str(request.POST.get('crp'))+','+str(request.POST.get('crp_nv'))
    procal=str(request.POST.get('procal'))+','+str(request.POST.get('procal_nv'))
    tropinin=str(request.POST.get('tropinin'))+','+str(request.POST.get('tropinin_nv'))
    ckmb=str(request.POST.get('ckmb'))+','+str(request.POST.get('ckmb_nv'))
    probnp=str(request.POST.get('probnp'))+','+str(request.POST.get('probnp_nv'))
    psa=str(request.POST.get('psa'))+','+str(request.POST.get('psa_nv'))
    cea=str(request.POST.get('cea'))+','+str(request.POST.get('cea_nv'))
    ca125=str(request.POST.get('ca125'))+','+str(request.POST.get('ca125_nv'))
    tsh=str(request.POST.get('tsh'))+','+str(request.POST.get('tsh_nv'))
    t3=str(request.POST.get('t3'))+','+str(request.POST.get('t3_nv'))
    t4=str(request.POST.get('t4'))+','+str(request.POST.get('t4_nv'))
    ft3=str(request.POST.get('ft3'))+','+str(request.POST.get('ft3_nv'))
    ft4=str(request.POST.get('ft4'))+','+str(request.POST.get('ft4_nv'))

    ana=str(request.POST.get('ana'))+','+str(request.POST.get('ana_nv'))
    ca19=str(request.POST.get('ca19'))+','+str(request.POST.get('ca19_nv'))


    # print(action)
    # print(encc)
    # print(orderid)
    # print(hosno)
    # print(request.POST.get('i_ctr'))
    

    if action == 'insert':
        try:
            a_immuno=requests.post(su_immuno,data={
                'enccode':encc,
                'order_id':orderid,
                'hpercode':hosno,
                'date': datetime.datetime.now().date(),
                'control_no': request.POST.get('i_ctr'),
                'kit_name':'kit',
                'troponin_i':tropinin,
                'ck_mb':ckmb,
                'tsh':tsh,
                'ca_125':ca125,
                'ft4':ft4,
                'ft3':ft3,
                't4':t4,
                't3':t3,
                'aso':aso,
                'crp':crp,
                'hscrp':'',
                'procalcitonin':procal,
                'reheu':rheu,
                'psa':psa,
                'pro_bnp':probnp,
                'cea':cea,
                'ana':ana,
                'ca_19_9':ca19,
                'note':request.POST.get('notes'),
                'perform_by':request.session['employee_id'],
            }).json()
            if a_immuno['status'] == 'success':
            
                try:
                    get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
                    for g in get_test['laboratory']:
                        if g['modality'] == 'IMMUN' or g['modality'] == 'THYRO' or g['modality'] == 'CARDI' or g['modality'] == 'BLGAS' or g['modality'] == 'TUMOR':
                            try:
                                samplemodality=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':orderid, 'status':'TOVERIFY','receive':g['received_specimen']}).json()
                                data=samplemodality['status']
                            except Exception as e:
                                data='failed update'

                        
                except Exception as e:
                    data=e
            else:
                data=a_immuno
        except Exception as e:
            data=e
    elif action == 'verify':

        try:
            u_immuno=requests.post(su_immuno,data={
            'enccode':encc,
            'order_id':orderid,
            'hpercode':hosno,
            'date': datetime.datetime.now().date(),
            'control_no': request.POST.get('i_ctr'),
            'kit_name':'kit',
            'troponin_i':tropinin,
            'ck_mb':ckmb,
            'tsh':tsh,
            'ca_125':ca125,
            'ft4':ft4,
            'ft3':ft3,
            't4':t4,
            't3':t3,
            'aso':aso,
            'crp':crp,
            'hscrp':'',
            'procalcitonin':procal,
            'reheu':rheu,
            'psa':psa,
            'pro_bnp':probnp,
            'cea':cea,
            'ana':ana,
            'ca_19_9':ca19,
            'note':request.POST.get('notes'),
            # 'perform_by':request.POST.get('perform_id'),
            'verified_by':request.session['employee_id'],
            }).json()
      
            if u_immuno['status'] == 'success':
                try:
                    get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
                
                    for g in get_test['laboratory']:
                        if g['modality'] == 'IMMUN' or g['modality'] == 'THYRO' or g['modality'] == 'CARDI' or g['modality'] == 'BLGAS' or g['modality'] == 'TUMOR':
                            try:
                                samplemodality=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':orderid, 'status':'COMPLETED','receive':g['received_specimen']}).json()
                                data=samplemodality['status']
                            except Exception as e:
                                data=e
                        
                except Exception as e:
                    print(e)    
                    data=e
            else:
                print(u_immuno)
                data='Error Verifying!'
        except Exception as e:
            print(e)

    return JsonResponse({'data':data})

@csrf_exempt
def get_immunoResult(request):
    orderid=request.POST.get('orderid')
    immuno_res=requests.post(im_result, data={'order_id': orderid}).json()
    n_values=requests.post(machineAll).json()


    return JsonResponse({'data':immuno_res['data'],'n_values':n_values['data']})

@csrf_exempt
def immuno_result(request,ward,physician,orderid,encc):
    # i_res=requests.post(immuno_result, data={'enccode': encc}).json()
    get_examination = requests.post(get_lab_request, data={'enccode': encc,'order_id':orderid}).json()
    ptx=get_examination['details']
    getres=requests.post(im_result,data={'order_id':orderid}).json()
    
    for i in getres['data']:
            i['date_verified'] = datetime.datetime.strptime(i['date_verified'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['date_verified']=datetime.datetime.strftime(i['date_verified'], '%b %d, %Y (%I:%M %p)')

            if i['tropinin_i'] == ',':
                trop=''
                trop_nv='--------------'
            else:
                trop_s=i['tropinin_i'].split(',')
                trop=trop_s[0]
                trop_nv=str(trop_s[1]+' - '+trop_s[2])
                

            if i['ck_mb'] == ',':
                ckmb=''
                ckmb_nv='--------------'
            else:
                ckmb_s=i['ck_mb'].split(',')
                ckmb=ckmb_s[0]
                ckmb_nv=str(ckmb_s[1]+' - '+ckmb_s[2])

            if i['tsh'] == ',':
                tsh=''
                tsh_nv='--------------'
     
            else:
                tsh_s=i['tsh'].split(',')
                tsh=tsh_s[0]
                tsh_nv=str(tsh_s[1]+' - '+tsh_s[2])
                
            
            if i['ft4'] == ',':
                ft4=''
                ft4_nv='--------------'

            else:
                ft4_s=i['ft4'].split(',')
                ft4=ft4_s[0]
                try:
                    ft4_nv=str(ft4_s[1]+' - '+ft4_s[2])
                except Exception as e:
                    ft4_nv=str(ft4_s[1])
            if i['ft3'] == ',':
                ft3=''
                ft3_nv='--------------'

            else:
                ft3_s=i['ft3'].split(',')
                ft3=ft3_s[0]
                ft3_nv=str(ft3_s[1]+' - '+ft3_s[2])
  

            if i['t4'] == ',':
                t4=''
                t4_nv='--------------'

            else:
                t4_s=i['t4'].split(',')
                t4=t4_s[0]
                t4_nv=str(t4_s[1]+' - '+t4_s[2])


            if i['t3'] == ',':
                t3=''
                t3_nv='--------------'

            else:
                t3_s=i['t3'].split(',')
                t3=t3_s[0]
                t3_nv=str(t3_s[1]+' - '+t3_s[2])
                

            if i['aso'] == ',':
                aso=''
                aso_nv='--------------'
            else:
                aso_s=i['aso'].split(',')
                aso=aso_s[0]
                aso_nv=str(aso_s[1]+' - '+aso_s[2])
    

            if i['crp'] == ',':
                crp=''
                crp_nv='--------------'
         
            else:
                crp_s=i['crp'].split(',')
                crp=crp_s[0]
                crp_nv=str(crp_s[1]+' - '+crp_s[2])
                

            if i['procalcitonin'] == ',':
                procal=''
                procal_nv='--------------'
            else:
                procal_s=i['procalcitonin'].split(',')
                procal=procal_s[0]
                procal_nv=str(procal_s[1]+' - '+procal_s[2])

            if i['reheu'] == ',':
                rheu=''
                rheu_nv='--------------'
            else:
                rheu_s=i['reheu'].split(',')
                rheu=rheu_s[0]
                rheu_nv=str(rheu_s[1]+' - '+rheu_s[2])
       

            if i['psa'] == ',':
                psa=''
                psa_nv='--------------'
  
            else:
                psa_s=i['psa'].split(',')
                psa=psa_s[0]
                psa_nv=str(psa_s[1]+' - '+psa_s[2])
                

            if i['pro_bnp'] == ',':
                probnp=''
                probnp_nv='--------------'

            else:
                probnp_s=i['pro_bnp'].split(',')
                probnp=probnp_s[0]
                probnp_nv=str(probnp_s[2])
            

            if i['cea'] == ',':
                cea=''
                cea_nv='--------------'
 
            else:
                cea_s=i['cea'].split(',')
                cea=cea_s[0]
                cea_nv=str(cea_s[1]+' - '+cea_s[2])
                
            try:
                if i['ana'] == ',':
                    ana=''
                    ana_nv='--------------'
  
                else:
                    ana_s=i['ana'].split(',')
                    ana=ana_s[0]
                    ana_nv=str(ana_s[1]+' - '+ana_s[2])
                 
            except Exception as e:
                ana=''
                ana_nv='-----------'

            try:
                if i['ca_19_9'] == ',':
                    ca19=''
                    ca19_nv='--------------'

                else:
                    ca19_s=i['ca_19_9'].split(',')
                    ca19=ca19_s[0]
                    ca19_nv=str(ca19_s[1]+' - '+ca19_s[2])
                    
            except Exception as e:
                ca19=''
                ca19_nv='-----------'
    



            data={
                'trop':trop,
                'trop_nv':trop_nv,

                'ckmb':ckmb,
                'ckmb_nv':ckmb_nv,

                'tsh':tsh,
                'tsh_nv':tsh_nv,

                'ft4':ft4,
                'ft4_nv':ft4_nv,

                'ft3':ft3,
                'ft3_nv':ft3_nv,

                't4':t4,
                't4_nv':t4_nv,

                't3':t3,
                't3_nv':t3_nv,

                'aso':aso,
                'aso_nv':aso_nv,

                'crp':crp,
                'crp_nv':crp_nv,

                'procal':procal,
                'procal_nv':procal_nv,

                'rheu':rheu,
                'rheu_nv':rheu_nv,

                'psa':psa,
                'psa_nv':psa_nv,

                'probnp':probnp,
                'probnp_nv':probnp_nv,

                'cea':cea,
                'cea_nv':cea_nv,

                'ana':ana,
                'ana_nv':ana_nv,

                'ca19':ca19,
                'ca19_nv':ca19_nv,

                'notes':i['note'],
                'performby':i['perform_by_name'],
                'verifyby':i['verified_by_name'],
                'dateverify':i['date_verified'],

            }
    
    return render(request,'integrated/laboratory/result_form/immunosero.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name'],'result':data,'test':getres['data'][0],'ptx':ptx[0],'ward':ward,'doctor':physician})
######################################### pdf

def makepdf(html, context_dict={}):
    template  = get_template('integrated/laboratory/result_form/404.html')
    HTML  =  template.render(context_dict)
    timestamp  = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name  = f'promissorynote_{timestamp}.doc'
    # saving pdf in media rootfile
    pdf_path  = os.path.join(settings.MEDIA_ROOT, 'doc', file_name)
    HTML(string=html).write_pdf(pdf_path)
    return  file_name

@pdf_decorator
def pdfview(request):
    return render(request, 'integrated/laboratory/labpdf.html')

######################################### PRINT C
def get_image_extension_from_base64(base64_str:str):
    if base64_str.startswith("data:image/"):
        base64_str = base64_str.split(";base64,", 1)[1]
    image_data = base64.b64decode(base64_str, validate=True)

    extension = imghdr.what(None, h=image_data)
    return extension

def cbcup_save(request):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if request.method == 'POST':
        img_url=request.POST.get('img_url')
        # img_file=request.FILES.get('file_img')
        if str(img_url).startswith("data:image/"):
            img_url = img_url.split(";base64,", 1)[1]
        decodedData = base64.b64decode(img_url,validate=True)
    
        # Write Image from Base64 File
        # imgFile = open('integrated/static/hema/072190.jpeg', 'wb')
        imgFile = open('12.png', 'wb')
        
        if imgFile.write(decodedData):
            imgFile.close()
            try:
                img_text=pytesseract.image_to_string(Image.open('hema.jpg'))
                data=img_text.splitlines(keepends=True)
                print(img_text)
                for d in data:
                    
                    dd=d[:3]
                    vv=d[4:][:5]
                    # print(d.splitlines(keepends=True))
                    if dd == 'PLT':
                        print(dd+'-'+vv)
                    if dd == 'WBC':
                        print(dd+'-'+vv)
                    if dd == 'HGB':
                        print(dd+'-'+vv)
                # print(data)
            except Exception as e:
                print(e)
    return JsonResponse({'data':data})

def cbc_uploads(request):
    context={}
    return render(request,'integrated/laboratory/hematology/cbc_upload.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})

@csrf_exempt
def print_c(request,encc,orderid):
    tcharge=[]
    total=0
    get_examination = requests.post(get_lab_request, data={'enccode':encc,'order_id':orderid}).json()
    for p in get_examination['details']:
        ptx=p['patlast']+', '+p['patfirst']+'  '+p['patmiddle']
        add=p['patbplace']
        hosno=p['hpercode']
    for c in get_examination['laboratory']:
        if c['status'] !='CANCELLED':
            tcharge.append(c)
            total=total + c['pchrgup']
    user=request.session.get("name")
    return render(request,'integrated/laboratory/print/p_charge.html',{'tests':tcharge,'ptx':ptx,'add':add,'hosno':hosno,'user':user,'ccount':len(tcharge),'total':total})

######################################### CHARGE SLIP
@csrf_exempt
def charge_now(request):
    ordid=request.POST.get('orderid')
    encc=request.POST.get('encc')
    get_examination = requests.post(get_lab_request, data={'enccode':encc,'order_id':ordid}).json()
    key=[]
    for e in get_examination['laboratory']:
        key.append(e['proccode'])                                                           
    try:
        charging=requests.post(charge,data={'items':key,'order_id':ordid}).json()
        data=charging['status']
    except Exception as e:
        data=e

    return JsonResponse({'data':data})

def chargeslip(request,encc,ordid,code):
    get_examination = requests.post(get_lab_request, data={'enccode':encc,'order_id':ordid}).json()
    for p in get_examination['details']:
        ptx=p['patlast']+', '+p['patfirst']+' '+p['patmiddle']
        hosno=p['hpercode']
        dob=p['birthdate']
        add=p['patbplace']
    total=0
    get_item=requests.post(get_charges,data={'code':code}).json()
    for i in get_item['data']:
        total=total+i['pcchrgamt']

    user=request.session.get("name")
    return render(request,'integrated/laboratory/print/chargeslip.html',{'user':user,'tests':get_item['data'],'total':total,'ptx':ptx,'hosno':hosno,'dob':dob,'add':add,'ccount':len(get_item['data'])})
  
######################################### GET CHARGES
@csrf_exempt
def getCharges(request):
    code=request.POST.get('code')
    get_item=requests.post(get_charges,data={'code':code}).json()
    return JsonResponse({'data':get_item['data']})
########################################## OPD 
@csrf_exempt
def getTotal(request):
    encc=request.POST.get('encc')
    ordid=request.POST.get('orderid')
    get_examination = requests.post(get_lab_request, data={'enccode': encc,'order_id':ordid}).json()
    total=0
    for t in get_examination['laboratory']:
        total=total + t['pchrgup']
    data=''

    return JsonResponse({'data':data,'total':total})

@csrf_exempt
def opd_labrequest(request):
    ordid=request.POST.get('ordid')
    encc=request.POST.get('encc')
    rtype=request.POST.get('rtype')
    if rtype == 'unseen':
        seen_update=requests.post(put_orderDetails, data={'order_id':ordid,'received_by':request.session.get('employee_id')}).json()
    get_examination = requests.post(get_lab_request, data={'enccode': encc,'order_id':ordid}).json()
    data=get_examination
    doctOrder = requests.post(doctorsOrderPatient).json()
    labrequest=doctOrder['data']
    for l in labrequest:
        if l['order_id'] == ordid:
            doctor=l['physician']

    for i in data['laboratory']:
        i['orcode'] = doctor
        i['enccode'] = i['enccode'].replace("/", "-")
        if i['datemod'] is not None:
            i['datemod'] = datetime.datetime.strptime(i['datemod'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['datemod']=datetime.datetime.strftime(i['datemod'], '%b %d, %y (%I:%M %p)')
        else:
            i['datemod'] = '---'
        # print(i)
    return JsonResponse({'data':data})

@csrf_exempt
def get_opd(request):
    rtype=request.POST.get('rtype')
    
    doctOrder = requests.post(doctorsOrderPatient).json()
    labrequest=doctOrder['data']
    test_=''
    tpending=''
    opd=[]
    o_waiting=[]
    o_received=[]

    for i in labrequest:
        i['enccode'] = i['enccode'].replace("/", "-")
        ordid=i['order_id']
        enctr=i['enccode']
            # print(i)
         
        get_examination = requests.post(get_lab_request, data={'enccode': enctr,'order_id':ordid}).json()
        test_=get_examination['laboratory']
        
        if i['toecode'] == 'OPD' and i['status'] =='PENDING' and len(test_) > 0:
            o_waiting.append(i['order_id'])
        if i['toecode'] == 'OPD' and i['status'] =='RECEIVED' and len(test_) > 0:
            o_received.append(i['order_id'])
        if i['toecode'] == 'OPD' and i['status'] == rtype: 
         if(len(test_) > 0):
             test_=test_
             opd.append(i)
             i['released_by']=len(test_)
    
    return JsonResponse({'data':opd,'waiting':len(o_waiting),'received':len(o_received)})


def lab_opd(request):
    doctOrder = requests.post(doctorsOrderPatient).json()
    labrequest=doctOrder['data']
    test_=''
    tpending=''
    opd=[]
    
    for i in labrequest:
        i['enccode'] = i['enccode'].replace("/", "-")
        ordid=i['order_id']
        enctr=i['enccode']
        if i['toecode'] == 'OPD' and i['status'] == 'PENDING':
    
            get_examination = requests.post(get_lab_request, data={'enccode': enctr,'order_id':ordid}).json()
            test_=get_examination['laboratory']
            if(len(test_) > 0):
                test_=test_
                opd.append(i)
                i['released_by']=len(test_)
    return render(request, 'integrated/laboratory/opd/index.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name'],'opd_request':opd,'tpending':tpending,'test':test_})
########################################## LABORATORY REQUEST FORM
def lab_request_print(request,encc,orderid,ward):
    doctOrder = requests.post(doctorsOrderPatient).json()
    labrequest=doctOrder['data']
    test_data=[]
    ptx_data=[]
    get_examination = requests.post(get_lab_request, data={'enccode': encc,'order_id':orderid}).json()
    tests=get_examination['laboratory']
    ptx=get_examination['details']
    # ward=get_examination['toecode']

    for c in tests:
        ctr=c['control_no']
        remarks=c['donotes']
        if c['status'] != 'CANCELLED':
            test_data.append(c)

    for l in labrequest:
        if l['order_id'] == orderid:
            date_encode=l['date_encoded']
            receive_by=l['receiver']
            r_doctor=l['physician']

    for p in ptx:
        dd=p['birthdate'].split(' ')
        
        pdata={
            'name':str(p['patlast'])+', '+str(p['patfirst']),
            'hosno':p['hpercode'],
            'dob':dd[0],
            'age':p['patage'],
            'stat':p['patcstat'],
            'gender':p['patsex'],
            'ward':p['wardname'],
            'encoded':date_encode,
            'ctr':ctr,
            'remarks':remarks,
            'received_by':receive_by,
            'place':p['patbplace'],
            
        }
    
    # for d in labrequest:
    #     if d['control_no'] == ctr:
           
    #        doctor=d['physician']
    
    # print(ptx)

    return render(request, 'integrated/laboratory/print/request.html',{'page': 'Laboratory', 'user_level': request.session['user_level'],'ptxdata':pdata, 'name': request.session['name'],'test':test_data,'ward':ward,'ptx':ptx,'ctr':ctr,'doctor':r_doctor})



########################################## BACTERIOLOGY
@csrf_exempt
def load_bacti(request):
    pending=[]
    onprocess=[]
    toverify=[]
    completed=[]
    released=[]
    op=[]
    rapid=[]
    htype=request.POST.get('rtype')
    get_bacti=requests.post(getLab_modality,data={'modality':'BACTI','status':htype}).json()


    rpending=requests.post(getLab_modality,data={'modality':'BACTI','status':'PENDING'}).json()
    for p in rpending['data']:
        if p['proccode'] == 'LABOR0051':
            pending.append(p['proccode'])
    ronprocess=requests.post(getLab_modality,data={'modality':'BACTI','status':'ONPROCESS'}).json()
    for p in ronprocess['data']:
        if p['proccode'] == 'LABOR0051':
            onprocess.append(p['proccode'])
    rtoverify=requests.post(getLab_modality,data={'modality':'BACTI','status':'TO VERIFY'}).json()
    for p in rtoverify['data']:
        if p['proccode'] == 'LABOR0051':
            toverify.append(p['proccode'])
    rcompleted=requests.post(getLab_modality,data={'modality':'BACTI','status':'COMPLETED'}).json()
    for p in rcompleted['data']:
        if p['proccode'] == 'LABOR0051':
            completed.append(p['proccode'])
    rreleased=requests.post(getLab_modality,data={'modality':'BACTI','status':'RELEASED'}).json()
    for r in rreleased['data']:
        if r['proccode'] == 'LABOR0051':
            released.append(r['proccode'])
           


    req=[]
    ctr=''
    for i in get_bacti['data']:
        if i['proccode'] == 'LABOR0051':
            i['enccode'] = i['enccode'].replace("/", "-")
            i['dodate'] = datetime.datetime.strptime(i['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['dodate']=datetime.datetime.strftime(i['dodate'], '%b %d, %y (%I:%M %p)')

            i['received_datetime'] = datetime.datetime.strptime(i['received_datetime'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['received_datetime']=datetime.datetime.strftime(i['received_datetime'], '%b %d, %y (%I:%M %p)')
            rapid.append(i)

            # if i['status']=='PENDING':
            #     pending.append(i['proccode'])
            # if i['status']=='ONPROCESS':
            #     onprocess.append(i['proccode'])
            # if i['status']=='TO VERIFY':
            #     toverify.append(i['proccode'])
            # if i['status']=='COMPLETED':
            #     completed.append(i['proccode'])
            # if i['status']=='RELEASED':
            #     released.append(i['proccode'])

            # age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
            # i['uomcode']=age['data']
    return JsonResponse({'data':rapid,'pend':len(pending),'onp':len(onprocess),'tovery':len(toverify),'compl':len(completed),'rel':len(released)})
    # return JsonResponse({'data':get_bacti['data'],'pend':len(pen_bacti['data']),'onp':len(on_bacti['data']),'tovery':len(tovery_bacti['data']),'compl':len(compl_bacti['data'])})

@csrf_exempt
def bacti_sentToProcess(request):
    encc=request.POST.get('encc')
    orderid=request.POST.get('orderid')
    key=request.POST.get('key')
    try:
        get_test = requests.post(get_lab_request, data={'enccode':encc,'order_id':orderid}).json()
        for g in get_test['laboratory']:
            if g['prikey'] == key:
                    sentToProcess=requests.post(update_status, data={'key': key, 'enccode': encc,'order_id':orderid, 'status':'ONPROCESS','receive':g['received_specimen']}).json()
                    data=sentToProcess['status']
    except Exception as e:
        data=e
    return JsonResponse({'data':data})

def save_rapid(request):
    action = request.POST.get('rdt_action')
    encc=request.POST.get('rdt_encc')
    orderid=request.POST.get('rdt_orderid')
    procode=request.POST.get('rdt_procode')
    key=request.POST.get('rdt_key')
    
    if action == 'insert':
        try:
            save_rdt=requests.post(save_rapid_result,data={
                'enccode':request.POST.get('rdt_encc'),
                'order_id':request.POST.get('rdt_orderid'),
                'proccode':request.POST.get('rdt_procode'),
                'age':request.POST.get('rdt_age'),
                'ward':request.POST.get('rdt_ward'),
                'licno':request.POST.get('rdt_licno'),
                'contact_no':request.POST.get('rdt_contact'),
                'type':request.POST.get('r_type'),
                'result':request.POST.get('rdt_result'),
                'kit':request.POST.get('rdt_kit'),
                'lot_no':request.POST.get('rdt_lotno'),
                'expiry':request.POST.get('rdt_expiry'),
                'remarks':request.POST.get('rdt_remarks'),
                'perform_by':request.session['employee_id'],
                'verify_by':'',
                'approved_by':''
            }).json()
            # print(save_rdt)
            if save_rdt['status'] == 'success':
                get_test = requests.post(get_lab_request, data={'enccode':encc,'order_id':orderid}).json()
                for g in get_test['laboratory']:
                    if g['prikey'] == key:
                        up_stat=requests.post(update_status, data={'key':key, 'enccode': encc,'order_id':orderid, 'status':'TO VERIFY','receive':g['received_specimen'],'remarks':request.POST.get('rdt_remarks')}).json()
                        status=up_stat['status']
        except Exception as e:
            status=e
            data=e
        
    elif action == 'verify':
        try:
            save_rdt=requests.post(save_rapid_result,data={
                'enccode':request.POST.get('rdt_encc'),
                'order_id':request.POST.get('rdt_orderid'),
                'proccode':request.POST.get('rdt_procode'),
                'age':request.POST.get('rdt_age'),
                'ward':request.POST.get('rdt_ward'),
                'licno':request.POST.get('rdt_licno'),
                'contact_no':request.POST.get('rdt_contact'),
                'type':request.POST.get('r_type'),
                'result':request.POST.get('rdt_result'),
                'kit':request.POST.get('rdt_kit'),
                'lot_no':request.POST.get('rdt_lotno'),
                'expiry':request.POST.get('rdt_expiry'),
                'remarks':request.POST.get('rdt_remarks'),
                'perform_by':request.POST.get('rdt_performById'),
                'verify_by':request.session['employee_id'],
                'approved_by':''
            }).json()
            if save_rdt['status'] == 'success':
                 get_test = requests.post(get_lab_request, data={'enccode':encc,'order_id':orderid}).json()
                 for g in get_test['laboratory']:
                     if g['prikey'] == key:
                        up_stat=requests.post(update_status, data={'key':key, 'enccode': encc,'order_id':orderid, 'status':'COMPLETED','receive':g['received_specimen'],'remarks':request.POST.get('rdt_remarks')}).json()
                        status=up_stat['status']
        except Exception as e:
            status=e
            data=e
    
    return JsonResponse({'data':status,'action':action})

@csrf_exempt
def get_rapidResult(request):
    
    get_rapid=requests.post(get_rapid_result,data={'order_id':request.POST.get('orderid'),'enccode':request.POST.get('encc')}).json()
    data=get_rapid

    return JsonResponse({'data':data})

@csrf_exempt
def result_rapid(request,toecode,orderid,encc,prikey):
    getPatient=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
    for l in getPatient['laboratory']:
        if l['prikey'] == prikey:
            l['datemod'] = datetime.datetime.strptime(l['datemod'],"%Y-%m-%dT%H:%M:%S.%fZ")
            l['datemod']=datetime.datetime.strftime(l['datemod'], '%b %d, %Y (%I:%M %p)')
            cdate=l['datemod']
    get_rapid=requests.post(get_rapid_result,data={'order_id':orderid,'enccode':encc}).json()
    # for r in get_rapid:
    #     r['expiry_date'] = datetime.datetime.strptime(r['expiry_date'],"%Y-%m-%dT%H:%M:%S.%fZ")
    #     r['expiry_date']=datetime.datetime.strftime(r['expiry_date'], '%b %d, %Y (%I:%M %p)')


    # print(getPatient)
    return render(request,'integrated/laboratory/result_form/rapidtest-result.html',{'result':get_rapid['data'][0],'ptx':getPatient['details'][0],'test':getPatient['laboratory'][0],'release_date':cdate})



########################################## CHEMISTRY
@csrf_exempt
def getlabtest(request):
    chem_test=[]
    age=requests.post(get_age, data={'enccode':request.POST.get('encc'),'toecode':request.POST.get('toecode')}).json()
    get_test=requests.post(get_lab_request,data={'enccode':request.POST.get('encc'),'order_id':request.POST.get('orderid')}).json()
    for c in get_test['laboratory']:
        if c['status'] != 'CANCELLED':
    
            chem_test.append(c)
    
    return JsonResponse({'data':chem_test,'age':age['data']})


def save_chem_result(request):
    orderid=request.POST.get('chem_orderid')
    encc=request.POST.get('chem_encc')
    hpercode=request.POST.get('chem_hpercode')
    action =request.POST.get('chem_action')
    
    hba1c=str(request.POST.get('hba1c'))+','+str(request.POST.get('hba1c_nv'))
    fbs=str(request.POST.get('fbs'))+','+str(request.POST.get('fbs_nv'))
    rbs=str(request.POST.get('rbs'))+','+str(request.POST.get('rbs_nv'))
    cholesterol=str(request.POST.get('cholesterol'))+','+str(request.POST.get('cholesterol_nv'))
    triglycerides=str(request.POST.get('triglyceride'))+','+str(request.POST.get('triglyceride_nv'))
    hdl_cholesterol=str(request.POST.get('hdl_col'))+','+str(request.POST.get('hdl_col_nv'))
    ldl_cholesterol=str(request.POST.get('ldl_col'))+','+str(request.POST.get('ldl_col_nv'))
    bua=str(request.POST.get('bua'))+','+str(request.POST.get('bua_nv'))
    bun=str(request.POST.get('bun'))+','+str(request.POST.get('bun_nv'))
    creatinine=str(request.POST.get('crea'))+','+str(request.POST.get('crea_nv'))
    alt_sgpt=str(request.POST.get('alt'))+','+str(request.POST.get('alt_nv'))
    ast_sgot=str(request.POST.get('ast'))+','+str(request.POST.get('ast_nv'))
    potassium=str(request.POST.get('potassium'))+','+str(request.POST.get('potassium_nv'))
    sodium=str(request.POST.get('sodium'))+','+str(request.POST.get('sodium_nv'))
    chloride=str(request.POST.get('chloride'))+','+str(request.POST.get('chloride_nv'))
    total_calcium=str(request.POST.get('tca'))+','+str(request.POST.get('tca_nv'))
    ionized_calcium=str(request.POST.get('ica'))+','+str(request.POST.get('ica_nv'))
    magnesium=str(request.POST.get('magnesium'))+','+str(request.POST.get('magnesium_nv'))
    phosphorus=str(request.POST.get('phosphorus'))+','+str(request.POST.get('phosphorus_nv'))
    total_protein=str(request.POST.get('tprotein'))+','+str(request.POST.get('tprotein_nv'))
    albumin=str(request.POST.get('albumin'))+','+str(request.POST.get('albumin_nv'))
    globulin=str(request.POST.get('globulin'))+','+str(request.POST.get('globulin_nv'))
    ag_ratio=str(request.POST.get('ag_ratio'))+','+str(request.POST.get('ag_ratio_nv'))
    alkaline_phospatase=str(request.POST.get('alkp'))+','+str(request.POST.get('alkp_nv'))
    amylase=str(request.POST.get('amylase'))+','+str(request.POST.get('amylase_nv'))
    lipase=str(request.POST.get('lipase'))+','+str(request.POST.get('lipase_nv'))
    ldh=str(request.POST.get('ldh'))+','+str(request.POST.get('ldh_nv'))
    total_bilirubin=str(request.POST.get('tbilirubin'))+','+str(request.POST.get('tbilirubin_nv'))
    direct_bilirubin=str(request.POST.get('dbilirubin'))+','+str(request.POST.get('dbilirubin_nv'))
    indirect_bilirubin=str(request.POST.get('ibilirubin'))+','+str(request.POST.get('ibilirubin_nv'))

    ggt=str(request.POST.get('ggt'))+','+str(request.POST.get('ggt_nv'))
    ferritin=str(request.POST.get('ferritin'))+','+str(request.POST.get('ferritin_nv'))
    cortisol=str(request.POST.get('cortisol'))+','+str(request.POST.get('cortisol_nv'))

    
    # hba1c_res=hba1c.split("/")
    # print(hba1c_res[0])
    # print(hba1c_res[1])

    if action == 'INSERT':
        try:
            chem_res=requests.post(save_chem, data={
                'enccode':request.POST.get('chem_encc'),
                'order_id':request.POST.get('chem_orderid'),
                'hpercode':request.POST.get('chem_hpercode'),
                'date':datetime.datetime.now(),
                'last_meal':request.POST.get('chem_lastmeal'),
                'extraction_time':request.POST.get('chem_ext_time'),
                'hba1c':hba1c,
                'glucose_fbs':fbs,
                'glucose_rbs':rbs,
                'cholesterol':cholesterol,
                'triglycerides':triglycerides,
                'hdl_cholesterol':hdl_cholesterol,
                'ldl_cholesterol':ldl_cholesterol,
                'blood_uric':bua,
                'blood_urea':bun,
                'creatinine':creatinine,
                'alt_sgpt':alt_sgpt,
                'ast_sgot':ast_sgot,
                'potassium':potassium,
                'sodium':sodium,
                'chloride':chloride,
                'total_calcium':total_calcium,
                'ionized_calcium':ionized_calcium,
                'magnesium':magnesium,
                'phosphorus':phosphorus,
                'total_protein':total_protein,
                'albumin':albumin,
                'globulin':globulin,
                'ag_ration':ag_ratio,
                'alkaline_phospatase':alkaline_phospatase,
                'amylase':amylase,
                'lipase':lipase,
                'ldh':ldh,
                'total_bilirubin':total_bilirubin,
                'direct_bilirubin':direct_bilirubin,
                'indirect_bilirubin':indirect_bilirubin,
                'ggt':ggt,
                'ferritin':ferritin,
                'cortisol':cortisol,
                'perform_by':request.session['employee_id']
            }).json()

            if chem_res['status'] == 'success':
                # data='INSERTED'
                get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
                for g in get_test['laboratory']:
                    if g['modality'] == 'CHEMI' and g['status'] !='CANCELLED':
                        key=g['prikey']
                        try:
                            samplemodality=requests.post(update_status, data={'key':key, 'enccode': encc,'order_id':orderid, 'status':'TOVERIFY','receive':g['received_specimen']}).json()
                            data=samplemodality['status']
                        except Exception as e:
                            print('error')
                            data=e
            else:
                data=chem_res
            

        except Exception as e:
            data='Error Saving'
            

    elif action == 'VERIFY':
        try:
            chem_res=requests.post(save_chem, data={
                'enccode':request.POST.get('chem_encc'),
                'order_id':request.POST.get('chem_orderid'),
                'hpercode':request.POST.get('chem_hpercode'),
                'date':datetime.datetime.now(),
                'last_meal':request.POST.get('chem_lastmeal'),
                'extraction_time':request.POST.get('chem_ext_time'),

                'hba1c':hba1c,
                'glucose_fbs':fbs,
                'glucose_rbs':rbs,
                'cholesterol':cholesterol,
                'triglycerides':triglycerides,
                'hdl_cholesterol':hdl_cholesterol,
                'ldl_cholesterol':ldl_cholesterol,
                'blood_uric':bua,
                'blood_urea':bun,
                'creatinine':creatinine,
                'alt_sgpt':alt_sgpt,
                'ast_sgot':ast_sgot,
                'potassium':potassium,
                'sodium':sodium,
                'chloride':chloride,
                'total_calcium':total_calcium,
                'ionized_calcium':ionized_calcium,
                'magnesium':magnesium,
                'phosphorus':phosphorus,
                'total_protein':total_protein,
                'albumin':albumin,
                'globulin':globulin,
                'ag_ration':ag_ratio,
                'alkaline_phospatase':alkaline_phospatase,
                'amylase':amylase,
                'lipase':lipase,
                'ldh':ldh,
                'total_bilirubin':total_bilirubin,
                'direct_bilirubin':direct_bilirubin,
                'indirect_bilirubin':indirect_bilirubin,
                'ggt':ggt,
                'ferritin':ferritin,
                'cortisol':cortisol,
                # 'perfom_by':int('617116'),
                'verified_by':request.session['employee_id']
                # 617116
            }).json()

            if chem_res['status'] == 'success':
                # data='VERIFIED'
                get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
                for g in get_test['laboratory']:
                    if g['modality'] == 'CHEMI' and g['status'] != 'CANCELLED':
                        key=g['prikey']
                        try:
                            samplemodality=requests.post(update_status, data={'key':key, 'enccode': encc,'order_id':orderid, 'status':'COMPLETED','receive':g['received_specimen']}).json()
                            data=samplemodality['status']
                        except Exception as e:
                            data=e
        except Exception as e:
            data='Error Verifying'
            
    else:
        act=''
    chem_res=''
    
    return JsonResponse({'data':data})

########################################### SAVE OCCULT BLOOD
def save_occult(request):
    ordid=request.POST.get('orderid')
    hosno=request.POST.get('hpercode')
    action=request.POST.get('action')
  
    if action == 'insert':
        try:
          save_occult=requests.post(fecalysisResult, data={
            'enccode':request.POST.get('encc'),
            'order_id':request.POST.get('orderid'),
            'hpercode':request.POST.get('hpercode'),
            'item':request.POST.get('proccode'),
            'fecocbld':request.POST.get('occult_results'),
            'performBy':request.session['employee_id'],}).json()
          if save_occult['status'] == 'success':
                get_test = requests.post(get_lab_request, data={'enccode':request.POST.get('encc'),'order_id':request.POST.get('orderid')}).json()
                for g in get_test['laboratory']:
                    if g['prikey'] == request.POST.get('prikey'):
                        up_stat=requests.post(update_status, data={'key': request.POST.get('prikey'), 'enccode': request.POST.get('encc'),'order_id':request.POST.get('orderid'), 'status':'TO VERIFY','receive':g['received_specimen']}).json()
                        status=up_stat['status']

        except Exception as e:
            status=e
    elif action == 'verify':
        try:
          verify_occult=requests.post(fecalysisResult, data={
            'enccode':request.POST.get('encc'),
            'order_id':request.POST.get('orderid'),
            'hpercode':request.POST.get('hpercode'),
            'item':request.POST.get('proccode'),
            'fecocbld':request.POST.get('occult_results'),
            'performBy':request.POST.get('performById'),
            'verifyBy':request.session['employee_id'],
            }).json()
        #   print(verify_occult)
          if verify_occult['status'] == 'success':
            get_test = requests.post(get_lab_request, data={'enccode':request.POST.get('encc'),'order_id':request.POST.get('orderid')}).json()
            for g in get_test['laboratory']:
                if g['prikey'] == request.POST.get('prikey'):
                    up_stat=requests.post(update_status, data={'key': request.POST.get('prikey'), 'enccode': request.POST.get('encc'),'order_id':request.POST.get('orderid'),'status':'COMPLETED','receive':g['received_specimen']}).json()
                    status=up_stat['status']
        except Exception as e:
            status=e
        
    return JsonResponse({'data':status})

########################################### SAVE FECALYSIS RESULT
@csrf_exempt
def save_fa_result(request):
    ordid=request.POST.get('orderid')
    hosno=request.POST.get('hpercode')
    action=request.POST.get('stype')
    proccode=request.POST.get('proccode')
   
    if action == 'INSERT':
        performby=request.session['employee_id']
        verifyby=''
        stat='TO VERIFY'
    elif action == 'VERIFY':
        performby=request.POST.get('performById')
        verifyby=request.session['employee_id']
        stat='COMPLETED'
    else:
        performby=''
        verifyby=''

    try:
        save_fa=requests.post(fecalysisResult, data={
          'enccode':request.POST.get('encc'),
          'order_id':request.POST.get('orderid'),
          'hpercode':request.POST.get('hpercode'),
          'item':request.POST.get('proccode'),
          'feccolor':request.POST.get('color'),
          'fecon':request.POST.get('consistency'),
          'fecocbld':request.POST.get('occult_blood'),   
          'fecrbc':request.POST.get('rcb'),
          'fecwbc':request.POST.get('wbc'),
          'fecyeast':request.POST.get('yeast'),
          'fecbac':request.POST.get('bacteria'),
          'fecfat':request.POST.get('fat_globules'),
          'fecascaris':request.POST.get('ascaris'),
          'fechookworm':request.POST.get('hookworm'),
          'fechisto':request.POST.get('histo'),
          'feccoli':request.POST.get('coli'),
          'fectri':request.POST.get('trichuris'),
          'fecvermi':request.POST.get('vermi'),
          'feothr':request.POST.get('other'),
          'fecnote':request.POST.get('note'),
          'performBy':performby,
          'verifyBy':verifyby
          }).json()
        if save_fa['status'] == 'success':  
            # print(save_fa)
            get_test = requests.post(get_lab_request, data={'enccode':request.POST.get('encc'),'order_id':request.POST.get('orderid')}).json()
            for g in get_test['laboratory']:
                if g['proccode'] == 'LABOR00334' or g['proccode'] == 'LABOR00407':
                    up_stat=requests.post(update_status, data={'key': g['prikey'], 'enccode': request.POST.get('encc'),'order_id':request.POST.get('orderid'), 'status':stat,'receive':g['received_specimen']}). json()
                    status=up_stat['status']
        else:
            print(save_fa)
    except Exception as e:
        status=e
        print(e)
   
    
    return JsonResponse({'data':status})
#######################################
@csrf_exempt
def get_fa_resultdata(request): 
    pord=request.POST.get('ordid')
    proc=request.POST.get('proc')
    getfa=requests.post(get_fecalysis, data={'order_id':pord}).json()
    try:
        for o in getfa['data']:
            if o['proccode'] == 'LABOR00334':
                result=o['fecocbld']
            elif o['proccode'] == 'LABOR00407':
                result=result
            
    except Exception as e:
        result=''
    data=getfa
    return JsonResponse({'status':data,'result':result,'proc':proc})

##################################### USED
@csrf_exempt
def view_labrequest(request):
    lab_user=request.session.get('employee_id')
    status=request.POST.get('encc')
    rtype=request.POST.get('rtype')
    chrg_code=''
    if rtype == 'unseen':
        seen_update=requests.post(put_orderDetails, data={'order_id':request.POST.get('ordid'),'received_by':lab_user}).json()
    view_req=requests.post(get_lab_request,data={'enccode':request.POST.get('encc'),'order_id':request.POST.get('ordid')}).json()
    
    for i in view_req['laboratory']:
        chrg_code=i['pcchrgcod']
        i['enccode'] = i['enccode'].replace("/", "-")
        i['dodate'] = datetime.datetime.strptime(i['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
        i['dodate']=datetime.datetime.strftime(i['dodate'], '%b %d, %y (%I:%M %p)')
        if i['datemod'] is not None:
            i['datemod'] = datetime.datetime.strptime(i['datemod'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['datemod']=datetime.datetime.strftime(i['datemod'], '(%I:%M %p)')
        
    # chk_charge=requests.post(get_charges,data={'code':chrg_code}).json()
    # if len(chk_charge['data']) > 0:
    #     chk=1
    # else:
    #     chk=0
    status={
        'labtest':view_req['laboratory'],
        'patient':view_req['details'],
        'ward':view_req['toecode'],
        # 'test':view_req
    }

    return JsonResponse({'data':status,'code':chrg_code})

@csrf_exempt
def load_accept_req(request):
    view_req=requests.post(get_lab_request,data={'enccode':request.POST.get('encc'),'order_id':request.POST.get('orderid')}).json()
    for i in view_req['laboratory']:
        i['enccode'] = i['enccode'].replace("/", "-")
        i['dodate'] = datetime.datetime.strptime(i['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
        i['dodate']=datetime.datetime.strftime(i['dodate'], '%b %d, %y (%I:%M %p)')
    status={
        'labtest':view_req['laboratory'],
        'patient':view_req['details'],
        'ward':view_req['toecode']
    }
    
    return JsonResponse({'data':status})

##########################################
@csrf_exempt
def get_ua_resultdata(request):
    getua=requests.post(get_urinalysis,data={'order_id':request.POST.get('ord'),'item':request.POST.get('procode')}).json()
    for g in getua['data']:
        performby=g['perform_by_id']
        
    if performby == request.session['employee_id']:
        user=0
    else:
        user=1
    status={
        'gdata':list(getua['data']),
        'user':user,
        'perform_id':performby
    }
    return JsonResponse({'data':status})
#/////////
# ////////SAVE VERIFY RESULT
@csrf_exempt
def save_vefify_ua_result(request):

    verify_ua=requests.post(adduptdate_urinalysis,data={
            'hpercode':request.POST.get('vhpercode'),
            'order_id':request.POST.get('vorderid'),
            'item':request.POST.get('vproccode'),
            'enccode':request.POST.get('vencc'),
            'color':request.POST.get('vcolor'),
            'transparency':request.POST.get('vtransparency'),
            'reaction':request.POST.get('vreaction'),
            'ph':request.POST.get('vph'),
            'specificGravity':request.POST.get('vgravity'),
            'protein':request.POST.get('vprotein'),
            'glucose':request.POST.get('vsugar'),
            'ketone':request.POST.get('vketone'),
            'nitrite':request.POST.get('vnitrite'),
            'bilirubin':request.POST.get('vbilirubin'),
            'uroblinogen':request.POST.get('vurobilinogen'),
            'leukocytes':request.POST.get('vleukocytes'),
            'manualChon':request.POST.get('vmchon'),
            'manualProtein':request.POST.get('vprotein'),
            'wbc':request.POST.get('vwbc'),
            'rbc':request.POST.get('vrbc'),
            'epithelial':request.POST.get('vepithelial'),
            'mucus':request.POST.get('vmucus'),
            'bacteria':request.POST.get('vbacteria'),
            'calcium':request.POST.get('vcalcium'),
            # not saved
            'cast':request.POST.get('vphosphate'),
            'ammonium':request.POST.get('vbiurate'),
            'uricAcid':request.POST.get('vuric'),
            'urnvamm':request.POST.get('vbiurate'),
            'fineGranular':request.POST.get('vfine'),
            'coarseGranular':request.POST.get('vcoarse'),
            'hyaline':request.POST.get('vhyaline'),
            'wbcCast':request.POST.get('vcwbc'),
            'rbcCast':request.POST.get('vcrbc'),
            'others':request.POST.get('vothers'),
            'preg':request.POST.get('vpregnancy'),
            'performBy':request.POST.get('vperformby_id'),
            'verifyBy':request.session['employee_id'],
            }).json()
    if verify_ua['status'] == 'success':
        setcompleted=requests.post(get_lab_request, data={'enccode':request.POST.get('vencc'),'order_id':request.POST.get('vorderid')}).json()
        for c in setcompleted['laboratory']:
            if c['prikey'] == request.POST.get('vprikey'):
                sentToDone=requests.post(update_status, data={'key': request.POST.get('vprikey'), 'enccode': request.POST.get('vencc'),'order_id':request.POST.get('vorderid'), 'status':'COMPLETED','receive':c['received_specimen']}).json()
                

        getua=requests.post(get_urinalysis,data={'order_id':request.POST.get('vorderid'),'item':request.POST.get('vproccode')}).json()
    
    return JsonResponse({'status':getua['status']})


###########################################
@csrf_exempt
def view_ua_toAddResult(request):
    pk=request.POST.get('pk')
    ord=request.POST.get('ord')
    enctr=request.POST.get('encc')

    ptx_req=requests.post(get_lab_request, data={'enccode':enctr,'order_id':ord}).json()
    ptx=ptx_req['laboratory']
    status={
        'prikey':request.POST.get('pk'),
        'orderid':request.POST.get('ord'),
        'encc':request.POST.get('encc'),
        'data':ptx
    }

    return JsonResponse({'status':status})

########################################### SAVE PREGNANCY RESULT

def save_preg_res(request):
    ord=request.POST.get('orderid')
    presult=request.POST.get('preg_result')
    action = request.POST.get('action')

    if action == 'insert':
        save_preg=requests.post(adduptdate_urinalysis,data={
            # 'hpercode':request.POST.get('vhpercode'),
            'enccode': request.POST.get('encc'),
            'hpercode':request.POST.get('hpercode'),
            'order_id':request.POST.get('orderid'),
            'item':request.POST.get('proccode'),
            'preg':request.POST.get('preg_result'),
            'performBy':request.session['employee_id'],

        }).json()
        if save_preg['status'] == 'success':
            get_test = requests.post(get_lab_request, data={'enccode':request.POST.get('encc'),'order_id':request.POST.get('orderid')}).json()
            for g in get_test['laboratory']:
                if g['prikey'] == request.POST.get('prikey'):
                    up_stat=requests.post(update_status, data={'key': request.POST.get('prikey'), 'enccode': request.POST.get('encc'),'order_id':request.POST.get('orderid'),'status':'TO VERIFY','receive':g['received_specimen']}).json()
                    status=up_stat['status']
    elif action == 'verify':
        save_vpreg=requests.post(adduptdate_urinalysis,data={
            # 'hpercode':request.POST.get('vhpercode'),
            'enccode': request.POST.get('encc'),
            'hpercode':request.POST.get('hpercode'),
            'order_id':request.POST.get('orderid'),
            'item':request.POST.get('proccode'),
            'preg':request.POST.get('preg_result'),
            'performBy':request.POST.get('preg_performById'),
            'verifyBy':request.session['employee_id'],

        }).json()
        if save_vpreg['status'] == 'success':
            get_test = requests.post(get_lab_request, data={'enccode':request.POST.get('encc'),'order_id':request.POST.get('orderid')}).json()
            for g in get_test['laboratory']:
                if g['prikey'] == request.POST.get('prikey'):
                    up_stat=requests.post(update_status, data={'key': request.POST.get('prikey'), 'enccode': request.POST.get('encc'),'order_id':request.POST.get('orderid'),'status':'COMPLETED','receive':g['received_specimen']}).json()
                    status=up_stat['status']
        else:
            status='Error'


    
    return JsonResponse({'status':status})
########################################## GET PREG TO VERIFY
@csrf_exempt
def get_preg_result(request):
   
    getpreg=requests.post(get_urinalysis,data={'order_id':request.POST.get('orderid'),'items':request.POST.get('prikey')}).json()
    # print(getpreg)
    pdata=getpreg['data']
    for p in pdata:
        if p['proccode'] == 'LABOR00081':
            status={
                'result':p["urnvpreg"],
                'performBy':p["perform_by"],
                'performById':p["perform_by_id"]
            }

    return JsonResponse({'status':status})
########################################## SAVE VERIFY PREGNANCY

def save_vpreg_res(request):
    action=request.POST.get('action')
    data=action
    return JsonResponse({'status':data})

########################################### VERIFY UA RESULT


@csrf_exempt
def save_ua_result(request):

    action=request.POST.get('stype')
    # print(request.POST.get('proccode'))
    if action == 'INSERT':
        performby=request.session['employee_id']
        verifyby=''
        st='TO VERIFY'
        ttype='ONPROCESS'
      
    elif action == 'VERIFY':
        performby=request.POST.get('performbyId')
        verifyby=request.session['employee_id']
        st='COMPLETED'
        ttype='TO VERIFY'
        
    else:
        performby=''
        verifyby=''
    
    try:
        save_ua=requests.post(adduptdate_urinalysis,data={
            'hpercode':request.POST.get('hpercode'),
            'order_id':request.POST.get('orderid'),
            'item':request.POST.get('proccode'),
            'enccode':request.POST.get('encc'),
            'color':request.POST.get('color'),
            'transparency':request.POST.get('transparency'),
            'reaction':request.POST.get('reaction'),
            'ph':request.POST.get('ph'),
            'specificGravity':request.POST.get('gravity'),
            'protein':request.POST.get('protein'),
            'glucose':request.POST.get('sugar'),
            'ketone':request.POST.get('ketone'),
            'nitrite':request.POST.get('nitrite'),
            'bilirubin':request.POST.get('bilirubin'),
            'uroblinogen':request.POST.get('urobilinogen'),
            'leukocytes':request.POST.get('leukocytes'),
            'manualChon':request.POST.get('mchon'),
            'manualProtein':request.POST.get('mlprotein'),
            'wbc':request.POST.get('wbc'),
            'rbc':request.POST.get('rbc'),
            'epithelial':request.POST.get('epithelial'),
            'mucus':request.POST.get('mucus'),
            'bacteria':request.POST.get('bacteria'),
            'calcium':request.POST.get('calcium'),
            'cast':request.POST.get('phosphate'),
            'ammonium':request.POST.get('biurate'),
            'uricAcid':request.POST.get('uric'),
            'urnvamm':request.POST.get('biurate'),
            'fineGranular':request.POST.get('fine'),
            'coarseGranular':request.POST.get('coarse'),
            'hyaline':request.POST.get('hyaline'),
            'wbcCast':request.POST.get('cwbc'),
            'rbcCast':request.POST.get('crbc'),
            'others':request.POST.get('others'),
            'preg':request.POST.get('pregnancy'),
            'performBy':performby,
            'verifyBy':verifyby
            }).json()
        
        if save_ua['status'] == 'success':
            get_test = requests.post(get_lab_request, data={'enccode':request.POST.get('encc'),'order_id':request.POST.get('orderid')}).json()
            for g in get_test['laboratory']:
                if  g['proccode'] == 'LABOR00081' or g['proccode'] == 'LABOR00078' or g['proccode'] == 'LABOR00076' and g['status'] != 'CANCELLED':
                    sentToVerify=requests.post(update_status, data={'key': g['prikey'], 'enccode': request.POST.get('encc'),'order_id':request.POST.get('orderid'), 'status':st,'receive':g['received_specimen']}).json()
                    status=sentToVerify['status']
            getua=requests.post(get_urinalysis,data={'order_id':request.POST.get('orderid'),'item':request.POST.get('proccode')}).json()
            status=getua['status']
            # print(getua)
           
        else:
            status=save_ua
            
        # status=save_ua
        # getua=requests.post(get_urinalysis,data={'order_id':request.POST.get('orderid')}).json()
        # print(getua)

    except Exception as e:
        print(e)
        status='Unable to Save'

    

    return JsonResponse({'data':status,'ttype':ttype})    

###########################################
@csrf_exempt
def load_microscopy(request):
    req='MICRO'
    get_micro=requests.post(getLab_modality,data={'modality':req,'status':request.POST.get('rtype')}).json()
    for i in get_micro['data']:
        # age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
        i['enccode'] = i['enccode'].replace("/", "-")
        i['received_datetime'] = datetime.datetime.strptime(i['received_datetime'],"%Y-%m-%dT%H:%M:%S.%fZ")
        i['received_datetime']=datetime.datetime.strftime(i['received_datetime'], '%b %d, %y (%I:%M %p)')
        i['dodate'] = datetime.datetime.strptime(i['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
        i['dodate']=datetime.datetime.strftime(i['dodate'], '%b %d, %Y (%I:%M %p)')
        i['birthdate'] = datetime.datetime.strptime(i['birthdate'],"%Y-%m-%dT%H:%M:%S.%fZ")
        i['birthdate']=datetime.datetime.strftime(i['birthdate'], '%b %d, %Y')
        # i['uomcode'] = age['data']
        # print(i)
    status={
        'result':get_micro['data'],
    }

    return JsonResponse({'data':status})   
########################################### OPD RELEASE RESULT
@csrf_exempt
def opd_release_result(request):
    rtest=request.POST.getlist('test[]')
    ordid=request.POST.get('orderid')
    encc=request.POST.get('encc')
    rtype=request.POST.get('rtype')
    orno=request.POST.get('orno')
    amountp=request.POST.get('amount')
    tamount=request.POST.get('tamount')
    try:
        opd_rel=requests.post(releasing,data={'date':now(),'type':rtype,'order_id':ordid,'amount':int(amountp),'total_paid':int(tamount),'charge_by':request.session['employee_id'],'proccode':rtest}).json()
        if opd_rel['status'] == 'success':
            get_rel=requests.post(get_released,data={'order_id':ordid}).json()
            # print(get_rel)
    except Exception as e:
        data=e
    get_test = requests.post(get_lab_request, data={'enccode':request.POST.get('encc'),'order_id':request.POST.get('orderid')}).json()
    for g in get_test['laboratory']:
        for d in rtest:
            if g['prikey'] == d:
                    recep_rel_res=requests.post(update_status, data={'key':d, 'enccode': request.POST.get('encc'),'order_id':request.POST.get('orderid'),'receive':g['received_specimen'], 'status':'RELEASED','remarks':'Released'}).json()
    
    return JsonResponse({'data':recep_rel_res['status']})

########################################### RECEPTION

@csrf_exempt
def release_result(request):
    rtest=request.POST.getlist('test[]')
    get_test = requests.post(get_lab_request, data={'enccode':request.POST.get('encc'),'order_id':request.POST.get('orderid')}).json()
    for g in get_test['laboratory']:
        for d in rtest:
            if g['prikey'] == d:
                    recep_rel_res=requests.post(update_status, data={'key':d, 'enccode': request.POST.get('encc'),'order_id':request.POST.get('orderid'),'receive':g['received_specimen'], 'status':'RELEASED','remarks':'Released'}).json()

    return JsonResponse({'data':recep_rel_res['status']})

@csrf_exempt
def get_endorsement(resquest):
    endorse=[]
    get_micro=requests.post(getLab_modality,data={'modality':'MICRO','status':'ENDORSED'}).json()
    if len(get_micro['data']) > 0:
        for e in get_micro['data']:
            endorse.append(e)
    get_chemi=requests.post(getLab_modality,data={'modality':'CHEMI','status':'ENDORSED'}).json()
    if len(get_chemi['data']) > 0:
        for e in get_chemi['data']:
            endorse.append(e)
    get_hemat=requests.post(getLab_modality,data={'modality':'HEMAT','status':'ENDORSED'}).json()
    if len(get_hemat['data']) > 0:
        for e in get_hemat['data']:
            endorse.append(e)
    get_serol=requests.post(getLab_modality,data={'modality':'SEROL','status':'ENDORSED'}).json()
    if len(get_serol['data']) > 0:
        for e in get_serol['data']:
            endorse.append(e)
    get_bacti=requests.post(getLab_modality,data={'modality':'BACTI','status':'ENDORSED'}).json()
    if len(get_bacti['data']) > 0:
        for e in get_bacti['data']:
            endorse.append(e)
    get_immuno=requests.post(getLab_modality,data={'modality':'IMMUN','status':'ENDORSED'}).json()
    if len(get_immuno['data']) > 0:
        for e in get_immuno['data']:
            endorse.append(e)
    get_thyro=requests.post(getLab_modality,data={'modality':'THYRO','status':'ENDORSED'}).json()
    if len(get_thyro['data']) > 0:
        for e in get_thyro['data']:
            endorse.append(e)
    get_cardi=requests.post(getLab_modality,data={'modality':'CARDI','status':'ENDORSED'}).json()
    if len(get_cardi['data']) > 0:
        for e in get_cardi['data']:
            endorse.append(e)
    get_blgas=requests.post(getLab_modality,data={'modality':'BLGAS','status':'ENDORSED'}).json()
    if len(get_blgas['data']) > 0:
        for e in get_blgas['data']:
            endorse.append(e)
    get_tumor=requests.post(getLab_modality,data={'modality':'TUMOR','status':'ENDORSED'}).json()
    if len(get_tumor['data']) > 0:
        for e in get_tumor['data']:
            endorse.append(e)
    # doctOrder = requests.post(doctorsOrderPatient).json()
    # labrequest=doctOrder['data'] 
  
    # for l in labrequest:
    #     if l['toecode'] != 'OPD':
         
    #         get_examination = requests.post(get_lab_request, data={'enccode': l['enccode'],'order_id':l['order_id']}).json()
    #         test_=get_examination['laboratory']
         
    #         for e in test_:
    #             if e['status'] =='ENDORSE':
    #                 e['uomcode'] =l['patlast']+', '+l['patfirst']
    #                 e['orcode']=l['toecode']
    #                 e['pcchrgcod']=l['order_id']
    #                 e['datemod'] = datetime.datetime.strptime(e['datemod'],"%Y-%m-%dT%H:%M:%S.%fZ")
    #                 e['datemod']=datetime.datetime.strftime(e['datemod'], '%b %d, %y (%I:%M %p)')
    #                 endorse.append(e)
 
    return JsonResponse({'data':endorse})


@csrf_exempt
def test_endorsement(request):
    remarks=request.POST.get('en_remarks')
    pkey=request.POST.get('en_key')
    encc=request.POST.get('en_encc')
    orderid=request.POST.get('en_orderid')
    endorse=requests.post(update_status, data={'key':pkey, 'enccode': encc,'order_id':orderid, 'status':'ENDORSE','remarks':remarks}).json()
    data=endorse['status']
    return JsonResponse({'data':data})

@csrf_exempt
def test_cancel(request):
    pkey=request.POST.get('key')
    orderid=request.POST.get('ordid')
    encc=request.POST.get('encc')
    get_test = requests.post(get_lab_request, data={'enccode':encc,'order_id':orderid}).json()
    for g in get_test['laboratory']:
      if g['prikey'] == pkey:
              cancel=requests.post(update_status, data={'key':pkey, 'enccode': encc,'order_id':orderid,'receive':g['received_specimen'], 'status':'CANCELLED','remarks':'Cancelled'}).json()
              data=cancel['status']
    # cancel=requests.post(update_status, data={'key':pkey, 'enccode': encc,'order_id':orderid, 'status':'CANCELLED'}).json()
    # data=cancel['status']
    return JsonResponse({'data':data})

@csrf_exempt
def request_notif(request):
    # status=''
    new=[]
    test=[]
    find_=[]
    try:
        doctOrder = requests.post(doctorsOrderPatient).json()
        labrequest=doctOrder['data']   
      
        for l in labrequest:
            if l['received_by'] is None and l['toecode'] != 'OPD':
               new.append(l['toecode'])
               get_examination = requests.post(get_lab_request, data={'enccode': l['enccode'],'order_id':l['order_id']}).json()
               test_=get_examination['laboratory']
            #    print(test_)
               if len(test_) > 0:
                    find_.append(l['toecode'])
               else:
                   status=0  
               ward=l['toecode']
            else:
                status=0
             
    except Exception as e:
        err=e
    if len(find_) > 0:
        status=1
    else:
        status=0
  
    return JsonResponse({'status':status,'ward':new})

@csrf_exempt
def accept_endorsement(request):
    key=request.POST.get('key')
    encc=request.POST.get('encc')
    orderid=request.POST.get('orderid')
 
    endorse=requests.post(update_status, data={'key': key, 'enccode':encc,'order_id':orderid, 'status':'PENDING','remarks':'This is a Remarks'}).json()
    data=endorse['status']
    return JsonResponse({'data':data})


@csrf_exempt
def get_request(request):
    ward=request.POST.get('wd')
    doctOrder = requests.post(doctorsOrderPatient).json()
    labrequest=doctOrder['data']    
    request=[]
    er=[]
    cc=1
    inp=[]
    result_=[]
    result =[]
    endorse=[]
    od=''
    for i in labrequest:
        ordid=i['order_id']
        enctr=i['enccode']
        
        if i['toecode'] == 'ADM':
            inp.append(i['toecode'])
        
        if i['toecode'] == 'ER':
            er.append(i['toecode'])

        if i['toecode'] == ward:
            request.append(i)
            # if ordid != od:
            #     od=i['order_id']
            #     request.append(i)
            #     print('not same')
            #     print(od)
            # else:
            #     print('same')

            i['enccode'] = i['enccode'].replace("/", "-")
            
            if i['received_datetime'] is not None:
                i['received_datetime'] = datetime.datetime.strptime(i['received_datetime'],"%Y-%m-%dT%H:%M:%S.%fZ")
                i['received_datetime']=datetime.datetime.strftime(i['received_datetime'], '%b %d, %y (%I:%M %p)')
            # get_examination = requests.post(get_lab_request, data={'enccode': enctr,'order_id':ordid}).json()
            # test_=get_examination['laboratory']

            # if len(test_) > 0:
            #     request.append(i)

            # for e in test_:
        
            #     if e['status'] == 'ENDORSE':
            #         endorse.append(e['status'])
                
            # if len(test_) > 0:
            #     result_.append(i)
                
            #     i['released_by']=len(test_)     
            # else:
            #     i['released_by'] = 0
    
    return JsonResponse({'status':result_,'t_inp':len(inp),'t_er':len(er),'t_endorse':len(endorse),'request':request})

###########################################
@csrf_exempt
def load_lastmeal(request):
     lastmeal=''
     ext_time=''
     getchemres=requests.post(get_chem_result,data={
         'order_id':request.POST.get('ordid'),
         'enccode':request.POST.get('encc')
     }).json()
     for c in getchemres['data']:
         lastmeal=c['last_meal']
         ext_time=c['extraction_time']
    
     return JsonResponse({'lastmeal':lastmeal,'exttime':ext_time})

############################################
@csrf_exempt
def recep_update_sample(request):
    modality=request.POST.get('modality')
    encc=request.POST.get('encc')
    orderid=request.POST.get('orderid')
    hpercode=request.POST.get('hpercode')
    now=str(datetime.datetime.now().strftime("%b %d,%y(%I:%M %p)"))
    lastmeal=request.POST.get('lastM')
    exttime=request.POST.get('extTime')
    if modality == 'CHEMI':
         chem_res=requests.post(save_chem, data={
                'enccode':encc,
                'order_id':orderid,
                'hpercode':hpercode,
                'date':datetime.datetime.now(),
                'last_meal':lastmeal,
                'extraction_time':exttime,
                # 'hba1c':'',
                # 'glucose_fbs':'',
                # 'glucose_rbs':'',
                # 'cholesterol':'',
                # 'triglycerides':'',
                # 'hdl_cholesterol':'',
                # 'ldl_cholesterol':'',
                # 'blood_uric':'',
                # 'blood_urea':'',
                # 'creatinine':'',
                # 'alt_sgpt':'',
                # 'ast_sgot':'',
                # 'potassium':'',
                # 'sodium':'',
                # 'chloride':'',
                # 'total_calcium':'',
                # 'ionized_calcium':'',
                # 'magnesium':'',
                # 'phosphorus':'',
                # 'total_protein':'',
                # 'albumin':'',
                # 'globulin':'',
                # 'ag_ratio':'',
                # 'alkaline_phospatase':'',
                # 'amylase':'',
                # 'lipase':'',
                # 'ldh':'',
                # 'total_bilirubin':'',
                # 'direct_bilirubin':'',
                # 'indirect_bilirubin':'',
                'perform_by':request.session['employee_id'],
                # 'verified_by':'',
            }).json()
    
    
    if modality == 'CHEMI' or modality == 'IMMUN' or modality == 'THYRO' or modality == 'CARDI' or modality == 'BLGAS' or modality == 'TUMOR' or modality == 'SEROL' or modality == 'HEMAT' :
        data='success'
        get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
        for g in get_test['laboratory']:
            if g['modality'] == modality and g['status'] != 'CANCELLED':
                key=g['prikey']
                try:
                    samplemodality=requests.post(update_status, data={'key':key, 'enccode': encc,'order_id':orderid,'receive':now, 'status':'PENDING','remarks':'Specimen Received'}).json()
                except Exception as e:
                    data=e
            else:
                data=''
    
    else:
        samplemodality=requests.post(update_status, data={'key': request.POST.get('pkey'), 'enccode': encc,'order_id':orderid,'receive':now, 'status':'PENDING','remarks':'Specimen Received'}).json()
        data=samplemodality['status']
            
      
    return JsonResponse({'status':data})

def opd_laboratory(request):
    return render(request, 'integrated/laboratory/opd_laboratory.html')

def laboratory(request):
    if request.session.get('employee_id') is not None:
        return render(request, 'integrated/laboratory/dashboard.html', {'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def laboratory_patient_search(request):
    if request.method == "POST":
        hospital_no = request.POST.get('no')
        lastname = request.POST.get('lastname')
        firstname = request.POST.get('firstname')
        middlename = request.POST.get('middlename')
        birthdate = request.POST.get('birthdate')
        if birthdate != '':
            birthdate = datetime.strptime(birthdate, '%Y-%m-%d')
            birthdate = datetime.strftime(birthdate, '%Y/%m/%d')
        result = requests.post(search_api, data={'hospno': hospital_no, 'lastname': lastname, 'firstname': firstname, 'middlename': middlename, 'birthdate': birthdate}).json()
        if result['status'] == "success":
            list_ = result['data']
            return render(request, 'integrated/him/search_result.html', {'page': 'HIM', 'user_level': request.session['user_level'], 'name': request.session['name'], 'user_level': user_level, 'list': list_})
    return render(request, 'integrated/laboratory/search.html', {'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})

def search_patient(request):
    if request.method=="POST":
        
        getAll=request.post(all_patients_api,data={'lastname':'CECILIO'}).json()
        if getAll['status']=='success':
            list_=getAll['data']
      
            return render(request, 'integrated/laboratory/search_patient.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': list_})
    return render(request, 'integrated/laboratory/search_patient.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})

def to_process(request,key,enctr,orderid):
    get_examination = requests.post(get_lab_request, data={'enccode': enctr,'order_id':orderid}).json()
    for g in get_examination['laboratory']: 
        if g['prikey'] == key:
            sentToProcess=requests.post(update_status, data={'key': key, 'enccode': enctr,'order_id':orderid, 'status':'ONPROCESS','receive':g['received_specimen']}).json()
    return HttpResponseRedirect("/lab_microscopy")

def lab_microscopy(request):
  
    return render(request, 'integrated/laboratory/microscopy/index.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})




# ################## microscopy new update

@csrf_exempt
def getfa_result(request):
    orderid=request.POST.get('orderid')

    getfa=requests.post(get_fecalysis, data={'order_id':orderid}).json()


    return JsonResponse({'data':getfa,'curr_user':request.session['employee_id']})

@csrf_exempt
def getua_result(request):

    orderid=request.POST.get('orderid')
    getua=requests.post(get_urinalysis,data={'order_id':orderid}).json()
    data=getua['data']

    return JsonResponse({'data':data,'status':getua,'curr_user':request.session['employee_id']})


@csrf_exempt
def micro_test(request):
    encc=request.POST.get('encc')
    orderid=request.POST.get('ord')
    proccode=request.POST.get('procode')
    test=[]
    testproc=[]
    get_examination = requests.post(get_lab_request, data={'enccode': encc,'order_id':orderid}).json()

    for g in get_examination['laboratory']:

        if proccode == 'LABOR00081' or proccode == 'LABOR00078' or proccode == 'LABOR00076':
            ttype='URINE'
            if g['proccode'] == 'LABOR00081' or g['proccode'] == 'LABOR00078' or g['proccode'] == 'LABOR00076' and g['status'] != 'CANCELLED':
                test.append(g['procdesc'])
                testproc.append(g['proccode'])
            
        elif proccode == 'LABOR00407' or proccode == 'LABOR00334':
            ttype='STOOL'
            if g['proccode'] == 'LABOR00407' or g['proccode'] == 'LABOR00334' and g['status'] != 'CANCELLED':
                test.append(g['procdesc'])
                testproc.append(g['proccode'])
        else:
            ttype='Not Recognized'
            test=[]

    data=test
    return JsonResponse({'data':data,'type':ttype,'action':'ONPROCESS','testproc':testproc})

@csrf_exempt
def micro_update_stat(request):
    action=request.POST.get('micro_action')
    encc=request.POST.get('micro_encc')
    orderid=request.POST.get('micro_orderid')
    ttype=request.POST.get('micro_type')

    get_examination = requests.post(get_lab_request, data={'enccode': encc,'order_id':orderid}).json()
    for g in get_examination['laboratory']:
        if ttype == 'URINE':
            if g['proccode'] == 'LABOR00081' or g['proccode'] == 'LABOR00078' or g['proccode'] == 'LABOR00076' and g['status'] != 'CANCELLED':
                microtest=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':orderid, 'status':action,'receive':g['received_specimen']}).json()
                data=microtest['status']

        elif ttype == 'STOOL':
            if g['proccode'] == 'LABOR00407' or g['proccode'] == 'LABOR00334' and g['status'] != 'CANCELLED':
                microtest=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':orderid, 'status':action,'receive':g['received_specimen']}).json()
                data=microtest['status']


    return JsonResponse({'data':data})

################################## End new Update

@csrf_exempt
def get_micro(request):
    req_type=request.POST.get('type')
    req='MICRO'
    get_gending=requests.post(getLab_modality,data={'modality':req,'status':'PENDING'}).json()
    get_onprocess=requests.post(getLab_modality,data={'modality':req,'status':'ONPROCESS'}).json()
    get_toverify=requests.post(getLab_modality,data={'modality':req,'status':'TO VERIFY'}).json()
    get_completed=requests.post(getLab_modality,data={'modality':req,'status':'COMPLETED'}).json()
    micro_pending_data=get_gending['data']
    micro_onprocess_data=get_onprocess['data']
    micro_toverify_data=get_toverify['data']
    micro_completed_data=get_completed['data']
    tpending=len(micro_pending_data)
    tonprocess=len(micro_onprocess_data)
    tcompleted=len(micro_completed_data)
    ttoverify=len(micro_toverify_data)
    
    get_req=requests.post(getLab_modality,data={'modality':'MICRO','status':req_type}).json()
    for i in get_req['data']:
        i['enccode'] = i['enccode'].replace("/", "-")
        i['dodate'] = datetime.datetime.strptime(i['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
        i['dodate']=datetime.datetime.strftime(i['dodate'], '%b %d, %y (%I:%M %p)')
        age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
        i['uomcode']=age['data']

    return JsonResponse({'data':get_req}) 


def lab_chemistry(request):

    return render(request, 'integrated/laboratory/chemistry/index.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})

def lab_hematology(request):

    return render(request, 'integrated/laboratory/hematology/index2.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})


def load_hemaMachine(request):
    data='POTAKA'
    return JsonResponse({'data':data})


def lab_opdxt_walkin(request):

    return render(request, 'integrated/laboratory/opd/walkin.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})

def lab_opdxt_opd(request):
    doctOrder = requests.post(doctorsOrderPatient).json()
    opdrequest=doctOrder['data']

    return render(request, 'integrated/laboratory/opd/opd.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name'],'opdrequest':opdrequest})

def lab_reception(request):

    return render(request, 'integrated/laboratory/reception/index.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})

def lab_rapidtest(request):

    
    return render(request, 'integrated/laboratory/rapidtest/index.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})


@csrf_exempt
def addkit(request):
    kitname=request.POST.get('kit_name')
    lotno=request.POST.get('lot_no')
    expiry=request.POST.get('expiry_date')
    modality=request.POST.get('modality')
    try:
        newkit=requests.post(su_kit, data={'kit_name':kitname,'lot_no':lotno,'expiry_date':expiry,'modality':modality,'status':'INACTIVE'}).json()
        if newkit['status'] == 'success':
            data='ok'
    except Exception as e:
        data=e
    return JsonResponse({'data':data})

@csrf_exempt
def change_kit(request):
    kitid=request.POST.get('kit_id')
    kitname=request.POST.get('kitname')
    lotno=request.POST.get('lot_no')
    modality=request.POST.get('modality')
    allkits=requests.post(allkit).json()
    for k in allkits['data']:
        if k['kit_id'] == kitid:
            usekit=requests.post(su_kit, data={'kit_name':k['kit_name'],'kit_id':kitid,'lot_no':'31ADH457B','expiry_date':k['expiry_date'],'modality':k['modality'],'status':'ACTIVE'}).json()
        else:
            updatekit=requests.post(su_kit, data={'kit_name':k['kit_name'],'kit_id':k['kit_id'],'lot_no':k['lot_no'],'expiry_date':k['expiry_date'],'modality':k['modality'],'status':'INACTIVE'}).json()
    data='ok'
    return JsonResponse({'data':data})

@csrf_exempt
def update_kit(request):
    kitid=request.POST.get('ukitid')
    kitname=request.POST.get('ukit_name')
    lotno=request.POST.get('ulot_no')
    expiry=request.POST.get('uexpiry_date')
    modality=request.POST.get('umodality')
    status=request.POST.get('ustatus')
    try:
        upkit=requests.post(su_kit, data={'kit_name':kitname,'kit_id':kitid,'lot_no':lotno,'expiry_date':expiry,'modality':modality,'status':status}).json()
        data=upkit['status']
    except Exception as e:
        data='Err'
        print(e)

        

    return JsonResponse({'data':data})


@csrf_exempt
def get_kit(request):
    data=[]
    allkits=requests.post(allkit).json()

    return JsonResponse({'data':allkits['data']})


def lab_bacteriology(request):
    kit=[]
    # gk=requests.post(getkit).json()
    try:
        allkits=requests.post(allkit).json()
        for k in allkits['data']:
            if k['status'] == 'ACTIVE' and k['modality'] == 'BACTI':
                k['expiry_date'] = datetime.datetime.strptime(k['expiry_date'],"%Y-%m-%dT%H:%M:%S.%fZ")
                k['expiry_date']=datetime.datetime.strftime(k['expiry_date'], '%b %d, %Y')

                kit.append(k)
            #     ukit=k['kit_name']
            #     lotno=k['lot_no']
            #     expiry=k['expiry_date']
            # else:
            #     ukit=''
            #     lotno=''
                # expiry=''
        
    except Exception as e:
            print(e)
            # ukit=''
            # lotno=''
            # expiry=''
    if len(kit) == 1:
        skit=kit
    else:
        skit=''
    
   
   
    return render(request, 'integrated/laboratory/bacteriology/index.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name'],'skit':skit})


def unseen_lab_request_details(request, enctr, orderid):
    lab_user=request.session.get('employee_id')

    
    seen_update=requests.post(put_orderDetails, data={'order_id':orderid,'received_by':lab_user}).json()
    latestControl=requests.post(get_latest_control).json()
    list_ = []
    get_examination = requests.post(get_lab_request, data={'enccode': enctr,'order_id':orderid}).json()
    ptype=get_examination['toecode']
    if get_examination['status'] == 'success':
        list_ = get_examination['laboratory']
        patient_=get_examination['details']
        for i in list_:
            i['enccode'] = i['enccode'].replace("/", "-")
    
    return render(request, 'integrated/laboratory/reception/request_details.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list_': list_,'patient':patient_,'orderid':orderid,'enctr':enctr,'ptype':ptype})

def seen_lab_request_details(request, enctr, orderid):
    lab_user=request.session.get('employee_id')
    latestControl=requests.post(get_latest_control).json()
    list_ = []
    get_examination = requests.post(get_lab_request, data={'enccode': enctr,'order_id':orderid}).json()
    ptype=get_examination['toecode']
    if get_examination['status'] == 'success':
        list_ = get_examination['laboratory']
        patient_=get_examination['details']
        for i in list_:
            i['enccode'] = i['enccode'].replace("/", "-")
            ctr_no=i['control_no']
            receiver=i['receiver']
    return render(request, 'integrated/laboratory/reception/request_details.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list_': list_,'patient':patient_,'orderid':orderid,'enctr':enctr,'ctr_no':ctr_no,'receiver':receiver,'ptype':ptype})

def lab_request_confirmation(request, key, enctr, orderid):
    
    updateStatus = requests.post(update_status, data={'key': key, 'enccode': enctr,'order_id':orderid, 'status':'PENDING'}).json()
    if updateStatus['status'] == 'success':
        return HttpResponseRedirect("/" + enctr + "/" +orderid + "/seen_lab_request_details")
    else:
        return HttpResponseRedirect("/" +  enctr +"/" +orderid + "/seen_lab_request_details")
    
def lab_request_undo(request, key, enctr, orderid):
    
    updateStatus = requests.post(update_status, data={'key': key, 'enccode': enctr,'order_id':orderid, 'status':'None'}).json()
    if updateStatus['status'] == 'success':
        return HttpResponseRedirect("/" + enctr + "/" +orderid + "/seen_lab_request_details")
    else:
        return HttpResponseRedirect("/" +  enctr +"/" +orderid + "/seen_lab_request_details")
def lab_request_reject(request, key, enctr, orderid):
    
    updateStatus = requests.post(update_status, data={'key': key, 'enccode': enctr,'order_id':orderid, 'status':'REJECTED'}).json()
    if updateStatus['status'] == 'success':
        return HttpResponseRedirect("/" + enctr + "/" +orderid + "/seen_lab_request_details")
    else:
        return HttpResponseRedirect("/" +  enctr +"/" +orderid + "/seen_lab_request_details")

def lab_request_confirm_all(request, enctr, orderid):
    chk_req=requests.post(get_lab_request, data={'enccode':enctr,'order_id':orderid}).json()
    test_d=chk_req['laboratory']
    teststat=[]
    update_allOrder= requests.post(accept_allOder, data={'enccode':enctr,'order_id':orderid,'status':'PENDING'}).json()
    for c in test_d:
        teststat.append(c['status'])
        
        if teststat != 'PENDING':
            st='not'
        else:
            st='yes'
    
    if update_allOrder['status'] == 'success':
        return HttpResponseRedirect("/" + enctr + "/" +orderid + "/seen_lab_request_details")
    else:
        return HttpResponseRedirect("/" +  enctr +"/" +orderid + "/seen_lab_request_details")
    
def generate_ctr(request,enctr,orderid,ptype):
    dat=datetime.date.today()
    nn=dat.strftime("%y")
    if ptype == 'ADM':
        pt='IN'
    elif ptype == 'ER':
        pt='ER'
    elif ptype == 'OPD':
        pt='OP'
    
    latestControl=requests.post(get_latest_control,data={'type':ptype}).json()
    if latestControl['status']== 'success':
        latestctr=latestControl['data']

        if len(latestctr) == 0:
            ctr=pt+''+nn+'-000001'
        else:
            for l in latestctr: 
                nw_ctr=l['control_no']
                ns=nw_ctr[:2]
                ls=nw_ctr[2:]
                d=ls.replace("-", "")
                nc=int(d)+1
                ncc=str(nc)
                ctr=nw_ctr[:2]+''+ncc[:2]+'-'+ncc[2:] 
        return HttpResponseRedirect("/" + enctr + "/" +orderid + "/seen_lab_request_details")
    else:
        return HttpResponseRedirect("/" +  enctr +"/" +orderid + "/seen_lab_request_details")

@csrf_exempt
def gen_ctr(request):
    dat=datetime.date.today()
    nn=dat.strftime("%y")
    ward=request.POST.get('ward')
    if ward == 'ADM':
        pt='IN'
    elif ward == 'ER':
        pt='ER'
    elif ward == 'OPD':
        pt='OP'
    try:
        latestControl=requests.post(get_latest_control,data={'type':ward}).json()
        
        if latestControl['status'] == 'success':
            latestctr=latestControl['data']
            if len(latestctr) == 0:
                ctr=pt+''+nn+'-000001'
            else:
                for l in latestctr: 
                    nw_ctr=l['control_no']
                    ns=nw_ctr[:2]
                    ls=nw_ctr[2:]
                    d=ls.replace("-", "")
                    nc=int(d)+1
                    ncc=str(nc)
                    ctr=nw_ctr[:2]+''+ncc[:2]+'-'+ncc[2:] 
    
            generate_ctr=requests.post(save_new_control_no,data={'enccode':request.POST.get('encc'),'order_id':request.POST.get('ordid'),'control_no':ctr}).json
            data='success'
    except Exception as e:
        data=e
    
    

    return JsonResponse({'data':data,'ctr':ctr})
    
    

def labres_chem(request,toecode,orderid,encc):

    try:
        chem_result=requests.post(get_chem_result,data={'order_id':orderid,'enccode':encc}).json()
        age=requests.post(get_age, data={'enccode':encc,'toecode':toecode}).json()
        
        chemres=chem_result['data']
        
        ptx_req=requests.post(get_lab_request, data={'enccode':encc,'order_id':orderid}).json()
      
        for p in ptx_req['laboratory']:
            # if p['modality'] == 'CHEMI':
            #     print(str(p['procdesc'])+' - '+str(p['proccode']))
            ctr=p['control_no']
        for c in chemres:
            c['date_verified'] = datetime.datetime.strptime(c['date_verified'],"%Y-%m-%dT%H:%M:%S.%fZ")
            c['date_verified']=datetime.datetime.strftime(c['date_verified'], '%b %d, %y (%I:%M %p)')
           


            if c['hba1c'] == ',':
                hba1c=''
                hba1c_nv='--------------'
                hba1c_flag=''
            else:
                hba1c_s=c['hba1c'].split(',')
                hba1c=hba1c_s[0]
                hba1c_nv=str(hba1c_s[1]+' - '+hba1c_s[2])
                
                nv=hba1c_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(hba1c) > float(hv[0]):
                    hba1c_flag='H'
                elif float(hba1c) < float(nv[0]):
                    hba1c_flag='L'
                else:
                    hba1c_flag='N'


            if c['glucose_fbs'] == ',':
                glucose_fbs=''
                glucose_fbs_nv='--------------'
                glucose_fbs_flag=''
            else:
                glucose_fbs_s=c['glucose_fbs'].split(',')
                glucose_fbs=glucose_fbs_s[0]
                glucose_fbs_nv=str(glucose_fbs_s[1]+' - '+glucose_fbs_s[2])

                nv=glucose_fbs_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(glucose_fbs) > float(hv[0]):
                    glucose_fbs_flag='H'
                elif float(glucose_fbs) < float(nv[0]):
                    glucose_fbs_flag='L'
                else:
                    glucose_fbs_flag='N'

            if c['glucose_rbs'] == ',':
                glucose_rbs=''
                glucose_rbs_nv='--------------'
                glucose_rbs_flag=''
            else:
                glucose_rbs_s=c['glucose_rbs'].split(',')
                glucose_rbs=glucose_rbs_s[0]
                glucose_rbs_nv=str(glucose_rbs_s[1]+' - '+glucose_rbs_s[2])

                nv=glucose_rbs_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(glucose_rbs) > float(hv[0]):
                    glucose_rbs_flag='H'
                elif float(glucose_rbs) < float(nv[0]):
                    glucose_rbs_flag='L'
                else:
                    glucose_rbs_flag='N'

            if c['cholesterol'] == ',':
                cholesterol=''
                cholesterol_nv='--------------'
                cholesterol_flag=''
            else:
                cholesterol_s=c['cholesterol'].split(',')
                cholesterol=cholesterol_s[0]
                cholesterol_nv=str(cholesterol_s[1]+' - '+cholesterol_s[2])

                nv=cholesterol_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(cholesterol) > float(hv[0]):
                    cholesterol_flag='H'
                elif float(cholesterol) < float(nv[0]):
                    cholesterol_flag='L'
                else:
                    cholesterol_flag='N'

            if c['triglycerides'] == ',':
                triglycerides=''
                triglycerides_nv='--------------'
                triglycerides_flag=''
            else:
                triglycerides_s=c['triglycerides'].split(',')
                triglycerides=triglycerides_s[0]
                triglycerides_nv=str(triglycerides_s[1]+' - '+triglycerides_s[2])
                # triglycerides_flag=''
                nv=triglycerides_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(triglycerides) > float(hv[0]):
                    triglycerides_flag='H'
                elif float(triglycerides) < float(nv[0]):
                    triglycerides_flag='L'
                else:
                    triglycerides_flag='N'

            if c['hdl_cholesterol'] == ',':
                hdl_cholesterol=''
                hdl_cholesterol_nv='--------------'
                hdl_cholesterol_flag=''

            else:
                hdl_cholesterol_s=c['hdl_cholesterol'].split(',')
                hdl_cholesterol=hdl_cholesterol_s[0]
                hdl_cholesterol_nv=str(hdl_cholesterol_s[1]+' - '+hdl_cholesterol_s[2])

                nv=hdl_cholesterol_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(hdl_cholesterol) > float(hv[0]):
                    hdl_cholesterol_flag='H'
                elif float(hdl_cholesterol) < float(nv[0]):
                    hdl_cholesterol_flag='L'
                else:
                    hdl_cholesterol_flag='N'
            
            if c['ldl_cholesterol'] == ',':
                ldl_cholesterol=''
                ldl_cholesterol_nv='--------------'
                ldl_cholesterol_flag=''
            else:
                ldl_cholesterol_s=c['ldl_cholesterol'].split(',')
                ldl_cholesterol=ldl_cholesterol_s[0]
                ldl_cholesterol_nv=str(ldl_cholesterol_s[1]+' - '+ldl_cholesterol_s[2])

                nv=ldl_cholesterol_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(ldl_cholesterol) > float(hv[0]):
                    ldl_cholesterol_flag='H'
                elif float(ldl_cholesterol) < float(nv[0]):
                    ldl_cholesterol_flag='L'
                else:
                    ldl_cholesterol_flag='N'
            
            if c['blood_uric'] == ',':
                blood_uric=''
                blood_uric_nv='--------------'
                blood_uric_flag=''
            else:
                blood_uric_s=c['blood_uric'].split(',')
                blood_uric=blood_uric_s[0]
                blood_uric_nv=str(blood_uric_s[1]+' - '+blood_uric_s[2])

                nv=blood_uric_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(blood_uric) > float(hv[0]):
                    blood_uric_flag='H'
                elif float(blood_uric) < float(nv[0]):
                    blood_uric_flag='L'
                else:
                    blood_uric_flag='N'

            if c['blood_urea'] == ',':
                blood_urea=''
                blood_urea_nv='--------------'
                blood_urea_flag=''
            else:
                blood_urea_s=c['blood_urea'].split(',')
                blood_urea=blood_urea_s[0]
                blood_urea_nv=str(blood_urea_s[1]+' - '+blood_urea_s[2])

                nv=blood_urea_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(blood_urea) > float(hv[0]):
                    blood_urea_flag='H'
                elif float(blood_urea) < float(nv[0]):
                    blood_urea_flag='L'
                else:
                    blood_urea_flag='N'

            if c['creatinine'] == ',':
                creatinine=''
                creatinine_nv='--------------'
                creatinine_flag=''
            else:
                creatinine_s=c['creatinine'].split(',')
                creatinine=creatinine_s[0]
                creatinine_nv=str(creatinine_s[1]+' - '+creatinine_s[2])

                nv=creatinine_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(creatinine) > float(hv[0]):
                    creatinine_flag='H'
                elif float(creatinine) < float(nv[0]):
                    creatinine_flag='L'
                else:
                    creatinine_flag='N'

            if c['alt_sgpt'] == ',':
                alt_sgpt=''
                alt_sgpt_nv='--------------'
                alt_sgpt_flag=''
            else:
                alt_sgpt_s=c['alt_sgpt'].split(',')
                alt_sgpt=alt_sgpt_s[0]
                alt_sgpt_nv=str(alt_sgpt_s[1]+' - '+alt_sgpt_s[2])

                nv=alt_sgpt_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(alt_sgpt) > float(hv[0]):
                    alt_sgpt_flag='H'
                elif float(alt_sgpt) < float(nv[0]):
                    alt_sgpt_flag='L'
                else:
                    alt_sgpt_flag='N'

            if c['ast_sgot'] == ',':
                ast_sgot=''
                ast_sgot_nv='--------------'
                ast_sgot_flag=''
            else:
                ast_sgot_s=c['ast_sgot'].split(',')
                ast_sgot=ast_sgot_s[0]
                ast_sgot_nv=str(ast_sgot_s[1]+' - '+ast_sgot_s[2])

                nv=ast_sgot_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(ast_sgot) > float(hv[0]):
                    ast_sgot_flag='H'
                elif float(ast_sgot) < float(nv[0]):
                    ast_sgot_flag='L'
                else:
                    ast_sgot_flag='N'

            if c['potassium'] == ',':
                potassium=''
                potassium_nv='--------------'
                potassium_flag=''
            else:
                potassium_s=c['potassium'].split(',')
                potassium=potassium_s[0]
                potassium_nv=str(potassium_s[1]+' - '+potassium_s[2])

                nv=potassium_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(potassium) > float(hv[0]):
                    potassium_flag='H'
                elif float(potassium) < float(nv[0]):
                    potassium_flag='L'
                else:
                    potassium_flag='N'

            if c['sodium'] == ',':
                sodium=''
                sodium_nv='--------------'
                sodium_flag=''
            else:
                sodium_s=c['sodium'].split(',')
                sodium=sodium_s[0]
                sodium_nv=str(sodium_s[1]+' - '+sodium_s[2])

                nv=sodium_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(sodium) > float(hv[0]):
                    sodium_flag='H'
                elif float(sodium) < float(nv[0]):
                    sodium_flag='L'
                else:
                    sodium_flag='N'

            if c['chloride'] == ',':
                chloride=''
                chloride_nv='--------------'
                chloride_flag=''
            else:
                chloride_s=c['chloride'].split(',')
                chloride=chloride_s[0]
                chloride_nv=str(chloride_s[1]+' - '+chloride_s[2])

                nv=chloride_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(chloride) > float(hv[0]):
                    chloride_flag='H'
                elif float(chloride) < float(nv[0]):
                    chloride_flag='L'
                else:
                    chloride_flag='N'

            if c['total_calcium'] == ',':
                total_calcium=''
                total_calcium_nv='--------------'
                total_calcium_flag=''
            else:
                total_calcium_s=c['total_calcium'].split(',')
                total_calcium=total_calcium_s[0]
                total_calcium_nv=str(total_calcium_s[1]+' - '+total_calcium_s[2])

                nv=total_calcium_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(total_calcium) > float(hv[0]):
                    total_calcium_flag='H'
                elif float(total_calcium) < float(nv[0]):
                    total_calcium_flag='L'
                else:
                    total_calcium_flag='N'

            if c['ionized_calcium'] == ',':
                ionized_calcium=''
                ionized_calcium_nv='--------------'
                ionized_calcium_flag=''
            else:
                ionized_calcium_s=c['ionized_calcium'].split(',')
                ionized_calcium=ionized_calcium_s[0]
                ionized_calcium_nv=str(ionized_calcium_s[1]+' - '+ionized_calcium_s[2])

                nv=ionized_calcium_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(ionized_calcium) > float(hv[0]):
                    ionized_calcium_flag='H'
                elif float(ionized_calcium) < float(nv[0]):
                    ionized_calcium_flag='L'
                else:
                    ionized_calcium_flag='N'

            if c['magnesium'] == ',':
                magnesium=''
                magnesium_nv='--------------'
                magnesium_flag=''
            else:
                magnesium_s=c['magnesium'].split(',')
                magnesium=magnesium_s[0]
                magnesium_nv=str(magnesium_s[1]+' - '+magnesium_s[2])

                nv=magnesium_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(magnesium) > float(hv[0]):
                    magnesium_flag='H'
                elif float(magnesium) < float(nv[0]):
                    magnesium_flag='L'
                else:
                    magnesium_flag='N'

            if c['phosphorus'] == ',':
                phosphorus=''
                phosphorus_nv='--------------'
                phosphorus_flag=''
            else:
                phosphorus_s=c['phosphorus'].split(',')
                phosphorus=phosphorus_s[0]
                phosphorus_nv=str(phosphorus_s[1]+' - '+phosphorus_s[2])

                nv=phosphorus_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(phosphorus) > float(hv[0]):
                    phosphorus_flag='H'
                elif float(phosphorus) < float(nv[0]):
                    phosphorus_flag='L'
                else:
                    phosphorus_flag='N'

            if c['total_protein'] == ',':
                total_protein=''
                total_protein_nv='--------------'
                total_protein_flag=''
            else:
                total_protein_s=c['total_protein'].split(',')
                total_protein=total_protein_s[0]
                total_protein_nv=str(total_protein_s[1]+' - '+total_protein_s[2])

                nv=total_protein_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(total_protein) > float(hv[0]):
                    total_protein_flag='H'
                elif float(total_protein) < float(nv[0]):
                    total_protein_flag='L'
                else:
                    total_protein_flag='N'

            if c['albumin'] == ',':
                albumin=''
                albumin_nv='--------------'
                albumin_flag=''
            else:
                albumin_s=c['albumin'].split(',')
                albumin=albumin_s[0]
                albumin_nv=str(albumin_s[1]+' - '+albumin_s[2])

                nv=albumin_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(albumin) > float(hv[0]):
                    albumin_flag='H'
                elif float(albumin) < float(nv[0]):
                    albumin_flag='L'
                else:
                    albumin_flag='N'

            if c['globulin'] == ',':
                globulin=''
                globulin_nv='--------------'
                globulin_flag=''
            else:
                globulin_s=c['globulin'].split(',')
                globulin=globulin_s[0]
                globulin_nv=str(globulin_s[1]+' - '+globulin_s[2])

                nv=globulin_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(globulin) > float(hv[0]):
                    globulin_flag='H'
                elif float(globulin) < float(nv[0]):
                    globulin_flag='L'
                else:
                    globulin_flag='N'

            if c['ag_ration'] == ',':
                ag_ration=''
                ag_ration_nv='--------------'
            else:
                ag_ration_s=c['ag_ration'].split(',')
                globulin=ag_ration_s[0]
                ag_ration_nv=str(ag_ration_s[1]+' - '+ag_ration_s[2])

            if c['alkaline_phospatase'] == ',':
                alkaline_phospatase=''
                alkaline_phospatase_nv='--------------'
                alkaline_phospatase_flag=''
            else:
                alkaline_phospatase_s=c['alkaline_phospatase'].split(',')
                alkaline_phospatase=alkaline_phospatase_s[0]
                alkaline_phospatase_nv=str(alkaline_phospatase_s[1]+' - '+alkaline_phospatase_s[2])

                nv=alkaline_phospatase_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(alkaline_phospatase) > float(hv[0]):
                    alkaline_phospatase_flag='H'
                elif float(alkaline_phospatase) < float(nv[0]):
                    alkaline_phospatase_flag='L'
                else:
                    alkaline_phospatase_flag='N'

            if c['amylase'] == ',':
                amylase=''
                amylase_nv='--------------'
                amylase_flag=''
            else:
                amylase_s=c['amylase'].split(',')
                amylase=amylase_s[0]
                amylase_nv=str(amylase_s[1]+' - '+amylase_s[2])

                nv=amylase_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(amylase) > float(hv[0]):
                    amylase_flag='H'
                elif float(amylase) < float(nv[0]):
                    amylase_flag='L'
                else:
                    amylase_flag='N'

            if c['lipase'] == ',':
                lipase=''
                lipase_nv='--------------'
                lipase_flag=''
            else:
                lipase_s=c['lipase'].split(',')
                lipase=lipase_s[0]
                lipase_nv=str(lipase_s[1]+' - '+lipase_s[2])

                nv=lipase_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(lipase) > float(hv[0]):
                    lipase_flag='H'
                elif float(lipase) < float(nv[0]):
                    lipase_flag='L'
                else:
                    lipase_flag='N'

            if c['GGT'] == ',':
                ggt=''
                ggt_nv='--------------'
            else:
                ggt_s=c['GGT'].split(',')
                ggt=ggt_s[0]
                ggt_nv=str(ggt_s[1]+' - '+ggt_s[2])

            if c['ldh'] == ',':
                ldh=''
                ldh_nv='--------------'
                ldh_flag=''
            else:
                ldh_s=c['ldh'].split(',')
                ldh=ldh_s[0]
                ldh_nv=str(ldh_s[1]+' - '+ldh_s[2])

                nv=ldh_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(ldh) > float(hv[0]):
                    ldh_flag='H'
                elif float(ldh) < float(nv[0]):
                    ldh_flag='L'
                else:
                    ldh_flag='N'

            if c['Ferritin'] == ',':
                ferritin=''
                ferritin_nv='--------------'
                ferritin_flag=''
            else:
                ferritin_s=c['Ferritin'].split(',')
                ferritin=ferritin_s[0]
                ferritin_nv=str(ferritin_s[1]+' - '+ferritin_s[2])

                nv=ferritin_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(ferritin) > float(hv[0]):
                    ferritin_flag='H'
                elif float(ferritin) < float(nv[0]):
                    ferritin_flag='L'
                else:
                    ferritin_flag='N'
            
            if c['Cortisol'] == ',':
                cortisol=''
                cortisol_nv='--------------'
                cortisol_flag=''
            else:
                cortisol_s=c['Cortisol'].split(',')
                cortisol=cortisol_s[0]
                cortisol_nv=str(cortisol_s[1]+' - '+cortisol_s[2])

                nv=cortisol_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(cortisol) > float(hv[0]):
                    cortisol_flag='H'
                elif float(cortisol) < float(nv[0]):
                    cortisol_flag='L'
                else:
                    cortisol_flag='N'

            
            if c['total_bilirubin'] == ',':
                total_bilirubin=''
                total_bilirubin_nv='--------------'
                total_bilirubin_flag=''
            else:
                total_bilirubin_s=c['total_bilirubin'].split(',')
                total_bilirubin=total_bilirubin_s[0]
                total_bilirubin_nv=str(total_bilirubin_s[1]+' - '+total_bilirubin_s[2])

                nv=total_bilirubin_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(total_bilirubin) > float(hv[0]):
                    total_bilirubin_flag='H'
                elif float(total_bilirubin) < float(nv[0]):
                    total_bilirubin_flag='L'
                else:
                    total_bilirubin_flag='N'

            if c['direct_bilirubin'] == ',':
                direct_bilirubin=''
                direct_bilirubin_nv='--------------'
                direct_bilirubin_flag=''
            else:
                direct_bilirubin_s=c['direct_bilirubin'].split(',')
                direct_bilirubin=direct_bilirubin_s[0]
                direct_bilirubin_nv=str(direct_bilirubin_s[1]+' - '+direct_bilirubin_s[2])

                nv=direct_bilirubin_s[2].split('-')
                hval=nv[1].strip()
                hv=hval.split(' ')
                if float(direct_bilirubin) > float(hv[0]):
                    direct_bilirubin_flag='H'
                elif float(direct_bilirubin) < float(nv[0]):
                    direct_bilirubin_flag='L'
                else:
                    direct_bilirubin_flag='N'

            if c['indirect_bilirubin'] == ',':
                indirect_bilirubin=''
                indirect_bilirubin_nv='--------------'
            else:
                indirect_bilirubin_s=c['indirect_bilirubin'].split(',')
                indirect_bilirubin=indirect_bilirubin_s[0]
                indirect_bilirubin_nv=str(indirect_bilirubin_s[1]+' - '+indirect_bilirubin_s[2])

            
            ################################

            data={
                'hba1c':hba1c,
                'hba1c_nv':hba1c_nv,
                'hba1c_flag':hba1c_flag,

                'glucose_fbs':glucose_fbs,
                'glucose_fbs_nv':glucose_fbs_nv,
                'glucose_fbs_flag':glucose_fbs_flag,

                'glucose_rbs':glucose_rbs,
                'glucose_rbs_nv':glucose_rbs_nv,
                'glucose_rbs_flag':glucose_rbs_flag,

                'cholesterol':cholesterol,
                'cholesterol_nv':cholesterol_nv,
                'cholesterol_flag':cholesterol_flag,

                'triglycerides':triglycerides,
                'triglycerides_nv':triglycerides_nv,
                'triglycerides_flag':triglycerides_flag,

                'hdl_cholesterol':hdl_cholesterol,
                'hdl_cholesterol_nv':hdl_cholesterol_nv,
                'hdl_cholesterol_flag':hdl_cholesterol_flag,

                'ldl_cholesterol':ldl_cholesterol,
                'ldl_cholesterol_nv':ldl_cholesterol_nv,
                'ldl_cholesterol_flag':ldl_cholesterol_flag,

                'blood_uric':blood_uric,
                'blood_uric_nv':blood_uric_nv,
                'blood_uric_flag':blood_uric_flag,

                'blood_urea':blood_urea,
                'blood_urea_nv':blood_urea_nv,
                'blood_urea_flag':blood_urea_flag,

                'creatinine':creatinine,
                'creatinine_nv':creatinine_nv,
                'creatinine_flag':creatinine_flag,

                'alt_sgpt':alt_sgpt,
                'alt_sgpt_nv':alt_sgpt_nv,
                'alt_sgpt_flag':alt_sgpt_flag,

                'ast_sgot':ast_sgot,
                'ast_sgot_nv':ast_sgot_nv,
                'ast_sgot_flag':ast_sgot_flag,

                'potassium':potassium,
                'potassium_nv':potassium_nv,
                'potassium_flag':potassium_flag,

                'sodium':sodium,
                'sodium_nv':sodium_nv,
                'sodium_flag':sodium_flag,

                'chloride':chloride,
                'chloride_nv':chloride_nv,
                'chloride_flag':chloride_flag,

                'total_calcium':total_calcium,
                'total_calcium_nv':total_calcium_nv,
                'total_calcium_flag':total_calcium_flag,

                'ionized_calcium':ionized_calcium,
                'ionized_calcium_nv':ionized_calcium_nv,
                'ionized_calcium_flag':ionized_calcium_flag,

                'magnesium':magnesium,
                'magnesium_nv':magnesium_nv,
                'magnesium_flag':magnesium_flag,

                'phosphorus':phosphorus,
                'phosphorus_nv':phosphorus_nv,
                'phosphorus_flag':phosphorus_flag,

                'total_protein':total_protein,
                'total_protein_nv':total_protein_nv,
                'total_protein_flag':total_protein_flag,

                'albumin':albumin,
                'albumin_nv':albumin_nv,
                'albumin_flag':albumin_flag,

                'globulin':globulin,
                'globulin_nv':globulin_nv,
                'globulin_flag':globulin_flag,

                'ag_ration':ag_ration,
                'ag_ration_nv':ag_ration_nv,

                'alkaline_phospatase':alkaline_phospatase,
                'alkaline_phospatase_nv':alkaline_phospatase_nv,
                'alkaline_phospatase_flag':alkaline_phospatase_flag,

                'amylase':amylase,
                'amylase_nv':amylase_nv,
                'amylase_flag':amylase_flag,

                'lipase':lipase,
                'lipase_nv':lipase_nv,
                'lipase_flag':lipase_flag,

                'ggt':ggt,
                'ggt_nv':ggt_nv,

                'ldh':ldh,
                'ldh_nv':ldh_nv,
                'ldh_flag':ldh_flag,

                'ferritin':ferritin,
                'ferritin_nv':ferritin_nv,
                'ferritin_flag':ferritin_flag,

                'cortisol':cortisol,
                'cortisol_nv':cortisol_nv,
                'cortisol_flag':cortisol_flag,
                
                'total_bilirubin':total_bilirubin,
                'total_bilirubin_nv':total_bilirubin_nv,
                'total_bilirubin_flag':total_bilirubin_flag,

                'direct_bilirubin':direct_bilirubin,
                'direct_bilirubin_nv':direct_bilirubin_nv,
                'direct_bilirubin_flag':direct_bilirubin_flag,

                'indirect_bilirubin':indirect_bilirubin,
                'indirect_bilirubin_nv':indirect_bilirubin_nv

            }
            
            ###################################
        if chem_result['status'] == 'success':       
            return render(request,'integrated/laboratory/result_form/chemistry-result.html',{'result':chemres,'res_data':data,'age':age['data'],'ctr':ctr,'ward':ptx_req['toecode']})
        else:
            # return HttpResponseRedirect("/errpage")
            print(chem_result)
    except Exception as e:
        print(e)
        # return HttpResponseRedirect("/errpage")

def errpage(html):
    htmldoc = html(string=html, base_url="integrated/laboratory/result_form/404.html")
    return htmldoc.write_pdf()

def labres_hema(request):
    
    return render(request,'integrated/laboratory/result_form/hematology.html')

def cbc_result(request,ward,physician,orderid,encc):
    ptx_req=requests.post(get_lab_request, data={'enccode':encc,'order_id':orderid}).json()
    
    # for c in ptx_req['details']:
    #     # print(c['birthdate'])
    #     c['birthdate'] = datetime.datetime.strptime(c['birthdate'],"%d-%m-%y %H:%M:%S.%f")
    #     c['birthdate']=datetime.datetime.strftime(c['birthdate'], '%b %d, %Y ')
    for p in ptx_req['laboratory']:
            ctr=p['control_no']
    cbc_res=requests.post(get_cbc_result, data={'order_id':orderid}).json()
    result=cbc_res['data']
    result_data=[]
    for c in result:
        c['date_verified'] = datetime.datetime.strptime(c['date_verified'],"%Y-%m-%dT%H:%M:%S.%fZ")
        c['date_verified']=datetime.datetime.strftime(c['date_verified'], '%b %d, %y (%I:%M %p)')

        if c['hemoglobin'] == ',':
            hemoglobin='-----'
            hemoglobin_res='-----'
            hemoglobin_nv='-----'
            hemoglobin_flag=''
        else:
            hemoglobin=c['hemoglobin'].split(',')
            hemoglobin_res=hemoglobin[0]
            hemoglobin_nv=hemoglobin[2]

            nv=hemoglobin[2].split('-')
            if float(hemoglobin_res) < float(nv[0]):
                hemoglobin_flag='L'
            elif float(hemoglobin_res) > float(nv[1]):
                hemoglobin_flag='H'
            else:
                hemoglobin_flag='N'

        if c['hematocrit'] == ',':
            hematocrit='-----'
            hematocrit_res='-----'
            hematocrit_nv='-----'
            hematocrit_flag=''
        else:
            hematocrit=c['hematocrit'].split(',')
            hematocrit_res=hematocrit[0]
            hematocrit_nv=hematocrit[2]

            nv=hematocrit[2].split('-')
            if float(hematocrit_res) < float(nv[0]):
                hematocrit_flag='L'
            elif float(hematocrit_res) > float(nv[1]):
                hematocrit_flag='H'
            else:
                hematocrit_flag='N'

        if c['rbc_count'] == ',':
            rbc_count='-----'
            rbc_count_res='-----'
            rbc_count_nv='-----'
            rbc_count_flag=''
        else:
            rbc_count=c['rbc_count'].split(',')
            rbc_count_res=rbc_count[0]
            rbc_count_nv=rbc_count[2]

            nv=rbc_count[2].split('-')
            if float(rbc_count_res) < float(nv[0]):
                rbc_count_flag='L'
            elif float(rbc_count_res) > float(nv[1]):
                rbc_count_flag='H'
            else:
                rbc_count_flag='N'

        if c['mcv'] == ',':
            mcv='-----'
            mcv_res='-----'
            mcv_nv='-----'
            mcv_flag=''
        else:
            mcv=c['mcv'].split(',')
            mcv_res=mcv[0]
            mcv_nv=mcv[2]
           
            nv=mcv[2].split('-')
            if float(mcv_res) < float(nv[0]):
                mcv_flag='L'
            elif float(mcv_res) > float(nv[1]):
                mcv_flag='H'
            else:
                mcv_flag='N'

        if c['mch'] == ',':
            mch='-----'
            mch_res='-----'
            mch_nv='-----'
            mch_flag=''
        else:
            mch=c['mch'].split(',')
            mch_res=mch[0]
            mch_nv=mch[2]
           
            nv=mch[2].split('-')
            if float(mch_res) < float(nv[0]):
                mch_flag='L'
            elif float(mch_res) > float(nv[1]):
                mch_flag='H'
            else:
                mch_flag='N'

        if c['mchc'] == ',':
            mchc='-----'
            mchc_res='-----'
            mchc_nv='-----'
            mchc_flag=''
        else:
            mchc=c['mchc'].split(',')
            mchc_res=mchc[0]
            mchc_nv=mchc[2]
           
            nv=mchc[2].split('-')
            if float(mchc_res) < float(nv[0]):
                mchc_flag='L'
            elif float(mchc_res) > float(nv[1]):
                mchc_flag='H'
            else:
                mchc_flag='N'

        if c['wbc_count'] == ',':
            wbc_count='-----'
            wbc_count_res='-----'
            wbc_count_nv='-----'
            wbc_count_flag=''
        else:
            wbc_count=c['wbc_count'].split(',')
            wbc_count_res=wbc_count[0]
            wbc_count_nv=wbc_count[2]
           
            nv=wbc_count[2].split('-')
            if float(wbc_count_res) < float(nv[0]):
                wbc_count_flag='L'
            elif float(wbc_count_res) > float(nv[1]):
                wbc_count_flag='H'
            else:
                wbc_count_flag='N'

        if c['neutrophil'] == ',':
            neutrophil='-----'
            neutrophil_res='-----'
            neutrophil_nv='-----'
            neutrophil_flag=''
        else:
            neutrophil=c['neutrophil'].split(',')
            neutrophil_res=neutrophil[0]
            neutrophil_nv=neutrophil[2]
           
            nv=neutrophil[2].split('-')
            if float(neutrophil_res) < float(nv[0]):
                neutrophil_flag='L'
            elif float(neutrophil_res) > float(nv[1]):
                neutrophil_flag='H'
            else:
                neutrophil_flag='N'

        if c['lymphocytes'] == ',':
            lymphocytes='-----'
            lymphocytes_res='-----'
            lymphocytes_nv='-----'
            lymphocytes_flag=''
        else:
            lymphocytes=c['lymphocytes'].split(',')
            lymphocytes_res=lymphocytes[0]
            lymphocytes_nv=lymphocytes[2]
           
            nv=lymphocytes[2].split('-')
            if float(lymphocytes_res) < float(nv[0]):
                lymphocytes_flag='L'
            elif float(lymphocytes_res) > float(nv[1]):
                lymphocytes_flag='H'
            else:
                lymphocytes_flag='N'

        if c['monocytes'] == ',':
            monocytes='-----'
            monocytes_res='-----'
            monocytes_nv='-----'
            monocytes_flag=''
        else:
            monocytes=c['monocytes'].split(',')
            monocytes_res=monocytes[0]
            monocytes_nv=monocytes[2]
           
            nv=monocytes[2].split('-')
            if float(monocytes_res) < float(nv[0]):
                monocytes_flag='L'
            elif float(monocytes_res) > float(nv[1]):
                monocytes_flag='H'
            else:
                monocytes_flag='N'

        if c['eosinophil'] == ',':
            eosinophil='-----'
            eosinophil_res='-----'
            eosinophil_nv='-----'
            eosinophil_flag=''
        else:
            eosinophil=c['eosinophil'].split(',')
            eosinophil_res=eosinophil[0]
            eosinophil_nv=eosinophil[2]
           
            nv=eosinophil[2].split('-')
            if float(eosinophil_res) < float(nv[0]):
                eosinophil_flag='L'
            elif float(eosinophil_res) > float(nv[1]):
                eosinophil_flag='H'
            else:
                eosinophil_flag='N'

        if c['basophils'] == ',':
            basophils='-----'
            basophils_res='-----'
            basophils_nv='-----'
            basophils_flag=''
        else:
            basophils=c['basophils'].split(',')
            basophils_res=basophils[0]
            basophils_nv=basophils[2]
           
            nv=basophils[2].split('-')
            if float(basophils_res) < float(nv[0]):
                basophils_flag='L'
            elif float(basophils_res) > float(nv[1]):
                basophils_flag='H'
            else:
                basophils_flag='N'

        if c['platelet_count'] == ',':
            platelet_count='-----'
            platelet_count_res='-----'
            platelet_count_nv='-----'
            platelet_count_flag=''
        else:
            platelet_count=c['platelet_count'].split(',')
            platelet_count_res=platelet_count[0]
            platelet_count_nv=platelet_count[2]
           
            nv=platelet_count[2].split('-')
            if float(platelet_count_res) < float(nv[0]):
                platelet_count_flag='L'
            elif float(platelet_count_res) > float(nv[1]):
                platelet_count_flag='H'
            else:
                platelet_count_flag='N'

        if c['reticulocytes_count'] == ',':
            reticulocytes_count='-----'
            reticulocytes_count_res='-----'
            reticulocytes_count_nv='-----'
            reticulocytes_count_flag=''
        else:
            reticulocytes_count=c['reticulocytes_count'].split(',')
            reticulocytes_count_res=reticulocytes_count[0]
            reticulocytes_count_nv=reticulocytes_count[2]
           
            nv=reticulocytes_count[2].split('-')
            if float(reticulocytes_count_res) < float(nv[0]):
                reticulocytes_count_flag='L'
            elif float(reticulocytes_count_res) > float(nv[1]):
                reticulocytes_count_flag='H'
            else:
                reticulocytes_count_flag='N'

        blood_group=c['blood_group']
        notes=c['note']

        cbc_res={
            'hemoglobin_res':hemoglobin_res,
            'hemoglobin_nv':hemoglobin_nv,
            'hemoglobin_flag':hemoglobin_flag,

            'hematocrit_res':hematocrit_res,
            'hematocrit_nv':hematocrit_nv,
            'hematocrit_flag':hematocrit_flag,

            'rbc_count_res':rbc_count_res,
            'rbc_count_nv':rbc_count_nv,
            'rbc_count_flag':rbc_count_flag,

            'mcv_res':mcv_res,
            'mcv_nv':mcv_nv,
            'mcv_flag':mcv_flag,

            'mch_res':mch_res,
            'mch_nv':mch_nv,
            'mch_flag':mch_flag,

            'mchc_res':mchc_res,
            'mchc_nv':mchc_nv,
            'mchc_flag':mchc_flag,

            'wbc_count_res':wbc_count_res,
            'wbc_count_nv':wbc_count_nv,
            'wbc_count_flag':wbc_count_flag,

            'neutrophil_res':neutrophil_res,
            'neutrophil_nv':neutrophil_nv,
            'neutrophil_flag':neutrophil_flag,

            'lymphocytes_res':lymphocytes_res,
            'lymphocytes_nv':lymphocytes_nv,
            'lymphocytes_flag':lymphocytes_flag,

            'monocytes_res':monocytes_res,
            'monocytes_nv':monocytes_nv,
            'monocytes_flag':monocytes_flag,

            'eosinophil_res':eosinophil_res,
            'eosinophil_nv':eosinophil_nv,
            'eosinophil_flag':eosinophil_flag,

            'basophils_res':basophils_res,
            'basophils_nv':basophils_nv,
            'basophils_flag':basophils_flag,

            'platelet_count_res':platelet_count_res,
            'platelet_count_nv':platelet_count_nv,
            'platelet_count_flag':platelet_count_flag,

            'reticulocytes_count_res':reticulocytes_count_res,
            'reticulocytes_count_nv':reticulocytes_count_nv,
            'reticulocytes_count_flag':reticulocytes_count_flag,

            'blood_group':blood_group,
            'notes':notes,

            'perform_by_name':c['perform_by_name'],
            'verify_by_name':c['verify_by_name'],
            'date_verified':c['date_verified'],

        }

        result_data.append(cbc_res)

    # print(result_data)
    return render(request,'integrated/laboratory/result_form/cbc_result.html',{'result':result_data,'patient':ptx_req['details'][0],'ctr':ctr,'doctor':physician,'ward':ward})


@csrf_exempt
def save_hema(request):
    cat=request.POST.get('htype')
    encc=request.POST.get('encc')
    orderid=request.POST.get('orderid')
    action=request.POST.get('action')

    hemoglobin=str(request.POST.get('hemoglobin'))+','+str(request.POST.get('hemoglobin_nv'))
    hematocrit=str(request.POST.get('hematocrit'))+','+str(request.POST.get('hematocrit_nv'))
    rbc_count=str(request.POST.get('rbc_count'))+','+str(request.POST.get('rbc_count_nv'))
    mcv=str(request.POST.get('mcv'))+','+str(request.POST.get('mcv_nv'))
    mch=str(request.POST.get('mch'))+','+str(request.POST.get('mch_nv'))
    mchc=str(request.POST.get('mchc'))+','+str(request.POST.get('mchc_nv'))
    wbc_count=str(request.POST.get('wbc_count'))+','+str(request.POST.get('wbc_count_nv'))
    neutrophil=str(request.POST.get('neutrophil'))+','+str(request.POST.get('neutrophil_nv'))
    lymphocytes=str(request.POST.get('lymphocytes'))+','+str(request.POST.get('lymphocytes_nv'))
    monocytes=str(request.POST.get('monocytes'))+','+str(request.POST.get('monocytes_nv'))
    eosinophil=str(request.POST.get('eosinophil'))+','+str(request.POST.get('eosinophil_nv'))
    basophils=str(request.POST.get('basophils'))+','+str(request.POST.get('basophils_nv'))
    platelet_count=str(request.POST.get('platelet_count'))+','+str(request.POST.get('platelet_count_nv'))
    reticulocytes_count=str(request.POST.get('reticulocytes'))+','+str(request.POST.get('reticulocytes_nv'))

    if cat == 'CBC':
        if action == 'INSERT':
            s_cbc=requests.post(save_cbc_result,data={
            'enccode':encc,
            'order_id':orderid,
            'date':datetime.datetime.now().date(),
            'control_no':request.POST.get('ctr'),
            'hemoglobin':hemoglobin,
            'hematocrit':hematocrit,
            'rbc_count':rbc_count,
            'mcv':mcv,
            'mch':mch,
            'mchc':mchc,
            'wbc_count':wbc_count,
            'diff_count':'',
            'neutrophil':neutrophil,
            'lymphocytes':lymphocytes,
            'monocytes':monocytes,
            'eosinophil':eosinophil,
            'basophils':basophils,
            'platelet_count':platelet_count,
            'blood_group':request.POST.get('bg'),
            'reticulocytes_count':reticulocytes_count,
            'note':request.POST.get('notes'),
            'perform_by':request.session['employee_id'],
        
            }).json()
            if s_cbc['status'] == 'success':
                get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
                for g in get_test['laboratory']:
                    if g['modality'] == 'HEMAT' and g['status'] !='CANCELLED':
                        if g['proccode'] == 'LABOR00406' or g['proccode'] == 'LABOR00408' or g['proccode'] == 'LABOR00022':
                            try:
                                samplemodality=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':orderid, 'status':'TOVERIFY','receive':g['received_specimen']}).json()
                                data=samplemodality['status']
                            except Exception as e:
                                print('error')
                                data=e
        
        elif action == 'VERIFY':
            s_cbc=requests.post(save_cbc_result,data={
            'enccode':encc,
            'order_id':orderid,
            'date':datetime.datetime.now().date(),
            'control_no':request.POST.get('ctr'),
            'hemoglobin':hemoglobin,
            'hematocrit':hematocrit,
            'rbc_count':rbc_count,
            'mcv':mcv,
            'mch':mch,
            'mchc':mchc,
            'wbc_count':wbc_count,
            'diff_count':'',
            'neutrophil':neutrophil,
            'lymphocytes':lymphocytes,
            'monocytes':monocytes,
            'eosinophil':eosinophil,
            'basophils':basophils,
            'platelet_count':platelet_count,
            'blood_group':request.POST.get('bg'),
            'reticulocytes_count':reticulocytes_count,
            'note':request.POST.get('notes'),
            'perform_by':request.POST.get('perform_id'),
            'verified_by':request.session['employee_id'],
        
            }).json()
            if s_cbc['status'] == 'success':
                get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
                for g in get_test['laboratory']:
                    if g['modality'] == 'HEMAT' and g['status'] !='CANCELLED':
                        if g['proccode'] == 'LABOR00406' or g['proccode'] == 'LABOR00408' or g['proccode'] == 'LABOR00022':
                            try:
                                samplemodality=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':orderid, 'status':'COMPLETED','receive':g['received_specimen']}).json()
                                data=samplemodality['status']
                            except Exception as e:
                                print('error')
                                data=e
    elif cat == 'COAG':
        data='No Coag database'

       
    return JsonResponse({'data':data})




def labres_rapidtest(request):
    
    return render(request,'integrated/laboratory/result_form/rapidtest.html')

def result_template(request):
    return render(request,'integrated/laboratory/result_form/rapidtest.html')

def main_rapidtest(request):
    
    return render(request,'integrated/laboratory/main/rapidtest.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})


def result_temp(request):
    logo = ImageReader(static_root + '/integrated/img/brghgmclogo.png')
    logo1 = ImageReader(static_root + '/integrated/img/dohlogo.png')
    padaba = ImageReader(static_root + '/integrated/img/pagpadaba.png')
    response = HttpResponse(content_type='application/pdf')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setPageSize((5.8465*inch,8.268*inch))
    p.drawImage(logo, 0.05*inch, 5.9*inch, mask='auto', width=32, height=32)
    p.drawImage(logo1, 0.5*inch, 5.9*inch, mask='auto', width=32, height=32)
    p.setFont("Times-Roman", 8, leading=None)
    p.setFillColor("green")
    p.drawString(1.0*inch, 6.3*inch, "Bicol Region General Hospital and Geriatric Medical Center")
    p.drawString(1.5*inch, 6.2*inch, "(Formely BICOL SANITARIUM)")
    p.setFillColor("black")
    p.drawString(1.35*inch, 6.1*inch, "San Pedro, Cabusao Camarines Sur")
    p.setFont("Times-Roman", 6, leading=None)
    p.drawString(1.2*inch, 6*inch, "Telephone Nos.: (054) 473-2244, 472-4422, 881-1033, 881-1761")
    p.drawString(1.3*inch, 5.9*inch, "E-mail Address: bicolsan@gmail.com, brghgmc@gmail.com")
    p.line(0, 5.8*inch, 1000, 5.8*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 12, leading=None)
    p.drawString(1.6*inch, 5.6*inch, "CHARGE SLIP")

    p.setFont("Times-Roman", 7, leading=None)
    p.drawString(2.6*inch, 5.4*inch, "Date:________________________ ")
    p.drawString(3.1*inch, 5.4*inch, '12-18-2023')
    p.drawString(0.2*inch, 5.2*inch, "Name:")
    p.setStrokeColorRGB(0.5,0.5,0.5) #choose your line color
    p.setLineWidth(0.1)
    p.line(35, 5.2*inch, 290, 5.2*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(0.6*inch, 5.21*inch, "SALVADOR B. CECILIO")
    p.setFont("Times-Roman", 7, leading=None)
    p.drawString(0.2*inch, 5*inch, "Address:")
    p.drawString(0.7*inch, 5.01*inch, "SIPOCOT")
    p.line(39, 5*inch, 290, 5*inch) #(x1, y1, x2, y2)
    
    p.drawString(0.2*inch, 4.8*inch, "Responsibility Center:")
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(1.2*inch, 4.8*inch, "LABORATORY")
    p.line(80, 4.79*inch, 290, 4.79*inch) #(x1, y1, x2, y2)

    p.setFont("Times-Roman", 7, leading=None)
    p.drawString(0.2*inch, 4.6*inch, "Hospital No.:")
    p.drawString(0.8*inch, 4.6*inch, "000000123")
    p.line(55, 4.59*inch, 290, 4.59*inch) #(x1, y1, x2, y2)

    data=  [['Qty', 'Particulars', 'Unit Price', 'Total'],
            ['1', 'URINALYSIS', '125', '125'],
            ['1', 'URINALYSIS', '125', '125'],
            ['1', 'URINALYSIS', '125', '125'],
            ['1', 'URINALYSIS', '125', '125'],
            ['', '', 'Total', '1125'],
        ]
    t = Table(data, colWidths=[0.5*inch, 1.5*inch, 0.9*inch, 0.9*inch])
    t.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (-1, -1), (-1, -1), 'TOP'),
            # ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONT', (0, 0), (-1, -1), 'Times-Roman', 8)
        ]))
    t.wrapOn(p, 0, 0)
    
    t.drawOn(p, 0.20*inch, 2*inch)
        

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(0.2*inch, 0.7*inch, "Issued by:")
    p.drawString(0.2*inch, 0.4*inch, "_______________________________")
    p.drawString(0.3*inch, 0.45*inch, request.session.get("name"))
    p.drawString(0.4*inch, 0.25*inch, "Signature Over Printed Name")
    p.drawString(2.5*inch, 0.7*inch, "Payment: ")
    p.drawString(2.5*inch, 0.5*inch, "OR No._______________________")
    p.drawString(2.5*inch, 0.3*inch, "Date.__________________________")

    p.line(0, 0.2*inch, 1000, 0.30*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Italic", 7, leading=None)
    p.drawString(0.1*inch, 0.1*inch, "BRGHGMC-F-AS-BIL-006")
    p.drawString(2*inch, 0.1*inch, "Rev 2")
    # p.drawString(2.9*inch, 0.1*inch, "Effectivity Date: January 6, 2020")
    p.drawImage(padaba, 2.9*inch, 0.05*inch, mask='auto', width=60, height=10)
    p.setTitle("MICROSCOPY")
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def result_Fecalysis(request,encc,orderid,proccode,toecode,ward):
    get_fa=requests.post(get_fecalysis,data={'order_id':orderid}).json()
    get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
    ptx_age=requests.post(get_age, data={'enccode':encc,'toecode':toecode}).json()
    for p in get_test['details']:
        patient=str(p['patlast']+', '+p['patfirst'])
        gender=p['patsex']
        hosno=p['hpercode']
        status=p['patcstat']

    for f in get_test['laboratory']:
        if f['proccode'] == 'LABOR00407' or f['proccode'] == 'LABOR00334':
            f['datemod'] = datetime.datetime.strptime(f['datemod'],"%Y-%m-%dT%H:%M:%S.%fZ")
            f['datemod']=datetime.datetime.strftime(f['datemod'], '%b %d, %Y (%I:%M %p)')
            data={
                'result_date':f['datemod'],
                'ctr_no':f['control_no'],
                'ward':ward,
                'patient':patient,
                'gender':gender,
                'hosno':hosno,
                'cstat':status,
                'age':ptx_age['data'],
                'result':get_fa['data']


            }
    # print(get_test)
    return render(request,'integrated/laboratory/result_form/fecalysis-result.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name'],'data':data,'r_data':get_fa['data']})


# def result_Fecalysis(request,encc,orderid,proccode,toecode,ward):
    get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
    for f in get_test['laboratory']:
        if f['proccode'] == 'LABOR00407' or f['proccode'] == 'LABOR00334':
            f['datemod'] = datetime.datetime.strptime(f['datemod'],"%Y-%m-%dT%H:%M:%S.%fZ")
            f['datemod']=datetime.datetime.strftime(f['datemod'], '%b %d, %Y (%I:%M %p)')
            resdate=f['datemod']
    get_fa=requests.post(get_fecalysis,data={'order_id':orderid}).json()
    ptx_age=requests.post(get_age, data={'enccode':encc,'toecode':toecode}).json()
    age=ptx_age['data']
    # print(encc+'-'+toecode)
    occult='--------'
    color='--------'
    consist='----------'
    rcb='-----------'
    wbc='-----------'
    yeast='------------'
    bacteria='---------'
    fat='-----------'
    chemi='-----------'
    ascaris='------'
    hookworm='-----'
    histo='----'
    coli='-----'
    trichu='-----'
    vermi='------'
    note='-----------'
    other='------------'
    if len(get_fa) == 2:
        for g in get_fa['data']:    
            if g['proccode'] == 'LABOR00334':
                occult=g['fecocbld']
    try:
        for f in get_fa['data']:
            ptx=f['name']
            dob=f['birthdate']
            sex=f['patsex']
            hospno=f['hpercode']
            physician=f['physician']
            if sex == 'M':
                sex='MALE'
            elif sex == 'F':
                sex='FEMALE'
            
            performBy=f['perform_by']
            verifyBy=f['verify_by']
            try:
                if f['proccode'] == 'LABOR00334':

                    occult=f['fecocbld']
                    
            except Exception as e:
                occult='--------------'
                data=e
            
            try:
                if f['proccode'] == 'LABOR00407':
                     #RESULT
                    if f['feccolor'] == '':
                        color='----------'
                    else:
                        color=f['feccolor']
                        
                    if f['fecon'] == '':    
                        consist='----------'
                    else:
                        consist=f['fecon']
                        
                    if f['fecrbc'] == '':
                        rcb='-----------'
                    else:
                        rcb=f['fecrbc']
                        
                    if f['fecwbc'] == '':
                        wbc='-----------'
                    else:
                        wbc=f['fecwbc']
                        
                    if f['fecyeast'] == '':
                        yeast='------------'
                    else:
                        yeast=f['fecyeast']
                        
                    if f['fecbac'] == '':
                        bacteria='---------'
                    else:
                        bacteria=f['fecbac']
                        
                    if f['fecfat'] == '':
                        fat='-----------'
                    else:
                        fat=f['fecfat']
                        
                    if f['fecchemi'] == '':
                        chemi='-----------'
                    else:
                        chemi=f['fecchemi']
                        
                    if f['fecascaris'] == '':
                        ascaris='------------'
                    else:
                        ascaris=f['fecascaris']
                        
                    if f['fechookworm'] == '':
                        hookworm='-----------'
                    else:
                        hookworm=f['fechookworm']
                        
                    if f['fechisto'] == '':
                        histo='----------'
                    else:
                        histo=f['fechisto']
                        
                    if f['feccoli'] == '':
                        coli='-----------'
                    else:
                        coli=f['feccoli']
                        
                    if f['fectrichuris'] == '':
                        trichu='-----------'
                    else:
                        trichu=f['fectrichuris']
                        
                    if f['fecvermi'] =='':
                        vermi='----------'
                    else:
                        vermi=f['fecvermi']
                        
                    if f['fecnote'] == '':
                        note='-----------'
                    else:
                        note=f['fecnote']
                        
                    if f['feothr'] == '':
                        other='------------'
                    else:
                        other=f['feothr']
                        
                    # if f['fecocbld'] is None or f['fecocbld'] == 'null':
                    #    occult=occult
                    
            except Exception as e:
                occult='-------------'
                data=e
        print(occult)
    except Exception as e:
        occult='-----------'
        data=e
  
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
    p.drawString(2.3*inch, 7.3*inch, "FECALYSIS")
    p.setLineWidth(0.1)
    p.setFont("Times-Roman", 8, leading=None)

    p.drawString(4.1*inch, 7.2*inch, "Date.:")
    p.line(325, 7.19*inch, 410, 7.19*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 9, leading=None)
    p.drawString(4.4*inch, 7.22*inch, resdate)
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(4.2*inch, 7*inch, "Control No.:")
    p.line(345, 7*inch, 410, 7*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 9, leading=None)
    p.drawString(4.8*inch, 7.02*inch,'INP23-0000021')

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(0.2*inch, 6.7*inch, "Name:")
    p.line(43, 6.7*inch, 220, 6.7*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 10, leading=None)
    p.drawString(0.6*inch, 6.72*inch, ptx)

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(3.2*inch, 6.7*inch, "Age:")
    p.line(250, 6.7*inch, 310, 6.7*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 10, leading=None)
    p.drawString(3.5*inch, 6.72*inch,str(age) )

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(4.4*inch, 6.7*inch, "Sex:")
    p.line(330, 6.7*inch, 410, 6.7*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 10, leading=None)
    p.drawString(5*inch, 6.72*inch, sex)

    # newline
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(0.2*inch, 6.5*inch, "Ward:")
    p.line(35, 6.5*inch, 130,6.5*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 10, leading=None)
    p.drawString(0.5*inch, 6.52*inch, ward)

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(1.85*inch, 6.5*inch, "Hospital No.:")
    p.line(180, 6.5*inch, 280,6.5*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 10, leading=None)
    p.drawString(2.5*inch, 6.52*inch, hospno)

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(3.95*inch, 6.5*inch, "Classification:")
    p.line(330, 6.5*inch, 410,6.5*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 10, leading=None)
    p.drawString(4.8*inch, 6.52*inch, "SERIVCES")

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(0.2*inch, 6.3*inch, "Requesting Physician:")
    p.line(85, 6.3*inch, 410, 6.3*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 10, leading=None)
    p.drawString(1.3*inch, 6.34*inch, physician)
    
    data=  [
            ['GROSS',' MICROSCOPIC:'],
            ['Color:           '+color,'RBC:                    '+ rcb +'  /HPF'],
            ['Consistency:     ' +consist,'WBC:                     '+wbc+' /HPF '],
            ['','Yeast Cells:        '+yeast],
            ['Chemical:   ','Bacteria:                    '+bacteria],
            ['','Fat Globules:                '+fat],
            ['Occult Blood:        '+occult,''],
          
      
            
        ]
    
    t = Table(data, colWidths=[ 2.5*inch,3*inch])
    t.setStyle(TableStyle([
            
            ('BOX', (0, 0), (-1, -1), 0.2, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.05, colors.gray),
            ('VALIGN', (-1, -1), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 2), (-1, 2), 'LEFT'),
            ('ALIGN',(3,1),(3,1),'CENTER'),
            ('FONT', (0, 0), (-1, -1), 'Times-Bold', 10)
        ]))
    t.wrapOn(p, 0, 0)
    
    t.drawOn(p, 0.22*inch, 4.2*inch)

    p.setFont("Times-Bold", 14, leading=None)
    p.drawString(2.2*inch, 3.5*inch, "PARASITES")
 
    pdata=  [
            ['Ascaris lumbricoides:   '+ascaris+'/LPF',' Trinchuris trichura:       '+trichu+' /LPF'],
            ['Hookworm:   '+hookworm+'/LPF',' Enterobius Vermicularis:       '+vermi+'/LPF'],
            ['Entamoeba Histolytica Cyst:  '+histo+'/LPF',' Others:    '+other],
            ['Entamoeba Coli Cyst:   '+coli+' /LPF',' '],
            ['NOTE:   '+note],
           
          
      
            
        ]
    
    pt = Table(pdata, colWidths=[ 2.5*inch,3*inch])
    pt.setStyle(TableStyle([
            
            ('BOX', (0, 0), (-1, -1), 0.2, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.05, colors.gray),
            ('VALIGN', (-1, -1), (-1, -1), 'MIDDLE'),
            
            ('ALIGN', (1, 2), (-1, 2), 'LEFT'),
            ('ALIGN',(3,1),(3,1),'CENTER'),
            ('FONT', (0, 0), (-1, -1), 'Times-Italic', 10)

        ]))
    pt.wrapOn(p, 0, 0)
    
    pt.drawOn(p, 0.22*inch, 2.1*inch)
    
    # style = ParagraphStyle(
    #     name='Normal',
    #     fontName='Inconsolata',
    #     fontSize=8,
    # )
    
    pb=performBy+'\nLic #0078995'
    vb=verifyBy+'\nLic #0078995'
    ab='RAYMUNDO B IBARRIENTOS, MD. \nLic #0078995'
   
  
    
    
    mdata=  [
            ['Performed By:','Verified By:','Approved By:'],
            [pb,vb,ab],
            ['Medical Technologist:','Medical Technologist:','Pathologisit'],
           
        ]
    
    mt = Table(mdata, colWidths=[ 1.8*inch,1.8*inch,1.8*inch],rowHeights=[0.2*inch,.70*inch,0.2*inch])
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
    
    mt.drawOn(p, 0.22*inch, .5*inch)
    

    p.line(0, 0.2*inch, 1000, 0.30*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Italic", 7, leading=None)
    p.drawString(0.1*inch, 0.1*inch, "BRGHGMC-F-MS-LAB-005")
    p.drawString(1.5*inch, 0.1*inch, "Rev 2")
    p.drawString(2.5*inch, 0.1*inch, "Effectivity Date: May 2, 2023")
    p.drawImage(padaba, 4.5*inch, 0.05*inch, mask='auto', width=80, height=10)

    p.setTitle("FECALYSIS -"+ptx)
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def result_Urinalysis(request,encc,orderid,wardname,doctor):
    getuaresult=requests.post(get_urinalysis,data={'order_id':orderid}).json()
    ptx_req=requests.post(get_lab_request, data={'enccode':encc,'order_id':orderid}).json()
    ptx_age=requests.post(get_age, data={'enccode':encc,'toecode':ptx_req['toecode']}).json()

    for t in ptx_req['laboratory']:
        ctr=t['control_no']
    
    for d in ptx_req['details']:
        gender=d['patsex']
        cstat=d['patcstat']
        hosno=d['hpercode']


    data={
        'control_no':ctr,
        'ward':wardname,
        'doctor':doctor,
        'hosno':hosno,
        'age':ptx_age['data'],
        'gender':gender,
        'cstat':cstat,
        'result':getuaresult['data']
    }
    # print(ptx_req['laboratory'])
    # print(getuaresult)
    return render(request,'integrated/laboratory/result_form/urinalysis-result.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name'],'data':data})
############################### HEMALOLOGY
@csrf_exempt
def load_hema(request):
    htype=request.POST.get('type')
    get_hema=requests.post(getLab_modality,data={'modality':'HEMAT','status':htype}).json()
    hdata=[]
    cc=0
    for i in get_hema['data']:
        cc=cc + 1
        i['enccode'] = i['enccode'].replace("/", "-")
        i['received_datetime'] = datetime.datetime.strptime(i['received_datetime'],"%Y-%m-%dT%H:%M:%S.%fZ")
        i['received_datetime']=datetime.datetime.strftime(i['received_datetime'], '%b %d, %y (%I:%M %p)')
        
        i['birthdate'] = datetime.datetime.strptime(i['birthdate'],"%Y-%m-%dT%H:%M:%S.%fZ")
        i['birthdate']=datetime.datetime.strftime(i['birthdate'], '%b %d, %Y')
    return JsonResponse({'data':get_hema['data']})

def get_hema_count(request):
    tpending=requests.post(getLab_modality,data={'modality':'HEMAT','status':'PENDING'}).json()
    tonprocess=requests.post(getLab_modality,data={'modality':'HEMAT','status':'ONPROCESS'}).json()
    tcompleted=requests.post(getLab_modality,data={'modality':'HEMAT','status':'TOVERIFY'}).json()
    treleased=requests.post(getLab_modality,data={'modality':'HEMAT','status':'COMPLETED'}).json()
    return JsonResponse({'tpending':len(tpending['data']),'tonprocess':len(tonprocess['data']),'tcompleted':len(tcompleted['data']),'treleased':len(treleased['data'])})

@csrf_exempt
def hema_sentToProcess(request):
    encc=request.POST.get('encc')
    ord=request.POST.get('orderid')
 
    get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':ord}).json()
    for g in get_test['laboratory']:

        if g['modality'] == 'HEMAT' and g['status'] == 'PENDING':
            try:
                samplemodality=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':ord, 'status':'ONPROCESS','receive':g['received_specimen']}).json()
                data=samplemodality['status']
            except Exception as e:
                data=e
        else:
            data=''
    return JsonResponse({'data':data}) 

@csrf_exempt
def hematest(request):
    encc=request.POST.get('encc')
    orderid=request.POST.get('orderid')
    ttype=request.POST.get('ttype')
    hema=[]
    n_values=[]
    normal_val=requests.post(machineAll).json()
    for n in normal_val['data']:
        if n['modality'] == 'HEMAT':
            n_values.append(n)

    get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()

    for h in get_test['laboratory']:
        if h['modality'] == 'HEMAT' and h['status'] != 'CANCELLED':
            # print(str(h['proccode'])+' - '+str(h['procdesc']))
            hema.append(h)

    return JsonResponse({'data':hema,'n_values':n_values})

@csrf_exempt
def gethematest(request):
    encc=request.POST.get('encc')
    orderid=request.POST.get('orderid')

    get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
    # for h in get_test['laboratory']:
        # print(h['proccode']+'-'+h['procdesc'])
    data=get_test
    return JsonResponse({'data':data})


@csrf_exempt
def sent_to_process(request):
    sentToProcess=requests.post(update_status, data={
        'key': request.POST.get('key'), 
        'enccode': request.POST.get('encc'),
        'order_id':request.POST.get('orderid'), 
        'status':'ONPROCESS'}).json()
    if sentToProcess['status'] == 'success':
        data='Process Success'
    else:
        data='Failed'
    return JsonResponse({'data':data})

@csrf_exempt
def hema_onprocess(request):
    data=requests.post(getLab_modality,data={'modality':'HEMAT','status':'ONPROCESS'}).json()
    return JsonResponse({'data':data}) 

@csrf_exempt
def save_cbc(request):
    encc=request.POST.get('h_encc')
    orderid=request.POST.get('h_orderid')
    hosno=request.POST.get('h_hpercode')
    key=request.POST.get('h_key')
    action=request.POST.get('action')
    if action == 'insert':
        s_cbc=requests.post(save_cbc_result,data={
        'enccode':encc,
        'order_id':orderid,
        'hpercode':hosno,
        'date':datetime.datetime.now().date(),
        'control_no':request.POST.get('h_ctr'),
        'hemoglobin':request.POST.get('hemoglobin'),
        'hematocrit':request.POST.get('hematocrit'),
        'rbc_count':request.POST.get('rbc_count'),
        'mcv':request.POST.get('mcv'),
        'mch':request.POST.get('mch'),
        'mchc':request.POST.get('mchc'),
        'wbc_count':request.POST.get('wbc'),
        'diff_count':request.POST.get('diff_count'),
        'neutrophil':request.POST.get('neutro'),
        'lymphocytes':request.POST.get('lymphocytes'),
        'monocytes':request.POST.get('monocytes'),
        'eosinophil':request.POST.get('eosinophil'),
        'basophils':request.POST.get('basophils'),
        'platelet_count':request.POST.get('pc'),
        'blood_group':request.POST.get('bg'),
        'reticulocytes_count':request.POST.get('retic'),
        'note':request.POST.get('notes'),
        'perform_by':request.session['employee_id'],
       
        }).json()
        if s_cbc['status'] == 'success':
            sentoverify=requests.post(update_status, data={'key': key, 'enccode': encc,'order_id':orderid, 'status':'TOVERIFY'}).json()
            if sentoverify['status'] == 'success':
                data='ok'
            else:
                data='Sent to Verify Error'
    elif action == 'verify':
        s_cbc=requests.post(save_cbc_result,data={
        'enccode':encc,
        'order_id':orderid,
        'hpercode':hosno,
        'date':datetime.datetime.now().date(),
        'control_no':request.POST.get('h_ctr'),
        'hemoglobin':request.POST.get('hemoglobin'),
        'hematocrit':request.POST.get('hematocrit'),
        'rbc_count':request.POST.get('rbc_count'),
        'mcv':request.POST.get('mcv'),
        'mch':request.POST.get('mch'),
        'mchc':request.POST.get('mchc'),
        'wbc_count':request.POST.get('wbc'),
        'diff_count':request.POST.get('diff_count'),
        'neutrophil':request.POST.get('neutro'),
        'lymphocytes':request.POST.get('lymphocytes'),
        'monocytes':request.POST.get('monocytes'),
        'eosinophil':request.POST.get('eosinophil'),
        'basophils':request.POST.get('basophils'),
        'platelet_count':request.POST.get('pc'),
        'blood_group':request.POST.get('bg'),
        'reticulocytes_count':request.POST.get('retic'),
        'note':request.POST.get('notes'),
        'perform_by':request.POST.get('perform_id'),
        'verified_by':request.session['employee_id'],
        }).json()
        if s_cbc['status'] == 'success':
            sentcompleted=requests.post(update_status, data={'key': key, 'enccode': encc,'order_id':orderid, 'status':'COMPLETED'}).json()
            if sentcompleted['status'] == 'success':
                data='ok'
            else:
                data='Sent to Verify Error'
    return JsonResponse({'data':data})

################################## GET CBC RESULT
@csrf_exempt
def getCbcResult(request):
    orderid=request.POST.get('orderid')
    encc=request.POST.get('encc')
    cbc_test=[]
    cbc=requests.post(get_cbc_result,data={'order_id':orderid}).json()

    n_values=[]
    normal_val=requests.post(machineAll).json()
    for n in normal_val['data']:
        if n['modality'] == 'HEMAT':
            n_values.append(n)

    get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
    for t in get_test['laboratory']:
        if t['modality'] == 'HEMAT':
            if t['proccode']=='LABOR00406' or t['proccode'] == 'LABOR00408' or t['proccode'] == 'LABOR00022':
                cbc_test.append(t)


    return JsonResponse({'res_data':cbc['data'],'test_data':cbc_test,'n_values':n_values})
################################## CHEMISTRY
@csrf_exempt
def chem_get_lastmeal(request):
    ord=request.POST.get('orderid')
    encc=request.POST.get('encc')
    lastmeal=''
    ext_time=''
    try:
        getlastmeal=requests.post(get_chem_result,data={'order_id':ord,'enccode':encc}).json()
        for c in getlastmeal['data']:
                 lastmeal=c['last_meal']
                 ext_time=c['extraction_time']
        data={
            'lastmeal':lastmeal,
            'ext_time':ext_time
        }
    except Exception as e:
        data={
            'lastmeal':'NONE',
            'ext_time':'NONE'
        }
 
    return JsonResponse({'data':data})

@csrf_exempt

def chem_completed(request):
    encc=request.POST.get('encc')
    ord=request.POST.get('orderid')
    modality=request.POST.get('modality')
    normal_val=requests.post(machineAll).json()
    data=[]
    try:
        getchemresult=requests.post(get_chem_result,data={'order_id':ord,'enccode':encc}).json()
        chem_res=getchemresult['data']
    except Exception as e:
        chem_res=[]
        print(e)
    
    try:
        get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':ord}).json()
        for g in get_test['laboratory']:
            if g['modality'] == 'CHEMI' and g['status'] !='CANCELLED':
                key=g['prikey']
                data.append(g['proccode']) 

    except Exception as e:
        print(e)
        data=[]
    return JsonResponse({'data':data,'chemresult':chem_res,'n_values':normal_val['data']})
  

@csrf_exempt
def chem_onprocess(request):
    encc=request.POST.get('encc')
    ord=request.POST.get('orderid')
    modality=request.POST.get('modality')
    pdata=[]
    td=[]

    normal_val=requests.post(machineAll).json()

    # print(normal_val['data'])

    try:
        get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':ord}).json()
        
        for g in get_test['laboratory']:
            if g['modality'] == 'CHEMI' and g['status'] != 'CANCELLED':
                key=g['prikey']
                # td.append(g['procdesc'])
                pdata.append(g['proccode'])   
                # print(g['procdesc']+'-'+g['proccode']+' - '+g['enccode']) 
    
    except Exception as e:
        data=[]
        print(e)
    return JsonResponse({'data':pdata,'td':td,'n_values':normal_val['data']})
 

@csrf_exempt
def chem_sentToProcess(request):
    modality=request.POST.get('modality')
    encc=request.POST.get('encc')
    ord=request.POST.get('orderid')
    get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':ord}).json()
    for g in get_test['laboratory']:
        if g['modality'] == modality and g['status'] != 'CANCELLED':
            key=g['prikey']
            try:
                samplemodality=requests.post(update_status, data={'key':key, 'enccode': encc,'order_id':ord, 'status':'ONPROCESS','receive':g['received_specimen']}).json()
                data=samplemodality['status']
            except Exception as e:
                data=e
        else:
            data=''
    return JsonResponse({'data':data}) 

def load_chem_count(request):
    c_pending=requests.post(getLab_modality,data={'modality':'CHEMI','status':'PENDING'}).json()
    c_onprocess=requests.post(getLab_modality,data={'modality':'CHEMI','status':'ONPROCESS'}).json()
    c_toverify=requests.post(getLab_modality,data={'modality':'CHEMI','status':'TOVERIFY'}).json()
    c_completed=requests.post(getLab_modality,data={'modality':'CHEMI','status':'COMPLETED'}).json()
    data={
        'cpending':len(c_pending['data']),
        'conprocess':len(c_onprocess['data']),
        'ccompleted':len(c_completed['data']),
        'cverify':len(c_toverify['data'])
    }
    return JsonResponse({'data':data})

@csrf_exempt
def load_chemi(request):
    
    htype=request.POST.get('type')
    get_chemi=requests.post(getLab_modality,data={'modality':'CHEMI','status':htype}).json()
    req=[]
    ctr=''
    chem_data=[]
    for i in get_chemi['data']:
        if i['status'] !='CANCELLED' or i['status'] !='ENDORSED':
            i['enccode'] = i['enccode'].replace("/", "-")
            i['dodate'] = datetime.datetime.strptime(i['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['dodate']=datetime.datetime.strftime(i['dodate'], '%b %d, %y (%I:%M %p)')

    return JsonResponse({'data':get_chemi['data']}) 

def upload_hema(request):

    return render(request,'integrated/laboratory/upload/hema_result.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})


@csrf_exempt
def csv_upload(request):
    csv_file = request.FILES.get("attendance-file")
    data=csv_file
    return JsonResponse({'data':data})


@csrf_exempt
def coag_hema_result(request):


    return render(request,'integrated/laboratory/result_form/coag-result.html')