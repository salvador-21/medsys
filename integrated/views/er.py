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
religion_list_api = root + "api/patients/getReligion"
province_list_api = root + "api/patients/getProvince"
search_api = root + "api/patients/patient-search-proc"
patient_details_api = root + "api/patients/details"
patient_address_api = root + "api/patients/getPatientAddress"
patient_update_api = root + "api/patients/update"
province_list_api = root + "api/patients/getProvince"
municipality_list_api = root + "api/patients/getMunicipality/"
barangay_list_api = root + "api/patients/getBarangay/"
#DOCTORS
doctors_list_api = root + "api/doctor/getDoctors"
#ER
get_er_patients_api = root + "api/er"
get_er_services_api = root + "api/er/services"
save_er_record_api = root + "api/er/save"
get_er_details_api = root + "api/er/details"
update_er_details_api = root + "api/er/update"
get_er_diagnosis_api = root + "api/er/diagnosis"
get_er_management_api = root + "api/er/management"
add_er_vs_api = root + "api/er/addVitalSign"
get_er_vs_api = root + "api/er/getVitalSign"
discharge_er_api = root + "api/er/discharge"
get_er_tat_api = root + "api/er/tat"
get_poi_api = root + "api/er/poi"
get_inj_api = root + "api/er/getInjury"
er_tat_api = root + "api/er/tatByDateRange"
er_daily_tat_api = root + "api/er/tatDaily"

class HtmlPdf(FPDF, HTMLMixin):
    pass

