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



static_root = "http://173.10.7.2/medsys-static-files"
#root = "http://173.10.2.108:9092/"
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
    doctOrder = requests.post(doctorsOrderPatient).json()
    labrequest=doctOrder['data']
    for i in labrequest:
        if i['toecode'] != 'OPD':
            i['enccode'] = i['enccode'].replace("/", "-")
            ordid=i['order_id']
            enctr=i['enccode']
            if i['received_datetime'] is not None:
                i['received_datetime'] = datetime.datetime.strptime(i['received_datetime'],"%Y-%m-%dT%H:%M:%S.%fZ")
                i['received_datetime']=datetime.datetime.strftime(i['received_datetime'], '%b %d, %y (%I:%M %p)')
            get_examination = requests.post(get_lab_request, data={'enccode': enctr,'order_id':ordid}).json()
            details=get_examination['details']
            for d in details:
        
                test_=get_examination['laboratory']
                for e in test_:
                
                    if e['status'] == 'COMPLETED':
                        data={
                            'ctr':e['control_no'],
                            'patient':d['patlast']+', '+d['patfirst'],
                            'labtest':e['procdesc'],
                            # 'wardname':d['wardname'],
                            'date':e['datemod'],
                            'encc':i['enccode'],
                            'orderid':i['order_id'],
                            'toecode':i['toecode']
                        }
                        torel.append(data)
    if len(torel) == 0:
        data=0
    else:
        data=len(torel)
    
    
    return JsonResponse({'data':data})

