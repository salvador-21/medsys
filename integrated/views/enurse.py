from typing import final
from django.shortcuts import render
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
from reportlab.platypus import Paragraph, Table, TableStyle, PageBreak, BaseDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from num2words import num2words
from storages.backends.ftp import FTPStorage
from django.contrib import messages

#API CALL
static_root = "http://173.10.7.2/medsys-static-files"
root = "http://173.10.2.108:9092/"
#root = "http://localhost:9091/"
patient_record_api = root + "api/patients/getPatientRecords"
patient_mgh_api = root + "api/patients/mayGoHome"
add_mgh_api = root + "api/patients/addMayGoHome"
update_mgh_api = root + "api/patients/updateMayGoHome"
all_patients_api = root + "api/enurse/getPatientPerWard"
patient_details_by_enc_api = root + "api/enc/getPatientDetailsByEnc"
patient_address_api = root + "api/patients/getPatientAddress"
age_api = root + "api/patients/age"
patient_diagnosis_api = root + "api/patients/getPatientDiagnosis"
ward_api = root + "api/room/ward"
assignment_api = root + "api/enurse/getWardAssignment"
doctors_list_api = root + "api/doctor/getDoctors"
#CHARGES
get_charges_api = root + "api/billing/getChargesByCode"
update_charges_api = root + "api/billing/updateCharges"
delete_charges_api = root + "api/charges/nursingdeleteCharges"
get_chargelist_api = root + "api/charges/chargelist"
add_charges_api = root + "api/charges/postChargesNurse"
load_charges_api = root + "api/enurse/getCharges"
del_charges_api = root + "api/charges/deleteCharges"