def er(request):
    if request.session.get('employee_id') is not None:
        return render(request, 'integrated/er/index.html', {'page': 'Emergency Room', 'user_level': request.session['user_level'], 'name': request.session['name']})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def ersearch(request):
    if request.session.get('employee_id') is not None:
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
                return render(request, 'integrated/er/search_result.html', {'page': 'Emergency Room', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': list_})
        return render(request, 'integrated/er/search.html', {'page': 'Emergency Room', 'user_level': request.session['user_level'], 'name': request.session['name']})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def erlist(request):
    if request.session.get('employee_id') is not None:
        try:
            patient_list = requests.post(get_er_patients_api).json()
            if patient_list['status'] == 'success':
                for i in patient_list['data']:
                    i['enccode'] = i['enccode'].replace('/', '-')
                patient_list_ = patient_list['data']
            else:
                patient_list_ = []
        except Exception as e:
            messages.warning(request, str(e))
        return render(request, 'integrated/er/erlist.html', {'page': 'Emergency Room', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': patient_list_})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def erlogpatient(request, no):
    if request.session.get('employee_id') is not None:
        msg = ''
        if request.method == 'POST':
            companion = request.POST.get("companion").upper()
            contact = request.POST.get("contact")
            date_of_arrival = request.POST.get("date_of_arrival")
            time_of_arrival = request.POST.get("time_of_arrival")
            referred_by = request.POST.get("referred_by").upper()
            esi = request.POST.get("esi")
            tscode = request.POST.get("services")
            condition = request.POST.get("condition")
            complaint = request.POST.get("complaint")
            rel_to_patient = request.POST.get("rel_to_patient")
            save = requests.post(save_er_record_api, data={'hpercode': no, 'companion': companion, 'contact_no': contact, 'date_of_arrival': date_of_arrival, 'time_of_arrival': time_of_arrival, 'refer': referred_by, 'esi': esi, 'services': tscode, 'condition': condition, 'complaint': complaint, 'entryby': request.session['employee_id'], 'rel': rel_to_patient}).json()
            if save['status'] == 'success':
                messages.success(request, "Patient successfully added to ER Records")
                encounter = save['enccode'].replace('/', '-') 
                return HttpResponseRedirect('/' + no + "/" + encounter + "/" + "erlogdetails")
            else:
                messages.error(request, "System has encountered an error, Please check your connection and try again")
        details_response = requests.post(patient_details_api, data={'hospital_no': no})
        details_json_response = details_response.json()
        if details_json_response['status'] == 'success':
            details = details_json_response['data']
            details['details'][0]['patbdate'] = datetime.strptime(details['details'][0]['patbdate'][:10], "%Y-%m-%d")
        now = datetime.now()
        addr_response = requests.post(patient_address_api, data={'no': no})
        addr_json_response = addr_response.json()
        if addr_json_response['status'] == 'success':
            addr = addr_json_response['data']
        else:
            addr = []
        services = requests.post(get_er_services_api).json()['data']
        return render(request, 'integrated/er/logpatient.html', {'page': 'Emergency Room', 'user_level': request.session['user_level'], 'name': request.session['name'], 'no':no, 'details': details, 'now': now, 'addr': addr, 'services':services, 'msg': msg})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def patientDetails(request, no):
    page = 'Emergency Room'
    if request.session.get('employee_id') is not None:
        religion = []
        provice = []
        municipality = []
        barangay = []
        if request.method == 'POST':
            lastname = request.POST.get("lastname").upper()
            firstname = request.POST.get("firstname").upper()
            middlename = request.POST.get("middlename").upper()
            suffix = request.POST.get("suffix")
            sex = request.POST.get("sex")
            birthdate = request.POST.get("birthdate")
            birthplace = request.POST.get("birthplace")
            street = request.POST.get("street")
            province = request.POST.get("province")
            municipality = request.POST.get("municipality")
            barangay = request.POST.get("barangay")
            nickname = request.POST.get("nickname")
            civilstatus = request.POST.get("civilstatus")
            employment = request.POST.get("employment")
            nationality = request.POST.get("nationality")
            religion = request.POST.get("religion")
            contactno = request.POST.get("contactno")
            occupation = request.POST.get("occupation").upper()
            encoder = request.session.get('employee_id')
            if nickname == "":
                nickname = "-"
            updatepatient_response = requests.post(patient_update_api, data={'hospital_no': no, 'lastname': lastname, 'firstname': firstname, 'middlename': middlename, 'suffix': suffix, 'sex': sex, 'birthdate': birthdate, 'birthplace': birthplace, 'street': street, 'province': province, 'municipality': municipality, 'barangay': barangay, 'nickname': nickname, 'civilstatus': civilstatus, 'employment': employment, 'nationality': nationality, 'religion': religion, 'contactno': contactno, 'occupation': occupation, 'encoder': encoder})
            updatepatient_json_response = updatepatient_response.json()
            if updatepatient_json_response['status'] == 'success':
                messages.success(request, "Record updated succesfully")
            else:
                messages.error(request, "Failed updating patient record, Please contact system administrator")
            # GET NEW DATA
            details_response = requests.post(patient_details_api, data={'hospital_no': no})
            details_json_response = details_response.json()
            if details_json_response['status'] == 'success':
                details = details_json_response['data']
                details['details'][0]['patbdate'] = details['details'][0]['patbdate'][:10]
            # GET RELIGION
            religion_response = requests.get(religion_list_api)
            religion_response_json = religion_response.json()
            if religion_response_json['status'] == 'success':
                religion = religion_response_json['data']
            #GET PROVINCE
            province_response = requests.get(province_list_api)
            province_response_json = province_response.json()
            if province_response_json['status'] == 'success':
                province = province_response_json['data']
            #GET MUNICIPALITY
            try:
                municipality_response = requests.get(municipality_list_api + details['address'][0]['provcode'])
                municipality_response_json = municipality_response.json()
                if municipality_response_json['status'] == 'success':
                    municipality = municipality_response_json['data']
            except:
                municipality = ""
            #GET BARANGAY
            try:
                barangay_response = requests.get(barangay_list_api + details['address'][0]['ctycode'])
                barangay_response_json = barangay_response.json()
                if barangay_response_json['status'] == 'success':
                    barangay = barangay_response_json['data']
            except:
                barangay = ""
            ##########################################################
            return render(request, 'integrated/er/patient_details.html', {'page': page, 'user_level': request.session['user_level'], 'name': request.session['name'], 'religion': religion, 'province': province, 'municipality': municipality, 'barangay': barangay, 'details': details, 'no': no})
        else:
            #GET DATA
            details_response = requests.post(patient_details_api, data={'hospital_no': no})
            details_json_response = details_response.json()
            if details_json_response['status'] == 'success':
                details = details_json_response['data']
                details['details'][0]['patbdate'] = details['details'][0]['patbdate'][:10]
            # GET RELIGION
            religion_response = requests.get(religion_list_api)
            religion_response_json = religion_response.json()
            if religion_response_json['status'] == 'success':
                religion = religion_response_json['data']
            #GET PROVINCE
            province_response = requests.get(province_list_api)
            province_response_json = province_response.json()
            if province_response_json['status'] == 'success':
                province = province_response_json['data']
            #GET MUNICIPALITY
            try:
                municipality_response = requests.get(municipality_list_api + details['address'][0]['provcode'])
                municipality_response_json = municipality_response.json()
                if municipality_response_json['status'] == 'success':
                    municipality = municipality_response_json['data']
            except:
                municipality = ""
            #GET BARANGAY
            try:
                barangay_response = requests.get(barangay_list_api + details['address'][0]['ctycode'])
                barangay_response_json = barangay_response.json()
                if barangay_response_json['status'] == 'success':
                    barangay = barangay_response_json['data']
            except:
                barangay = ""
            ##########################################################
            return render(request, 'integrated/er/patient_details.html', {'page': page, 'user_level': request.session['user_level'], 'name': request.session['name'], 'religion': religion, 'province': province, 'municipality': municipality, 'barangay': barangay, 'details': details, 'no': no})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def erpatientlog(request, no, enctr):
    if request.session.get('employee_id') is not None:
        if request.method == 'POST':
            companion = request.POST.get("companion").upper()
            contact = request.POST.get("contact")
            date_of_arrival = request.POST.get("date_of_arrival")
            time_of_arrival = request.POST.get("time_of_arrival")
            referred_by = request.POST.get("referred_by").upper()
            esi = request.POST.get("esi")
            tscode = request.POST.get("services")
            condition = request.POST.get("condition")
            complaint = request.POST.get("complaint")
            rel_to_patient = request.POST.get("rel_to_patient")
            diagnosis = request.POST.get("diagnosis")
            management = request.POST.get("management")
            time_seen = request.POST.get("time_seen")
            disp_time = request.POST.get("disp_time")
            disposition = request.POST.get("disposition")
            condition2 = request.POST.get("condition2")
            discharged_date = request.POST.get("discharged_date")
            discharged_time = request.POST.get("discharged_time")
            doctor = request.POST.get("doctor")
            bp = request.POST.get("bp")
            hr = request.POST.get("hr")
            rr = request.POST.get("rr")
            temp = request.POST.get("temp")
            sat = request.POST.get("sat", None)
            weight = request.POST.get("weight")
            height = request.POST.get("height")
            accident = request.POST.get("injury")
            er_remarks = request.POST.get("er_remarks")
            remarks = ""
            if accident == "1":
                noi = request.POST.get("noi")
                doi = request.POST.get("doi")
                toi = request.POST.get("toi")
                poi = request.POST.get("poi")
                remarks = request.POST.get("remarks")
            else:
                noi, doi, toi, poi = '', '', '', ''
            update = requests.post(update_er_details_api, data={'enccode': enctr, 'hpercode': no, 'companion': companion, 'rel': rel_to_patient, 'refer': referred_by, 'date_of_arrival': date_of_arrival, 'time_of_arrival': time_of_arrival, 'contact_no': contact, 'esi': esi, 'services': tscode, 'condition': condition, 'entryby': request.session['employee_id'], 'complaint': complaint, 'diagnosis': diagnosis, 'management': management, 'time_seen': time_seen, 'disposition': disposition, 'condition2': condition2, 'discharged_date': discharged_date, 'discharged_time': discharged_time, 'doctor': doctor, 'disp_time': disp_time, 'inj': accident, 'noi': noi, 'doi': doi, 'toi': toi, 'poi': poi, 'remarks': remarks, 'er_remarks': er_remarks})
            vsadd = requests.post(add_er_vs_api, data={'enccode': enctr, 'bp': bp, 'hr': hr, 'rr': rr, 'temp': temp, 'sat': sat, 'weight': weight, 'height': height, 'entryby': request.session['employee_id']}).json()
        details_response = requests.post(patient_details_api, data={'hospital_no': no})
        details_json_response = details_response.json()
        if details_json_response['status'] == 'success':
            details = details_json_response['data']
            details['details'][0]['patbdate'] = datetime.strptime(details['details'][0]['patbdate'][:10], "%Y-%m-%d")
        now = datetime.now()
        addr_response = requests.post(patient_address_api, data={'no': no})
        addr_json_response = addr_response.json()
        if addr_json_response['status'] == 'success':
            addr = addr_json_response['data']
        else:
            addr = []
        services = requests.post(get_er_services_api).json()['data']
        erdetails = requests.post(get_er_details_api, data={'enccode': enctr}).json()['data']
        doctors = requests.get(doctors_list_api).json()['data']
        for i in erdetails:
            i['erdate'] = datetime.strptime(i['erdate'][:10], '%Y-%m-%d')
            #check er version
            rev4Date = datetime(2023,2,28)
            if i['erdate'] > rev4Date:
                version = "rev4"
            else:
                version = "rev3"
            if i['date_arrival']:
                i['date_arrival'] = datetime.strptime(i['date_arrival'][:10], '%Y-%m-%d')
            if i['timearrive']:
                i['timearrive'] = datetime.strptime(i['timearrive'][11:19], '%H:%M:%S')
            if i['TmeSeenDr']: 
                i['TmeSeenDr'] = datetime.strptime(i['TmeSeenDr'][11:19], '%H:%M:%S')
            if i['erdtedis']:
                i['disdate'] = datetime.strptime(i['erdtedis'][:10], '%Y-%m-%d')
                i['distime'] = datetime.strptime(i['erdtedis'][11:19], '%H:%M:%S')
            if i['disptime']:
                i['disptime'] = datetime.strptime(i['disptime'][11:19], '%H:%M:%S')
        diagnosis = requests.post(get_er_diagnosis_api, data={'enccode': enctr}).json()['data']
        management = requests.post(get_er_management_api, data={'enccode': enctr}).json()['data']
        vs = requests.post(get_er_vs_api, data={'enccode': enctr}).json()["data"]
        place_of_incident = requests.post(get_poi_api).json()["data"]
        inj = requests.post(get_inj_api, data={'enccode': enctr}).json()["data"]
        if len(inj) == 0:
            injury = 0
            noi, doi, toi, poi = '', '', '', ''
        else:
            injury = 1
            try:
                inj[0]['injdte'] = datetime.strptime(inj[0]['injdte'][:10], '%Y-%m-%d')
                inj[0]['ijntme'] = datetime.strptime(inj[0]['ijntme'][11:19], '%H:%M:%S')
            except:
                inj[0]['injdte'] = ""
                inj[0]['ijntme'] = ""
        try:
            hw = vs['hw']
        except:
            hw = []
        try:
            vitals = vs['vs']
        except:
            vitals = []
        try:
            sat = vs['sat']
        except:
            sat = []       
        return render(request, 'integrated/er/logpatientdetails.html', {'page': 'Emergency Room', 'user_level': request.session['user_level'], 'name': request.session['name'], 'no':no, 'details': details, 'now': now, 'addr': addr, 'services':services, 'erdetails': erdetails, 'enctr': enctr, 'doctors': doctors, 'diagnosis': diagnosis, 'management': management, 'hw': hw, 'vs': vitals, 'sat': sat, 'place_of_incident': place_of_incident, 'injury': injury, 'inj': inj, 'version': version})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def erpatientdischarged(request, no, enctr):
    if request.session.get('employee_id') is not None:
        if request.method == 'POST':
            companion = request.POST.get("companion").upper()
            contact = request.POST.get("contact")
            date_of_arrival = request.POST.get("date_of_arrival")
            time_of_arrival = request.POST.get("time_of_arrival")
            referred_by = request.POST.get("referred_by").upper()
            esi = request.POST.get("esi")
            tscode = request.POST.get("services")
            condition = request.POST.get("condition")
            complaint = request.POST.get("complaint")
            rel_to_patient = request.POST.get("rel_to_patient")
            diagnosis = request.POST.get("diagnosis")
            management = request.POST.get("management")
            time_seen = request.POST.get("time_seen")
            disp_time = request.POST.get("disp_time")
            disposition = request.POST.get("disposition")
            condition2 = request.POST.get("condition2")
            discharged_date = request.POST.get("discharged_date")
            discharged_time = request.POST.get("discharged_time")
            doctor = request.POST.get("doctor")
            bp = request.POST.get("bp")
            hr = request.POST.get("hr")
            rr = request.POST.get("rr")
            temp = request.POST.get("temp")
            sat = request.POST.get("sat")
            weight = request.POST.get("weight")
            height = request.POST.get("height")
            accident = request.POST.get("injury")
            er_remarks = request.POST.get("er_remarks")
            remarks = ""
            if accident == "1":
                noi = request.POST.get("noi")
                doi = request.POST.get("doi")
                toi = request.POST.get("toi")
                poi = request.POST.get("poi")
                remarks = request.POST.get("remarks")
            else:
                noi, doi, toi, poi = '', '', '', ''
            update = requests.post(discharge_er_api, data={'enccode': enctr, 'hpercode': no, 'companion': companion, 'rel': rel_to_patient, 'refer': referred_by, 'date_of_arrival': date_of_arrival, 'time_of_arrival': time_of_arrival, 'contact_no': contact, 'esi': esi, 'services': tscode, 'condition': condition, 'entryby': request.session['employee_id'], 'complaint': complaint, 'diagnosis': diagnosis, 'management': management, 'time_seen': time_seen, 'disposition': disposition, 'condition2': condition2, 'discharged_date': discharged_date, 'discharged_time': discharged_time, 'doctor': doctor, 'disp_time': disp_time, 'inj': accident, 'noi': noi, 'doi': doi, 'toi': toi, 'poi': poi, 'remarks': remarks, 'er_remarks': er_remarks})
            vsadd = requests.post(add_er_vs_api, data={'enccode': enctr, 'bp': bp, 'hr': hr, 'rr': rr, 'temp': temp, 'sat': sat, 'weight': weight, 'height': height, 'entryby': request.session['employee_id']}).json()
            return HttpResponseRedirect('/er')
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def printerrecord(request, enctr):
    try:
        no = ""
        erdetails = requests.post(get_er_details_api, data={'enccode': enctr}).json()['data']
        for i in erdetails:
            i['erdate'] = datetime.strptime(i['erdate'][:10], '%Y-%m-%d')
            #check er version
            rev4Date = datetime(2023,2,28)
            if i['erdate'] > rev4Date:
                version = "rev4"
            else:
                version = "rev3"
            if i['date_arrival']:
                date_arrive = datetime.strptime(i['date_arrival'][:10], '%Y-%m-%d')
            else:
                i['erdate'] = str(i['erdate'])
                date_arrive = datetime.strptime(i['erdate'][:10], '%Y-%m-%d')
            date_arrive = datetime.strftime(date_arrive, '%m/%d/%y')
            time_arrive = ""
            if i['timearrive']:
                time_arrive = datetime.strptime(i['timearrive'][11:19], '%H:%M:%S')
            else:
                time_arrive = datetime.strptime(i['erdate'][11:19], '%H:%M:%S')
            time_arrive = datetime.strftime(time_arrive, '%I:%M %p')
            no = i['hpercode']
            age = str(i['patage'])
            companion = i['companion']
            if i['erbrouby'] == 'FAMEM':
                comrel = 'FAMILY MEMBER'
            elif i['erbrouby'] == 'FREND':
                comrel = 'FRIEND'
            elif i['erbrouby'] == 'NEIGH':
                comrel = 'NEIGHBOR'
            elif i['erbrouby'] == 'POLIC':
                comrel = 'POLICE'
            elif i['erbrouby'] == 'RELAT':
                comrel = 'RELATIVES'
            elif i['erbrouby'] == 'SELF':
                comrel = 'SELF'
            elif i['erbrouby'] == 'AMBUL':
                comrel = 'AMBULANCE'
            elif i['erbrouby'] == 'OTHRS':
                comrel = 'OTHERS'
            else:
                comrel = ''
            ercond = i['ercond']
            timeseen = i['TmeSeenDr']
            
            refer = i['reffered_by']
            esi = i['esi']
            tscode = i['tscode']
            tsdesc = i['tsdesc']
            complaint = i['chief_complaint']
        details = requests.post(patient_details_api, data={'hospital_no': no}).json()["data"]
        religion_list = requests.get(religion_list_api).json()["data"]
        addr_response = requests.post(patient_address_api, data={'no': no})
        diagnosis = requests.post(get_er_diagnosis_api, data={'enccode': enctr}).json()['data']
        management = requests.post(get_er_management_api, data={'enccode': enctr}).json()['data']
        vs = requests.post(get_er_vs_api, data={'enccode': enctr}).json()["data"]
        inj = requests.post(get_inj_api, data={'enccode': enctr}).json()["data"]

        try:
            if len(inj) == 0:
                noi, doi, toi, poi = '', '', '', ''
            else:
                noi = inj[0]['injadd']
                doi = datetime.strptime(inj[0]['injdte'][:10], '%Y-%m-%d')
                toi = datetime.strptime(inj[0]['ijntme'][11:19], '%H:%M:%S')
                poi = inj[0]['injdesc']
        except:
            noi, doi, toi, poi = '', '', '', ''

        try:
            hw = vs['hw']
            vitals = vs['vs']
            sat = vs['sat']   
        except:
            hw = ""
            vitals = ""
            sat = ""         
        try:
            diagnosis_text = diagnosis[0]['diagtext']
            physician = diagnosis[0]['physician']
        except:
            physician_text = ''
            diagnosis_text = ''
        addr_json_response = addr_response.json()
        if addr_json_response['status'] == 'success':
            addr = addr_json_response['data'][0]['address']
        else:
            addr = []
        for i in details['details']:
            name = i['patlast'] + ", " + i['patfirst'] + " " + i['patmiddle']
            religioncode = i['relcode']
            bdate = datetime.strptime(i['patbdate'][:10], '%Y-%m-%d')
            bdate = datetime.strftime(bdate, "%m/%d/%y")
            bplace = i['patbplace']
        
            if i['patsex'] == 'M':
                sex = "MALE"
            else:
                sex = "FEMALE"
            if i['patcstat'] == 'C':
                cs = "CHILD"
            elif i['patcstat'] == 'D':
                cs = "DIVORSED"
            elif i['patcstat'] == 'M':
                cs = "MARRIED"
            elif i['patcstat'] == 'X':
                cs = "SEPARATED"
            elif i['patcstat'] == 'S':
                cs = "SINGLE"
            elif i['patcstat'] == 'W' and i['patsex'] == 'M':
                cs = "WIDOWER"
            elif i['patcstat'] == 'W' and i['patsex'] == 'F':
                cs = "WIDOW"
            
            if i['natcode'] == 'FIL':
                nat = 'FILIPINO'
            else:
                nat = ''
            
            
        for i in religion_list:
            if religioncode == i['relcode']:
                religion = i['reldesc']
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        logo = ImageReader(static_root + '/integrated/img/brglogo.png')
        dohlogo = ImageReader(static_root + '/integrated/img/dohlogo.png')
        pagpadabalogo = ImageReader(static_root + "/integrated/img/pagpadaba.png")
        response = HttpResponse(content_type='application/pdf')
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setPageSize((8.5*inch, 13*inch))
        p.drawImage(dohlogo, 0.3*inch, 12*inch, mask='auto', width=72, height=72)
        p.drawImage(logo, 1.4*inch, 12*inch, mask='auto', width=72, height=72)
        p.setFont("Times-Roman", 12, leading=None)
        p.setFillColor("green")
        p.drawString(2.8*inch, 12.8*inch, "Bicol Region General Hospital and Geriatric Medical Center")
        p.drawString(3.7*inch, 12.6*inch, "(Formely BICOL SANITARIUM)")
        p.setFont("Times-Roman", 11, leading=None)
        p.setFillColor("black")
        p.drawString(3.8*inch, 12.45*inch, "San Pedro, Cabusao Camarines Sur")
        p.drawString(2.8*inch, 12.3*inch, "Telephone Nos.: (054) 473-2244, 472-4422, 881-1033, 881-1761")
        p.drawString(2.95*inch, 12.16*inch, "E-mail Address: bicolsan@gmail.com, brghgmc@gmail.com")
        p.drawString(3.85*inch, 12*inch, "Website: bicolsanitarium.doh.gov.ph")
        p.line(0, 11.95*inch, 1000, 11.95*inch) #(x1, y1, x2, y2)

        p.setFont("Times-Bold", 12, leading=None)
        p.drawString(3.1*inch, 11.7*inch, "EMERGENCY ROOM RECORD")
        p.setFont("Times-Italic", 9, leading=None)
        p.drawString(0.3*inch, 11.5*inch, "Please use BLUE INK in filling out this form.")
        p.drawString(7.7*inch, 11.5*inch, "Page 1 of 2")
        p.line(0.3*inch, 11.45*inch, 8.3*inch, 11.45*inch) #(x1, y1, x2, y2) top border
        p.line(0.3*inch, 11.45*inch, 0.3*inch, 10*inch) #(x1, y1, x2, y2) left border
        p.line(8.3*inch, 11.45*inch, 8.3*inch, 10*inch) #(x1, y1, x2, y2) right border
        p.line(0.3*inch, 10*inch, 8.3*inch, 10*inch) #(x1, y1, x2, y2) bottom border


        p.setFont("Times-Italic", 9, leading=None)
        p.drawString(1.25*inch, 11.3*inch, "(Last name, Given name, Middle name)")
        p.drawString(5.25*inch, 10.85*inch, "(mm/dd/yy)")
        p.setFont("Times-Bold", 9, leading=None)
        p.drawString(0.35*inch, 11.3*inch, "Name of Patient:")
        p.drawString(4.5*inch, 11.3*inch, "Age:")
        p.drawString(5.3*inch, 11.3*inch, "Sex:")
        p.drawString(6.3*inch, 11.3*inch, "Hospital no.:")
        p.drawString(4.49*inch, 11.05*inch, "Civil Status:")
        p.drawString(6.3*inch, 11.05*inch, "Religion:")
        p.line(0.3*inch, 11*inch, 8.3*inch, 11*inch) #(x1, y1, x2, y2)
        p.line(4.45*inch, 11.45*inch, 4.45*inch, 10*inch) #(x1, y1, x2, y2) name|age division
        p.line(5.25*inch, 11.45*inch, 5.25*inch, 11.25*inch) #(x1, y1, x2, y2) age|sex division
        p.line(6.25*inch, 11.45*inch, 6.25*inch, 10*inch) #(x1, y1, x2, y2) sex|hospital no division
        p.line(4.45*inch, 11.25*inch, 8.3*inch, 11.25*inch) #(x1, y1, x2, y2) age/civil status

        #data
        p.setFont("Times-Bold", 9, leading=None)
        p.setFillColorRGB(0,0,255)
        p.drawString(0.5*inch, 11.1*inch, name)
        p.drawString(4.8*inch, 11.3*inch, age)
        p.drawString(5.55*inch, 11.3*inch, sex)
        p.drawString(7.1*inch, 11.3*inch, no)
        p.drawString(5.2*inch, 11.05*inch, cs)
        p.drawString(6.85*inch, 11.05*inch, religion.upper())
        if len(addr) <= 45:
            p.drawString(0.85*inch, 10.85*inch, addr)
        else:
            p.drawString(0.85*inch, 10.85*inch, addr[:45])
            p.drawString(0.5*inch, 10.70*inch, addr[46:])
        p.drawString(5*inch, 10.65*inch, bdate)
        if len(bplace) <=25:
            p.drawString(6.3*inch, 10.65*inch, bplace)
        else:
            p.setFont("Times-Bold", 7, leading=None)
            p.drawString(6.3*inch, 10.65*inch, bplace)
        p.setFont("Times-Bold", 9, leading=None)
        if companion:
            p.drawString(0.5*inch, 10.15*inch, companion)
        p.drawString(4.5*inch, 10.15*inch, comrel)
        p.drawString(6.95*inch, 10.1*inch, nat)
        if refer == 'SELF':
            p.roundRect(0.55*inch, 9.6*inch, 6, 6, 2, stroke=1, fill=1)
        elif refer == 'OPD':
            p.roundRect(1.25*inch, 9.6*inch, 6, 6, 2, stroke=1, fill=1)
        elif refer == 'PRIVATE':
            p.roundRect(1.95*inch, 9.6*inch, 6, 6, 2, stroke=1, fill=1)
        elif refer == 'OTHER HOSPITAL':
            p.roundRect(4.15*inch, 9.6*inch, 6, 6, 2, stroke=1, fill=1)
            p.drawString(5*inch, 9.6*inch, "Other Hospital")
        elif refer == 'OTHERS':
            p.roundRect(4.15*inch, 9.6*inch, 6, 6, 2, stroke=1, fill=1)
        p.drawString(6.65*inch, 9.8*inch, date_arrive)
        p.drawString(7.2*inch, 9.6*inch, time_arrive)
        if version == 'rev3':
            if esi == 'Resuscitation':
                p.roundRect(0.55*inch, 9.2*inch, 6, 6, 2, stroke=1, fill=1)
            elif esi == 'Emergent':
                p.roundRect(0.55*inch, 9*inch, 6, 6, 2, stroke=1, fill=1)
            elif esi == 'Urgent':
                p.roundRect(0.55*inch, 8.8*inch, 6, 6, 2, stroke=1, fill=1)
            elif esi == 'Less urgent':
                p.roundRect(1.55*inch, 9.2*inch, 6, 6, 2, stroke=1, fill=1)
            elif esi == 'Least urgent':
                p.roundRect(1.55*inch, 9*inch, 6, 6, 2, stroke=1, fill=1)
        elif version == 'rev4':
            if esi == 'Immediate':
                p.roundRect(0.55*inch, 9.2*inch, 6, 6, 2, stroke=1, fill=1)
            elif esi == 'Emergency':
                p.roundRect(0.55*inch, 9*inch, 6, 6, 2, stroke=1, fill=1)
            elif esi == 'Urgent':
                p.roundRect(0.55*inch, 8.8*inch, 6, 6, 2, stroke=1, fill=1)
            elif esi == 'Semi-urgent':
                p.roundRect(1.55*inch, 9.2*inch, 6, 6, 2, stroke=1, fill=1)
            elif esi == 'Non-urgent':
                p.roundRect(1.55*inch, 9*inch, 6, 6, 2, stroke=1, fill=1)

        if tscode == '017':#eent
            p.roundRect(2.65*inch, 9.25*inch, 6, 6, 2, stroke=1, fill=1)
        elif tscode == '001':#medine
            p.roundRect(3.35*inch, 9.25*inch, 6, 6, 2, stroke=1, fill=1)
        elif tscode == '002':#ob
            p.roundRect(4.25*inch, 9.25*inch, 6, 6, 2, stroke=1, fill=1)
        elif tscode == '003':#gyne
            p.roundRect(4.25*inch, 9.25*inch, 6, 6, 2, stroke=1, fill=1)
        elif tscode == '004':#pedia
            p.roundRect(5.25*inch, 9.25*inch, 6, 6, 2, stroke=1, fill=1)
        elif tscode == '005':#surgery
            p.roundRect(2.65*inch, 9*inch, 6, 6, 2, stroke=1, fill=1)
        else:
            p.roundRect(3.35*inch, 9*inch, 6, 6, 2, stroke=1, fill=1)
            p.drawString(4*inch, 9*inch, tsdesc)
        
        try:
            p.drawString(6.9*inch, 9.1*inch, timeseen[11:19])
        except:
            pass
        p.drawString(2.15*inch, 4.75*inch, diagnosis_text)
        if complaint is not None:
            p.drawString(0.5*inch, 8.4*inch, complaint)
        try:
            if len(management[0]['management']) < 140:
                p.drawString(0.4*inch, 4.2*inch, management[0]['management'])
            elif len(management[0]['management']) > 140 and len(management[0]['management']) < 300:
                p.drawString(0.4*inch, 4.2*inch, management[0]['management'][:140])
                p.drawString(0.4*inch, 4*inch, management[0]['management'][140:300])
        except:
            pass

        try:
            p.drawString(1.4*inch, 5.7*inch, vitals[0]['vsbp'])
            p.drawString(3.4*inch, 5.7*inch, vitals[0]['vsresp'])
            p.drawString(1.6*inch, 5.5*inch, vitals[0]['vspulse'])
            p.drawString(3.4*inch, 5.5*inch, vitals[0]['vstemp'])
        except:
            pass

        try:
            p.drawString(5.3*inch, 5.7*inch, sat[0]['o2sat'])
        except:
            pass

        try:
            p.drawString(5.3*inch, 5.5*inch, str(hw[0]['vsweight']))
            p.drawString(6.9*inch, 5.5*inch, str(hw[0]['vsheight']))
        except:
            pass

        try:
            p.drawString(5.7*inch, 7.95*inch, str(noi))
            p.drawString(5.7*inch, 7.75*inch, datetime.strftime(toi, '%I:%M %p'))
            p.drawString(5.7*inch, 7.55*inch, str(poi))
            p.drawString(5.7*inch, 7.35*inch, datetime.strftime(doi, '%m/%d/%y'))
        except:
            pass
        #end

        p.setFillColorRGB(0,0,0)
        p.setFont("Times-Bold", 9, leading=None)
        p.drawString(0.35*inch, 10.85*inch, "Address:")
        p.drawString(4.49*inch, 10.85*inch, "Date of Birth:")
        p.drawString(6.3*inch, 10.85*inch, "Place of Birth:")
        p.line(0.3*inch, 10.5*inch, 8.3*inch, 10.5*inch) #(x1, y1, x2, y2) address/companion

        p.drawString(0.35*inch, 10.35*inch, "Companion:")
        p.drawString(4.49*inch, 10.35*inch, "Relationship to patient:")
        p.drawString(6.3*inch, 10.35*inch, "Occupation:")
        p.line(6.25*inch, 10.25*inch, 8.3*inch, 10.25*inch) #(x1, y1, x2, y2) occupation/citizenship
        p.drawString(6.3*inch, 10.1*inch, "Citizenship:")

        p.line(0.3*inch, 9.95*inch, 8.3*inch, 9.95*inch) #(x1, y1, x2, y2) top border
        p.line(0.3*inch, 9.95*inch, 0.3*inch, 8.75*inch) #(x1, y1, x2, y2) left border
        p.line(6.25*inch, 9.95*inch, 6.25*inch, 8.75*inch) #(x1, y1, x2, y2) referred by|date
        p.line(8.3*inch, 9.95*inch, 8.3*inch, 8.75*inch) #(x1, y1, x2, y2) right border
        p.line(0.3*inch, 8.75*inch, 8.3*inch, 8.75*inch) #(x1, y1, x2, y2) bottom border
        p.drawString(0.35*inch, 9.8*inch, "Referred by:")
        p.setFont("Times-Roman", 9, leading=None)
        p.drawString(0.5*inch, 9.6*inch, "(   ) Self")
        p.drawString(1.2*inch, 9.6*inch, "(   ) OPD")
        p.drawString(1.9*inch, 9.6*inch, "(   ) Private MD _____________________")
        p.drawString(4.1*inch, 9.6*inch, "(   ) Others: _______________________")
        p.line(0.3*inch, 9.55*inch, 8.3*inch, 9.55*inch) #(x1, y1, x2, y2) referred by / esi
        p.setFont("Times-Bold", 9, leading=None)
        p.drawString(6.3*inch, 9.8*inch, "Date:")
        p.drawString(6.3*inch, 9.6*inch, "Time of arrival:")
        p.line(6.25*inch, 9.75*inch, 8.3*inch, 9.75*inch) #(x1, y1, x2, y2) date / time of arrival
        p.setFont("Times-Roman", 9, leading=None)
        if version == 'rev3':
            p.drawString(0.35*inch, 9.4*inch, "Emergency Severity Index (ESI)")
            p.setFont("Times-Roman", 9, leading=None)
            p.drawString(0.5*inch, 9.2*inch, "(   ) Resuscitation")
            p.drawString(0.5*inch, 9*inch, "(   ) Emergent")
            p.drawString(0.5*inch, 8.8*inch, "(   ) Urgent")
            p.drawString(1.5*inch, 9.2*inch, "(   ) Less urgent")
            p.drawString(1.5*inch, 9*inch, "(   ) Least urgent")
        elif version == 'rev4':
            p.drawString(0.35*inch, 9.4*inch, "Emergency Triage System")
            p.setFont("Times-Roman", 9, leading=None)
            p.drawString(0.5*inch, 9.2*inch, "(   ) Immediate")
            p.drawString(0.5*inch, 9*inch, "(   ) Emergency")
            p.drawString(0.5*inch, 8.8*inch, "(   ) Urgent")
            p.drawString(1.5*inch, 9.2*inch, "(   ) Semi-urgent")
            p.drawString(1.5*inch, 9*inch, "(   ) Non-urgent")
        p.setFont("Times-Bold", 9, leading=None)
        p.drawString(2.5*inch, 9.4*inch, "Service:")
        p.setFont("Times-Roman", 9, leading=None)
        p.drawString(2.6*inch, 9.25*inch, "(   ) EENT")
        p.drawString(3.3*inch, 9.25*inch, "(   ) Medicine")
        p.drawString(4.2*inch, 9.25*inch, "(   ) OB/Gyne")
        p.drawString(5.2*inch, 9.25*inch, "(   ) Pedia")
        p.drawString(2.6*inch, 9*inch, "(   ) Surgery")
        p.drawString(3.3*inch, 9*inch, "(   ) Others: ____________________________________")
        p.setFont("Times-Bold", 9, leading=None)
        p.drawString(6.3*inch, 9.4*inch, "Time seen by ER Doctor:")
        p.line(2.45*inch, 9.55*inch, 2.45*inch, 8.75*inch) #(x1, y1, x2, y2) esi/services

        p.line(0.3*inch, 8.7*inch, 8.3*inch, 8.7*inch) #(x1, y1, x2, y2) top border
        p.line(0.3*inch, 8.7*inch, 0.3*inch, 1.85*inch) #(x1, y1, x2, y2) left border
        p.line(8.3*inch, 8.7*inch, 8.3*inch, 1.85*inch) #(x1, y1, x2, y2) right border
        p.line(0.3*inch, 1.85*inch, 8.3*inch, 1.85*inch) #(x1, y1, x2, y2) bottom border
        p.setFont("Times-Bold", 9, leading=None)
        p.drawString(0.3*inch, 8.55*inch, " I. CHIEF COMPLAINT:")
        p.line(0.3*inch, 8.3*inch, 8.3*inch, 8.3*inch) #(x1, y1, x2, y2) chief complaint/history
        p.drawString(0.3*inch, 8.15*inch, " II. HISTORY OF PRESENT ILLNESS:")
        p.drawString(5.4*inch, 8.15*inch, "Trauma/injuries:")
        p.drawString(5.4*inch, 7.15*inch, "OB/Gyne: G____ P ____ (                                              )")
        p.setFont("Times-Roman", 9, leading=None)
        p.drawString(5.4*inch, 7.95*inch, "NOI:")
        p.drawString(5.4*inch, 7.75*inch, "TOI:")
        p.drawString(5.4*inch, 7.55*inch, "POI:")
        p.drawString(5.4*inch, 7.35*inch, "DOI:")
        p.line(5.35*inch, 8.3*inch, 5.35*inch, 6.5*inch) #(x1, y1, x2, y2) HISTORY/TRAUMA
        p.line(5.35*inch, 7.3*inch, 8.3*inch, 7.3*inch) #(x1, y1, x2, y2) Trauma/Ob
        p.drawString(5.4*inch, 6.95*inch, "LMP:")
        p.drawString(5.4*inch, 6.75*inch, "EDC:")
        p.drawString(5.4*inch, 6.55*inch, "AOG:")
        p.setFont("Times-Bold", 9, leading=None)
        p.drawString(0.7*inch, 6.95*inch, "Allergy/ies:")
        p.drawString(0.7*inch, 6.75*inch, "Current Medication:")
        p.drawString(0.7*inch, 6.55*inch, "Date of last tetanus injection(if any):")
        p.line(0.3*inch, 6.5*inch, 8.3*inch, 6.5*inch) #(x1, y1, x2, y2) History/physical

        p.setFont("Times-Bold", 9, leading=None)
        p.drawString(0.3*inch, 6.35*inch, " III. PHYSICAL EXAMINATION (pertinent findings):")
        p.drawString(0.7*inch, 6.2*inch, "Condition upon arrival:")
        p.drawString(0.7*inch, 5.85*inch, "Vital Signs:")
        p.drawString(0.7*inch, 5.35*inch, "Other findings:")
        p.setFont("Times-Roman", 9, leading=None)
        p.rect(1*inch,6*inch,10,10, stroke=1, fill=0)
        p.drawString(1.2*inch, 6.03*inch, "Ambulatory")
        if ercond == "AMBUL":
            p.rect(1*inch,6*inch,10,10, stroke=1, fill=1)
        else:
            p.rect(1*inch,6*inch,10,10, stroke=1, fill=0)
        p.drawString(2.2*inch, 6.03*inch, "Unconcious")
        if ercond == 'UNCON':
            p.rect(2*inch,6*inch,10,10, stroke=1, fill=1)
        else:
            p.rect(2*inch,6*inch,10,10, stroke=1, fill=0)
        p.drawString(3.2*inch, 6.03*inch, "DOA")
        if ercond == 'DOA':
            p.rect(3*inch,6*inch,10,10, stroke=1, fill=1)
        else:
            p.rect(3*inch,6*inch,10,10, stroke=1, fill=0)
        if str(ercond) != 'AMBUL' and str(ercond) != 'UNCON' and str(ercond) != 'DOA': 
            p.rect(4*inch,6*inch,10,10, stroke=1, fill=0)
            if ercond == 'CORNA':
                ercond = 'CORNATOSE'
                p.rect(4*inch,6*inch,10,10, stroke=1, fill=1)
                p.drawString(4.7*inch, 6.03*inch, ercond)
            elif ercond == 'HEMOR':
                ercond = 'HEMORRHAGIC'
                p.rect(4*inch,6*inch,10,10, stroke=1, fill=1)
                p.drawString(4.7*inch, 6.03*inch, ercond)
            p.setFont("Times-Bold", 9, leading=None)
            p.setFillColorRGB(0,0,255)
            p.setFillColorRGB(0,0,0)
            p.setFont("Times-Roman", 9, leading=None)
        p.drawString(4.2*inch, 6.03*inch, "Others: _____________________________________________________")
        p.drawString(1*inch, 5.7*inch, "BP:  _____________ mmHg")
        p.drawString(2.8*inch, 5.7*inch, "RR:  _____________ /min")
        p.drawString(4.5*inch, 5.7*inch, "O2 Sat.:  _____________ %")
        p.drawString(6.2*inch, 5.7*inch, "GCS:  ____(E: ___ V: ___ M: ____)")
        p.drawString(1*inch, 5.5*inch, "HR:  _____________ /min")
        p.drawString(2.7*inch, 5.5*inch, "Temp:  _____________ °C")
        p.drawString(4.5*inch, 5.5*inch, "Weight:  _____________ kg")
        p.drawString(6.2*inch, 5.5*inch, "Height:  _____________ cm")
        p.line(0.3*inch, 4.9*inch, 8.3*inch, 4.9*inch) #(x1, y1, x2, y2) physical/impression

        p.setFont("Times-Bold", 9, leading=None)
        p.drawString(0.3*inch, 4.75*inch, " IV. IMPRESSION/DIAGNOSIS:")
        p.line(0.3*inch, 4.5*inch, 8.3*inch, 4.5*inch) #(x1, y1, x2, y2) impression/management

        p.setFont("Times-Bold", 9, leading=None)
        p.drawString(0.3*inch, 4.35*inch, " V. MANAGEMENT:")
        p.line(0.3*inch, 2.8*inch, 8.3*inch, 2.8*inch) #(x1, y1, x2, y2) management/disposition

        p.setFont("Times-Bold", 9, leading=None)
        p.drawString(0.3*inch, 2.65*inch, " VI. DISPOSITION:")
        p.drawString(2.3*inch, 2.65*inch, "TIME:")
        p.drawString(6.4*inch, 2.65*inch, "Condition upon discharge:")
        p.setFont("Times-Roman", 9, leading=None)
        p.drawString(0.7*inch, 2.5*inch, "(    ) Treated and Sent Home")
        p.drawString(0.7*inch, 2.35*inch, "(    ) Admitted to: _________________________")
        p.drawString(0.7*inch, 2.2*inch, "(    ) Refused admission: _________________________")
        p.drawString(0.7*inch, 2.05*inch, "(    ) Referred to: _________________________")
        p.drawString(4*inch, 2.5*inch, "(    ) Absconded")
        p.drawString(4*inch, 2.35*inch, "(    ) Died")
        p.drawString(3.6*inch, 2.05*inch, "(    ) Self conduction")
        p.drawString(4.7*inch, 2.05*inch, "(    ) BRGHGMC Ambulance")
        p.drawString(3.6*inch, 1.9*inch, "(    ) Other vehicle: _________________")
        p.line(6.25*inch, 2.8*inch, 6.25*inch, 1.85*inch) #(x1, y1, x2, y2) disposition/condition
        p.drawString(6.5*inch, 2.35*inch, "(    ) Stable")
        p.drawString(6.5*inch, 2.2*inch, "(    ) Critical")
        p.drawString(6.5*inch, 2.05*inch, "(    ) Expired")

        p.line(0.8*inch, 0.7*inch, 3.5*inch, 0.7*inch)
        p.setFont("Times-Bold", 9, leading=None)
        p.drawString(1.6*inch, 0.55*inch, "ER Nurse-on-Duty")
        p.setFont("Times-Italic", 9, leading=None)
        p.drawString(1.6*inch, 0.75*inch, "Name and Signature")

        p.line(5*inch, 0.7*inch, 7.5*inch, 0.7*inch)
        p.setFont("Times-Bold", 9, leading=None)
        p.drawString(5.7*inch, 0.55*inch, "ER Doctor-on-Duty")
        p.setFont("Times-Italic", 9, leading=None)
        p.drawString(5.7*inch, 0.75*inch, "Name and Signature")

        p.line(0.8*inch, 1.3*inch, 3.5*inch, 1.3*inch)
        p.setFont("Times-Bold", 9, leading=None)
        p.drawString(1.6*inch, 1.2*inch, "Consent to Care")
        p.setFont("Times-Italic", 9, leading=None)
        p.drawString(1.3*inch, 1.35*inch, "Name of patient and Signature")

        p.line(5*inch, 1.3*inch, 7.5*inch, 1.3*inch)
        p.setFont("Times-Bold", 9, leading=None)
        p.drawString(5.7*inch, 1.2*inch, "Consent to Care")
        p.setFont("Times-Italic", 9, leading=None)
        p.drawString(4.7*inch, 1.35*inch, "Name of patient and Signature (if patient is unable to write)")

        p.line(0, 0.30*inch, 1000, 0.30*inch) #(x1, y1, x2, y2)
        p.setFont("Times-Italic", 10, leading=None)
        p.drawString(0.3*inch, 0.15*inch, "BRGHGMC-F-MS-HIM-013")
        if version == 'rev3':
            p.drawString(4*inch, 0.15*inch, "Rev. 3")
            p.drawString(6.5*inch, 0.15*inch, "Effectivity Date: January 3, 2020")
        elif version == 'rev4':
            p.drawString(2.6*inch, 0.15*inch, "Rev. 5")
            p.drawString(3.8*inch, 0.15*inch, "Effectivity Date: May 2, 2023")
            p.drawImage(pagpadabalogo, 7.2*inch, 0.05*inch, mask='auto', width=80, height=13)
        p.setTitle("ER Record")
        p.showPage()

        # page 2
        if version == 'rev3':
            p.drawImage(logo, 0.3*inch, 12*inch, mask='auto', width=72, height=72)
            p.drawImage(dohlogo, 1.4*inch, 12*inch, mask='auto', width=72, height=72)
            p.setFont("Times-Roman", 12, leading=None)
            p.setFillColor("green")
            p.drawString(2.8*inch, 12.8*inch, "Bicol Region General Hospital and Geriatric Medical Center")
            p.drawString(3.7*inch, 12.6*inch, "(Formely BICOL SANITARIUM)")
            p.setFont("Times-Roman", 11, leading=None)
            p.setFillColor("black")
            p.drawString(3.8*inch, 12.45*inch, "San Pedro, Cabusao Camarines Sur")
            p.drawString(2.8*inch, 12.3*inch, "Telephone Nos.: (054) 473-2244, 472-4422, 881-1033, 881-1761")
            p.drawString(2.95*inch, 12.16*inch, "E-mail Address: bicolsan@gmail.com, brghgmc@gmail.com")
            p.drawString(3.85*inch, 12*inch, "Website: bicolsanitarium.doh.gov.ph")
            p.line(0, 11.95*inch, 1000, 11.95*inch) #(x1, y1, x2, y2)


            p.line(0, 0.30*inch, 1000, 0.30*inch) #(x1, y1, x2, y2)
            p.setFont("Times-Italic", 10, leading=None)
            p.drawString(0.3*inch, 0.15*inch, "BRGHGMC-F-MS-HIM-013")
            p.drawString(4*inch, 0.15*inch, "Rev. 3 ")
            p.drawString(6.5*inch, 0.15*inch, "Effectivity Date: January 3, 2020")
            p.setFont("Times-Bold", 10, leading=None)
            p.drawString(0.3*inch, 11.8*inch, "For Trauma/Injuries:")
            p.setFont("Times-Italic", 9, leading=None)
            p.drawString(7.7*inch, 11.8*inch, "Page 2 of 2")
            body = ImageReader(static_root + '/integrated/img/er_body.png')
            p.drawImage(body, 0.5*inch, 8.8*inch, mask='auto', width=500, height=200)
            p.setFont("Times-Bold", 10, leading=None)
            p.drawString(0.3*inch, 8.5*inch, "Nurse's Notes")
            p.drawString(0.35*inch, 8.28*inch, "DATE/SHIFT")
            p.drawString(0.55*inch, 8.14*inch, "TIME")
            p.drawString(1.7*inch, 8.22*inch, "FOCUS/DATA")
            p.drawString(4.4*inch, 8.22*inch, "ACTION")
            p.drawString(7*inch, 8.22*inch, "RESPONSE")
            p.line(0.3*inch, 8.4*inch, 0.3*inch, 0.6*inch) #(x1, y1, x2, y2)
            p.line(8.3*inch, 8.4*inch, 8.3*inch, 0.6*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 8.4*inch, 8.3*inch, 8.4*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 8.1*inch, 8.3*inch, 8.1*inch) #(x1, y1, x2, y2)
            p.line(1.25*inch, 8.4*inch, 1.25*inch, 0.6*inch) #(x1, y1, x2, y2)
            p.line(3*inch, 8.4*inch, 3*inch, 0.6*inch) #(x1, y1, x2, y2)
            p.line(6.4*inch, 8.4*inch, 6.4*inch, 0.6*inch) #(x1, y1, x2, y2)

            p.line(0.3*inch, 7.8*inch, 8.3*inch, 7.8*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 7.5*inch, 8.3*inch, 7.5*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 7.2*inch, 8.3*inch, 7.2*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 6.9*inch, 8.3*inch, 6.9*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 6.6*inch, 8.3*inch, 6.6*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 6.3*inch, 8.3*inch, 6.3*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 6*inch, 8.3*inch, 6*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 5.7*inch, 8.3*inch, 5.7*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 5.4*inch, 8.3*inch, 5.4*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 5.1*inch, 8.3*inch, 5.1*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 4.8*inch, 8.3*inch, 4.8*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 4.5*inch, 8.3*inch, 4.5*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 4.2*inch, 8.3*inch, 4.2*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 3.9*inch, 8.3*inch, 3.9*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 3.6*inch, 8.3*inch, 3.6*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 3.3*inch, 8.3*inch, 3.3*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 3*inch, 8.3*inch, 3*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 2.7*inch, 8.3*inch, 2.7*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 2.4*inch, 8.3*inch, 2.4*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 2.1*inch, 8.3*inch, 2.1*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 1.8*inch, 8.3*inch, 1.8*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 1.5*inch, 8.3*inch, 1.5*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 1.2*inch, 8.3*inch, 1.2*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 0.9*inch, 8.3*inch, 0.9*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 0.6*inch, 8.3*inch, 0.6*inch) #(x1, y1, x2, y2)
        elif version == 'rev4':
            p.drawImage(logo, 0.3*inch, 12*inch, mask='auto', width=72, height=72)
            p.drawImage(dohlogo, 1.4*inch, 12*inch, mask='auto', width=72, height=72)
            p.setFont("Times-Roman", 12, leading=None)
            p.setFillColor("green")
            p.drawString(2.8*inch, 12.8*inch, "Bicol Region General Hospital and Geriatric Medical Center")
            p.drawString(3.7*inch, 12.6*inch, "(Formely BICOL SANITARIUM)")
            p.setFont("Times-Roman", 11, leading=None)
            p.setFillColor("black")
            p.drawString(3.8*inch, 12.45*inch, "San Pedro, Cabusao Camarines Sur")
            p.drawString(2.8*inch, 12.3*inch, "Telephone Nos.: (054) 473-2244, 472-4422, 881-1033, 881-1761")
            p.drawString(2.95*inch, 12.16*inch, "E-mail Address: bicolsan@gmail.com, brghgmc@gmail.com")
            p.drawString(3.85*inch, 12*inch, "Website: bicolsanitarium.doh.gov.ph")
            p.line(0, 11.95*inch, 1000, 11.95*inch) #(x1, y1, x2, y2)

            p.line(0, 0.30*inch, 1000, 0.30*inch) #(x1, y1, x2, y2)
            p.setFont("Times-Italic", 10, leading=None)
            p.drawString(0.3*inch, 0.15*inch, "BRGHGMC-F-MS-HIM-013")
            p.drawString(2.6*inch, 0.15*inch, "Rev. 5")
            p.drawString(3.8*inch, 0.15*inch, "Effectivity Date: May 2, 2023")
            p.drawImage(pagpadabalogo, 7.2*inch, 0.05*inch, mask='auto', width=80, height=13)

            body = ImageReader(static_root + '/integrated/img/traumapic.jpg')
            p.drawImage(body, 0.3*inch, 9.5*inch, mask='auto', width=250, height=150)

            p.line(0.3*inch, 11.8*inch, 0.3*inch, 0.6*inch) #(x1, y1, x2, y2)
            p.line(8.3*inch, 11.8*inch, 8.3*inch, 0.6*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 11.8*inch, 8.3*inch, 11.8*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 11.55*inch, 8.3*inch, 11.55*inch) #(x1, y1, x2, y2)

            p.line(3.8*inch, 11.8*inch, 3.8*inch, 0.6*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 6.1*inch, 8.3*inch, 6.1*inch) #(x1, y1, x2, y2)

            p.line(3.8*inch, 11.3*inch, 8.3*inch, 11.3*inch) #(x1, y1, x2, y2)
            p.line(3.8*inch, 11.1*inch, 8.3*inch, 11.1*inch) #(x1, y1, x2, y2)
            p.line(3.8*inch, 10.9*inch, 8.3*inch, 10.9*inch) #(x1, y1, x2, y2)
            p.line(3.8*inch, 10.7*inch, 8.3*inch, 10.7*inch) #(x1, y1, x2, y2)
            p.line(3.8*inch, 10.5*inch, 8.3*inch, 10.5*inch) #(x1, y1, x2, y2)
            p.line(3.8*inch, 10.3*inch, 8.3*inch, 10.3*inch) #(x1, y1, x2, y2)
            p.line(3.8*inch, 10.1*inch, 8.3*inch, 10.1*inch) #(x1, y1, x2, y2)
            p.line(3.8*inch, 9.9*inch, 8.3*inch, 9.9*inch) #(x1, y1, x2, y2)
            p.line(3.8*inch, 9.7*inch, 8.3*inch, 9.7*inch) #(x1, y1, x2, y2)
            
            p.line(0.3*inch, 9.5*inch, 8.3*inch, 9.5*inch) #(x1, y1, x2, y2)
            p.line(1.5*inch, 9.3*inch, 8.3*inch, 9.3*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 9.1*inch, 8.3*inch, 9.1*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 8.9*inch, 8.3*inch, 8.9*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 8.7*inch, 8.3*inch, 8.7*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 8.5*inch, 8.3*inch, 8.5*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 8.3*inch, 8.3*inch, 8.3*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 8.1*inch, 8.3*inch, 8.1*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 7.9*inch, 8.3*inch, 7.9*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 7.7*inch, 8.3*inch, 7.7*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 7.5*inch, 8.3*inch, 7.5*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 7.3*inch, 8.3*inch, 7.3*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 7.1*inch, 8.3*inch, 7.1*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 6.9*inch, 8.3*inch, 6.9*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 6.7*inch, 8.3*inch, 6.7*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 6.5*inch, 8.3*inch, 6.5*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 6.3*inch, 8.3*inch, 6.3*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 6.1*inch, 8.3*inch, 6.1*inch) #(x1, y1, x2, y2)

            p.line(0.9*inch, 9.1*inch, 0.9*inch, 0.6*inch) #(x1, y1, x2, y2)
            p.line(1.5*inch, 9.5*inch, 1.5*inch, 6.1*inch) #(x1, y1, x2, y2)
            p.line(2.2*inch, 9.3*inch, 2.2*inch, 6.1*inch) #(x1, y1, x2, y2)
            p.line(2.7*inch, 9.3*inch, 2.7*inch, 6.1*inch) #(x1, y1, x2, y2)
            p.line(3.3*inch, 9.3*inch, 3.3*inch, 6.1*inch) #(x1, y1, x2, y2)

            p.line(5.8*inch, 11.8*inch, 5.8*inch, 6.1*inch) #(x1, y1, x2, y2)
            p.line(6.5*inch, 11.8*inch, 6.5*inch, 6.1*inch) #(x1, y1, x2, y2)
            p.line(7.2*inch, 11.8*inch, 7.2*inch, 6.1*inch) #(x1, y1, x2, y2)

            p.line(4.5*inch, 6.1*inch, 4.5*inch, 0.6*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 5.7*inch, 8.3*inch, 5.7*inch) #(x1, y1, x2, y2)
            p.line(0.3*inch, 0.6*inch, 8.3*inch, 0.6*inch) #(x1, y1, x2, y2)
            
            p.setFont("Times-Roman", 11, leading=None)
            p.drawString(1.2*inch, 11.64*inch, "FOR TRAUMA/INJURIES")
            p.drawString(4.2*inch, 11.64*inch, "CONTRAPTIONS")
            p.drawString(5.95*inch, 11.64*inch, "DATE")
            p.drawString(6.65*inch, 11.64*inch, "TIME")
            p.drawString(7.32*inch, 11.64*inch, "SIGNATURE")

            p.drawString(4.45*inch, 10.54*inch, "IV FLUIDS")
            p.drawString(5.95*inch, 10.54*inch, "DATE")
            p.drawString(6.65*inch, 10.54*inch, "TIME")
            p.drawString(7.32*inch, 10.54*inch, "SIGNATURE")

            p.drawString(4.43*inch, 9.54*inch, "SIDE DRIPS")
            p.drawString(5.95*inch, 9.54*inch, "DATE")
            p.drawString(6.65*inch, 9.54*inch, "TIME")
            p.drawString(7.32*inch, 9.54*inch, "SIGNATURE")

            p.drawString(3.85*inch, 8.54*inch, "MEDICATION/TREATMENT")
            p.drawString(5.95*inch, 8.54*inch, "DATE")
            p.drawString(6.65*inch, 8.54*inch, "TIME")
            p.drawString(7.32*inch, 8.54*inch, "SIGNATURE")

            p.drawString(0.44*inch, 9.32*inch, "DIAGNOSTIC")
            p.drawString(0.45*inch, 9.19*inch, "PROCEDURE")
            p.drawString(2.2*inch, 9.35*inch, "DATE/TIME")

            p.drawString(0.43*inch, 6.95*inch, "DIET")
            p.drawString(0.38*inch, 5.93*inch, "DATE/")
            p.drawString(0.4*inch, 5.78*inch, "TIME")

            p.drawString(1.7*inch, 5.85*inch, "DOCTOR'S ORDER")

            p.drawString(3.93*inch, 5.93*inch, "DATE/")
            p.drawString(3.95*inch, 5.78*inch, "TIME")

            p.drawString(5.8*inch, 5.83*inch, "NURSE'S NOTES")

            p.setFont("Times-Roman", 8, leading=None)
            p.drawString(1.53*inch, 9.16*inch, "REQUESTED")
            p.drawString(2.3*inch, 9.16*inch, "DONE")
            p.drawString(2.72*inch, 9.16*inch, "AWAITING")
            p.drawString(3.5*inch, 9.16*inch, "IN")

        p.showPage()
        p.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
    except Exception as e:
        messages.error(request, str(e))
        return HttpResponseRedirect("/erlist")

def ertat_report(request):
    if request.session.get('employee_id') is not None:
        list_ = []
        count = 0
        hit = 0
        ave_sum = 0
        total_ave = 0
        if request.method == 'POST':
            start = request.POST.get('start')
            end = request.POST.get('end')
            lists = requests.post(er_tat_api, data={'start': start, 'end': end}).json()
            if lists['status'] == 'success':
                list_ = lists['data']
                for i in list_:
                    ave = (i['discharged']/i['count'])*100
                    i['ave'] = round(ave, 2)
                    count += i['count']
                    hit += i['discharged']
                total_ave = round((hit/count)*100, 2)

        return render(request, 'integrated/reports/er_tat.html', {'page': 'Reports', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': list_, 'ave': total_ave})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def er_tat_daily_report(request, date):
    if request.session.get('employee_id') is not None:
        lists = requests.post(er_daily_tat_api, data={'date': date}).json()
        if lists['status'] == 'success':
            list_ = lists['data']
            for i in list_:
                i['enccode'] = i['enccode'].replace('/', '-')
        return render(request, 'integrated/reports/er_tat_daily.html', {'page': 'Reports', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': list_})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})
    