@csrf_exempt
def get_torelease(request):
    torel=[]
    ward=''
    doctOrder = requests.post(doctorsOrderPatient).json()
    labrequest=doctOrder['data']
    for i in labrequest:
        if i['toecode'] != 'OPD':
            i['enccode'] = i['enccode'].replace("/", "-")
            ordid=i['order_id']
            enctr=i['enccode']
            if i['received_datetime'] is not None:
                i['received_datetime'] = datetime.datetime.strptime(i['received_datetime'],"%Y-%m-%dT%H:%M:%S.%fZ")
                i['received_datetime']=datetime.datetime.strftime(i['received_datetime'], '%b %d, %y (%I:%M %p)')
            get_examination = requests.post(get_lab_request, data={'enccode': enctr,'order_id':ordid}).json()
            details=get_examination['details']
            # print(details)
            for d in details:
                try:
                    ward=d['wardname']
                except Exception as e:
                    ward=d['tsdesc']
                test_=get_examination['laboratory']
            
                for e in test_:
                    if len(test_) > 0:
                        try:
                            e['dodate'] = datetime.datetime.strptime(e['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
                            e['dodate']=datetime.datetime.strftime(e['dodate'], '%b %d, %y (%I:%M %p)')
                            dodate=e['dodate']
                        except Exception as err:
                            dodate=''
                        
                    else:
                        dodate=''
                    if e['status'] == 'COMPLETED':
                        data={
                            'prikey':e['prikey'],
                            'proccode':e['proccode'],
                            'ctr':e['control_no'],
                            'patient':d['patlast']+', '+d['patfirst'],
                            'labtest':e['procdesc'],
                            'ward':ward,
                            'date':e['datemod'],
                            'encc':i['enccode'],
                            'orderid':i['order_id'],
                            'dodate':dodate,
                            'toecode':i['toecode']
                        }
                        torel.append(data)
            
    data=torel
    return JsonResponse({'data':data})

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
    gdata=[]
    try:
        get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
        for s in get_test['laboratory']:
            if s['modality'] == 'BACTI':
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
            i['dodate'] = datetime.datetime.strptime(i['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['dodate']=datetime.datetime.strftime(i['dodate'], '%b %d, %y (%I:%M %p)')
            age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
            i['uomcode']=age['data']
            hdata.append(i)
    return JsonResponse({'data':hdata})

@csrf_exempt
def bio_sentToProcess(request):
    modality=request.POST.get('modality')
    encc=request.POST.get('encc')
    ord=request.POST.get('orderid')
    key=request.POST.get('key')
    get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':ord}).json()
    for g in get_test['laboratory']:
        if g['modality'] == 'BACTI':
            try:
                samplemodality=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':ord, 'status':'ONPROCESS','receive':g['received_specimen']}).json()
                data=samplemodality['status']
            except Exception as e:
                data=e
        else:
            data=''
    data=get_test['laboratory']
    return JsonResponse({'data':data}) 

@csrf_exempt
def save_bio(request):
    action=request.POST.get('action')
    encc=request.POST.get('i_encc')
    orderid=request.POST.get('i_orderid')
    hosno=request.POST.get('i_hpercode')
    key=request.POST.get('i_key')
    ctr=request.POST.get('i_ctr')
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
                    if g['modality'] == 'BACTI':
                        try:
                            samplemodality=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':orderid, 'status':'TOVERIFY','receive':g['received_specimen']}).json()
                            data=samplemodality['status']
                        except Exception as e:
                            data=e
                    else:
                        data=''
            else:
                data='error add Result'
        except Exception as e:
            data='failed'
    elif action == 'verify':
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
                    if g['modality'] == 'BACTI':
                        try:
                            samplemodality=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':orderid, 'status':'COMPLETED','receive':g['received_specimen']}).json()
                            data=samplemodality['status']
                        except Exception as e:
                            data=e
                    else:
                        data=''
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

            age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
            i['uomcode']=age['data']
            hdata.append(i)
        else:
            test=test + 1            
        
    return JsonResponse({'data':hdata})

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
                        data='Failed Add Status'
                

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
    return render(request,'integrated/laboratory/result_form/serology.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name'],'test':sero_res['data'][0],'ptx':ptx[0],'ward':ward,'doctor':physician})


##################################### IMMUNOLOGY

@csrf_exempt
def immuno_ToProcess(request):
    encc=request.POST.get('encc')
    ord=request.POST.get('orderid')
    try:
        get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':ord}).json()
        for g in get_test['laboratory']:
            if g['modality'] == 'IMMUN' or g['modality'] == 'THYRO' or g['modality'] == 'CARDI' or g['modality'] == 'BLGAS' or g['modality'] == 'TUMOR':
                try:
                    samplemodality=requests.post(update_status, data={'key':g['prikey'], 'enccode': encc,'order_id':ord, 'status':'ONPROCESS','receive':g['received_specimen']}).json()
                    data=samplemodality['status']
                except Exception as e:
                    data=e
            else:
                data=''
    except Exception as e:
        data=e
    return JsonResponse({'data':data}) 


@csrf_exempt
def get_immunview(request):
    encc=request.POST.get('encc')
    orderid=request.POST.get('orderid')
    gdata=[]
    try:
        get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
        for s in get_test['laboratory']:
            if s['modality'] == 'IMMUN' or s['modality'] == 'THYRO' or s['modality'] == 'CARDI' or s['modality'] == 'BLGAS' or s['modality'] == 'TUMOR':
                gdata.append(s)
                data = gdata
    except Exception as e:
        data=e
    return JsonResponse({'data':data})


def lab_immuno(request):

    return render(request,'integrated/laboratory/immuno/index.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})

@csrf_exempt
def load_immuno(request):
    stat=request.POST.get('type')
    get_immun=requests.post(getLab_modality,data={'modality':'IMMUN','status':stat}).json()
    get_thyro=requests.post(getLab_modality,data={'modality':'THYRO','status':stat}).json()
    get_cardi=requests.post(getLab_modality,data={'modality':'CARDI','status':stat}).json()
    get_tumor=requests.post(getLab_modality,data={'modality':'TUMOR','status':stat}).json()
    get_blgas=requests.post(getLab_modality,data={'modality':'TUMOR','status':stat}).json()
    hdata=[]
    display=[]
    test=0
    cc=0
    encc=''
    ctr=''
    ntest=0
  
    for i in get_immun['data']:
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

            age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
            i['uomcode']=age['data']
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
            i['dodate'] = datetime.datetime.strptime(i['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['dodate']=datetime.datetime.strftime(i['dodate'], '%b %d, %Y (%I:%M %p)')

            i['received_datetime'] = datetime.datetime.strptime(i['received_datetime'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['received_datetime']=datetime.datetime.strftime(i['received_datetime'], '%b %d, %Y (%I:%M %p)')

            age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
            i['uomcode']=age['data']
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
            i['dodate'] = datetime.datetime.strptime(i['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['dodate']=datetime.datetime.strftime(i['dodate'], '%b %d, %Y (%I:%M %p)')

            i['received_datetime'] = datetime.datetime.strptime(i['received_datetime'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['received_datetime']=datetime.datetime.strftime(i['received_datetime'], '%b %d, %Y (%I:%M %p)')

            age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
            i['uomcode']=age['data']
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
            i['dodate'] = datetime.datetime.strptime(i['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['dodate']=datetime.datetime.strftime(i['dodate'], '%b %d, %Y (%I:%M %p)')

            i['received_datetime'] = datetime.datetime.strptime(i['received_datetime'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['received_datetime']=datetime.datetime.strftime(i['received_datetime'], '%b %d, %Y (%I:%M %p)')

            age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
            i['uomcode']=age['data']
            hdata.append(i)
        else:
            test=test + 1 
    for i in get_blgas['data']:
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

            age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
            i['uomcode']=age['data']
            hdata.append(i)
        else:
            test=test + 1 
    
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

   
    if action == 'insert':
        a_immuno=requests.post(su_immuno,data={
            'enccode':encc,
            'order_id':orderid,
            'hpercode':hosno,
            'date': datetime.datetime.now().date(),
            'control_no': request.POST.get('i_ctr'),
            'kit_name':'kit',
            'troponin_i':request.POST.get('tropinin'),
            'ck_mb':request.POST.get('ckmb'),
            'tsh':request.POST.get('tsh'),
            'ca_125':request.POST.get('ca125'),
            'ft4':request.POST.get('ft4'),
            'ft3':request.POST.get('ft3'),
            't4':request.POST.get('t4'),
            't3':request.POST.get('t3'),
            'aso':request.POST.get('aso'),
            'crp':request.POST.get('crp'),
            'hscrp':'',
            'procalcitonin':request.POST.get('procal'),
            'reheu':request.POST.get('rheu'),
            'psa':request.POST.get('psa'),
            'pro_bnp':request.POST.get('probnp'),
            'cea':request.POST.get('cea'),
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

                    else:
                        data='failed modality'
            except Exception as e:
                data=e
        else:
            data=a_immuno['status']
    elif action == 'verify':
        u_immuno=requests.post(su_immuno,data={
            'enccode':encc,
            'order_id':orderid,
            'hpercode':hosno,
            'date': datetime.datetime.now().date(),
            'control_no': request.POST.get('i_ctr'),
            'kit_name':'kit',
            'troponin_i':request.POST.get('tropinin'),
            'ck_mb':request.POST.get('ckmb'),
            'tsh':request.POST.get('tsh'),
            'ca_125':request.POST.get('ca125'),
            'ft4':request.POST.get('ft4'),
            'ft3':request.POST.get('ft3'),
            't4':request.POST.get('t4'),
            't3':request.POST.get('t3'),
            'aso':request.POST.get('aso'),
            'crp':request.POST.get('crp'),
            'hscrp':'',
            'procalcitonin':request.POST.get('procal'),
            'reheu':request.POST.get('rheu'),
            'psa':request.POST.get('psa'),
            'pro_bnp':request.POST.get('probnp'),
            'cea':request.POST.get('cea'),
            'note':request.POST.get('notes'),
            # 'perform_by':request.POST.get('perform_id'),
            'verified_by':request.session['employee_id'],
        }).json()
        # up_stat=requests.post(update_status, data={'key':key, 'enccode': encc,'order_id':orderid, 'status':'COMPLETED'}).json()
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
                    else:
                        data=''
            except Exception as e:
                data=e
        else:
            data='Error Verifying!'

    return JsonResponse({'data':data})

@csrf_exempt
def get_immunoResult(request):
    orderid=request.POST.get('orderid')
    immuno_res=requests.post(im_result, data={'order_id': orderid}).json()
    return JsonResponse({'data':immuno_res['data']})

@csrf_exempt
def immuno_result(request,ward,physician,orderid,encc):
    # i_res=requests.post(immuno_result, data={'enccode': encc}).json()
    get_examination = requests.post(get_lab_request, data={'enccode': encc,'order_id':orderid}).json()
    ptx=get_examination['details']
    getres=requests.post(im_result,data={'order_id':orderid}).json()
    for i in getres['data']:
            i['date_verified'] = datetime.datetime.strptime(i['date_verified'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['date_verified']=datetime.datetime.strftime(i['date_verified'], '%b %d, %Y (%I:%M %p)')
    
    return render(request,'integrated/laboratory/result_form/immunosero.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name'],'test':getres['data'][0],'ptx':ptx[0],'ward':ward,'doctor':physician})
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

    get_examination = requests.post(get_lab_request, data={'enccode': encc,'order_id':orderid}).json()
    tests=get_examination['laboratory']
    ptx=get_examination['details']
    # ward=get_examination['toecode']

    for c in tests:
        ctr=c['control_no']
    doctor=''
    for d in labrequest:
        if d['control_no'] == ctr:
           doctor=d['physician']
   
    return render(request, 'integrated/laboratory/print/lab_request.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name'],'test':tests,'ward':ward,'ptx':ptx,'ctr':ctr,'doctor':doctor})



########################################## BACTERIOLOGY
@csrf_exempt
def load_bacti(request):
    pending=[]
    onprocess=[]
    toverify=[]
    completed=[]
    op=[]
   
    htype=request.POST.get('rtype')
    get_bacti=requests.post(getLab_modality,data={'modality':'BACTI','status':htype}).json()
    pen_bacti=requests.post(getLab_modality,data={'modality':'BACTI','status':'PENDING'}).json()
    on_bacti=requests.post(getLab_modality,data={'modality':'BACTI','status':'ONPROCESS'}).json()
    tovery_bacti=requests.post(getLab_modality,data={'modality':'BACTI','status':'TO VERIFY'}).json()
    compl_bacti=requests.post(getLab_modality,data={'modality':'BACTI','status':'COMPLETED'}).json()
    req=[]
    ctr=''
    for i in get_bacti['data']:
        i['enccode'] = i['enccode'].replace("/", "-")
        i['dodate'] = datetime.datetime.strptime(i['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
        i['dodate']=datetime.datetime.strftime(i['dodate'], '%b %d, %y (%I:%M %p)')

        i['received_datetime'] = datetime.datetime.strptime(i['received_datetime'],"%Y-%m-%dT%H:%M:%S.%fZ")
        i['received_datetime']=datetime.datetime.strftime(i['received_datetime'], '%b %d, %y (%I:%M %p)')

        age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
        i['uomcode']=age['data']
    return JsonResponse({'data':get_bacti['data'],'pend':len(pen_bacti['data']),'onp':len(on_bacti['data']),'tovery':len(tovery_bacti['data']),'compl':len(compl_bacti['data'])})

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
            print(save_rdt)
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
########################################## CHEMISTRY
@csrf_exempt
def getlabtest(request):
    chem_test=[]
    get_test=requests.post(get_lab_request,data={'enccode':request.POST.get('encc'),'order_id':request.POST.get('orderid')}).json()
   
    for c in get_test['laboratory']:
        if c['status'] != 'CANCELLED':
    
            chem_test.append(c)
    return JsonResponse({'data':chem_test})


def save_chem_result(request):
    orderid=request.POST.get('chem_orderid')
    encc=request.POST.get('chem_encc')
    hpercode=request.POST.get('chem_hpercode')
    action =request.POST.get('chem_action')
  
    if action == 'INSERT':
        try:
            chem_res=requests.post(save_chem, data={
                'enccode':request.POST.get('chem_encc'),
                'order_id':request.POST.get('chem_orderid'),
                'hpercode':request.POST.get('chem_hpercode'),
                'date':datetime.datetime.now(),
                'last_meal':request.POST.get('chem_lastmeal'),
                'extraction_time':request.POST.get('chem_ext_time'),
                'hba1c':request.POST.get('hba1c'),
                'glucose_fbs':request.POST.get('fbs'),
                'glucose_rbs':request.POST.get('rbs'),
                'cholesterol':request.POST.get('cholesterol'),
                'triglycerides':request.POST.get('triglyceride'),
                'hdl_cholesterol':request.POST.get('hdl_col'),
                'ldl_cholesterol':request.POST.get('ldl_col'),
                'blood_uric':request.POST.get('bua'),
                'blood_urea':request.POST.get('bun'),
                'creatinine':request.POST.get('crea'),
                'alt_sgpt':request.POST.get('alt'),
                'ast_sgot':request.POST.get('ast'),
                'potassium':request.POST.get('potassium'),
                'sodium':request.POST.get('sodium'),
                'chloride':request.POST.get('chloride'),
                'total_calcium':request.POST.get('tca'),
                'ionized_calcium':request.POST.get('ica'),
                'magnesium':request.POST.get('magnesium'),
                'phosphorus':request.POST.get('phosphorus'),
                'total_protein':request.POST.get('tprotein'),
                'albumin':request.POST.get('albumin'),
                'globulin':request.POST.get('globulin'),
                'ag_ration':request.POST.get('ag_ratio'),
                'alkaline_phospatase':request.POST.get('alkp'),
                'amylase':request.POST.get('amylase'),
                'lipase':request.POST.get('lipase'),
                'ldh':request.POST.get('ldh'),
                'total_bilirubin':request.POST.get('tbilirubin'),
                'direct_bilirubin':request.POST.get('dbilirubin'),
                'indirect_bilirubin':request.POST.get('ibilirubin'),
                'perform_by':request.session['employee_id']
            }).json()

            if chem_res['status'] == 'success':
                get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
                for g in get_test['laboratory']:
                    if g['modality'] == 'CHEMI' and g['status'] !='CANCELLED':
                        key=g['prikey']
                        try:
                            samplemodality=requests.post(update_status, data={'key':key, 'enccode': encc,'order_id':orderid, 'status':'TOVERIFY','receive':g['received_specimen']}).json()
                            data=samplemodality
                        except Exception as e:
                            data=e
                    else:
                       data='bad'
            

        except Exception as e:
            data='potaka'
            

    elif action == 'VERIFY':
        try:
            chem_res=requests.post(save_chem, data={
                'enccode':request.POST.get('chem_encc'),
                'order_id':request.POST.get('chem_orderid'),
                'hpercode':request.POST.get('chem_hpercode'),
                'date':datetime.datetime.now(),
                'last_meal':request.POST.get('chem_lastmeal'),
                'extraction_time':request.POST.get('chem_ext_time'),
                'hba1c':request.POST.get('hba1c'),
                'glucose_fbs':request.POST.get('fbs'),
                'glucose_rbs':request.POST.get('rbs'),
                'cholesterol':request.POST.get('cholesterol'),
                'triglycerides':request.POST.get('triglyceride'),
                'hdl_cholesterol':request.POST.get('hdl_col'),
                'ldl_cholesterol':request.POST.get('ldl_col'),
                'blood_uric':request.POST.get('bua'),
                'blood_urea':request.POST.get('bun'),
                'creatinine':request.POST.get('crea'),
                'alt_sgpt':request.POST.get('alt'),
                'ast_sgot':request.POST.get('ast'),
                'potassium':request.POST.get('potassium'),
                'sodium':request.POST.get('sodium'),
                'chloride':request.POST.get('chloride'),
                'total_calcium':request.POST.get('tca'),
                'ionized_calcium':request.POST.get('ica'),
                'magnesium':request.POST.get('magnesium'),
                'phosphorus':request.POST.get('phosphorus'),
                'total_protein':request.POST.get('tprotein'),
                'albumin':request.POST.get('albumin'),
                'globulin':request.POST.get('globulin'),
                'ag_ration':request.POST.get('ag_ratio'),
                'alkaline_phospatase':request.POST.get('alkp'),
                'amylase':request.POST.get('amylase'),
                'lipase':request.POST.get('lipase'),
                'ldh':request.POST.get('ldh'),
                'total_bilirubin':request.POST.get('tbilirubin'),
                'direct_bilirubin':request.POST.get('dbilirubin'),
                'indirect_bilirubin':request.POST.get('ibilirubin'),
                # 'perfom_by':int('617116'),
                'verified_by':request.session['employee_id']
                # 617116
            }).json()

            if chem_res['status'] == 'success':
                get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':orderid}).json()
                for g in get_test['laboratory']:
                    if g['modality'] == 'CHEMI' and g['status'] != 'CANCELLED':
                        key=g['prikey']
                        try:
                            samplemodality=requests.post(update_status, data={'key':key, 'enccode': encc,'order_id':orderid, 'status':'COMPLETED','receive':g['received_specimen']}).json()
                            data=samplemodality
                        except Exception as e:
                            data=e
                    else:
                       data='bad'
            

        except Exception as e:
            data='potaka'
            
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
    action=request.POST.get('action')
    proccode=request.POST.get('proccode')
   
    if action == 'insert':
      try:
          save_fa=requests.post(fecalysisResult, data={
          'enccode':request.POST.get('encc'),
          'order_id':request.POST.get('orderid'),
          'hpercode':request.POST.get('hpercode'),
          'item':request.POST.get('proccode'),
          'feccolor':request.POST.get('color'),
          'fecon':request.POST.get('consistency'),
        #   'fecocbld':request.POST.get('occult_blood'),   
          'fecrbc':request.POST.get('rcb'),
          'fecwbc':request.POST.get('wbc'),
          'fecyeast':request.POST.get('yeast_cell'),
          'fecbac':request.POST.get('bacteria'),
          'fecfat':request.POST.get('fat_globules'),
          'fecascaris':request.POST.get('ascaris'),
          'fechookworm':request.POST.get('hookworm'),
          'fechisto':request.POST.get('histo'),
          'feccoli':request.POST.get('coli'),
          'fectrichuris':request.POST.get('trichuris'),
          'fecvermi':request.POST.get('vermi'),
          'feothr':request.POST.get('other'),
          'fecnote':request.POST.get('note'),
          'performBy':request.session['employee_id'],
          }).json()
          print(save_fa)
          if save_fa['status'] == 'success':  
            get_test = requests.post(get_lab_request, data={'enccode':request.POST.get('encc'),'order_id':request.POST.get('orderid')}).json()
            for g in get_test['laboratory']:
                if g['prikey'] == request.POST.get('prikey'):
                    up_stat=requests.post(update_status, data={'key': request.POST.get('prikey'), 'enccode': request.POST.get('encc'),'order_id':request.POST.get('orderid'), 'status':'TO VERIFY','receive':g['received_specimen']}). json()
                    status=up_stat['status']
      except Exception as e:
          status=e
    elif action == 'verify':
        try:
          verify_fa=requests.post(fecalysisResult, data={
          'enccode':request.POST.get('encc'),
          'order_id':request.POST.get('orderid'),
          'hpercode':request.POST.get('hpercode'),
          'item':proccode,
          'feccolor':request.POST.get('color'),
          'fecon':request.POST.get('consistency'),
          'fecocbld':request.POST.get('occult_blood'),   
          'fecrbc':request.POST.get('rcb'),
          'fecwbc':request.POST.get('wbc'),
          'fecyeast':request.POST.get('yeast_cell'),
          'fecbac':request.POST.get('bacteria'),
          'fecfat':request.POST.get('fat_globules'),
          'fecascaris':request.POST.get('ascaris'),
          'fechookworm':request.POST.get('hookworm'),
          'fechisto':request.POST.get('histo'),
          'feccoli':request.POST.get('coli'),
          'fectrichuris':request.POST.get('trichuris'),
          'fecvermi':request.POST.get('vermi'),
          'feothr':request.POST.get('other'),
          'fecnote':request.POST.get('note'),
          'performBy':request.POST.get('performById'),
          'verifyBy':request.session['employee_id'],
          }).json()
          print(save_fa)
          if verify_fa['status'] == 'success':
            get_test = requests.post(get_lab_request, data={'enccode':request.POST.get('encc'),'order_id':request.POST.get('orderid')}).json()
            for g in get_test['laboratory']:
                if g['prikey'] == request.POST.get('prikey'):
                    up_stat=requests.post(update_status, data={'key': request.POST.get('prikey'), 'enccode': request.POST.get('encc'),'order_id':request.POST.get('orderid'), 'status':'COMPLETED','receive':g['received_specimen']}). json()
                    status=up_stat['status']
        
        except Exception as e:
            status='verify Failed'

    
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
        
    chk_charge=requests.post(get_charges,data={'code':chrg_code}).json()
    if len(chk_charge['data']) > 0:
        chk=1
    else:
        chk=0
    status={
        'labtest':view_req['laboratory'],
        'patient':view_req['details'],
        'ward':view_req['toecode'],
        # 'test':view_req
    }

    return JsonResponse({'data':status,'charge':chk,'code':chrg_code})

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
            # 'urnvapu':request.POST.get('phosphate'),
            'ammonium':request.POST.get('vbiurate'),
            'uricAcid':request.POST.get('vuric'),
            'urnvamm':request.POST.get('vbiurate'),
            'fineGranular':request.POST.get('vfine'),
            'coarseGranular':request.POST.get('vcoarse'),
            'hyaline':request.POST.get('vhyaline'),
            'wbcCast':request.POST.get('vcwbc'),
            'rbcCast':request.POST.get('vrwbc'),
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
            'manualProtein':request.POST.get('protein'),
            'wbc':request.POST.get('wbc'),
            'rbc':request.POST.get('rbc'),
            'epithelial':request.POST.get('epithelial'),
            'mucus':request.POST.get('mucus'),
            'bacteria':request.POST.get('bacteria'),
            'calcium':request.POST.get('calcium'),
            'urnvapu':request.POST.get('phosphate'),
            'ammonium':request.POST.get('biurate'),
            'uricAcid':request.POST.get('uric'),
            'urnvamm':request.POST.get('biurate'),
            'fineGranular':request.POST.get('fine'),
            'coarseGranular':request.POST.get('coarse'),
            'hyaline':request.POST.get('hyaline'),
            'wbcCast':request.POST.get('cwbc'),
            'rbcCast':request.POST.get('crbc'),
            'others':request.POST.get('others'),
            # 'preg':request.POST.get('pregnancy'),
            'performBy':request.session['employee_id'],
            # 'performBy':'520408',
            }).json()
        
        print(save_ua)

        if save_ua['status'] == 'success':
            get_test = requests.post(get_lab_request, data={'enccode':request.POST.get('encc'),'order_id':request.POST.get('orderid')}).json()
            for g in get_test['laboratory']:
                if g['prikey'] == request.POST.get('prikey'):
                    sentToDone=requests.post(update_status, data={'key': request.POST.get('prikey'), 'enccode': request.POST.get('encc'),'order_id':request.POST.get('orderid'), 'status':'TO VERIFY','receive':g['received_specimen']}).json()
            getua=requests.post(get_urinalysis,data={'order_id':request.POST.get('orderid'),'item':request.POST.get('proccode')}).json()
            status=getua['status']
       

    except Exception as e:
        status='Unable to Save'

    return JsonResponse({'data':status})    

###########################################
@csrf_exempt
def load_microscopy(request):
    req='MICRO'
    get_micro=requests.post(getLab_modality,data={'modality':req,'status':request.POST.get('rtype')}).json()
    for i in get_micro['data']:
        i['enccode'] = i['enccode'].replace("/", "-")
        i['received_datetime'] = datetime.datetime.strptime(i['received_datetime'],"%Y-%m-%dT%H:%M:%S.%fZ")
        i['received_datetime']=datetime.datetime.strftime(i['received_datetime'], '%b %d, %y (%I:%M %p)')
        i['dodate'] = datetime.datetime.strptime(i['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
        i['dodate']=datetime.datetime.strftime(i['dodate'], '%b %d, %Y (%I:%M %p)')
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
    doctOrder = requests.post(doctorsOrderPatient).json()
    labrequest=doctOrder['data'] 
  
    for l in labrequest:
        if l['toecode'] != 'OPD':
         
            get_examination = requests.post(get_lab_request, data={'enccode': l['enccode'],'order_id':l['order_id']}).json()
            test_=get_examination['laboratory']
         
            for e in test_:
                if e['status'] =='ENDORSE':
                    e['uomcode'] =l['patlast']+', '+l['patfirst']
                    e['orcode']=l['toecode']
                    e['pcchrgcod']=l['order_id']
                    e['datemod'] = datetime.datetime.strptime(e['datemod'],"%Y-%m-%dT%H:%M:%S.%fZ")
                    e['datemod']=datetime.datetime.strftime(e['datemod'], '%b %d, %y (%I:%M %p)')
                    endorse.append(e)
 
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
    er=[]
    cc=1
    inp=[]
    result_=[]
    result =[]
    endorse=[]
    for i in labrequest:
        i['enccode'] = i['enccode'].replace("/", "-")
        ordid=i['order_id']
        enctr=i['enccode']
        if i['received_datetime'] is not None:
            i['received_datetime'] = datetime.datetime.strptime(i['received_datetime'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['received_datetime']=datetime.datetime.strftime(i['received_datetime'], '%b %d, %y (%I:%M %p)')
        get_examination = requests.post(get_lab_request, data={'enccode': enctr,'order_id':ordid}).json()
        test_=get_examination['laboratory']
   
        for e in test_:
            
            
            if e['status'] == 'ENDORSE':
                endorse.append(e['status'])
            
        if len(test_) > 0:
            result_.append(i)
            if i['toecode'] == 'ADM':
                inp.append(i['toecode'])
            if i['toecode'] == 'ER':
                 er.append(i['toecode'])
            if i['toecode'] == ward:
                for t in test_:
                    cc + 1
                    result.append(t['procdesc'])
                    cres=len(t)
                    # no. of test proxy
            i['released_by']=len(test_)     
        else:
            i['released_by'] = 0
    
    return JsonResponse({'status':result_,'t_inp':len(inp),'t_er':len(er),'t_endorse':len(endorse)})

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
    
    
    if modality == 'CHEMI' or modality == 'IMMUN' or modality == 'THYRO' or modality == 'CARDI' or modality == 'TUMOR' or modality == 'SEROL' or modality == 'BACTI' :
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

    return render(request, 'integrated/laboratory/hematology/index.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})





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
def get_kit(request):
    data=[]
    allkits=requests.post(allkit).json()

    return JsonResponse({'data':allkits['data']})


def lab_bacteriology(request):
  
    # gk=requests.post(getkit).json()
    try:
        allkits=requests.post(allkit).json()
        for k in allkits['data']:
            if k['status'] == 'ACTIVE' and k['modality'] == 'BACTI':
                k['expiry_date'] = datetime.datetime.strptime(k['expiry_date'],"%Y-%m-%dT%H:%M:%S.%fZ")
                k['expiry_date']=datetime.datetime.strftime(k['expiry_date'], '%b %d, %Y')
                ukit=k['kit_name']
                lotno=k['lot_no']
                expiry=k['expiry_date']
            else:
                ukit=''
                lotno=''
                expiry=''
    except Exception as e:
            ukit=''
            lotno=''
            expiry=''

    return render(request, 'integrated/laboratory/bacteriology/index.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name'],'kit':ukit,'lotno':lotno,'expiry':expiry})


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
            ctr=p['control_no']
        for c in chemres:
            c['date_verified'] = datetime.datetime.strptime(c['date_verified'],"%Y-%m-%dT%H:%M:%S.%fZ")
            c['date_verified']=datetime.datetime.strftime(c['date_verified'], '%b %d, %y (%I:%M %p)')
        if chem_result['status'] == 'success':       
            return render(request,'integrated/laboratory/result_form/chemistry.html',{'result':chemres,'age':age['data'],'ctr':ctr,'ward':ptx_req['toecode']})
        else:
            return HttpResponseRedirect("/errpage")
    except Exception as e:
        return HttpResponseRedirect("/errpage")

def errpage(html):
    htmldoc = HTML(string=html, base_url="integrated/laboratory/result_form/404.html")
    return htmldoc.write_pdf()

def labres_hema(request):
    
    return render(request,'integrated/laboratory/result_form/hematology.html')

def cbc_result(request,ward,physician,orderid,encc):
    ptx_req=requests.post(get_lab_request, data={'enccode':encc,'order_id':orderid}).json()
    ptx=ptx_req['details'][0]
    for p in ptx_req['laboratory']:
            ctr=p['control_no']
    cbc_res=requests.post(get_cbc_result, data={'order_id':orderid}).json()
    result=cbc_res['data']

    for c in result:
        c['date_verified'] = datetime.datetime.strptime(c['date_verified'],"%Y-%m-%dT%H:%M:%S.%fZ")
        c['date_verified']=datetime.datetime.strftime(c['date_verified'], '%b %d, %y (%I:%M %p)')


    return render(request,'integrated/laboratory/result_form/cbc_result.html',{'result':result,'patient':ptx,'ctr':ctr,'doctor':physician,'ward':ward})




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

    p.drawString(4.5*inch, 7.2*inch, "Date.:")
    p.line(345, 7.19*inch, 410, 7.19*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Bold", 9, leading=None)
    p.drawString(4.8*inch, 7.22*inch, time.strftime("%m-%d-%Y"))
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
        i['dodate'] = datetime.datetime.strptime(i['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
        i['dodate']=datetime.datetime.strftime(i['dodate'], '%b %d, %y (%I:%M %p)')
        age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
        i['uomcode']=age['data']
        hdata.append(i)
    
    return JsonResponse({'data':hdata})

def get_hema_count(request):
    tpending=requests.post(getLab_modality,data={'modality':'HEMAT','status':'PENDING'}).json()
    tonprocess=requests.post(getLab_modality,data={'modality':'HEMAT','status':'ONPROCESS'}).json()
    tcompleted=requests.post(getLab_modality,data={'modality':'HEMAT','status':'TOVERIFY'}).json()
    treleased=requests.post(getLab_modality,data={'modality':'HEMAT','status':'COMPLETED'}).json()
    return JsonResponse({'tpending':len(tpending['data']),'tonprocess':len(tonprocess['data']),'tcompleted':len(tcompleted['data']),'treleased':len(treleased['data'])})

@csrf_exempt
def hema_sentToProcess(request):
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
    cbc=requests.post(get_cbc_result,data={'order_id':orderid}).json()
    return JsonResponse({'data':cbc['data']})
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
    try:
        getchemresult=requests.post(get_chem_result,data={'order_id':ord,'enccode':encc}).json()
        chem_res=getchemresult['data']
    except Exception as e:
        chem_res=[]
        print(e)
    
    try:
        get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':ord}).json()
        data=[]
        for g in get_test['laboratory']:
            if g['modality'] == modality and g['status'] !='CANCELLED':
                key=g['prikey']
                data.append(g['proccode'])     
            else:
                data=''
    except Exception as e:
        data=e
    return JsonResponse({'data':data,'chemresult':chem_res})

@csrf_exempt
def chem_onprocess(request):
    encc=request.POST.get('encc')
    ord=request.POST.get('orderid')
    modality=request.POST.get('modality')
    pdata=[]
    td=[]
    # print(encc)
    # print(ord)
    # print(modality)
    try:
        get_test=requests.post(get_lab_request,data={'enccode':encc,'order_id':ord}).json()
        
        for g in get_test['laboratory']:
            if g['modality'] == 'CHEMI' and g['status'] != 'CANCELLED':
                key=g['prikey']
                # td.append(g['procdesc'])
                pdata.append(g['proccode'])   
                # print(pdata)  
            else:
                data=[]
    
    except Exception as e:
        data=[]
        print(e)
    return JsonResponse({'data':pdata,'td':td})
 

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
    # print(htype)
    get_chemi=requests.post(getLab_modality,data={'modality':'CHEMI','status':htype}).json()
    req=[]
    ctr=''
    chem_data=[]
    for i in get_chemi['data']:
        if i['status'] !='CANCELLED':
            i['enccode'] = i['enccode'].replace("/", "-")
            i['dodate'] = datetime.datetime.strptime(i['dodate'],"%Y-%m-%dT%H:%M:%S.%fZ")
            i['dodate']=datetime.datetime.strftime(i['dodate'], '%b %d, %y (%I:%M %p)')
        
            age=requests.post(get_age, data={'enccode':i['enccode'],'toecode':i['toecode']}).json()
            i['uomcode']=age['data']
            chem_data.append(i)
    
    return JsonResponse({'data':chem_data}) 

def upload_hema(request):

    return render(request,'integrated/laboratory/upload/hema_result.html',{'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name']})


@csrf_exempt
def csv_upload(request):
    csv_file = request.FILES.get("attendance-file")
    data=csv_file
    return JsonResponse({'data':data})