def enurse(request):
    if request.session.get('employee_id') is not None:
        user_id = request.session['userid']
        arr = []
        getAssignment = requests.post(assignment_api, data={'username': user_id}).json()
        if getAssignment['status'] == 'success':
            for i in getAssignment['data']:
                li = requests.post(all_patients_api, data={'wardcode': i['wardcode']}).json()
                if li['status'] == 'success':
                    for x in li['data']:
                        x['enccode'] = x['enccode'].replace('/', '-')
                        arr.append(x)
        return render(request, 'integrated/enurse/index.html', {'page': 'E-Nurse', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': arr})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def enurse_patient(request, enctr):
    if request.session.get('employee_id') is not None:
        patient_details = requests.post(patient_details_by_enc_api, data={'enccode': enctr}).json()["data"]
        patient_address = requests.post(patient_address_api, data={'no': patient_details[0]['hpercode']}).json()["data"]
        age = requests.post(age_api, data={'enccode': enctr, 'toecode': 'ADM'}).json()["data"]
        records = requests.post(patient_record_api, data={'hospital_no': patient_details[0]['hpercode']}).json()["data"]
        diagnosis = requests.post(patient_diagnosis_api, data={'encounter_no': enctr}).json()["data"]
        mgh = requests.post(patient_mgh_api, data={'enccode': enctr}).json()["data"]
        for i in records:
            i[0]['date'] = datetime.strptime(i[0]['date'][:10], "%Y-%m-%d")
        for j in mgh:
            j['dodate'] = datetime.strptime(j['dodate'][:10], "%Y-%m-%d")
            j['dotime'] = datetime.strptime(j['dotime'][11:19], "%H:%M:%S")
        return render(request, 'integrated/enurse/details.html', {'page': 'E-Nurse', 'user_level': request.session['user_level'], 'name': request.session['name'], 'details': patient_details, 'address': patient_address, 'age': age, 'records': records, 'diagnosis': diagnosis, 'enctr': enctr, 'mgh': mgh})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def addmgh(request, enctr):
    if request.session.get('employee_id') is not None:
        doctors = requests.get(doctors_list_api).json()["data"]
        if request.method == 'POST':
            dt = request.POST.get("dt")
            physician = request.POST.get("physician") 
            add = requests.post(add_mgh_api, data={'enccode': enctr, 'licno': physician, 'dt': dt, 'encoder': request.session['employee_id']}).json()
            if add['status'] == 'success':
                messages.success(request, 'May Go Home order created')
            else:
                messages.error(request, 'Opps!An error occured while processing your request, Please try again')
        return render(request, 'integrated/enurse/addmgh.html', {'page': 'E-Nurse', 'user_level': request.session['user_level'], 'name': request.session['name'], 'doctors': doctors, 'enctr': enctr})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def editmgh(request, enctr):
    if request.session.get('employee_id') is not None:
        doctors = requests.get(doctors_list_api).json()["data"]
        mgh = requests.post(patient_mgh_api, data={'enccode': enctr}).json()["data"]
        for j in mgh:
            j['dodate'] = datetime.strptime(j['dodate'][:10], "%Y-%m-%d")
            j['dotime'] = datetime.strptime(j['dotime'][11:19], "%H:%M:%S")
        if request.method == 'POST':
            dt = request.POST.get("dt")
            physician = request.POST.get("physician") 
            update = requests.post(update_mgh_api, data={'enccode': enctr, 'licno': physician, 'dt': dt, 'encoder': request.session['employee_id']}).json()
            if update['status'] == 'success':
                messages.success(request, 'May go home order updated')
            else:
                messages.error(request, 'Opps!An error occured while processing your request, Please try again')
            mgh = requests.post(patient_mgh_api, data={'enccode': enctr}).json()["data"]
            for j in mgh:
                j['dodate'] = datetime.strptime(j['dodate'][:10], "%Y-%m-%d")
                j['dotime'] = datetime.strptime(j['dotime'][11:19], "%H:%M:%S")
        return render(request, 'integrated/enurse/editmgh.html', {'page': 'E-Nurse', 'user_level': request.session['user_level'], 'name': request.session['name'], 'doctors': doctors, 'enctr': enctr, 'mgh': mgh})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def nurse_assignment(request):
    if request.session.get('employee_id') is not None:
        nurse_list = []
        wardcode = ""
        getWard = requests.post(ward_api).json()
        if getWard['status'] == 'success':
            list_ = getWard['data']
        else:
            list_ = []
        if request.method == 'POST':
            wardcode = request.POST.get('ward')
            get_nurse_list = requests.post(nurse_list_api, data={'wardcode': wardcode}).json()
            if get_nurse_list['status'] == 'success':
                nurse_list = get_nurse_list['data']
            else:
                nurse_list = []
        return render(request, 'integrated/enurse/assignment_list.html', {'page': 'E-Nurse', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': list_, 'nurse_list': nurse_list, 'wardcode': wardcode})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def nurse_charges(request, enctr):
    if request.session.get('employee_id') is not None:
        if request.method == 'POST':
            itemcode = request.POST.get('procedure')
            qty = request.POST.get('qty')
            add = requests.post(add_charges_api, data={'enc': enctr, 'exam': itemcode, 'encoder': request.session['userid'], 'qty': qty}).json()
            if add['status'] == 'success':
                messages.success(request, 'Item added successfully')
            else:
                messages.error(request, 'Error occured while adding item')
        patient_details = requests.post(patient_details_by_enc_api, data={'enccode': enctr}).json()["data"]
        patient_address = requests.post(patient_address_api, data={'no': patient_details[0]['hpercode']}).json()["data"]
        age = requests.post(age_api, data={'enccode': enctr, 'toecode': 'ADM'}).json()["data"]
        charges = requests.post(load_charges_api, data={'enccode': enctr}).json()["data"]
        list_of_charges = requests.post(get_chargelist_api).json()["data"]
        gt = 0
        for i in charges['hproc']:
            gt += i['pcchrgamt']
        return render(request, 'integrated/enurse/charges2.html', {'page': 'E-Nurse', 'user_level': request.session['user_level'], 'name': request.session['name'], 'details': patient_details, 'address': patient_address, 'age': age,'enctr': enctr, 'charges': charges, 'gt': gt, 'list_of_charges': list_of_charges['hproc']})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def nurse_delete_charges(request, enctr, code):
    if request.session.get('employee_id') is not None:
        delete = requests.post(delete_charges_api, data={'enccode': enctr, 'pcchrgcod': code}).json()
        if delete['status'] == 'success':
            messages.success(request, 'Item deleted successfully')
            return HttpResponseRedirect('/' + enctr + '/nursecharges')
        else:
            messages.error(request, 'Error occured while deleting charges')
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def load_nurse_charges(request, enctr):
    charges = requests.post(load_charges_api, data={'enccode': enctr}).json()["data"]
    return render(request, 'integrated/enurse/reload_charges.html', {'charges': charges, 'enctr': enctr})
