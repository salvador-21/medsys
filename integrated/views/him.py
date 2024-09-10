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
search_api = root + "api/patients/patient-search-proc"
get_patient_record_api = root + "api/patients/getPatientRecords"
get_patient_details_api = root + "api/patients/getPatientDetails"
get_patient_digitize_details_api = root + "api/patients/getDigitizePatientDetails"
save_patient_digitize_record_api = root + "api/patients/saveDigitizeLink"
get_patient_link_api = root + "api/patients/digitizeLink"
class HtmlPdf(FPDF, HTMLMixin):
    pass

def him(request):
    if request.session.get('employee_id') is not None:
        user_level = request.session['user_level']
        return render(request, 'integrated/him/index.html', {'page': 'HIM', 'user_level': request.session['user_level'], 'name': request.session['name'], 'user_level': user_level})
    else:
        return HttpResponseRedirect('/login')

def digitize_search(request):
    if request.session.get('employee_id') is not None:
        user_level = request.session['user_level']
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
                return render(request, 'integrated/him/digitize_search_result.html', {'page': 'HIM', 'user_level': request.session['user_level'], 'name': request.session['name'], 'user_level': user_level, 'list': list_})
        return render(request, 'integrated/him/digitize_search.html', {'page': 'HIM', 'user_level': request.session['user_level'], 'name': request.session['name'], 'user_level': user_level})
    else:
        return HttpResponseRedirect('/login')

def digitize_patient(request, code):
    user_level = request.session['user_level']
    data = requests.post(get_patient_record_api, data={'hospital_no': code}).json()
    details = requests.post(get_patient_details_api, data={'no': code}).json()
    if details['status'] == 'success':
        details_ = details['data']
    else:
        details_ = []
    
    if data['status'] == 'success':
        for i in data['data']:
            i[0]['enccode'] = i[0]['enccode'].replace('/', '-')
            i[0]['date'] = datetime.strptime(i[0]['date'][:10], '%Y-%m-%d')
        data_ = data['data']
    else:
        data_ = []
    return render(request, 'integrated/him/digitize_patient.html', {'page': 'HIM', 'user_level': request.session['user_level'], 'name': request.session['name'], 'user_level': user_level, 'details': details_, 'data': data_})

def upload(request, enctr):
    details = requests.post(get_patient_digitize_details_api, data={'enccode': enctr}).json()
    no = ""
    if details['status'] == 'success':
        for i in details['data']:
            i['encdate'] = datetime.strptime(i['encdate'][:10], '%Y-%m-%d')
            no = i['hpercode']
        details_ = details['data']
    else:
        details_ = ""
    if request.method == "POST":
        file_url = ""
        try:
            fs = FTPStorage()
            if bool(request.FILES.get('file', False)) == True:
                uploaded_file =  request.FILES['file']
                lookup = uploaded_file.name.rfind(".")
                upload_file = fs.save(uploaded_file.name, uploaded_file)
                file_url = upload_file
                to_server = requests.post(save_patient_digitize_record_api, data={'enccode': enctr, 'filename': file_url}).json()
                if to_server['status'] == 'success':
                    messages.success(request, "Record uploaded succesfully")
                    return HttpResponseRedirect("/" + no + "/digitizepatient")
                else:
                    messages.warning(request, "Encountered and error while saving file...Please contact the system administrator")
        except Exception as e:
            messages.error(request, "Failed uploading patient digitize file")
            file_url = ""
    return render(request, 'integrated/him/upload_digitize_record.html', {'page': 'HIM', 'user_level': request.session['user_level'], 'name': request.session['name'],  'enctr': enctr, 'details': details_})

def digitize_record(request, enctr):
    details = requests.post(get_patient_digitize_details_api, data={'enccode': enctr}).json()
    link = requests.post(get_patient_link_api, data={'enccode': enctr}).json()
    no = ""
    if details['status'] == 'success':
        for i in details['data']:
            i['encdate'] = datetime.strptime(i['encdate'][:10], '%Y-%m-%d')
            no = i['hpercode']
        details_ = details['data']
    else:
        details_ = ""
    if link['status'] == 'success':
        link_url = link['data'][0]['document_link']
    else:
        link_url = ""
    return render(request, 'integrated/him/digitize_patient_record.html', {'page': 'HIM', 'user_level': request.session['user_level'], 'name': request.session['name'], 'enctr': enctr, 'details': details_, 'link_url': link_url})