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
#root = "http://173.10.2.108:9092/"
root = "http://172.22.10.11:9091/"
login_api = root + "api/login"
opd_patient_list_api = root + "api/opd/getPatientList"
opd_patient_for_retrieval_api = root + "api/opd/getPatientForRetrieval"
opd_patient_for_printing_api = root + "api/opd/getPatientForPrinting"
patient_search_api = root + "api/patients/patient-search"
patient_search_rfid_api = root + "api/patients/patient-search-rfid"
patient_search_enc_api = root + "api/enc/getEncounterByNo"
religion_list_api = root + "api/patients/getReligion"
province_list_api = root + "api/patients/getProvince"
municipality_list_api = root + "api/patients/getMunicipality/"
barangay_list_api = root + "api/patients/getBarangay/"
new_patient_api = root + "api/patients/addPatient"
patient_details_api = root + "api/patients/details"
update_patient_rfid_api = root + "api/patients/updateRFID"
patient_update_api = root + "api/patients/update"
consultation_list_api = root + "api/enc/getEncounterByNo"
add_prehomis_api = root + "api/opd/prehomis"
get_prehomise_patient_api = root + "api/opd/triagePatient"
get_prehomise_details_api = root + "api/opd/prehomisdetails"
opd_log_patient_api = root + "api/opd/"
#RECORD
opd_record_api = root + "api/patients/getOPDRecord"
vital_sign_api = root + "api/patients/getVitalSign"
height_weight_api = root + "api/patients/getHeightWeight"
patient_address_api = root + "api/patients/getPatientAddress"
present_illlness_api = root + "api/patients/getPresentIllness"
complaint_api = root + "api/patients/getPatientComplaint"
diagnosis_api = root + "api/patients/getDiagnosis"
#BILLING
all_patients_api = root + "api/enc/getAllEncounter"
soa_header_api = root + "api/billing/generateSOA"
detailed_soa_header_api = root + "api/billing/generateDetailedSOA"
soa_other_det_api = root + "api/billing/saveSoaOthDet"
maip_report_api = root + "api/billing/maipReport"
#DISCOUNT 
add_discount_api = root + "api/billing/addDiscount"
add_pf_discount_api = root + "api/billing/addPfDiscount"
delete_discount_api = root + "api/billing/deleteDiscount"
delete_pf_discount_api = root + "api/billing/delPfDiscount"
#DIAGNOSIS
patient_diagnosis_api = root + "api/patients/getPatientDiagnosis"
add_diagnosis_api = root + "api/patients/addDiagnosis"
patient_details_by_enc_api = root + "api/enc/getPatientDetailsByEnc"
delete_diagnosis_api = root + "api/patients/deleteDiagnosis"
#DOCTORS
doctors_list_api = root + "api/doctor/getDoctors"
#CASE RATE
patient_case_rate_api = root + "api/patients/getPatientCaseRate"
first_case_api = root + "api/caserate/firstcase"
second_case_api = root + "api/caserate/secondcase"
add_case_rate_api = root + "api/caserate/addcaserate"
delete_case_rate_api = root + "api/caserate/deleteCaseRate"
#PROFESSIONAL FEE
patient_proffee_api = root + "api/patients/getPatientProffee"
add_proffee_api = root + "api/patients/addPatientProffee"
delete_proffee_api = root + "api/patients/deletePatientProffee"
#RADIOLOGY
rad_exam_api = root + "api/radio/getExaminations"
rad_charges_api = root + "api/radio/getCharges"
rad_charges_by_doc_api = root + "api/radio/getChargesByDoc"
rad_simple_charge_api = root + "api/radio/simpleCharge"
rad_del_charge_api = root + "api/radio/deleteSimpleCharge"
rad_total_charge_api = root + "api/radio/getTotalAmount"
rad_exam_result_api = root + "api/radio/getRadExamResult"
rad_exam_add_result_api = root + "api/radio/saveRadExamResult"
#LABORATORY
lab_exam_api = root + "api/laboratory/getExaminations"
lab_simple_charge_api = root + "api/laboratory/simpleCharge"
lab_del_charge_api = root + "api/laboratory/deleteSimpleCharge"
lab_charges_api = root + "api/laboratory/getCharges"
lab_total_charge_api = root + "api/laboratory/getTotalAmount"
#PHARMACY
pha_patient_api = root + "api/pharmacy"
pha_prescription_api = root + "api/pharmacy/prescription"
pha_release_prescription_api = root + "api/pharmacy/release"
pha_undo_prescription_api = root + "api/pharmacy/undo"
pres_md_api = root + "api/pharmacy/getPrescribingDoctor"
age_api = root + "api/patients/age"
#E-NURSE
patient_record_api = root + "api/patients/getPatientRecords"
patient_mgh_api = root + "api/patients/mayGoHome"
add_mgh_api = root + "api/patients/addMayGoHome"
update_mgh_api = root + "api/patients/updateMayGoHome"
nurse_clearance_api = root + "api/enurse/clearance"
#PROFILE
update_user_api = root + "api/profile/updateProfile"
update_user_pw_api = root + "api/profile/updatePassword"
#CLEARANCE 
clearance_api = root + "api/clearance"
patient_clearance_api = root + "api/clearance/clear"
patient_undo_clearance_api = root + "api/clearance/undo"
#PRINTED CHARGESLIP
add_printed_cl_api = root + "api/charges/addPrintedChargeSlip"
get_printed_cl_api = root + "api/charges/getPrintedChargeSlip"
#CHARGES
get_charges_api = root + "api/billing/getChargesByCode"
update_charges_api = root + "api/billing/updateCharges"
delete_charges_api = root + "api/billing/deleteCharges"
get_chargelist_api = root + "api/charges/chargelist"
add_charges_api = root + "api/charges/postCharges2"
load_charges_api = root + "api/charges/getCharges"
del_charges_api = root + "api/charges/deleteCharges"
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
#MSS
get_mss_class_api = root + "api/mss/getClassification"
get_mss_patient_list_api = root + "api/mss"
get_patient_typser_api = root + "api/enc/getServices"
add_patient_mss_class_api = root + "api/mss/addMSSRecord2"
get_patient_mss_api = root + "api/mss/getPatientMSSClass"
#DIALYSIS
dial_pat_list_api = root + "api/dialysis/patients"
dial_enrollment_api = root + "api/dialysis/enroll"
dial_log_api = root + "api/dialysis"
dial_add_api = root + "api/dialysis/log"
dial_add_vs_api = root + "api/dialysis/addVS"
dial_update_api = root + "api/dialysis/update"
dial_details_api = root + "api/dialysis/logdetails"
dial_enrolled_api = root + "api/dialysis/patientEnrolled"
dial_update_patient_api = root + "api/dialysis/updatePatient"
dial_discharged_api = root + "api/dialysis/updateDischarged"
#REPORTS
rep_er_referral = root + "api/reports/getERReferral"
rep_er_incoming_referral = root + "api/reports/getIncomingReferals"
rep_er_outgoing_referral = root + "api/reports/getOutgoingReferals"
daily_movement_api = root + "api/reports/dailyPatientMovement"
bill_rendered_api = root + "api/reports/billRendered"

class HtmlPdf(FPDF, HTMLMixin):
    pass

def index(request):
    if request.session.get('employee_id') is not None:
        user_level = request.session['user_level']
        if user_level == 2:
            clearance = requests.post(nurse_clearance_api, data={'username': request.session['userid']}).json()["data"]
            for i in clearance:
                i['date_gen'] = datetime.strptime(i['date_gen'][:10] + " " + i['date_gen'][11:18], "%Y-%m-%d %H:%M:%S")
                if i['cssr']:
                    i['cssr'] = datetime.strptime(i['cssr'][:10] + " " + i['cssr'][11:18], "%Y-%m-%d %H:%M:%S")
                if i['phic']:
                    i['phic'] = datetime.strptime(i['phic'][:10] + " " + i['phic'][11:18], "%Y-%m-%d %H:%M:%S")
                if i['lab']:
                    i['lab'] = datetime.strptime(i['lab'][:10] + " " + i['lab'][11:18], "%Y-%m-%d %H:%M:%S")
                if i['rad']:
                    i['rad'] = datetime.strptime(i['rad'][:10] + " " + i['rad'][11:18], "%Y-%m-%d %H:%M:%S")
                if i['billing']:
                    i['billing'] = datetime.strptime(i['billing'][:10] + " " + i['billing'][11:18], "%Y-%m-%d %H:%M:%S")
                if i['cashier']:
                    i['cashier'] = datetime.strptime(i['cashier'][:10] + " " + i['cashier'][11:18], "%Y-%m-%d %H:%M:%S")
                if i['nurse']:
                    i['nurse'] = datetime.strptime(i['nurse'][:10] + " " + i['nurse'][11:18], "%Y-%m-%d %H:%M:%S")
                if i['pharmacy']:
                    i['pharmacy'] = datetime.strptime(i['pharmacy'][:10] + " " + i['pharmacy'][11:18], "%Y-%m-%d %H:%M:%S")
        else:
            clearance = requests.post(clearance_api).json()["data"]
            for i in clearance:
                i['date_gen'] = datetime.strptime(i['date_gen'][:10] + " " + i['date_gen'][11:18], "%Y-%m-%d %H:%M:%S")
                if i['cssr']:
                    i['cssr'] = datetime.strptime(i['cssr'][:10] + " " + i['cssr'][11:18], "%Y-%m-%d %H:%M:%S")
                if i['phic']:
                    i['phic'] = datetime.strptime(i['phic'][:10] + " " + i['phic'][11:18], "%Y-%m-%d %H:%M:%S")
                if i['lab']:
                    i['lab'] = datetime.strptime(i['lab'][:10] + " " + i['lab'][11:18], "%Y-%m-%d %H:%M:%S")
                if i['rad']:
                    i['rad'] = datetime.strptime(i['rad'][:10] + " " + i['rad'][11:18], "%Y-%m-%d %H:%M:%S")
                if i['billing']:
                    i['billing'] = datetime.strptime(i['billing'][:10] + " " + i['billing'][11:18], "%Y-%m-%d %H:%M:%S")
                if i['cashier']:
                    i['cashier'] = datetime.strptime(i['cashier'][:10] + " " + i['cashier'][11:18], "%Y-%m-%d %H:%M:%S")
                if i['nurse']:
                    i['nurse'] = datetime.strptime(i['nurse'][:10] + " " + i['nurse'][11:18], "%Y-%m-%d %H:%M:%S")
                if i['pharmacy']:
                    i['pharmacy'] = datetime.strptime(i['pharmacy'][:10] + " " + i['pharmacy'][11:18], "%Y-%m-%d %H:%M:%S")
        today = datetime.now()
        end = today - timedelta(days=today.isoweekday())
        start = end - timedelta(days=7)
        end = datetime.strftime(end, "%Y-%m-%d")
        start = datetime.strftime(start, "%Y-%m-%d")
        er_tat = requests.post(get_er_tat_api).json()["data"]
        label = []
        data = []
        for i in er_tat:
            label.append(str(i['date']))
            if i['discharged'] != 0:
                data.append((i['discharged']/i['count']) * 100)
            else:
                data.append(0)
        return render(request, 'integrated/index.html', {'page': 'Dashboard', 'user_level': request.session['user_level'], 'name': request.session['name'], 'user_level': user_level, 'clearance': clearance, 'label': label, 'data': data})
    else:
        return HttpResponseRedirect('/login')

def clearance(request, uid):
    user_level = request.session['user_level']
    if user_level == 3:#LABORATORY
        clear = requests.post(patient_clearance_api, data={'ref': 'lab', 'uid': uid}).json()["status"]
    elif user_level == 4:#RADIOLOGY
        clear = requests.post(patient_clearance_api, data={'ref': 'rad', 'uid': uid}).json()["status"]
    elif user_level == 5:#PHARMACY
        clear = requests.post(patient_clearance_api, data={'ref': 'pharmacy', 'uid': uid}).json()["status"]
    elif user_level == 15:#BILLING
        clear = requests.post(patient_clearance_api, data={'ref': 'billing', 'uid': uid}).json()["status"]
    elif user_level == 16:#CASHIERING
        clear = requests.post(patient_clearance_api, data={'ref': 'cashier', 'uid': uid}).json()["status"]
    elif user_level == 2:#NURSING
        clear = requests.post(patient_clearance_api, data={'ref': 'nurse', 'uid': uid}).json()["status"]
    elif user_level == 6:#PHILHEALTH
        clear = requests.post(patient_clearance_api, data={'ref': 'phic', 'uid': uid}).json()["status"]
    elif user_level == 11:#CSSR
        clear = requests.post(patient_clearance_api, data={'ref': 'cssr', 'uid': uid}).json()["status"]
    return HttpResponseRedirect('/')

def clearance_undo(request, uid):
    user_level = request.session['user_level']
    if user_level == 3:#LABORATORY
        clear = requests.post(patient_undo_clearance_api, data={'ref': 'lab', 'uid': uid}).json()["status"]
    elif user_level == 4:#RADIOLOGY
        clear = requests.post(patient_undo_clearance_api, data={'ref': 'rad', 'uid': uid}).json()["status"]
    elif user_level == 5:#PHARMACY
        clear = requests.post(patient_undo_clearance_api, data={'ref': 'pharmacy', 'uid': uid}).json()["status"]
    elif user_level == 15:#BILLING
        clear = requests.post(patient_undo_clearance_api, data={'ref': 'billing', 'uid': uid}).json()["status"]
    elif user_level == 16:#CASHIERING
        clear = requests.post(patient_undo_clearance_api, data={'ref': 'cashier', 'uid': uid}).json()["status"]
    elif user_level == 2:#NURSING
        clear = requests.post(patient_undo_clearance_api, data={'ref': 'nurse', 'uid': uid}).json()["status"]
    elif user_level == 6:#PHILHEALTH
        clear = requests.post(patient_undo_clearance_api, data={'ref': 'phic', 'uid': uid}).json()["status"]
    elif user_level == 11:#CSSR
        clear = requests.post(patient_undo_clearance_api, data={'ref': 'cssr', 'uid': uid}).json()["status"]
    return HttpResponseRedirect('/')

def opd(request):
    if request.session.get('employee_id') is not None:
        return render(request, 'integrated/opd/index.html', {'page': 'Out-Patient', 'user_level': request.session['user_level'], 'name': request.session['name']})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def log_opd(request, no):
    if request.session.get('employee_id') is not None:
        if request.method == "POST":
            items = request.POST.getlist('charges')
            items = tuple(items)
            add_prehomis = requests.post(add_prehomis_api, data={'hospital_no': no, 'items': items}).json()
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
        return render(request, 'integrated/opd/log.html', {'page': 'Out-Patient', 'user_level': request.session['user_level'], 'name': request.session['name'], 'no':no, 'details': details, 'now': now, 'addr': addr})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def opd_triage(request):
    if request.session.get('employee_id') is not None:
        data = requests.post(get_prehomise_patient_api).json()["data"]
        return render(request, 'integrated/opd/triage.html', {'page': 'Out-Patient', 'user_level': request.session['user_level'], 'name': request.session['name'], 'data': data})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def opd_patient_triage(request, uid):
    if request.session.get('employee_id') is not None:
        details_response = requests.post(get_prehomise_details_api, data={'pre_uid': uid}).json()
        if details_response['status'] == 'success':
            details = details_response['data']
            details['details'][0]['patbdate'] = datetime.strptime(details['details'][0]['patbdate'][:10], "%Y-%m-%d")
            no = details['details'][0]['hpercode']
        if request.method == "POST":
            services = request.POST.get('services')
            type_of_consultation = request.POST.get("type_of_consultation")
            chief_complaint = request.POST.get("complaint")
            log = requests.post(opd_log_patient_api, data={'pre_uid': uid, 'hpercode': no, 'tscode': services, 'type_of_consultation': type_of_consultation, 'chief_complaint': chief_complaint, 'entryby': request.session['employee_id']}).json()['status']
        now = datetime.now()
        addr_response = requests.post(patient_address_api, data={'no': no})
        addr_json_response = addr_response.json()
        if addr_json_response['status'] == 'success':
            addr = addr_json_response['data']
        else:
            addr = []
        now = datetime.now()
        return render(request, 'integrated/opd/triage_log.html', {'page': 'Out-Patient', 'user_level': request.session['user_level'], 'name': request.session['name'], 'no':no, 'details': details, 'now': now, 'addr': addr, 'uid': uid})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})


def opd_retrieval(request):
    if request.session.get('employee_id') is not None:
        patient_list_response = requests.post(opd_patient_for_retrieval_api)
        patient_list_json_response = patient_list_response.json()
        if patient_list_json_response['status'] == 'success':
            return render(request, 'integrated/retrieval.html', {'page': 'Out-Patient', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': patient_list_json_response['data']})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def opd_printing(request):
    if request.session.get('employee_id') is not None:
        patient_list_response = requests.post(opd_patient_for_printing_api)
        patient_list_json_response = patient_list_response.json()
        if patient_list_json_response['status'] == 'success':
            return render(request, 'integrated/printing.html', {'page': 'Out-Patient', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': patient_list_json_response['data']})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def patient_search(request, page):
    if request.session.get('employee_id') is not None:
        if request.method == 'POST':
            today = datetime.today()
            hospital_no = request.POST.get("hospital_no")
            lastname = request.POST.get("lastname").upper()
            firstname = request.POST.get("firstname").upper()
            middlename = request.POST.get("middlename").upper()
            no = 't'
            search_response = requests.post(patient_search_api, data={'no': hospital_no, 'lastname': lastname, 'firstname': firstname, 'middlename': middlename})
            search_json_response = search_response.json()
            if search_json_response['status'] == 'success':
                for i in search_json_response['data']:
                    i['dob'] = datetime.strptime(i['dob'][:11], "%b %d %Y")
                return render(request, 'integrated/patient_search_result.html', {'result': search_json_response['data'], 'user_level': request.session['user_level'], 'name': request.session['name'], 'today': today, 'page': page, 'no': no})
            else:
                msg = "Record not found"
                return render(request, 'integrated/patient_search_result.html', {'page': 'Search Result', 'msg': msg, 'user_level': request.session['user_level'], 'name': request.session['name'], 'page': page})
        else:
            msg = "Incorrect Search Procedure, Please ask for assistance"
            return render(request, 'integrated/patient_search_result.html', {'page': 'Search Result', 'msg': msg, 'user_level': request.session['user_level'], 'name': request.session['name'], 'page': page})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def patient_search_opd(request):
    if request.session.get('employee_id') is not None:
        if request.method == 'POST':
            today = datetime.today()
            hospital_no = request.POST.get("hospital_no")
            lastname = request.POST.get("lastname").upper()
            firstname = request.POST.get("firstname").upper()
            middlename = request.POST.get("middlename").upper()
            no = 't'
            search_response = requests.post(patient_search_api, data={'no': hospital_no, 'lastname': lastname, 'firstname': firstname, 'middlename': middlename})
            search_json_response = search_response.json()
            if search_json_response['status'] == 'success':
                for i in search_json_response['data']:
                    i['dob'] = datetime.strptime(i['dob'][:11], "%b %d %Y")
                return render(request, 'integrated/opd/patient_search_result.html', {'result': search_json_response['data'], 'user_level': request.session['user_level'], 'name': request.session['name'], 'today': today, 'no': no})
            else:
                msg = "Record not found"
                return render(request, 'integrated/opd/patient_search_result.html', {'page': 'Search Result', 'msg': msg, 'user_level': request.session['user_level'], 'name': request.session['name']})
        else:
            msg = "Incorrect Search Procedure, Please ask for assistance"
            return render(request, 'integrated/opd/patient_search_result.html', {'page': 'Search Result', 'msg': msg, 'user_level': request.session['user_level'], 'name': request.session['name']})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def patient_search_rfid(request, page):
    if request.session.get('employee_id') is not None:
        if request.method == 'POST':
            today = datetime.today()
            rfid = request.POST.get("rfid")
            hospno = ""
            search_response = requests.post(patient_search_rfid_api, data={'rfid': rfid})
            search_json_response = search_response.json()
            if search_json_response['status'] == 'success':
                if search_json_response['data']:
                    for i in search_json_response['data']:
                        i['dob'] = datetime.strptime(i['dob'][:11], "%b %d %Y")
                        hospno = i['hpercode']
                    # print(hospno)
                    return HttpResponseRedirect("/" + hospno + "/" + page + "/patientdetails")
                    #return render(request, 'integrated/patient_search_result.html', {'result': search_json_response['data'], 'user_level': request.session['user_level'], 'name': request.session['name'], 'today': today, 'page': page})
                else:
                    msg = "Record not found"
                    return render(request, 'integrated/patient_search_result.html', {'page': 'Search Result', 'msg': msg, 'user_level': request.session['user_level'], 'name': request.session['name'], 'page': page})
            else:
                msg = "Record not found"
                return render(request, 'integrated/patient_search_result.html', {'page': 'Search Result', 'msg': msg, 'user_level': request.session['user_level'], 'name': request.session['name'], 'page': page})
        else:
            msg = "Incorrect Search Procedure, Please ask for assistance"
            return render(request, 'integrated/patient_search_result.html', {'page': 'Search Result', 'msg': msg, 'user_level': request.session['user_level'], 'name': request.session['name'], 'page': page})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def new_patient(request):
    if request.session.get('employee_id') is not None:
        if request.method == "POST":
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
            newpatient_response = requests.post(new_patient_api, data={'lastname': lastname, 'firstname': firstname, 'middlename': middlename, 'suffix': suffix, 'sex': sex, 'birthdate': birthdate, 'birthplace': birthplace, 'street': street, 'province': province, 'municipality': municipality, 'barangay': barangay, 'nickname': nickname, 'civilstatus': civilstatus, 'employment': employment, 'nationality': nationality, 'religion': religion, 'contactno': contactno, 'occupation': occupation, 'hfhudcode': '0000258', 'encoder': encoder})
            newpatient_json_response = newpatient_response.json()
            if newpatient_json_response['status'] == 'success':
                return HttpResponseRedirect('/' + newpatient_json_response['data']['hospital_no'] + "/Emergency Room/patientdetails")
            religion = []
            provice = []
            municipality = []
            barangay = []
            if request.method == 'POST':
                return render(request, 'integrated/new_patient.html', {'page': 'New Patient Record', 'user_level': request.session['user_level'], 'name': request.session['name']})
            else:
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
                municipality_response = requests.get(municipality_list_api + "0517")
                municipality_response_json = municipality_response.json()
                if municipality_response_json['status'] == 'success':
                    municipality = municipality_response_json['data']
                #GET BARANGAY
                barangay_response = requests.get(barangay_list_api + "051718")
                barangay_response_json = barangay_response.json()
                if barangay_response_json['status'] == 'success':
                    barangay = barangay_response_json['data']
                return render(request, 'integrated/new_patient.html', {'page': 'New Patient Record', 'user_level': request.session['user_level'], 'name': request.session['name'], 'religion': religion, 'province': province, 'municipality': municipality, 'barangay': barangay})
        else:
            religion = []
            provice = []
            municipality = []
            barangay = []
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
            municipality_response = requests.get(municipality_list_api + "0517")
            municipality_response_json = municipality_response.json()
            if municipality_response_json['status'] == 'success':
                municipality = municipality_response_json['data']
            #GET BARANGAY
            barangay_response = requests.get(barangay_list_api + "051718")
            barangay_response_json = barangay_response.json()
            if barangay_response_json['status'] == 'success':
                barangay = barangay_response_json['data']
            return render(request, 'integrated/new_patient.html', {'page': 'New Patient Record', 'user_level': request.session['user_level'], 'name': request.session['name'], 'religion': religion, 'province': province, 'municipality': municipality, 'barangay': barangay})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})
    
def patientDetailsOPD(request, no):
    if request.session.get('employee_id') is not None:
        religion = []
        provice = []
        municipality = []
        barangay = []
        msg = ""
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
            try:
                fs = FTPStorage()
                if bool(request.FILES.get('image', False)) == True:
                    image =  request.FILES['image']
                    lookup = image.name.rfind(".")
                    image.name = str(no) + image.name[lookup:]
                    up_image = fs.save(image.name, image)
                    image_url = settings.MEDIA_URL + up_image
            except Exception as e:
                print(e)
                image_url = ""
            if nickname == "":
                nickname = "-"
            updatepatient_response = requests.post(patient_update_api, data={'hospital_no': no, 'lastname': lastname, 'firstname': firstname, 'middlename': middlename, 'suffix': suffix, 'sex': sex, 'birthdate': birthdate, 'birthplace': birthplace, 'street': street, 'province': province, 'municipality': municipality, 'barangay': barangay, 'nickname': nickname, 'civilstatus': civilstatus, 'employment': employment, 'nationality': nationality, 'religion': religion, 'contactno': contactno, 'occupation': occupation, 'encoder': encoder, 'picture': image_url})
            updatepatient_json_response = updatepatient_response.json()
            if updatepatient_json_response['status'] == 'success':
                msg = "success"
            else:
                msg = "failed"
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
            # GET NEW DATA
            
            return render(request, 'integrated/opd/patient_details.html', {'user_level': request.session['user_level'], 'name': request.session['name'], 'religion': religion, 'province': province, 'municipality': municipality, 'barangay': barangay, 'details': details, 'no': no, 'msg': msg})
        else:
            ##########################################################
            # GET DATA
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
            return render(request, 'integrated/opd/patient_details.html', {'user_level': request.session['user_level'], 'name': request.session['name'], 'religion': religion, 'province': province, 'municipality': municipality, 'barangay': barangay, 'details': details, 'no': no, 'msg': msg})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def patientDetails(request, no, page):
    if request.session.get('employee_id') is not None:
        religion = []
        provice = []
        municipality = []
        barangay = []
        msg = ""
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
                msg = "success"
            else:
                msg = "failed"
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
            return render(request, 'integrated/patient_details.html', {'page': page, 'user_level': request.session['user_level'], 'name': request.session['name'], 'religion': religion, 'province': province, 'municipality': municipality, 'barangay': barangay, 'details': details, 'no': no, 'msg': msg})
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
            return render(request, 'integrated/patient_details.html', {'page': page, 'user_level': request.session['user_level'], 'name': request.session['name'], 'religion': religion, 'province': province, 'municipality': municipality, 'barangay': barangay, 'details': details, 'no': no, 'msg': msg})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def consultations(request, no):
    if request.session.get('employee_id') is not None:
        consultation = []
        list_response = requests.post(consultation_list_api, data={'hospital_no': no})
        list_json_response = list_response.json()
        if list_json_response['status'] == 'success':
            for i in list_json_response['data']:
                i['date'] =  datetime.strptime(i['date'][:10], '%Y-%m-%d')
                i['enccode'] = i['enccode'].replace('/', '-')
            consultation = list_json_response['data']
        return render(request, 'integrated/consultations/consultations.html', {'page': 'Consultations', 'user_level': request.session['user_level'], 'name': request.session['name'], 'consultation': consultation})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def consultation_details(request, enctr, typ):
    if request.session.get('employee_id') is not None:
        encounter_no = enctr
        encounter = ""
        today = datetime.today()
        no = ""
        #This is for OPD Consultation Records
        if typ == 'OPD' or typ == 'OPDAD':
            response = requests.post(opd_record_api, data={'encounter_no': enctr})
            json_response = response.json()
            if json_response['status'] == 'success':
                if not json_response['data']:
                    enctr = enctr.replace('-', '/')
                    response = requests.post(opd_record_api, data={'encounter_no': enctr})
                    json_response = response.json()
                    if json_response['status'] == 'success':
                        encounter = enctr
                        for i in json_response['data']:
                            i['opddate'] = datetime.strptime(i['opddate'][:10], "%Y-%m-%d")
                            i['birthdate'] = datetime.strptime(i['birthdate'][:10], "%Y-%m-%d")
                            no = i['hpercode']
                        record = json_response['data']
                else:
                    encounter = enctr
                    for i in json_response['data']:
                        i['opddate'] = datetime.strptime(i['opddate'][:10], "%Y-%m-%d")
                        i['birthdate'] = datetime.strptime(i['birthdate'][:10], "%Y-%m-%d")
                        no = i['hpercode']
                    record = json_response['data']
            vital_response = requests.post(vital_sign_api, data={'encounter_no': encounter})
            vital_json_response = vital_response.json()
            if vital_json_response['status'] == 'success':
                vitals = vital_json_response['data']
            else:
                vitals = []
            hw_response = requests.post(height_weight_api, data={'encounter_no': enctr})
            hw_json_response = hw_response.json()
            if hw_json_response['status'] == 'success':
                hw = hw_json_response['data']
            else:
                hw = []
            addr_response = requests.post(patient_address_api, data={'no': no})
            addr_json_response = addr_response.json()
            if addr_json_response['status'] == 'success':
                addr = addr_json_response['data']
            else:
                addr = []
            illness_response = requests.post(present_illlness_api, data={'encounter_no': enctr})
            illness_json_response = illness_response.json()
            if illness_json_response['status'] == 'success':
                illness = illness_json_response['data']
            else:
                illness = []
            complaint_response = requests.post(complaint_api, data={'encounter_no': enctr})
            complaint_json_response = complaint_response.json()
            if complaint_json_response['status'] == 'success':
                complaint = complaint_json_response['data']
            else:
                complaint = []
            diagnosis_response = requests.post(diagnosis_api, data={'encounter_no': enctr})
            diagnosis_json_response = diagnosis_response.json()
            if diagnosis_json_response['status'] == 'success':
                diagnosis = diagnosis_json_response['data']
            else:
                diagnosis = []
            return render(request, 'integrated/consultations/opd_consultation_details.html', {'page': 'Consultations', 'user_level': request.session['user_level'], 'name': request.session['name'], 'record': record, 'today': today, 'vitals': vitals, 'hw': hw, 'addr': addr, 'illness': illness, 'complaint': complaint, 'diagnosis': diagnosis, 'enctr': encounter_no})
        #This is for OPD Consultation Records
        elif typ == 'ER' or typ == 'ERADM':
            patient_details = requests.post(patient_details_by_enc_api, data={'enccode': enctr}).json()["data"]
            return HttpResponseRedirect('/' + patient_details[0]['hpercode'] + '/' + encounter_no + '/erlogdetails')
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def print_opd_record(request, enctr):
    encounter = ""
    today = datetime.today()
    no = ""
    height = ""
    weight = ""
    # Data Population
    response = requests.post(opd_record_api, data={'encounter_no': enctr})
    json_response = response.json()
    if json_response['status'] == 'success':
        if not json_response['data']:
            enctr = enctr.replace('-', '/')
            response = requests.post(opd_record_api, data={'encounter_no': enctr})
            json_response = response.json()
            if json_response['status'] == 'success':
                encounter = enctr
                for i in json_response['data']:
                    i['opddate'] = datetime.strptime(i['opddate'][:10], "%Y-%m-%d")
                    no = i['hpercode']
                record = json_response['data']
        else:
            encounter = enctr
            for i in json_response['data']:
                i['opddate'] = datetime.strptime(i['opddate'][:10], "%Y-%m-%d")
                i['birthdate'] = datetime.strptime(i['birthdate'][:10], "%Y-%m-%d")
                no = i['hpercode']
            record = json_response['data']
        vital_response = requests.post(vital_sign_api, data={'encounter_no': encounter})
        vital_json_response = vital_response.json()
        if vital_json_response['status'] == 'success':
            vitals = vital_json_response['data']
        else:
            vitals = []

        hw_response = requests.post(height_weight_api, data={'encounter_no': enctr})
        hw_json_response = hw_response.json()
        if hw_json_response['status'] == 'success':
            hw = hw_json_response['data']
            for i in hw:
                if i['othrvs'] == 'HEIGH':
                    height = str(i['othrmeas']) + " cm"
                elif i['othrvs'] == 'WEIGH':
                    weight = str(i['othrmeas']) + " kl"
                else:
                    height = ""
                    weight = "" 
        else:
            hw = []
            height = ""
            weight = "" 
        addr_response = requests.post(patient_address_api, data={'no': no})
        addr_json_response = addr_response.json()
        if addr_json_response['status'] == 'success':
            addr = addr_json_response['data']
        else:
            addr = []
        illness_response = requests.post(present_illlness_api, data={'encounter_no': enctr})
        illness_json_response = illness_response.json()
        if illness_json_response['status'] == 'success':
            illness = illness_json_response['data']
        else:
            illness = ""
        complaint_response = requests.post(complaint_api, data={'encounter_no': enctr})
        complaint_json_response = complaint_response.json()
        if complaint_json_response['status'] == 'success':
            complaint = complaint_json_response['data']
        else:
            complaint = []
        diagnosis_response = requests.post(diagnosis_api, data={'encounter_no': enctr})
        diagnosis_json_response = diagnosis_response.json()
        if diagnosis_json_response['status'] == 'success':
            diagnosis = diagnosis_json_response['data']
        else:
            diagnosis = []
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    form = p.acroForm
    logo = ImageReader(static_root + '/integrated/img/brghgmclogo.png')
    response = HttpResponse(content_type='application/pdf')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setPageSize((8.5*inch, 13*inch))
    p.drawImage(logo, 0.5*inch, 12*inch, mask='auto', width=72, height=72)
    p.setFont("Times-Roman", 12, leading=None)
    p.setFillColor("green")
    p.drawString(2.2*inch, 12.8*inch, "Bicol Region General Hospital and Geriatric Medical Center")
    p.drawString(3*inch, 12.6*inch, "(Formely BICOL SANITARIUM)")
    p.setFont("Times-Roman", 11, leading=None)
    p.setFillColor("black")
    p.drawString(3.1*inch, 12.45*inch, "San Pedro, Cabusao Camarines Sur")
    p.drawString(2.3*inch, 12.3*inch, "Telephone Nos.: (054) 473-2244, 472-4422, 881-1033, 881-1761")
    p.drawString(2.4*inch, 12.16*inch, "E-mail Address: bicolsan@gmail.com, brghgmc@gmail.com")
    p.line(0, 12*inch, 1000, 12*inch) #(x1, y1, x2, y2)

    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(0.3*inch, 11.8*inch, "DATE AND TIME OF VISIT")
    p.drawString(0.3*inch, 11.65*inch, "DATE: " + record[0]['opd_datetime'])
    p.drawString(0.3*inch, 11.50*inch, "TIME: " + record[0]['opd_datetime'])
    p.drawString(0.3*inch, 11.30*inch, "HOSPITAL NUMBER: " + record[0]['hpercode'])
    p.line(0, 0.3*inch, 1000, 0.3*inch) #(x1, y1, x2, y2)

    p.setFont("Times-Roman", 12, leading=None)
    p.drawString(6*inch, 11*inch, record[0]['tsdesc'])
    p.drawString(3.5*inch, 10.5*inch, "OPD RECORD")
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(0.3*inch, 10*inch, "PATIENT'S NAME:")
    
    p.setFont("Times-Roman", 9, leading=None)
    p.drawString(1.5*inch, 9.9*inch, "Last Name")
    p.drawString(1.6*inch, 10.05*inch, record[0]['patlast'])
    p.drawString(4*inch, 9.9*inch, "First Name")
    p.drawString(4*inch, 10.05*inch, record[0]['patfirst'])
    p.drawString(6.3*inch, 9.9*inch, "Middle Name")
    p.drawString(6.3*inch, 10.05*inch, record[0]['patmiddle'])
    p.line(1.5*inch, 10*inch, 8*inch, 10*inch) #(x1, y1, x2, y2)

    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(0.3*inch, 9.6*inch, "ADDRESS:  " + addr[0]['address'])
    p.line(1*inch, 9.6*inch, 8*inch, 9.6*inch) #(x1, y1, x2, y2)

    if record[0]['pattelno']:
        p.drawString(0.3*inch, 9.4*inch, "TELEPHONE NO: " + str(record[0]['pattelno']))
    else:
        p.drawString(0.3*inch, 9.4*inch, "TELEPHONE NO: ")
    p.line(1.4*inch, 9.35*inch, 2.5*inch, 9.35*inch) #(x1, y1, x2, y2)

    bdate = datetime.strptime(record[0]['birthdate'][:10], "%Y-%m-%d")
    p.drawString(2.6*inch, 9.4*inch, "BIRTHDATE:    " + datetime.strftime(bdate, "%m/%d/%Y"))
    p.line(3.5*inch, 9.35*inch, 4.4*inch, 9.35*inch) #(x1, y1, x2, y2)

    p.drawString(4.5*inch, 9.4*inch, "AGE:    " + str(record[0]['Age']))
    p.line(4.9*inch, 9.35*inch, 5.3*inch, 9.35*inch) #(x1, y1, x2, y2)

    if record[0]['status'] == 'C':
        p.drawString(5.4*inch, 9.4*inch, "STATUS:  CHILD")
    elif record[0]['status'] == 'D':
        p.drawString(5.4*inch, 9.4*inch, "STATUS:  DIVORSED")
    elif record[0]['status'] == 'M':
        p.drawString(5.4*inch, 9.4*inch, "STATUS:  MARRIED")
    elif record[0]['status'] == 'X':
        p.drawString(5.4*inch, 9.4*inch, "STATUS:  SEPARATED")
    elif record[0]['status'] == 'S':
        p.drawString(5.4*inch, 9.4*inch, "STATUS:  SINGLE")
    elif record[0]['status'] == 'W':
        p.setFont("Times-Roman", 7, leading=None)
        p.drawString(5.4*inch, 9.4*inch, "STATUS:  WIDOW/WIDOWER")
    p.line(6*inch, 9.35*inch, 7*inch, 9.35*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 9, leading=None)

    if record[0]['Sex'] == "M":
        p.drawString(7.1*inch, 9.4*inch, "SEX:   MALE")
    else:
        p.drawString(7.1*inch, 9.4*inch, "SEX:   FEMALE")
    p.line(7.4*inch, 9.35*inch, 8*inch, 9.35*inch) #(x1, y1, x2, y2)

    if record[0]['occupation']:
        p.drawString(0.3*inch, 9.2*inch, "OCCUPATION: " + record[0]['occupation'])
    else:
        p.drawString(0.3*inch, 9.2*inch, "OCCUPATION: ")
    p.line(1.3*inch, 9.15*inch, 4*inch, 9.15*inch) #(x1, y1, x2, y2)

    p.drawString(4.1*inch, 9.2*inch, "COMPANY:")
    p.line(4.9*inch, 9.15*inch, 8*inch, 9.15*inch) #(x1, y1, x2, y2)

    p.drawString(0.3*inch, 9*inch, "REFERRAL:")
    p.line(1.1*inch, 8.95*inch, 8*inch, 8.95*inch) #(x1, y1, x2, y2)

    p.drawString(0.3*inch, 8.7*inch, "CONSULTING DOCTOR/SIGNATURE:")
    p.rect(0.3*inch, 8.15*inch, 7.7*inch, 0.5*inch, fill=0)#Doctor Signature Box

    p.drawString(3.4*inch, 8*inch, "PATIENT CASE SUMMARY")

    p.drawString(0.3*inch, 7.8*inch, "VITAL SIGNS:")
    p.drawString(0.5*inch, 7.6*inch, "HEIGHT:              " + height)
    p.line(1.1*inch, 7.55*inch, 2.5*inch, 7.55*inch) #(x1, y1, x2, y2)
    p.drawString(3*inch, 7.6*inch, "WEIGHT:             " + weight)
    p.line(3.7*inch, 7.55*inch, 4.9*inch, 7.55*inch) #(x1, y1, x2, y2)

    try:
        vstemp = str(vitals[0]['vstemp'])
        vspulse = str(vitals[0]['vspulse'])
        vsbp = str(vitals[0]['vsbp'])
        vsresp = str(vitals[0]['vsresp'])
    except IndexError:
        vstemp = ""
        vspulse = ""
        vsbp = ""
        vsresp = ""

    p.drawString(5.5*inch, 7.6*inch, "TEMPERATURE:                 " + vstemp)
    p.line(6.6*inch, 7.55*inch, 8*inch, 7.55*inch) #(x1, y1, x2, y2)

    p.drawString(0.5*inch, 7.2*inch, "PULSE:                     " +  vspulse)
    p.line(1.1*inch, 7.15*inch, 2.5*inch, 7.15*inch) #(x1, y1, x2, y2)

    p.drawString(3*inch, 7.2*inch, "BP:                       " + vsbp)
    p.line(3.7*inch, 7.15*inch, 4.9*inch, 7.15*inch) #(x1, y1, x2, y2)

    p.drawString(5.5*inch, 7.2*inch, "RR:                                          " + vsresp )
    p.line(6.6*inch, 7.15*inch, 8*inch, 7.15*inch) #(x1, y1, x2, y2)

    p.drawString(0.3*inch, 6.9*inch, "PRESENT ILLNESS:")
    y = 6.7
    for i in illness:
        p.drawString(0.3*inch, y*inch, i['history'])
        y = y - 0.1
    p.drawString(0.3*inch, 6*inch, "CHIEF COMPLAINT:")
    y = 5.8
    for i in complaint:
        p.drawString(0.3*inch, y*inch, i['history'])
        y = y - 0.1

    p.drawString(0.3*inch, 4*inch, "DIAGNOSIS:")
    y = 3.8
    for i in diagnosis:
        p.drawString(0.3*inch, y*inch, i['diagtext'])
        y = y - 0.1
    p.drawString(0.3*inch, 1.5*inch, "DATE AND TIME DISCHARGED IN OPD")
    p.drawString(3.5*inch, 1.5*inch, "DISPOSITION")

    try:
        p.drawString(0.3*inch, 1.3*inch, "DATE: "  + record[0]['discharged_date'])
        p.drawString(0.3*inch, .75*inch, "TIME: "  + record[0]['discharged_date'])
    except:
        p.drawString(0.3*inch, 1.3*inch, "DATE: ")
        p.drawString(0.3*inch, .75*inch, "TIME: ")
    p.setFont("Times-Roman", 9, leading=None)
    p.drawString(3.5*inch, 1.3*inch, "Treated and Sent Home")
    p.drawString(3.5*inch, .75*inch, "For Admission")

    p.drawString(5.5*inch, 1.3*inch, "Refused Admission")
    p.drawString(5.5*inch, .75*inch, "Referred")

    p.drawString(7*inch, 1.3*inch, "Out When Called")

    if record[0]['opddisp'] == 'ADMIT':
        p.rect(3.2*inch, 1.25*inch, 0.2*inch, 0.2*inch, fill=0)#Treated and Sent Home
        p.rect(5.2*inch, 1.25*inch, 0.2*inch, 0.2*inch, fill=0)#Refused Admission
        p.rect(6.7*inch, 1.25*inch, 0.2*inch, 0.2*inch, fill=0)#Out When Called
        p.rect(3.2*inch, 0.70*inch, 0.2*inch, 0.2*inch, fill=1)#For Admission
        p.rect(5.2*inch, 0.70*inch, 0.2*inch, 0.2*inch, fill=0)#Referred
    elif record[0]['opddisp'] == 'OWC':
        p.rect(3.2*inch, 1.25*inch, 0.2*inch, 0.2*inch, fill=0)#Treated and Sent Home
        p.rect(5.2*inch, 1.25*inch, 0.2*inch, 0.2*inch, fill=0)#Refused Admission
        p.rect(6.7*inch, 1.25*inch, 0.2*inch, 0.2*inch, fill=1)#Out When Called
        p.rect(3.2*inch, 0.70*inch, 0.2*inch, 0.2*inch, fill=0)#For Admission
        p.rect(5.2*inch, 0.70*inch, 0.2*inch, 0.2*inch, fill=0)#Referred
    elif record[0]['opddisp'] == 'REFAD':
        p.rect(3.2*inch, 1.25*inch, 0.2*inch, 0.2*inch, fill=0)#Treated and Sent Home
        p.rect(5.2*inch, 1.25*inch, 0.2*inch, 0.2*inch, fill=1)#Refused Admission
        p.rect(6.7*inch, 1.25*inch, 0.2*inch, 0.2*inch, fill=0)#Out When Called
        p.rect(3.2*inch, 0.70*inch, 0.2*inch, 0.2*inch, fill=0)#For Admission
        p.rect(5.2*inch, 0.70*inch, 0.2*inch, 0.2*inch, fill=0)#Referred
    elif record[0]['opddisp'] == 'REFER':
        p.rect(3.2*inch, 1.25*inch, 0.2*inch, 0.2*inch, fill=0)#Treated and Sent Home
        p.rect(5.2*inch, 1.25*inch, 0.2*inch, 0.2*inch, fill=0)#Refused Admission
        p.rect(6.7*inch, 1.25*inch, 0.2*inch, 0.2*inch, fill=0)#Out When Called
        p.rect(3.2*inch, 0.70*inch, 0.2*inch, 0.2*inch, fill=0)#For Admission
        p.rect(5.2*inch, 0.70*inch, 0.2*inch, 0.2*inch, fill=1)#Referred
    elif record[0]['opddisp'] == 'TRASH':
        p.rect(3.2*inch, 1.25*inch, 0.2*inch, 0.2*inch, fill=1)#Treated and Sent Home
        p.rect(5.2*inch, 1.25*inch, 0.2*inch, 0.2*inch, fill=0)#Refused Admission
        p.rect(6.7*inch, 1.25*inch, 0.2*inch, 0.2*inch, fill=0)#Out When Called
        p.rect(3.2*inch, 0.70*inch, 0.2*inch, 0.2*inch, fill=0)#For Admission
        p.rect(5.2*inch, 0.70*inch, 0.2*inch, 0.2*inch, fill=0)#Referred
    else:
        p.rect(3.2*inch, 1.25*inch, 0.2*inch, 0.2*inch, fill=0)#Treated and Sent Home
        p.rect(5.2*inch, 1.25*inch, 0.2*inch, 0.2*inch, fill=0)#Refused Admission
        p.rect(6.7*inch, 1.25*inch, 0.2*inch, 0.2*inch, fill=0)#Out When Called
        p.rect(3.2*inch, 0.70*inch, 0.2*inch, 0.2*inch, fill=0)#For Admission
        p.rect(5.2*inch, 0.70*inch, 0.2*inch, 0.2*inch, fill=0)#Referred

    p.setFont("Times-Italic", 10, leading=None)
    p.drawString(0.3*inch, 0.15*inch, "BRGHGMC-F-MS-HIM-036")
    p.drawString(4*inch, 0.15*inch, "Rev 1")
    p.drawString(6.5*inch, 0.15*inch, "Effectivity Date: January 6, 2020")
    p.setTitle("OPD RECORD")
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def print_medical_cert(request, enctr, cert_no):
    encounter = ""
    today = datetime.today()
    no = ""
    height = ""
    weight = ""
    PAGE_WIDTH  = defaultPageSize[0]
    PAGE_HEIGHT = defaultPageSize[1]
    # Data Population
    response = requests.post(opd_record_api, data={'encounter_no': enctr})
    json_response = response.json()
    if json_response['status'] == 'success':
        if not json_response['data']:
            enctr = enctr.replace('-', '/')
            response = requests.post(opd_record_api, data={'encounter_no': enctr})
            json_response = response.json()
            if json_response['status'] == 'success':
                encounter = enctr
                for i in json_response['data']:
                    i['opddate'] = datetime.strptime(i['opddate'][:10], "%Y-%m-%d")
                    no = i['hpercode']
                record = json_response['data']
        else:
            encounter = enctr
            for i in json_response['data']:
                i['opddate'] = datetime.strptime(i['opddate'][:10], "%Y-%m-%d")
                i['birthdate'] = datetime.strptime(i['birthdate'][:10], "%Y-%m-%d")
                no = i['hpercode']
            record = json_response['data']
        vital_response = requests.post(vital_sign_api, data={'encounter_no': encounter})
        vital_json_response = vital_response.json()
        if vital_json_response['status'] == 'success':
            vitals = vital_json_response['data']
        else:
            vitals = []

        addr_response = requests.post(patient_address_api, data={'no': no})
        addr_json_response = addr_response.json()
        if addr_json_response['status'] == 'success':
            addr = addr_json_response['data']
        else:
            addr = []
        illness_response = requests.post(present_illlness_api, data={'encounter_no': enctr})
        illness_json_response = illness_response.json()
        if illness_json_response['status'] == 'success':
            illness = illness_json_response['data']
        else:
            illness
        complaint_response = requests.post(complaint_api, data={'encounter_no': enctr})
        complaint_json_response = complaint_response.json()
        if complaint_json_response['status'] == 'success':
            complaint = complaint_json_response['data']
        else:
            complaint = []
        diagnosis_response = requests.post(diagnosis_api, data={'encounter_no': enctr})
        diagnosis_json_response = diagnosis_response.json()
        if diagnosis_json_response['status'] == 'success':
            diagnosis = diagnosis_json_response['data']
        else:
            diagnosis = []
    c_len = len(record[0]['opd_datetime'])
    c_time_len = len(record[0]['opd_datetime']) -7
    d_len = len(record[0]['discharged_date'])
    d_time_len = len(record[0]['discharged_date']) - 7
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    form = p.acroForm
    logo = ImageReader(static_root + '/integrated/img/brghgmclogo.png')
    response = HttpResponse(content_type='application/pdf')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setPageSize("A4")
    p.drawImage(logo, 0.5*inch, 10*inch, mask='auto', width=72, height=72)
    p.setFont("Times-Roman", 12, leading=None)
    p.setFillColor("green")
    p.drawString(2.2*inch, 10.8*inch, "Bicol Region General Hospital and Geriatric Medical Center")
    p.drawString(3*inch, 10.6*inch, "(Formely BICOL SANITARIUM)")
    p.setFont("Times-Roman", 11, leading=None)
    p.setFillColor("black")
    p.drawString(3.1*inch, 10.45*inch, "San Pedro, Cabusao Camarines Sur")
    p.drawString(2.3*inch, 10.3*inch, "Telephone Nos.: (054) 473-2244, 472-4422, 881-1033, 881-1761")
    p.drawString(2.4*inch, 10.16*inch, "E-mail Address: bicolsan@gmail.com, brghgmc@gmail.com")
    p.line(0, 10*inch, 1000, 10*inch) #(x1, y1, x2, y2)

    p.drawString(6*inch, 9.5*inch, "Cert. No.  " + cert_no)
    p.drawString(6*inch, 9.3*inch, "Date:  " + datetime.strftime(datetime.now(), "%B %d, %Y"))

    p.setFont("Times-Bold", 12, leading=None)
    p.drawString(3*inch, 8.6*inch, "MEDICAL CERTIFICATE")
    p.setFont("Times-Bold", 11, leading=None)
    p.drawString(0.5*inch, 8*inch, "TO WHOM IT MAY CONCERN:")

    p.setFont("Times-Roman", 11, leading=None)
    p.drawString(1*inch, 7.5*inch, "This is to certify that ____________________________________________________________________")
    if record[0]['patsuffix']:
        p.drawString(2.4*inch, 7.5*inch, record[0]['patlast'] + ", " + record[0]['patfirst'] +  " " + record[0]['patsuffix'] + " " + record[0]['patmiddle'])
    else:
        p.drawString(2.4*inch, 7.5*inch, record[0]['patlast'] + ", " + record[0]['patfirst'] + " " + record[0]['patmiddle'])
    p.drawString(6.9*inch, 7.5*inch, str(record[0]['Age']))
    p.setFont("Times-Italic", 11, leading=None)
    p.drawString(3.5*inch, 7.3*inch, "(Name of Patient)")
    p.drawString(6.8*inch, 7.3*inch, "(Age)")

    p.setFont("Times-Roman", 11, leading=None)
    p.drawString(0.5*inch, 7*inch, "of ___________________________________________________________________________________________")
    p.drawString(0.8*inch, 7*inch, addr[0]['address'])
    p.setFont("Times-Italic", 11, leading=None)
    p.drawString(4*inch, 6.8*inch, "(Address)")

    p.setFont("Times-Roman", 11, leading=None)
    p.drawString(0.5*inch, 6.5*inch, "was examined/treated in this hospital on ____________________ with the following findings and/or diagnosis:")
    p.drawString(3.5*inch, 6.5*inch, record[0]['opd_datetime'][:c_time_len])

    p.setFont("Times-Bold", 12, leading=None)
    p.drawString(4*inch, 5.8*inch, "X")
    y = 5.5
    for i in diagnosis:
        text_width = stringWidth(i['diagtext'], "Times-Bold", 12)
        p.drawString(3.2*inch, y*inch, i['diagtext'])
        begin = (PAGE_WIDTH*inch - text_width*inch) / 2.0*inch
        p.drawString(begin, y*inch, i['diagtext'])
        y = y - 0.2
    y = y - 0.2
    p.drawString(4*inch, y*inch, "X")
    p.setFont("Times-Roman", 11, leading=None)
    p.drawString(0.5*inch, 4*inch, "and would need medical attention _________________ days barring complications")    

    p.setFont("Times-Bold", 11, leading=None)
    p.drawString(0.5*inch, 3.5*inch, "Note:")
    p.setFont("Times-Roman", 11, leading=None)

    if record[0]['Sex'] == "M":
        p.drawString(1*inch, 3.5*inch, "This certification is being issued upon request of patient himself for whatever purpose he may deem proper")
    else:
        p.drawString(1*inch, 3.5*inch, "This certification is being issued upon request of patient herself for whatever purpose she may deem proper")
    p.setFont("Times-Bold", 11, leading=None)
    p.drawString(0.5*inch, 3.3*inch, "except for Medico Legal Purpose.")
    p.setFont("Times-Roman", 11, leading=None)
    p.setFont("Times-Bold", 11, leading=None)
    p.drawString(4.6*inch, 2*inch, diagnosis[0]['physician'])
    p.setFont("Times-Roman", 11, leading=None)
    p.drawString(4.6*inch, 1.8*inch, diagnosis[0]['postitle'])
    p.drawString(4.6*inch, 1.6*inch, "License No. " + diagnosis[0]['licno'])

    p.setFont("Times-Italic", 11, leading=None)
    p.drawString(0.5*inch, 1*inch, "(NOT VALID WITHOUT SEAL)")
    
    p.line(0, 0.30*inch, 1000, 0.30*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Italic", 10, leading=None)
    p.drawString(0.3*inch, 0.15*inch, "BRGHGMC-F-MS-HIM-021")
    p.drawString(4*inch, 0.15*inch, "Rev 2")
    p.drawString(6.5*inch, 0.15*inch, "Effectivity Date: January 6, 2020")
    p.setTitle("MEDICAL CERTIFICATE")
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def getMunicipality(request):
    province = request.GET.get("province")
    #GET MUNICIPALITY
    municipality_response = requests.get(municipality_list_api + province)
    municipality_response_json = municipality_response.json()
    if municipality_response_json['status'] == 'success':
        municipality = municipality_response_json['data']
        return JsonResponse(municipality, safe=False)
    else:
        return JsonResponse()

def getBarangay(request):
    municipality = request.GET.get("municipality")
    #GET BARANGAY
    barangay_response = requests.get(barangay_list_api + municipality)
    barangay_response_json = barangay_response.json()
    if barangay_response_json['status'] == 'success':
        barangay = barangay_response_json['data']
        return JsonResponse(barangay, safe=False)
    else:
        return JsonResponse()

def laboratory_opd(request):
    if request.session.get('employee_id') is not None:
        patient_list = requests.get(all_patients_api).json()['data']
        for i in patient_list:
            i['enccode'] = i['enccode'].replace('/', '-')
            i['encdate'] = datetime.strptime(i['encdate'], '%m/%d/%Y')
            i['since'] = (datetime.now() - i['encdate']).days
        return render(request, 'integrated/laboratory/opd.html', {'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': patient_list})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def laboratory_er(request):
    if request.session.get('employee_id') is not None:
        patient_list = requests.get(all_patients_api).json()['data']
        for i in patient_list:
            i['enccode'] = i['enccode'].replace('/', '-')
            i['encdate'] = datetime.strptime(i['encdate'], '%m/%d/%Y')
            i['since'] = (datetime.now() - i['encdate']).days
        return render(request, 'integrated/laboratory/er.html', {'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': patient_list})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def printLabCharges(request, enctr):
    charges = requests.post(lab_charges_api, data={'enccode': enctr}).json()['data']
    total = requests.post(lab_total_charge_api, data={'enccode': enctr}).json()['data'][0]['amt']
    patient_details = requests.post(patient_details_by_enc_api, data={'enccode': enctr}).json()["data"]
    patient_address = requests.post(patient_address_api, data={'no': patient_details[0]['hpercode']}).json()["data"]
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    logo = ImageReader(static_root + '/integrated/img/brghgmclogo.png')
    response = HttpResponse(content_type='application/pdf')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setPageSize((4.25*inch, 6.5*inch))
    p.drawImage(logo, 0.2*inch, 6*inch, mask='auto', width=32, height=32)
    p.setFont("Times-Roman", 8, leading=None)
    p.setFillColor("green")
    p.drawString(0.9*inch, 6.3*inch, "Bicol Region General Hospital and Geriatric Medical Center")
    p.drawString(1.4*inch, 6.2*inch, "(Formely BICOL SANITARIUM)")
    p.setFillColor("black")
    p.drawString(1.35*inch, 6.1*inch, "San Pedro, Cabusao Camarines Sur")
    p.drawString(0.8*inch, 6*inch, "Telephone Nos.: (054) 473-2244, 472-4422, 881-1033, 881-1761")
    p.drawString(0.9*inch, 5.9*inch, "E-mail Address: bicolsan@gmail.com, brghgmc@gmail.com")
    p.line(0, 5.8*inch, 1000, 5.8*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(1.6*inch, 5.6*inch, "CHARGE SLIP")
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(2.6*inch, 5.4*inch, "Date:____________________ ")
    p.drawString(3.1*inch, 5.4*inch, datetime.today().strftime('%m-%d-%Y'))
    p.drawString(0.2*inch, 5.2*inch, "Name:_______________________________________________________________ ")
    p.drawString(0.6*inch, 5.2*inch, patient_details[0]['patlast'] + ", " + patient_details[0]['patfirst'] + " " + patient_details[0]['patmiddle'][0])
    p.drawString(0.2*inch, 5*inch, "Address:_____________________________________________________________ ")
    p.drawString(0.7*inch, 5*inch, patient_address[0]['address'])
    p.drawString(0.2*inch, 4.8*inch, "Responsibility Center:__________________________________________________ ")
    p.drawString(1.5*inch, 4.8*inch, "LABORATORY")
    p.drawString(0.2*inch, 4.6*inch, "Hospital No.:__________________________________________________________ ")
    p.drawString(1*inch, 4.6*inch, patient_details[0]['hpercode'])

    #CONTENT
    styles = getSampleStyleSheet()
    styles2 = getSampleStyleSheet()
    styles3 = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleN.alignment = TA_CENTER
    styleN.fontSize = 8 
    styleN.fontName = "Times-Bold"

    style_td = styles2["BodyText"]
    style_td.alignment = TA_LEFT
    style_td.fontSize = 8 
    style_td.fontName = "Times-Roman"

    h_qty = Paragraph('Qty', styleN)
    h_particulars = Paragraph('Particular', styleN)
    h_up = Paragraph('Unit Price', styleN)
    h_total = Paragraph('Total', styleN)

    style_amt = styles3["BodyText"]
    style_amt.alignment = TA_RIGHT
    style_amt.fontSize = 8 
    style_amt.fontName = "Times-Roman"

    table_data = [[h_qty, h_particulars, h_up, h_total]]
    if charges != "[]":
        ac = 0
        for i in charges:
            ac += 1
            table_data.append([Paragraph(str("{:,}".format(i['pchrgqty'])), style_amt), Paragraph(i['procdesc'], style_td), Paragraph(str("{:,}".format(i['pchrgup'])), style_amt), Paragraph(str("{:,}".format(i['pcchrgamt'])), style_amt)]) 
        if total is not None:
            table_data.append(['', Paragraph('TOTAL', style_td), '', Paragraph(str("{:,}".format(total)), style_amt)])    

        t = Table(table_data, colWidths=[0.4*inch, 2.2*inch, 0.7*inch, 0.7*inch])
        t.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONT', (0, 0), (-1, -1), 'Times-Roman', 8)
        ]))
        t.wrapOn(p, 0, 0)
        if ac == 1:
            t.drawOn(p, 0.1*inch, 3.7*inch)
        elif ac == 2:
            t.drawOn(p, 0.1*inch, 3.5*inch)
        elif ac == 3:
            t.drawOn(p, 0.1*inch, 3.2*inch)
        elif ac == 4:
            t.drawOn(p, 0.1*inch, 3*inch)
        elif ac == 5:
            t.drawOn(p, 0.1*inch, 2.8*inch)
        elif ac == 6:
            t.drawOn(p, 0.1*inch, 2.4*inch)
        elif ac == 7:
            t.drawOn(p, 0.1*inch, 2.2*inch)
        elif ac == 8:
            t.drawOn(p, 0.1*inch, 2*inch)
        elif ac == 9:
            t.drawOn(p, 0.1*inch, 1.8*inch)
        elif ac == 10:
            t.drawOn(p, 0.1*inch, 1.4*inch)
        elif ac == 11:
            t.drawOn(p, 0.1*inch, 1.2*inch)
        elif ac == 12:
            t.drawOn(p, 0.1*inch, 1*inch)
        else:
            t.drawOn(p, 0.1*inch, 0.8*inch)

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(0.2*inch, 0.7*inch, "Issued by:")
    p.drawString(0.2*inch, 0.4*inch, "_______________________________")
    p.drawString(0.3*inch, 0.45*inch, request.session.get("name"))
    p.drawString(0.4*inch, 0.25*inch, "Signature Over Printed Name")
    p.drawString(2.5*inch, 0.7*inch, "Payment:")
    p.drawString(2.5*inch, 0.5*inch, "OR No._______________________")
    p.drawString(2.5*inch, 0.3*inch, "Date.__________________________")

    p.line(0, 0.2*inch, 1000, 0.30*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Italic", 7, leading=None)
    p.drawString(0.1*inch, 0.1*inch, "BRGHGMC-F-AS-BIL-006")
    p.drawString(2*inch, 0.1*inch, "Rev 2")
    p.drawString(2.9*inch, 0.1*inch, "Effectivity Date: January 6, 2020")
    p.setTitle("RADIOLOGY CHARGESLIP")
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def printLatestLabCharges(request, enctr):
    charges = requests.post(lab_charges_api, data={'enccode': enctr}).json()['data']
    #total = requests.post(lab_total_charge_api, data={'enccode': enctr}).json()['data'][0]['amt']
    total = 0
    patient_details = requests.post(patient_details_by_enc_api, data={'enccode': enctr}).json()["data"]
    patient_address = requests.post(patient_address_api, data={'no': patient_details[0]['hpercode']}).json()["data"]
    printed = requests.post(get_printed_cl_api, data={'enccode': enctr}).json()["data"]
    docointkey = []
    for i in printed:
        docointkey.append(i['docointkey'])
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    logo = ImageReader(static_root + '/integrated/img/brghgmclogo.png')
    response = HttpResponse(content_type='application/pdf')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setPageSize((4.25*inch, 6.5*inch))
    p.drawImage(logo, 0.2*inch, 6*inch, mask='auto', width=32, height=32)
    p.setFont("Times-Roman", 8, leading=None)
    p.setFillColor("green")
    p.drawString(0.9*inch, 6.3*inch, "Bicol Region General Hospital and Geriatric Medical Center")
    p.drawString(1.4*inch, 6.2*inch, "(Formely BICOL SANITARIUM)")
    p.setFillColor("black")
    p.drawString(1.35*inch, 6.1*inch, "San Pedro, Cabusao Camarines Sur")
    p.drawString(0.8*inch, 6*inch, "Telephone Nos.: (054) 473-2244, 472-4422, 881-1033, 881-1761")
    p.drawString(0.9*inch, 5.9*inch, "E-mail Address: bicolsan@gmail.com, brghgmc@gmail.com")
    p.line(0, 5.8*inch, 1000, 5.8*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(1.6*inch, 5.6*inch, "CHARGE SLIP")
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(2.6*inch, 5.4*inch, "Date:____________________ ")
    p.drawString(3.1*inch, 5.4*inch, datetime.today().strftime('%m-%d-%Y'))
    p.drawString(0.2*inch, 5.2*inch, "Name:_______________________________________________________________ ")
    p.drawString(0.6*inch, 5.2*inch, patient_details[0]['patlast'] + ", " + patient_details[0]['patfirst'] + " " + patient_details[0]['patmiddle'][0])
    p.drawString(0.2*inch, 5*inch, "Address:_____________________________________________________________ ")
    p.drawString(0.7*inch, 5*inch, patient_address[0]['address'])
    p.drawString(0.2*inch, 4.8*inch, "Responsibility Center:__________________________________________________ ")
    p.drawString(1.5*inch, 4.8*inch, "LABORATORY")
    p.drawString(0.2*inch, 4.6*inch, "Hospital No.:__________________________________________________________ ")
    p.drawString(1*inch, 4.6*inch, patient_details[0]['hpercode'])

    #CONTENT
    styles = getSampleStyleSheet()
    styles2 = getSampleStyleSheet()
    styles3 = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleN.alignment = TA_CENTER
    styleN.fontSize = 8 
    styleN.fontName = "Times-Bold"

    style_td = styles2["BodyText"]
    style_td.alignment = TA_LEFT
    style_td.fontSize = 8 
    style_td.fontName = "Times-Roman"

    h_qty = Paragraph('Qty', styleN)
    h_particulars = Paragraph('Particular', styleN)
    h_up = Paragraph('Unit Price', styleN)
    h_total = Paragraph('Total', styleN)

    style_amt = styles3["BodyText"]
    style_amt.alignment = TA_RIGHT
    style_amt.fontSize = 8 
    style_amt.fontName = "Times-Roman"

    table_data = [[h_qty, h_particulars, h_up, h_total]]
    if charges != "[]":
        ac = 0
        for i in charges:
            if i['docointkey'] not in docointkey:
                ac += 1
                total += i['pcchrgamt']
                table_data.append([Paragraph(str("{:,}".format(i['pchrgqty'])), style_amt), Paragraph(i['procdesc'], style_td), Paragraph(str("{:,}".format(i['pchrgup'])), style_amt), Paragraph(str("{:,}".format(i['pcchrgamt'])), style_amt)]) 
        if total is not None:
            table_data.append(['', Paragraph('TOTAL', style_td), '', Paragraph(str("{:,}".format(total)), style_amt)])    

        t = Table(table_data, colWidths=[0.4*inch, 2.2*inch, 0.7*inch, 0.7*inch])
        t.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONT', (0, 0), (-1, -1), 'Times-Roman', 8)
        ]))
        t.wrapOn(p, 0, 0)
        if ac == 1:
            t.drawOn(p, 0.1*inch, 3.7*inch)
        elif ac == 2:
            t.drawOn(p, 0.1*inch, 3.5*inch)
        elif ac == 3:
            t.drawOn(p, 0.1*inch, 3.2*inch)
        elif ac == 4:
            t.drawOn(p, 0.1*inch, 3*inch)
        elif ac == 5:
            t.drawOn(p, 0.1*inch, 2.8*inch)
        elif ac == 6:
            t.drawOn(p, 0.1*inch, 2.4*inch)
        elif ac == 7:
            t.drawOn(p, 0.1*inch, 2.2*inch)
        elif ac == 8:
            t.drawOn(p, 0.1*inch, 2*inch)
        elif ac == 9:
            t.drawOn(p, 0.1*inch, 1.8*inch)
        elif ac == 10:
            t.drawOn(p, 0.1*inch, 1.4*inch)
        elif ac == 11:
            t.drawOn(p, 0.1*inch, 1.2*inch)
        elif ac == 12:
            t.drawOn(p, 0.1*inch, 1*inch)
        else:
            t.drawOn(p, 0.1*inch, 0.8*inch)

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(0.2*inch, 0.7*inch, "Issued by:")
    p.drawString(0.2*inch, 0.4*inch, "_______________________________")
    p.drawString(0.3*inch, 0.45*inch, request.session.get("name"))
    p.drawString(0.4*inch, 0.25*inch, "Signature Over Printed Name")
    p.drawString(2.5*inch, 0.7*inch, "Payment:")
    p.drawString(2.5*inch, 0.5*inch, "OR No._______________________")
    p.drawString(2.5*inch, 0.3*inch, "Date.__________________________")

    p.line(0, 0.2*inch, 1000, 0.30*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Italic", 7, leading=None)
    p.drawString(0.1*inch, 0.1*inch, "BRGHGMC-F-AS-BIL-006")
    p.drawString(2*inch, 0.1*inch, "Rev 2")
    p.drawString(2.9*inch, 0.1*inch, "Effectivity Date: January 6, 2020")
    p.setTitle("RADIOLOGY CHARGESLIP")
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    for i in charges:
        addPrintedChargeSlip = requests.post(add_printed_cl_api, data={'enccode': i['enccode'], 'docointkey': i['docointkey']})
    return response

def patient_laboratory_charges(request, enctr):
    if request.session.get('employee_id') is not None:
        xray = []
        ultra = []
        scan = []
        exam = requests.get(lab_exam_api).json()['data']
        charges = requests.post(lab_charges_api, data={'enccode': enctr}).json()['data']
        total = requests.post(lab_total_charge_api, data={'enccode': enctr}).json()['data'][0]['amt']
        patient_details = requests.post(patient_details_by_enc_api, data={'enccode': enctr}).json()["data"]
        if total is None:
            total = 0
        return render(request, 'integrated/laboratory/charges.html', {'page': 'Laboratory', 'user_level': request.session['user_level'], 'name': request.session['name'], 'exam': exam, 'charges': charges, 'enctr': enctr, 'total': total, 'patient_details': patient_details})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def addLabCharges(request):
    ex = request.GET.get("exam", None)
    enctr = request.GET.get("enctr", None)
    add = requests.post(lab_simple_charge_api, data={'enc': enctr, 'exam': ex, 'encoder': request.session['employee_id']}).json()["status"]
    total = requests.post(lab_total_charge_api, data={'enccode': enctr}).json()['data'][0]['amt']
    if total is None:
        total = 0
    return HttpResponse(json.dumps(total))

def load_laboratory_charges(request, enctr):
    charges = requests.post(lab_charges_api, data={'enccode': enctr}).json()["data"]
    return render(request, 'integrated/laboratory/reload_charges.html', {'charges': charges, 'enctr': enctr})

def delLabCharges(request):
    docint = request.GET.get("intkey", None)
    enctr = request.GET.get("enctr", None)
    delete = requests.post(lab_del_charge_api, data={'docintkey': docint}).json()["status"]
    total = requests.post(lab_total_charge_api, data={'enccode': enctr}).json()['data'][0]['amt']
    if total is None:
        total = 0
    return HttpResponse(json.dumps(total))

def radiology(request):
    if request.session.get('employee_id') is not None:
        patient_list = requests.get(all_patients_api).json()['data']
        for i in patient_list:
            i['enccode'] = i['enccode'].replace('/', '-')
        return render(request, 'integrated/radiology/index.html', {'page': 'Radiology', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': patient_list})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def radiology_opd(request):
    if request.session.get('employee_id') is not None:
        patient_list = requests.get(all_patients_api).json()['data']
        for i in patient_list:
            i['enccode'] = i['enccode'].replace('/', '-')
            i['encdate'] = datetime.strptime(i['encdate'], '%m/%d/%Y')
            i['since'] = (datetime.now() - i['encdate']).days
        return render(request, 'integrated/radiology/opd.html', {'page': 'Radiology', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': patient_list})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def radiology_er(request):
    if request.session.get('employee_id') is not None:
        patient_list = requests.get(all_patients_api).json()['data']
        for i in patient_list:
            i['enccode'] = i['enccode'].replace('/', '-')
            i['encdate'] = datetime.strptime(i['encdate'], '%m/%d/%Y')
            i['since'] = (datetime.now() - i['encdate']).days
        return render(request, 'integrated/radiology/er.html', {'page': 'Radiology', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': patient_list})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def patient_radiology_charges(request, enctr):
    if request.session.get('employee_id') is not None:
        xray = []
        ultra = []
        scan = []
        exam = requests.get(rad_exam_api).json()['data']
        charges = requests.post(rad_charges_api, data={'enccode': enctr}).json()['data']
        total = requests.post(rad_total_charge_api, data={'enccode': enctr}).json()['data'][0]['amt']
        patient_details = requests.post(patient_details_by_enc_api, data={'enccode': enctr}).json()["data"]
        if total is None:
            total = 0
        for i in exam:
            if i['proccode'].find("RADIO") != -1:
                xray.append(i)
            elif i['proccode'].find("ULTRA") != -1:
                ultra.append(i)
            elif i['proccode'].find("SCAN") != -1:
                scan.append(i)
        return render(request, 'integrated/radiology/charges.html', {'page': 'Radiology', 'user_level': request.session['user_level'], 'name': request.session['name'], 'xray': xray, 'ultra': ultra, 'scan': scan, 'charges': charges, 'enctr': enctr, 'total': total, 'patient_details': patient_details})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def load_radiology_charges(request, enctr):
    charges = requests.post(rad_charges_api, data={'enccode': enctr}).json()["data"]
    return render(request, 'integrated/radiology/reload_charges.html', {'charges': charges, 'enctr': enctr})

def addRadCharges(request):
    ex = request.GET.get("exam", None)
    enctr = request.GET.get("enctr", None)
    add = requests.post(rad_simple_charge_api, data={'enc': enctr, 'exam': ex, 'encoder': request.session['employee_id']}).json()["status"]
    total = requests.post(rad_total_charge_api, data={'enccode': enctr}).json()['data'][0]['amt']
    if total is None:
        total = 0
    return HttpResponse(json.dumps(total))

def delRadCharges(request):
    docint = request.GET.get("intkey", None)
    enctr = request.GET.get("enctr", None)
    delete = requests.post(rad_del_charge_api, data={'docintkey': docint}).json()["status"]
    total = requests.post(rad_total_charge_api, data={'enccode': enctr}).json()['data'][0]['amt']
    if total is None:
        total = 0
    return HttpResponse(json.dumps(total))

def printRadCharges(request, enctr):
    charges = requests.post(rad_charges_api, data={'enccode': enctr}).json()['data']
    #total = requests.post(rad_total_charge_api, data={'enccode': enctr}).json()['data'][0]['amt']
    patient_details = requests.post(patient_details_by_enc_api, data={'enccode': enctr}).json()["data"]
    patient_address = requests.post(patient_address_api, data={'no': patient_details[0]['hpercode']}).json()["data"]
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    logo = ImageReader(static_root + '/integrated/img/brghgmclogo.png')
    response = HttpResponse(content_type='application/pdf')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setPageSize((8.5*inch, 6.5*inch))
    p.drawImage(logo, 0.2*inch, 6*inch, mask='auto', width=32, height=32)
    p.setFont("Times-Roman", 8, leading=None)
    p.setFillColor("green")
    p.drawString(0.9*inch, 6.3*inch, "Bicol Region General Hospital and Geriatric Medical Center")
    p.drawString(1.4*inch, 6.2*inch, "(Formely BICOL SANITARIUM)")
    p.setFillColor("black")
    p.drawString(1.35*inch, 6.1*inch, "San Pedro, Cabusao Camarines Sur")
    p.drawString(0.8*inch, 6*inch, "Telephone Nos.: (054) 473-2244, 472-4422, 881-1033, 881-1761")
    p.drawString(0.9*inch, 5.9*inch, "E-mail Address: bicolsan@gmail.com, brghgmc@gmail.com")
    p.line(0, 5.8*inch, 1000, 5.8*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(1.6*inch, 5.6*inch, "CHARGE SLIP")
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(2.6*inch, 5.4*inch, "Date:____________________ ")
    p.drawString(3.1*inch, 5.4*inch, datetime.today().strftime('%m-%d-%Y'))
    p.drawString(0.2*inch, 5.2*inch, "Name:_______________________________________________________________ ")
    p.drawString(0.6*inch, 5.2*inch, patient_details[0]['patlast'] + ", " + patient_details[0]['patfirst'] + " " + patient_details[0]['patmiddle'][0])
    p.drawString(0.2*inch, 5*inch, "Address:_____________________________________________________________ ")
    p.drawString(0.7*inch, 5*inch, patient_address[0]['address'])
    p.drawString(0.2*inch, 4.8*inch, "Responsibility Center:__________________________________________________ ")
    p.drawString(1.5*inch, 4.8*inch, "RADIOLOGY")
    p.drawString(0.2*inch, 4.6*inch, "Hospital No.:__________________________________________________________ ")
    p.drawString(1*inch, 4.6*inch, patient_details[0]['hpercode'])

    #DUPLICATE
    p.line(4.25*inch, 0, 4.25*inch, 1000) #(x1, y1, x2, y2)
    p.drawImage(logo, 4.5*inch, 6*inch, mask='auto', width=32, height=32)
    p.setFont("Times-Roman", 8, leading=None)
    p.setFillColor("green")
    p.drawString(5.1*inch, 6.3*inch, "Bicol Region General Hospital and Geriatric Medical Center")
    p.drawString(5.6*inch, 6.2*inch, "(Formely BICOL SANITARIUM)")
    p.setFillColor("black")
    p.drawString(5.55*inch, 6.1*inch, "San Pedro, Cabusao Camarines Sur")
    p.drawString(5*inch, 6*inch, "Telephone Nos.: (054) 473-2244, 472-4422, 881-1033, 881-1761")
    p.drawString(5.1*inch, 5.9*inch, "E-mail Address: bicolsan@gmail.com, brghgmc@gmail.com")
    p.line(0, 5.8*inch, 1000, 5.8*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(5.9*inch, 5.6*inch, "CHARGE SLIP")
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(7*inch, 5.4*inch, "Date:____________________ ")
    p.drawString(7.5*inch, 5.4*inch, datetime.today().strftime('%m-%d-%Y'))
    p.drawString(4.5*inch, 5.2*inch, "Name:_______________________________________________________________ ")
    p.drawString(4.9*inch, 5.2*inch, patient_details[0]['patlast'] + ", " + patient_details[0]['patfirst'] + " " + patient_details[0]['patmiddle'][0])
    p.drawString(4.5*inch, 5*inch, "Address:_____________________________________________________________ ")
    p.drawString(5*inch, 5*inch, patient_address[0]['address'])
    p.drawString(4.5*inch, 4.8*inch, "Responsibility Center:__________________________________________________ ")
    p.drawString(5.8*inch, 4.8*inch, "RADIOLOGY")
    p.drawString(4.5*inch, 4.6*inch, "Hospital No.:__________________________________________________________ ")
    p.drawString(5.3*inch, 4.6*inch, patient_details[0]['hpercode'])


    #CONTENT
    styles = getSampleStyleSheet()
    styles2 = getSampleStyleSheet()
    styles3 = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleN.alignment = TA_CENTER
    styleN.fontSize = 8 
    styleN.fontName = "Times-Bold"

    style_td = styles2["BodyText"]
    style_td.alignment = TA_LEFT
    style_td.fontSize = 8 
    style_td.fontName = "Times-Roman"

    h_qty = Paragraph('Qty', styleN)
    h_particulars = Paragraph('Particular', styleN)
    h_up = Paragraph('Unit Price', styleN)
    h_total = Paragraph('Total', styleN)

    style_amt = styles3["BodyText"]
    style_amt.alignment = TA_RIGHT
    style_amt.fontSize = 8 
    style_amt.fontName = "Times-Roman"

    table_data = [[h_qty, h_particulars, h_up, h_total]]
    pf_table_data = [[h_qty, h_particulars, h_up, h_total]]
    if charges != "[]":
        ac = 0
        ax = 0
        pf_tot = 0
        ch_tot = 0
        for i in charges:
            if i['procdesc'].find('Professional') > 0:
                ax += 1
                pf_tot += i['pcchrgamt']
                pf_table_data.append([Paragraph(str("{:,}".format(i['pchrgqty'])), style_amt), Paragraph(i['procdesc'], style_td), Paragraph(str("{:,}".format(i['pchrgup'])), style_amt), Paragraph(str("{:,}".format(i['pcchrgamt'])), style_amt)]) 
            else:
                ac += 1
                ch_tot += i['pcchrgamt']
                table_data.append([Paragraph(str("{:,}".format(i['pchrgqty'])), style_amt), Paragraph(i['procdesc'], style_td), Paragraph(str("{:,}".format(i['pchrgup'])), style_amt), Paragraph(str("{:,}".format(i['pcchrgamt'])), style_amt)]) 
        if ch_tot is not None:
            table_data.append(['', Paragraph('TOTAL', style_td), '', Paragraph(str("{:,}".format(ch_tot)), style_amt)])
        if pf_tot is not None:
            pf_table_data.append(['', Paragraph('TOTAL', style_td), '', Paragraph(str("{:,}".format(pf_tot)), style_amt)])    

        t = Table(table_data, colWidths=[0.4*inch, 2.2*inch, 0.7*inch, 0.7*inch])
        t.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONT', (0, 0), (-1, -1), 'Times-Roman', 8)
        ]))
        t.wrapOn(p, 0, 0)
        if ac == 1:
            t.drawOn(p, 0.1*inch, 3.7*inch)
        elif ac == 2:
            t.drawOn(p, 0.1*inch, 3.5*inch)
        elif ac == 3:
            t.drawOn(p, 0.1*inch, 3.2*inch)
        elif ac == 4:
            t.drawOn(p, 0.1*inch, 3*inch)
        elif ac == 5:
            t.drawOn(p, 0.1*inch, 2.8*inch)
        elif ac == 6:
            t.drawOn(p, 0.1*inch, 2.4*inch)
        elif ac == 7:
            t.drawOn(p, 0.1*inch, 2.2*inch)
        elif ac == 8:
            t.drawOn(p, 0.1*inch, 2*inch)
        elif ac == 9:
            t.drawOn(p, 0.1*inch, 1.8*inch)
        elif ac == 10:
            t.drawOn(p, 0.1*inch, 1.4*inch)
        elif ac == 11:
            t.drawOn(p, 0.1*inch, 1.2*inch)
        elif ac == 12:
            t.drawOn(p, 0.1*inch, 1*inch)
        else:
            t.drawOn(p, 0.1*inch, 0.8*inch)

        if ax == 0:
            t2 = Table(table_data, colWidths=[0.4*inch, 2.2*inch, 0.7*inch, 0.7*inch])
            t2.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONT', (0, 0), (-1, -1), 'Times-Roman', 8)
            ]))
            t2.wrapOn(p, 0, 0)
            if ac == 1:
                t2.drawOn(p, 4.4*inch, 3.7*inch)
            elif ac == 2:
                t2.drawOn(p, 4.4*inch, 3.5*inch)
            elif ac == 3:
                t2.drawOn(p, 4.4*inch, 3.2*inch)
            elif ac == 4:
                t2.drawOn(p, 4.4*inch, 3*inch)
            elif ac == 5:
                t2.drawOn(p, 4.4*inch, 2.8*inch)
            elif ac == 6:
                t2.drawOn(p, 4.4*inch, 2.4*inch)
            elif ac == 7:
                t2.drawOn(p, 4.4*inch, 2.2*inch)
            elif ac == 8:
                t2.drawOn(p, 4.4*inch, 2*inch)
            elif ac == 9:
                t2.drawOn(p, 4.4*inch, 1.8*inch)
            elif ac == 10:
                t2.drawOn(p, 4.4*inch, 1.4*inch)
            elif ac == 11:
                t2.drawOn(p, 4.4*inch, 1.2*inch)
            elif ac == 12:
                t2.drawOn(p, 4.4*inch, 1*inch)
            else:
                t2.drawOn(p, 4.4*inch, 0.8*inch)
        else:
            #DUPLICATE
            tx = Table(pf_table_data, colWidths=[0.4*inch, 2.2*inch, 0.7*inch, 0.7*inch])
            tx.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONT', (0, 0), (-1, -1), 'Times-Roman', 8)
            ]))
            tx.wrapOn(p, 0, 0)
            if ax == 1:
                tx.drawOn(p, 4.4*inch, 3.7*inch)
            elif ax == 2:
                tx.drawOn(p, 4.4*inch, 3.5*inch)
            elif ax == 3:
                tx.drawOn(p, 4.4*inch, 3.2*inch)
            elif ax == 4:
                tx.drawOn(p, 4.4*inch, 3*inch)
            elif ax == 5:
                tx.drawOn(p, 4.4*inch, 2.8*inch)
            elif ax == 6:
                tx.drawOn(p, 4.4*inch, 2.4*inch)
            elif ax == 7:
                tx.drawOn(p, 4.4*inch, 2.2*inch)
            elif ax == 8:
                tx.drawOn(p, 4.4*inch, 2*inch)
            elif ax == 9:
                tx.drawOn(p, 4.4*inch, 1.8*inch)
            elif ax == 10:
                tx.drawOn(p, 4.4*inch, 1.4*inch)
            elif ax == 11:
                tx.drawOn(p, 4.4*inch, 1.2*inch)
            elif ax == 12:
                tx.drawOn(p, 4.4*inch, 1*inch)
            else:
                tx.drawOn(p, 4.4*inch, 0.8*inch)

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(0.2*inch, 0.7*inch, "Issued by:")
    p.drawString(0.2*inch, 0.4*inch, "_______________________________")
    p.drawString(0.3*inch, 0.45*inch, request.session.get("name"))
    p.drawString(0.4*inch, 0.25*inch, "Signature Over Printed Name")
    p.drawString(2.5*inch, 0.7*inch, "Payment:")
    p.drawString(2.5*inch, 0.5*inch, "OR No._______________________")
    p.drawString(2.5*inch, 0.3*inch, "Date.__________________________")

    #DUPLICATE

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(4.5*inch, 0.7*inch, "Issued by:")
    p.drawString(4.5*inch, 0.4*inch, "_______________________________")
    p.drawString(4.7*inch, 0.45*inch, request.session.get("name"))
    p.drawString(4.7*inch, 0.28*inch, "Signature Over Printed Name")
    p.drawString(6.8*inch, 0.7*inch, "Payment:")
    p.drawString(6.8*inch, 0.5*inch, "OR No._______________________")
    p.drawString(6.8*inch, 0.32*inch, "Date.__________________________")

    p.line(0, 0.2*inch, 1000, 0.30*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Italic", 7, leading=None)
    p.drawString(0.1*inch, 0.1*inch, "BRGHGMC-F-AS-BIL-006")
    p.drawString(2*inch, 0.1*inch, "Rev 2")
    p.drawString(2.9*inch, 0.1*inch, "Effectivity Date: January 6, 2020")

    #DUPLICATE
    p.setFont("Times-Italic", 7, leading=None)
    p.drawString(4.3*inch, 0.1*inch, "BRGHGMC-F-AS-BIL-006")
    p.drawString(6.3*inch, 0.1*inch, "Rev 2")
    p.drawString(7.1*inch, 0.1*inch, "Effectivity Date: January 6, 2020")

    p.setTitle("RADIOLOGY CHARGESLIP")
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def printLatestRadCharges(request, enctr):
    charges = requests.post(rad_charges_api, data={'enccode': enctr}).json()['data']
    #total = requests.post(rad_total_charge_api, data={'enccode': enctr}).json()['data'][0]['amt']
    total = 0
    patient_details = requests.post(patient_details_by_enc_api, data={'enccode': enctr}).json()["data"]
    patient_address = requests.post(patient_address_api, data={'no': patient_details[0]['hpercode']}).json()["data"]
    printed = requests.post(get_printed_cl_api, data={'enccode': enctr}).json()["data"]
    docointkey = []
    for i in printed:
        docointkey.append(i['docointkey'])
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    logo = ImageReader(static_root + '/integrated/img/brghgmclogo.png')
    response = HttpResponse(content_type='application/pdf')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setPageSize((8.5*inch, 6.5*inch))
    p.drawImage(logo, 0.2*inch, 6*inch, mask='auto', width=32, height=32)
    p.setFont("Times-Roman", 8, leading=None)
    p.setFillColor("green")
    p.drawString(0.9*inch, 6.3*inch, "Bicol Region General Hospital and Geriatric Medical Center")
    p.drawString(1.4*inch, 6.2*inch, "(Formely BICOL SANITARIUM)")
    p.setFillColor("black")
    p.drawString(1.35*inch, 6.1*inch, "San Pedro, Cabusao Camarines Sur")
    p.drawString(0.8*inch, 6*inch, "Telephone Nos.: (054) 473-2244, 472-4422, 881-1033, 881-1761")
    p.drawString(0.9*inch, 5.9*inch, "E-mail Address: bicolsan@gmail.com, brghgmc@gmail.com")
    p.line(0, 5.8*inch, 1000, 5.8*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(1.6*inch, 5.6*inch, "CHARGE SLIP")
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(2.6*inch, 5.4*inch, "Date:____________________ ")
    p.drawString(3.1*inch, 5.4*inch, datetime.today().strftime('%m-%d-%Y'))
    p.drawString(0.2*inch, 5.2*inch, "Name:_______________________________________________________________ ")
    p.drawString(0.6*inch, 5.2*inch, patient_details[0]['patlast'] + ", " + patient_details[0]['patfirst'] + " " + patient_details[0]['patmiddle'][0])
    p.drawString(0.2*inch, 5*inch, "Address:_____________________________________________________________ ")
    p.drawString(0.7*inch, 5*inch, patient_address[0]['address'])
    p.drawString(0.2*inch, 4.8*inch, "Responsibility Center:__________________________________________________ ")
    p.drawString(1.5*inch, 4.8*inch, "RADIOLOGY")
    p.drawString(0.2*inch, 4.6*inch, "Hospital No.:__________________________________________________________ ")
    p.drawString(1*inch, 4.6*inch, patient_details[0]['hpercode'])

    #DUPLICATE
    p.line(4.25*inch, 0, 4.25*inch, 1000) #(x1, y1, x2, y2)
    p.drawImage(logo, 4.5*inch, 6*inch, mask='auto', width=32, height=32)
    p.setFont("Times-Roman", 8, leading=None)
    p.setFillColor("green")
    p.drawString(5.1*inch, 6.3*inch, "Bicol Region General Hospital and Geriatric Medical Center")
    p.drawString(5.6*inch, 6.2*inch, "(Formely BICOL SANITARIUM)")
    p.setFillColor("black")
    p.drawString(5.55*inch, 6.1*inch, "San Pedro, Cabusao Camarines Sur")
    p.drawString(5*inch, 6*inch, "Telephone Nos.: (054) 473-2244, 472-4422, 881-1033, 881-1761")
    p.drawString(5.1*inch, 5.9*inch, "E-mail Address: bicolsan@gmail.com, brghgmc@gmail.com")
    p.line(0, 5.8*inch, 1000, 5.8*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(5.9*inch, 5.6*inch, "CHARGE SLIP")
    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(7*inch, 5.4*inch, "Date:____________________ ")
    p.drawString(7.5*inch, 5.4*inch, datetime.today().strftime('%m-%d-%Y'))
    p.drawString(4.5*inch, 5.2*inch, "Name:_______________________________________________________________ ")
    p.drawString(4.9*inch, 5.2*inch, patient_details[0]['patlast'] + ", " + patient_details[0]['patfirst'] + " " + patient_details[0]['patmiddle'][0])
    p.drawString(4.5*inch, 5*inch, "Address:_____________________________________________________________ ")
    p.drawString(5*inch, 5*inch, patient_address[0]['address'])
    p.drawString(4.5*inch, 4.8*inch, "Responsibility Center:__________________________________________________ ")
    p.drawString(5.8*inch, 4.8*inch, "RADIOLOGY")
    p.drawString(4.5*inch, 4.6*inch, "Hospital No.:__________________________________________________________ ")
    p.drawString(5.3*inch, 4.6*inch, patient_details[0]['hpercode'])

    #CONTENT
    styles = getSampleStyleSheet()
    styles2 = getSampleStyleSheet()
    styles3 = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleN.alignment = TA_CENTER
    styleN.fontSize = 8 
    styleN.fontName = "Times-Bold"

    style_td = styles2["BodyText"]
    style_td.alignment = TA_LEFT
    style_td.fontSize = 8 
    style_td.fontName = "Times-Roman"

    h_qty = Paragraph('Qty', styleN)
    h_particulars = Paragraph('Particular', styleN)
    h_up = Paragraph('Unit Price', styleN)
    h_total = Paragraph('Total', styleN)

    style_amt = styles3["BodyText"]
    style_amt.alignment = TA_RIGHT
    style_amt.fontSize = 8 
    style_amt.fontName = "Times-Roman"

    table_data = [[h_qty, h_particulars, h_up, h_total]]
    pf_table_data = [[h_qty, h_particulars, h_up, h_total]]
    if charges != "[]":
        ac = 0
        ax = 0
        pf_tot = 0
        ch_tot = 0
        for i in charges:
            if i['procdesc'].find('Professional') > 0:
                ax += 1
                pf_tot += i['pcchrgamt']
                pf_table_data.append([Paragraph(str("{:,}".format(i['pchrgqty'])), style_amt), Paragraph(i['procdesc'], style_td), Paragraph(str("{:,}".format(i['pchrgup'])), style_amt), Paragraph(str("{:,}".format(i['pcchrgamt'])), style_amt)]) 
            else:
                ac += 1
                ch_tot += i['pcchrgamt']
                table_data.append([Paragraph(str("{:,}".format(i['pchrgqty'])), style_amt), Paragraph(i['procdesc'], style_td), Paragraph(str("{:,}".format(i['pchrgup'])), style_amt), Paragraph(str("{:,}".format(i['pcchrgamt'])), style_amt)]) 
        if ch_tot is not None:
            table_data.append(['', Paragraph('TOTAL', style_td), '', Paragraph(str("{:,}".format(ch_tot)), style_amt)])
        if pf_tot is not None:
            pf_table_data.append(['', Paragraph('TOTAL', style_td), '', Paragraph(str("{:,}".format(pf_tot)), style_amt)])    

        t = Table(table_data, colWidths=[0.4*inch, 2.2*inch, 0.7*inch, 0.7*inch])
        t.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONT', (0, 0), (-1, -1), 'Times-Roman', 8)
        ]))
        t.wrapOn(p, 0, 0)
        if ac == 1:
            t.drawOn(p, 0.1*inch, 3.7*inch)
        elif ac == 2:
            t.drawOn(p, 0.1*inch, 3.5*inch)
        elif ac == 3:
            t.drawOn(p, 0.1*inch, 3.2*inch)
        elif ac == 4:
            t.drawOn(p, 0.1*inch, 3*inch)
        elif ac == 5:
            t.drawOn(p, 0.1*inch, 2.8*inch)
        elif ac == 6:
            t.drawOn(p, 0.1*inch, 2.4*inch)
        elif ac == 7:
            t.drawOn(p, 0.1*inch, 2.2*inch)
        elif ac == 8:
            t.drawOn(p, 0.1*inch, 2*inch)
        elif ac == 9:
            t.drawOn(p, 0.1*inch, 1.8*inch)
        elif ac == 10:
            t.drawOn(p, 0.1*inch, 1.4*inch)
        elif ac == 11:
            t.drawOn(p, 0.1*inch, 1.2*inch)
        elif ac == 12:
            t.drawOn(p, 0.1*inch, 1*inch)
        else:
            t.drawOn(p, 0.1*inch, 0.8*inch)

        #DUPLICATE
        tx = Table(pf_table_data, colWidths=[0.4*inch, 2.2*inch, 0.7*inch, 0.7*inch])
        tx.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONT', (0, 0), (-1, -1), 'Times-Roman', 8)
        ]))
        tx.wrapOn(p, 0, 0)
        if ax == 1:
            tx.drawOn(p, 4.4*inch, 3.7*inch)
        elif ax == 2:
            tx.drawOn(p, 4.4*inch, 3.5*inch)
        elif ax == 3:
            tx.drawOn(p, 4.4*inch, 3.2*inch)
        elif ax == 4:
            tx.drawOn(p, 4.4*inch, 3*inch)
        elif ax == 5:
            tx.drawOn(p, 4.4*inch, 2.8*inch)
        elif ax == 6:
            tx.drawOn(p, 4.4*inch, 2.4*inch)
        elif ax == 7:
            tx.drawOn(p, 4.4*inch, 2.2*inch)
        elif ax == 8:
            tx.drawOn(p, 4.4*inch, 2*inch)
        elif ax == 9:
            tx.drawOn(p, 4.4*inch, 1.8*inch)
        elif ax == 10:
            tx.drawOn(p, 4.4*inch, 1.4*inch)
        elif ax == 11:
            tx.drawOn(p, 4.4*inch, 1.2*inch)
        elif ax == 12:
            tx.drawOn(p, 4.4*inch, 1*inch)
        else:
            tx.drawOn(p, 4.4*inch, 0.8*inch)


    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(0.2*inch, 0.7*inch, "Issued by:")
    p.drawString(0.2*inch, 0.4*inch, "_______________________________")
    p.drawString(0.3*inch, 0.45*inch, request.session.get("name"))
    p.drawString(0.4*inch, 0.25*inch, "Signature Over Printed Name")
    p.drawString(2.5*inch, 0.7*inch, "Payment:")
    p.drawString(2.5*inch, 0.5*inch, "OR No._______________________")
    p.drawString(2.5*inch, 0.3*inch, "Date.__________________________")

    #DUPLICATE

    p.setFont("Times-Roman", 8, leading=None)
    p.drawString(4.5*inch, 0.7*inch, "Issued by:")
    p.drawString(4.5*inch, 0.4*inch, "_______________________________")
    p.drawString(4.7*inch, 0.45*inch, request.session.get("name"))
    p.drawString(4.7*inch, 0.28*inch, "Signature Over Printed Name")
    p.drawString(6.8*inch, 0.7*inch, "Payment:")
    p.drawString(6.8*inch, 0.5*inch, "OR No._______________________")
    p.drawString(6.8*inch, 0.32*inch, "Date.__________________________")

    p.line(0, 0.2*inch, 1000, 0.30*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Italic", 7, leading=None)
    p.drawString(0.1*inch, 0.1*inch, "BRGHGMC-F-AS-BIL-006")
    p.drawString(2*inch, 0.1*inch, "Rev 2")
    p.drawString(2.9*inch, 0.1*inch, "Effectivity Date: January 6, 2020")

    #DUPLICATE
    p.setFont("Times-Italic", 7, leading=None)
    p.drawString(4.3*inch, 0.1*inch, "BRGHGMC-F-AS-BIL-006")
    p.drawString(6.3*inch, 0.1*inch, "Rev 2")
    p.drawString(7.1*inch, 0.1*inch, "Effectivity Date: January 6, 2020")

    p.setTitle("RADIOLOGY CHARGESLIP")
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    if charges != "[]":
        for i in charges:
            addPrintedChargeSlip = requests.post(add_printed_cl_api, data={'enccode': i['enccode'], 'docointkey': i['docointkey']})
    return response

def rad_patient_exam(request, enctr):
    if request.session.get('employee_id') is not None:
        xray = []
        ultra = []
        scan = []
        exam = requests.get(rad_exam_api).json()['data']
        charges = requests.post(rad_charges_api, data={'enccode': enctr}).json()['data']
        total = requests.post(rad_total_charge_api, data={'enccode': enctr}).json()['data'][0]['amt']
        patient_details = requests.post(patient_details_by_enc_api, data={'enccode': enctr}).json()["data"]
        if total is None:
            total = 0
        for i in exam:
            if i['proccode'].find("RADIO") != -1:
                xray.append(i)
            elif i['proccode'].find("ULTRA") != -1:
                ultra.append(i)
            elif i['proccode'].find("SCAN") != -1:
                scan.append(i)
        for x in charges:
            x['docointkey'] = x['docointkey'].replace('/', '-')
        return render(request, 'integrated/radiology/patient_exam.html', {'page': 'Radiology', 'user_level': request.session['user_level'], 'name': request.session['name'], 'xray': xray, 'ultra': ultra, 'scan': scan, 'charges': charges, 'enctr': enctr, 'total': total, 'patient_details': patient_details})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def rad_exam_result(request, docintkey, enctr):
    if request.session.get('employee_id') is not None:
        docintkey = docintkey.replace("-", '/')
        if request.method == 'POST':
            xray_no = request.POST.get("xray_no")
            report_date = request.POST.get("date")
            procdesc = request.POST.get("examination")
            notes = request.POST.get("notes")
            radiologist = request.POST.get("radiologist")
            insert_data = requests.post(rad_exam_add_result_api, data={'docintkey': docintkey, 'notes': notes, 'procdesc': procdesc, 'radiologist': radiologist, 'xray_no': xray_no, 'report_date': report_date})      
        patient_details = requests.post(patient_details_by_enc_api, data={'enccode': enctr}).json()["data"]
        charges = requests.post(rad_charges_by_doc_api, data={'docointkey': docintkey}).json()["data"]
        result = requests.post(rad_exam_result_api, data={'docintkey': docintkey}).json()["data"]
        age = requests.post(age_api, data={'enccode': enctr, 'toecode': patient_details[0]['toecode']}).json()["data"]
        docintkey = docintkey.replace("/", '-')
        return render(request, 'integrated/radiology/patient_exam_result.html', {'page': 'Radiology', 'user_level': request.session['user_level'], 'name': request.session['name'], 'patient_details': patient_details, 'result': result, 'age': age, 'charges': charges, 'docintkey': docintkey, 'enctr': enctr})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def print_rad_result(result, docintkey, enctr):
    docintkey = docintkey.replace("-", '/')
    patient_details = requests.post(patient_details_by_enc_api, data={'enccode': enctr}).json()["data"]
    charges = requests.post(rad_charges_by_doc_api, data={'docointkey': docintkey}).json()["data"]
    result = requests.post(rad_exam_result_api, data={'docintkey': docintkey}).json()["data"]
    age = requests.post(age_api, data={'enccode': enctr, 'toecode': patient_details[0]['toecode']}).json()["data"]
    addr = requests.post(patient_address_api, data={'no': patient_details[0]['hpercode']}).json()["data"]
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    logo = ImageReader(static_root + '/integrated/img/brghgmclogo.png')
    response = HttpResponse(content_type='application/pdf')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setPageSize((8.5*inch, 13*inch))
    p.drawImage(logo, 0.5*inch, 12*inch, mask='auto', width=72, height=72)
    p.setFont("Times-Roman", 12, leading=None)
    p.setFillColor("green")
    p.drawString(2.2*inch, 12.8*inch, "Bicol Region General Hospital and Geriatric Medical Center")
    p.drawString(3*inch, 12.6*inch, "(Formely BICOL SANITARIUM)")
    p.setFont("Times-Roman", 11, leading=None)
    p.setFillColor("black")
    p.drawString(3.1*inch, 12.45*inch, "San Pedro, Cabusao Camarines Sur")
    p.drawString(2.3*inch, 12.3*inch, "Telephone Nos.: (054) 473-2244, 472-4422, 881-1033, 881-1761")
    p.drawString(2.4*inch, 12.16*inch, "E-mail Address: bicolsan@gmail.com, brghgmc@gmail.com")
    p.line(0, 11.95*inch, 1000, 11.95*inch) #(x1, y1, x2, y2)
    p.setTitle("XRAY RESULT")
    p.setFont("Times-Bold", 14, leading=None)
    p.drawString(3.1*inch, 11.7*inch, "RADIOLOGY SECTION")
    p.setFont("Times-Bold", 12, leading=None)
    if 'RADIO' in charges[0]['itemcode']:
        p.drawString(3.5*inch, 11.5*inch, "X-RAY REPORT")
    elif 'ULTRA' in charges[0]['itemcode']:
        p.drawString(3.5*inch, 11.5*inch, "ULTRASOUND REPORT")
    p.setFont("Times-Roman", 12, leading=None)
    p.drawString(0.5*inch, 11*inch, "X-RAY NO: __________________")
    if result[0]['xray_no']:
        p.drawString(1.5*inch, 11*inch, result[0]['xray_no'])
    p.drawString(6*inch, 11*inch, "DATE: __________________")
    if result[0]['report_date']:
        p.drawString(6.8*inch, 11*inch, result[0]['report_date'])
    p.drawString(0.5*inch, 10.7*inch, "HOMIS NO: __________________")
    if patient_details[0]['hpercode']:
        p.drawString(1.5*inch, 10.7*inch, patient_details[0]['hpercode'])
    p.drawString(0.5*inch, 10.2*inch, "NAME: _________________________________________")
    try:
        lastname = patient_details[0]['patlast']
        firstname = patient_details[0]['patfirst']
    except:
        lastname = ""
        firstname = ""
    
    if patient_details[0]['patmiddle']:
        middlename = patient_details[0]['patmiddle'][:1] + '. '
    else:
        middlename = ""
    if patient_details[0]['patsuffix']: 
        suffix = patient_details[0]['patsuffix']
    else:
        suffix = ""
    
    p.drawString(1.1*inch, 10.2*inch, firstname + ' ' + middlename + lastname + " " + suffix)
    p.drawString(4.5*inch, 10.2*inch, "AGE: ______")
    p.drawString(5.05*inch, 10.2*inch, str(age))
    p.drawString(5.5*inch, 10.2*inch, "SEX: ______")
    p.drawString(6.1*inch, 10.2*inch, patient_details[0]['patsex'])
    p.drawString(6.5*inch, 10.2*inch, "STATUS: ___________")
    if patient_details[0]['patcstat'] == 'C':
        p.drawString(7.2*inch, 10.2*inch, "CHILD")
    elif patient_details[0]['patcstat'] == 'D':
        p.drawString(7.2*inch, 10.2*inch, "DIVORSED")
    elif patient_details[0]['patcstat'] == 'M':
        p.drawString(7.2*inch, 10.2*inch, "MARRIED")
    elif patient_details[0]['patcstat'] == 'X':
        p.drawString(7.2*inch, 10.2*inch, "SEPARATED")
    elif patient_details[0]['patcstat'] == 'S':
        p.drawString(7.2*inch, 10.2*inch, "SINGLE")
    elif patient_details[0]['patcstat'] == 'W' and patient_details[0]['patsex'] == 'F':
        p.drawString(7.2*inch, 10.2*inch, "WIDOW")
    elif patient_details[0]['patcstat'] == 'W' and patient_details[0]['patsex'] == 'M':
        p.drawString(7.2*inch, 10.2*inch, "WIDOWER")

    p.drawString(0.5*inch, 9.9*inch, "ADDRESS: __________________________________________________________________________________")
    if addr[0]['address']:
        p.drawString(1.4*inch, 9.9*inch, addr[0]['address'])
    p.drawString(1*inch, 9.6*inch, "OPD: __________")
    p.drawString(2.5*inch, 9.6*inch, "IN-PATIENT: __________")
    if patient_details[0]['toecode'] == 'OPD' or patient_details[0]['toecode'] == 'OPDAD':
        p.drawString(1.7*inch, 9.6*inch, "X")
    if patient_details[0]['toecode'] == 'ADM':
        p.drawString(3.8*inch, 9.6*inch, "X")
    p.drawString(4.5*inch, 9.6*inch, "WARD: __________")
    p.drawString(6.2*inch, 9.6*inch, "BED: __________")
    p.drawString(0.5*inch, 9.3*inch, "EXAMINATION PERFORMED: __________________________________________________________")
    if result[0]['procdesc']:
        p.drawString(2.9*inch, 9.3*inch, result[0]['procdesc'])
    else:
        p.drawString(2.9*inch, 9.3*inch, charges[0]['procdesc'])
    p.setFont("Times-Bold", 12, leading=None)
    p.drawString(0.5*inch, 8.9*inch, "FINDINGS:")
    if result[0]['notes']:
        p.setFont("Times-Roman", 12, leading=None)
        p.drawString(0.8*inch, 8.6*inch, result[0]['notes'][:75])
        p.drawString(0.5*inch, 8.4*inch, result[0]['notes'][75:154])
        p.drawString(0.5*inch, 8.2*inch, result[0]['notes'][154:233])
        p.drawString(0.5*inch, 8*inch, result[0]['notes'][312:391])
        p.drawString(0.5*inch, 7.8*inch, result[0]['notes'][391:470])
        p.drawString(0.5*inch, 7.6*inch, result[0]['notes'][470:549])
        p.drawString(0.5*inch, 7.4*inch, result[0]['notes'][628:707])
        p.drawString(0.5*inch, 7.2*inch, result[0]['notes'][707:786])
        p.drawString(0.5*inch, 7*inch, result[0]['notes'][786:865])
        p.drawString(0.5*inch, 6.8*inch, result[0]['notes'][865:944])
        p.drawString(0.5*inch, 6.6*inch, result[0]['notes'][944:1023])
        p.drawString(0.5*inch, 6.4*inch, result[0]['notes'][1023:1102])
        p.drawString(0.5*inch, 6.2*inch, result[0]['notes'][1102:1181])
        p.drawString(0.5*inch, 6*inch, result[0]['notes'][1181:1260])
        p.drawString(0.5*inch, 5.8*inch, result[0]['notes'][1260:1339])
        p.drawString(0.5*inch, 5.6*inch, result[0]['notes'][1339:1418])
        p.drawString(0.5*inch, 5.4*inch, result[0]['notes'][1418:1497])
        p.drawString(0.5*inch, 5.2*inch, result[0]['notes'][1497:1576])
        p.drawString(0.5*inch, 5*inch, result[0]['notes'][1576:])

    p.setFont("Times-Roman", 12, leading=None)
    p.drawString(5*inch, 1*inch, "________________________________")
    if result[0]['radiologist'] == 'COLLAO':
        p.drawString(5.1*inch, 1.05*inch, "MAHGN R. COLLAO, MD, FPCR")
    p.drawString(5*inch, 1*inch, "________________________________")
    p.drawString(5.75*inch, 0.8*inch, "RADIOLOGIST")
    p.setFont("Times-Roman", 9, leading=None)
    p.drawString(5.35*inch, 0.65*inch, "This is an electronically signed report")

    p.line(0, 0.30*inch, 1000, 0.30*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Italic", 10, leading=None)
    p.drawString(0.3*inch, 0.15*inch, "BRGHGMC-F-MS-RAD-001")
    p.drawString(4*inch, 0.15*inch, "Rev. 3")
    p.drawString(6.5*inch, 0.15*inch, "Effectivity Date: January 6, 2020")
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def enc_patient_search(request):
    if request.session.get('employee_id') is not None:
        if request.method == 'POST':
            today = datetime.today()
            hospital_no = request.POST.get("hospital_no")
            lastname = request.POST.get("lastname").upper()
            firstname = request.POST.get("firstname").upper()
            middlename = request.POST.get("middlename").upper()
            search_response = requests.post(patient_search_api, data={'no': hospital_no, 'lastname': lastname, 'firstname': firstname, 'middlename': middlename})
            search_json_response = search_response.json()
            if search_json_response['status'] == 'success':
                for i in search_json_response['data']:
                    if i['dob']:
                        i['dob'] = datetime.strptime(i['dob'][:11], "%b %d %Y")
                return render(request, 'integrated/patient_search_result.html', {'page': 'Search Result', 'result': search_json_response['data'], 'user_level': request.session['user_level'], 'name': request.session['name'], 'today': today})
            else:
                msg = "Record not found"
                return render(request, 'integrated/patient_search_result.html', {'page': 'Search Result', 'msg': msg, 'user_level': request.session['user_level'], 'name': request.session['name']})
        else:
            msg = "Incorrect Search Procedure, Please ask for assistance"
            return render(request, 'integrated/patient_search_result.html', {'page': 'Search Result', 'msg': msg, 'user_level': request.session['user_level'], 'name': request.session['name']})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def billing(request):
    if request.session.get('employee_id') is not None:
        patient_response = requests.get(all_patients_api)
        patient_json_response = patient_response.json()
        if patient_json_response['status'] == 'success':
            for i in patient_json_response['data']:
                i['enccode'] = i['enccode'].replace('/', '-')
            patients = patient_json_response['data']
        else:
            patients = []
        return render(request, 'integrated/billing/index.html', {'page': 'Billing', 'user_level': request.session['user_level'], 'name': request.session['name'], 'patients': patients})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def billing_maip_report(request):
    if request.session.get('employee_id') is not None:
        report = []
        if request.method == 'POST':
            fr = request.POST.get('start')
            to = request.POST.get('end')
            typ = request.POST.get('type')
            report = requests.post(maip_report_api, data={'fr': fr, 'to': to, 'type': typ}).json()['data']['resultset']
        return render(request, 'integrated/billing/maip.html', {'page': 'Billing', 'user_level': request.session['user_level'], 'name': request.session['name'], 'report': report})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def billing_detailed_bill_excel(request, enctr):
    enctr = enctr.replace('-', '/')
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="detailed_bill.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Detailed Bill')
    row_num = 0
    header_response = requests.post(detailed_soa_header_api, data={'enctr': enctr})
    header_json_response = header_response.json()
    if header_json_response['status'] == 'success':
        if header_json_response['data'] is None:
            enctr = enctr.replace('-', '/')
            header_response = requests.post(detailed_soa_header_api, data={'enctr': enctr})
            header_json_response = header_response.json()
            if header_json_response['status'] == 'success':
                header = header_json_response['data']
        else:
            header = header_json_response['data']

        name = header['patient'][0]['patlast'] + ", " + header['patient'][0]['patfirst'] + " " + header['patient'][0]['patmiddle']

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Name', name]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    columns = ['Date', 'Charge Slip No.', 'Qty', 'Particulars', 'Unit Cost', 'Amount']
    for col_num in range(len(columns)):
        row_num = 1
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()
    try:
        if header['rnb']:
            column_data = ['Room and Board']
            for data_num in range(len(column_data)):
                row_num += 1
                ws.write(row_num, data_num, column_data[data_num], font_style)
            for i in header['rnb']:
                row_num += 1
                column_data = [i['date'], '', i['days'], i['wardname'], i['rmrate'], i['rmcharge']]
                for data_num in range(len(column_data)):
                    ws.write(row_num, data_num, column_data[data_num], font_style)
    except:
        pass

    try:
        if header['meds']:
            column_data = ['Drugs and Medicine']
            for data_num in range(len(column_data)):
                row_num += 1
                ws.write(row_num, data_num, column_data[data_num], font_style)
            for i in header['meds']:
                row_num += 1
                column_data = [i['date'], i['pcchrgcod'], i['pchrgqty'], i['gendesc'], i['pchrgup'], i['pcchrgamt']]
                for data_num in range(len(column_data)):
                    ws.write(row_num, data_num, column_data[data_num], font_style)
    except:
        pass
    
    try:
        if header['medsup2']:
            column_data = ['Medical Supply']
            for data_num in range(len(column_data)):
                row_num += 1
                ws.write(row_num, data_num, column_data[data_num], font_style)
            for i in header['medsup']:
                row_num += 1
                column_data = [i['date'], i['pcchrgcod'], i['pchrgqty'], i['cl2desc'], i['pchrgup'], i['pcchrgamt']]
                for data_num in range(len(column_data)):
                    ws.write(row_num, data_num, column_data[data_num], font_style)
    except:
        pass

    try:
        if header['lab']:
            column_data = ['Laboratory']
            for data_num in range(len(column_data)):
                row_num += 1
                ws.write(row_num, data_num, column_data[data_num], font_style)
            for i in header['lab']:
                row_num += 1
                column_data = [i['date'], i['pcchrgcod'], i['pchrgqty'], i['procdesc'], i['pchrgup'], i['pcchrgamt']]
                for data_num in range(len(column_data)):
                    ws.write(row_num, data_num, column_data[data_num], font_style)
    except:
        pass

    try:
        if header['rad']:
            column_data = ['Radiology']
            for data_num in range(len(column_data)):
                row_num += 1
                ws.write(row_num, data_num, column_data[data_num], font_style)
            for i in header['rad']:
                row_num += 1
                column_data = [i['date'], i['pcchrgcod'], i['pchrgqty'], i['procdesc'], i['pchrgup'], i['pcchrgamt']]
                for data_num in range(len(column_data)):
                    ws.write(row_num, data_num, column_data[data_num], font_style)
    except:
        pass

    try:
        if header['mrict']:
            column_data = ['MRI/CT Scan']
            for data_num in range(len(column_data)):
                row_num += 1
                ws.write(row_num, data_num, column_data[data_num], font_style)
            for i in header['mrict']:
                row_num += 1
                column_data = [i['date'], i['pcchrgcod'], i['pchrgqty'], i['procdesc'], i['pchrgup'], i['pcchrgamt']]
                for data_num in range(len(column_data)):
                    ws.write(row_num, data_num, column_data[data_num], font_style)
    except:
        pass
    
    try:
        if header['er']:
            column_data = ['Emergency Room']
            for data_num in range(len(column_data)):
                row_num += 1
                ws.write(row_num, data_num, column_data[data_num], font_style)
            for i in header['er']:
                row_num += 1
                column_data = [i['date'], i['pcchrgcod'], i['pchrgqty'], i['procdesc'], i['pchrgup'], i['pcchrgamt']]
                for data_num in range(len(column_data)):
                    ws.write(row_num, data_num, column_data[data_num], font_style)
    except:
        pass

    try:
        if header['ordr']:
            column_data = ['Operating/Emergency Room']
            for data_num in range(len(column_data)):
                row_num += 1
                ws.write(row_num, data_num, column_data[data_num], font_style)
            for i in header['ordr']:
                row_num += 1
                column_data = [i['date'], i['pcchrgcod'], i['pchrgqty'], i['procdesc'], i['pchrgup'], i['pcchrgamt']]
                for data_num in range(len(column_data)):
                    ws.write(row_num, data_num, column_data[data_num], font_style)
    except:
        pass

    try:
        if header['nursing']:
            column_data = ['Nursing Care Procedure']
            for data_num in range(len(column_data)):
                row_num += 1
                ws.write(row_num, data_num, column_data[data_num], font_style)
            for i in header['nursing']:
                row_num += 1
                column_data = [i['date'], i['pcchrgcod'], i['pchrgqty'], i['procdesc'], i['pchrgup'], i['pcchrgamt']]
                for data_num in range(len(column_data)):
                    ws.write(row_num, data_num, column_data[data_num], font_style)
    except:
        pass

    try:
        if header['ecg']:
            column_data = ['ECG']
            for data_num in range(len(column_data)):
                row_num += 1
                ws.write(row_num, data_num, column_data[data_num], font_style)
            for i in header['ecg']:
                row_num += 1
                column_data = [i['date'], i['pcchrgcod'], i['pchrgqty'], i['procdesc'], i['pchrgup'], i['pcchrgamt']]
                for data_num in range(len(column_data)):
                    ws.write(row_num, data_num, column_data[data_num], font_style)
    except:
        pass

    try:
        if header['pt']:
            column_data = ['Physical Therapy']
            for data_num in range(len(column_data)):
                row_num += 1
                ws.write(row_num, data_num, column_data[data_num], font_style)
            for i in header['pt']:
                row_num += 1
                column_data = [i['date'], i['pcchrgcod'], i['pchrgqty'], i['procdesc'], i['pchrgup'], i['pcchrgamt']]
                for data_num in range(len(column_data)):
                    ws.write(row_num, data_num, column_data[data_num], font_style)
    except:
        pass

    try:
        if header['dialysis']:
            column_data = ['Dialysis']
            for data_num in range(len(column_data)):
                row_num += 1
                ws.write(row_num, data_num, column_data[data_num], font_style)
            for i in header['dialysis']:
                row_num += 1
                column_data = [i['date'], i['pcchrgcod'], i['pchrgqty'], i['procdesc'], i['pchrgup'], i['pcchrgamt']]
                for data_num in range(len(column_data)):
                    ws.write(row_num, data_num, column_data[data_num], font_style)
    except:
        pass

    try:
        if header['abtc']:
            column_data = ['ABTC']
            for data_num in range(len(column_data)):
                row_num += 1
                ws.write(row_num, data_num, column_data[data_num], font_style)
            for i in header['abtc']:
                row_num += 1
                column_data = [i['date'], i['pcchrgcod'], i['pchrgqty'], i['procdesc'], i['pchrgup'], i['pcchrgamt']]
                for data_num in range(len(column_data)):
                    ws.write(row_num, data_num, column_data[data_num], font_style)
    except:
        pass

    try:
        if header['nbs']:
            column_data = ['New Born Screening']
            for data_num in range(len(column_data)):
                row_num += 1
                ws.write(row_num, data_num, column_data[data_num], font_style)
            for i in header['nbs']:
                row_num += 1
                column_data = [i['date'], i['pcchrgcod'], i['pchrgqty'], i['procdesc'], i['pchrgup'], i['pcchrgamt']]
                for data_num in range(len(column_data)):
                    ws.write(row_num, data_num, column_data[data_num], font_style)
    except:
        pass

    try:
        if header['nbh']:
            column_data = ['New Born Hearing Test']
            for data_num in range(len(column_data)):
                row_num += 1
                ws.write(row_num, data_num, column_data[data_num], font_style)
            for i in header['nbh']:
                row_num += 1
                column_data = [i['date'], i['pcchrgcod'], i['pchrgqty'], i['procdesc'], i['pchrgup'], i['pcchrgamt']]
                for data_num in range(len(column_data)):
                    ws.write(row_num, data_num, column_data[data_num], font_style)
    except:
        pass

    try:
        if header['amb']:
            column_data = ['Ambulance Fee']
            for data_num in range(len(column_data)):
                row_num += 1
                ws.write(row_num, data_num, column_data[data_num], font_style)
            for i in header['amb']:
                row_num += 1
                column_data = [i['date'], i['pcchrgcod'], i['pchrgqty'], ii['procdesc'], i['pchrgup'], i['pcchrgamt']]
                for data_num in range(len(column_data)):
                    ws.write(row_num, data_num, column_data[data_num], font_style)
    except:
        pass


    wb.save(response)
    return response

def billing_maip_excel_report(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="maip.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('MAIP Report')
    row_num = 0
    report = []
    if request.method == 'POST':
        fr = request.POST.get('start')
        to = request.POST.get('end')
        typ = request.POST.get('type')
        report = requests.post(maip_report_api, data={'fr': fr, 'to': to, 'type': typ}).json()['data']['resultset']
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Date', 'Name of Patient', 'Homis No.', 'Philhealth No.', 'Date of Birth', 'Age', 'Address', 'Contact Number', 'Diagnosis', 'Point of Entry', 'Classification', 'MSS Classification', 'Income', 'MAIP Code', 'Total Professional Fee Charges with Philhealth Deductions', 'Total Actual Charges', 'Total Actual Charges with Professional Fee', 'Drugs and Medicines', 'Medical Supplies', 'Laboratory', 'Xray/Ultrasound/2D Echo', 'CT Scan', 'Dental', 'OR/DR/ER Bill', 'Nursing Care Procedure', 'ECG', 'Physical Therapy', 'Others (Newborn Screening, Hearing Test)', 'OPD Bill', 'Hemodialysis', 'MAIP']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()
    for i in report:
        row_num += 1
        try:
            phic = i['phicnum']
        except:
            phic = ''
        column_data = [i['date'], i['name'], i['hpercode'], phic, i['birthdate'], i['age'], i['address'], '', i['diagnosis'], i['poe'], i['tacode'], i['mss'], '', '', i['prof_fee'], i['actual_charges'], i['prof_plus_actual'], i['drugs_meds'], i['med_supp'], i['lab'], i['rad'], i['ct'], '', i['er'], i['nursing'], i['ecg'], i['pt'], i['others'], '', i['hemodialysis'], i['maip']]
        for data_num in range(len(column_data)):
            ws.write(row_num, data_num, column_data[data_num], font_style)
    wb.save(response)
    return response

def patient_bill(request, enctr):
    encounter = enctr
    enctr = enctr.replace('-', '/')
    if request.session.get('employee_id') is not None:
        if request.method == 'POST':
            soa_no = request.POST.get("soa_no")
            soa_date = request.POST.get("soa_date")
            conf = request.POST.get("conforme")
            conf_name = request.POST.get("conforme_name")
            conf_date = request.POST.get("conforme_date")
            conf_contact = request.POST.get("conforme_contact")
            if conf == 'REP':
                conf_relation = request.POST.get("relation")
            else:
                conf_relation = ''
            edit = requests.post(soa_other_det_api, data={'enccode': enctr, 'soa_no': soa_no, 'soa_date': soa_date, 'conf': conf, 'conf_name': conf_name, 'conf_date': conf_date, 'conf_contact': conf_contact, 'relation': conf_relation})
        sc_pwd = 0
        qfs = 0
        maip = 0
        pcso = 0
        dswd = 0
        op = 0
        header_response = requests.post(soa_header_api, data={'enctr': enctr})
        header_json_response = header_response.json()
        if header_json_response['status'] == 'success':
            if header_json_response['data'] is None:
                enctr = enctr.replace('-', '/')
                header_response = requests.post(soa_header_api, data={'enctr': enctr})
                header_json_response = header_response.json()
                if header_json_response['status'] == 'success':
                    header = header_json_response['data']
            else:
                header = header_json_response['data']

        try:
            tscode = header['tscode']
        except:
            tscode = ""

        try:
            if header['abtc']:
                abtc = header['abtc'][0]['pcchrgamt'] 
            else:
                abtc = 0
        except:
            abtc = 0

        try:
            if header['nbs']:
                nbs = header['nbs'][0]['pcchrgamt'] 
            else:
                nbs = 0                
        except:
            nbs = 0

        try:
            if header['nbh']:
                nbh = header['nbh'][0]['pcchrgamt']
            else:
                nbh = 0
        except:
            nbh = 0

        try:
            if header['amb']:
                amb = header['amb'][0]['pcchrgamt']
            else:
                amb = 0
        except:
            amb = 0

        hosp_summary = add(header['rnb'], header['meds'], header['medsup'], header['lab'], header['rad'], header['mrict'], header['er'], header['ordr'], header['nursing'], header['ecg'], header['pt'], header['dialysis'], abtc, nbs, nbh, amb)
        
        bal = hosp_summary
        prof_summary = 0
        prof_sc = 0
        prof_qfs = 0
        prof_bal = 0
        prof_sum_bal = 0
        prof_phic = 0

        phiccase = 0
        phiccasepf = 0
        if header['prof']:
            for i in header['prof']:
                prof_summary += i['pfamt']
                prof_qfs += i['pfdisc']
                if i['pfsenior']:
                    prof_sc += i['pfsenior']
                prof_sum_bal += add(i['balance'])
                if i['phicamount'] is not None:
                    prof_phic += i['phicamount']
        else:
            prof_summary = 0

        try:
            if header['disc']:
                for i in header['disc']:
                    sc_pwd += bal * 0.2
                    bal -= bal * 0.2 
        except:
            pass

        caseone = 0
        casetwo = 0
        caseonepf = 0
        casetwopf = 0
        try:
            if header['philhealth']:
                caseone = header['philhealth'][0]['amthosp1'] 
                casetwo = header['philhealth'][0]['amthosp2']
                phiccase = header['philhealth'][0]['amthosp1'] + header['philhealth'][0]['amthosp2']
                phiccasepf = header['philhealth'][0]['amtpf1'] + header['philhealth'][0]['amtpf2']
                caseonepf = header['philhealth'][0]['amtpf1']
                casetwopf = header['philhealth'][0]['amtpf2']
                bal -= phiccase
                prof_bal -= phiccasepf
        except:
            pass

        try:
            if header['othdisc']:
                for i in header['othdisc']:
                    bal -= i['amount']
                    if i['disccode'] == 'QFS':
                        qfs = i['amount']
        except:
            pass
        try:
            if header['pdaf']:
                for i in header['pdaf']:
                    bal -= i['amount']
                    if i['fundcode'].strip() == 'MAP':
                        maip = i['amount']
                    elif i['fundcode'].strip() == 'DSWD':
                        dswd = i['amount']
                    elif i['fundcode'].strip() == 'PCSO':
                        pcso = i['amount']
                    elif i['fundcode'].strip() == 'OP':
                        op = i['amount']
        except:
            pass

        # if bal < 0:
        #     bal = 0
        if prof_bal < 0:
            prof_bal = 0

        toecode = ''
        if header['toecode'] == 'OPD':
            toecode = 'OUT-PATIENT'
        elif header['toecode'] == 'OPDAD':
            toecode = 'OUT-PATIENT'
        elif header['toecode'] == 'ER':
            toecode = 'EMERGENCY'
        elif header['toecode'] == 'ERADM':
            toecode = 'EMERGENCY'
        elif header['toecode'] == 'ADM':
            toecode = 'IN-PATIENT'

        try:
            other_info = header['oth']
        except:
            other_info = []
            pass
        return render(request, 'integrated/billing/bill.html', {'page': 'Billing', 'user_level': request.session['user_level'], 'name': request.session['name'], 'header': header, 'hosp_summ': hosp_summary, 'sc_pwd': sc_pwd, 'maip': maip, 'dswd': dswd, 'pcso': pcso, 'qfs': qfs, 'op': op, 'bal': bal, 'prof_summary': prof_summary, 'prof_sc': prof_sc, 'prof_bal': prof_bal, 'prof_phic': prof_phic, 'prof_sum_bal': prof_sum_bal, 'encounter': encounter, 'phiccase': phiccase, 'phiccasepf': phiccasepf, 'toecode': toecode, 'prof_qfs': prof_qfs, 'other_info': other_info, 'caseone': caseone, 'casetwo': casetwo, 'caseonepf': caseonepf, 'casetwopf': casetwopf, 'tscode': tscode})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def print_patient_bill(request, enctr):
    # DATA #
    encounter = enctr
    height, width = A4
    today = date.today()
    styles = getSampleStyleSheet()
    styles2 = getSampleStyleSheet()
    styles3 = getSampleStyleSheet()
    styles4 = getSampleStyleSheet()
    enctr = enctr.replace('-', '/')
    if request.session.get('employee_id') is not None:
        style_header = styles4["BodyText"]
        style_header = styles["BodyText"]
        style_header.alignment = TA_LEFT
        style_header.fontSize = 8 
        style_header.fontName = "Times-Roman"
        sc_pwd = 0
        qfs = 0
        maip = 0
        pcso = 0
        dswd = 0
        op = 0
        phiccase = 0
        phiccasepf = 0
        header_response = requests.post(soa_header_api, data={'enctr': enctr})
        header_json_response = header_response.json()
        if header_json_response['status'] == 'success':
            if header_json_response['data'] is None:
                enctr = enctr.replace('-', '/')
                header_response = requests.post(soa_header_api, data={'enctr': enctr})
                header_json_response = header_response.json()
                if header_json_response['status'] == 'success':
                    header = header_json_response['data']
            else:
                header = header_json_response['data']

        try:
            if header['abtc']:
                abtc = header['abtc'][0]['pcchrgamt'] 
            else:
                abtc = 0
        except:
            abtc = 0

        try:
            if header['nbs']:
                nbs = header['nbs'][0]['pcchrgamt'] 
            else:
                nbs = 0                
        except:
            nbs = 0

        try:
            if header['nbh']:
                nbh = header['nbh'][0]['pcchrgamt']
            else:
                nbh = 0
        except:
            nbh = 0
        
        try:
            if header['amb']:
                amb = header['amb'][0]['pcchrgamt']
            else:
                amb = 0
        except:
            amb = 0

        hosp_summary = add(header['rnb'], header['meds'], header['medsup'], header['lab'], header['rad'], header['mrict'], header['er'], header['ordr'], header['nursing'], header['ecg'], header['pt'], header['dialysis'], abtc, nbs, nbh, amb) 
        bal = hosp_summary
        
        prof_summary = 0
        prof_sc = 0
        prof_qfs = 0
        prof_bal = 0
        prof_sum_bal = 0
        prof_phic = 0
        phic_summary = 0
        if header['prof']:
            for i in header['prof']:
                prof_summary += i['pfamt']
                prof_qfs += i['pfdisc']
                if i['pfsenior']:
                    prof_sc += i['pfsenior']
                # prof_sum_bal += add(i['balance'])
                if i['phicamount'] is not None:
                    prof_phic += i['phicamount']
            prof_sum_bal = prof_summary - (prof_qfs + prof_sc + prof_phic)
            if prof_sum_bal < 0:
                prof_sum_bal = 0
        else:
            prof_summary = 0


        try:
            if header['disc']:
                for i in header['disc']:
                    sc_pwd += bal * 0.2
                    bal -= bal * 0.2 
        except:
            pass
        caseone = 0
        casetwo = 0
        caseonepf = 0
        casetwopf = 0
        try:
            if header['philhealth']:
                phiccase = header['philhealth'][0]['amthosp1']
                caseone = header['philhealth'][0]['amthosp1']
                if header['philhealth'][0]['amt2']:
                    casetwo = header['philhealth'][0]['amthosp2']
                    phiccase += header['philhealth'][0]['amthosp2']
                phiccasepf = header['philhealth'][0]['amtpf1']
                caseonepf = header['philhealth'][0]['amtpf1']
                if header['philhealth'][0]['amtpf2']:
                    phiccasepf += header['philhealth'][0]['amtpf2']
                    casetwopf = header['philhealth'][0]['amtpf2']
                bal -= phiccase
                prof_bal -= phiccasepf
        except:
            caseone = 0
            casetwo = 0
            caseonepf = 0
            casetwopf = 0


        if phiccase is None:
            phiccase = 0
            
        try:
            if header['othdisc']:
                for i in header['othdisc']:
                    bal -= i['amount']
                    if i['disccode'] == 'QFS':
                        qfs = i['amount']
        except:
            pass
        try:
            if header['pdaf']:
                for i in header['pdaf']:
                    bal -= i['amount']
                    if i['fundcode'].strip() == 'MAP':
                        maip = i['amount']
                    elif i['fundcode'].strip() == 'DSWD':
                        dswd = i['amount']
                    elif i['fundcode'].strip() == 'PCSO':
                        pcso = i['amount']
                    elif i['fundcode'].strip() == 'OP':
                        op = i['amount']
        except:
            pass
        
        try:
            if header['patient'][0]['patsuffix']:
                suffix = header['patient'][0]['patsuffix']
            else:
                suffix = ""
        except:
            suffix = ""
            pass

        try:
            if header['diagnosis']:
                for i in header['diagnosis']:
                    if i['primediag'] == 'Y':
                        final_diagnosis = i['diagtext'].upper()
                        physician = i['physician']

                    if i['tdcode'] == 'OTHER':
                        other_diagnosis = i['diagtext']
                    else:
                        other_diagnosis = ""
        except:
            final_diagnosis = ""
            other_diagnosis = ""
            physician = ""
            pass

        try: 
            if header['philhealth']:
                firstcase = header['philhealth'][0]['firstcase']
                secondcase = header['philhealth'][0]['secondcase']
            else:
                firstcase = ""
                secondcase = ""
        except:
            firstcase = ""
            secondcase = ""
            pass
        try:
            if header['member_type']:
                phicnum = header['member_type'][0]['phicnum']
                mem_type = header['member_type'][0]['typedesc']
                phictype = header['member_type'][0]['phictypemem']
            else:
                phicnum = ""
                mem_type = ""
                phictype = ""
        except:
            phicnum = ""
            mem_type = ""
            phictype = ""
            pass

        if bal < 0:
            bal = 0
        if prof_bal < 0:
            prof_bal = 0

        toecode = ''
        if header['toecode'] == 'OPD':
            toecode = 'OUT-PATIENT'
        elif header['toecode'] == 'OPDAD':
            toecode = 'OUT-PATIENT'
        elif header['toecode'] == 'ER':
            toecode = 'EMERGENCY'
        elif header['toecode'] == 'ERADM':
            toecode = 'EMERGENCY'
        elif header['toecode'] == 'ADM':
            toecode = 'IN-PATIENT'

        try:
            soa_no = header['oth'][0]['soa_no']
            soa_date = header['oth'][0]['soa_date']
            conf_type = header['oth'][0]['conforme_type']
            conf_name = header['oth'][0]['conforme_name']
            conf_date_signed = header['oth'][0]['conforme_date_signed']
            conf_contact = header['oth'][0]['conforme_contact']
            conf_relation = header['oth'][0]['fsoarelto']
        except:
            soa_no = ""
            soa_date = datetime.today().strftime('%m-%d-%Y')
            conf_type = ""
            conf_name = ""
            conf_date_signed = ""
            conf_contact = ""
            conf_relation = ""
            pass

    # END DATA #
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
    p.drawString(3.1*inch, 11.8*inch, "STATEMENT OF ACCOUNT")

    p.setFont("Times-Roman", 9, leading=None)
    
    p.drawString(7*inch, 11.6*inch, "SOA NO.    : " + soa_no)
    p.drawString(0.3*inch, 11.4*inch, "NAME OF PATIENT          : " + header['patient'][0]['patlast'] + ", " + header['patient'][0]['patfirst'] + " " + header['patient'][0]['patmiddle'] + " " + suffix)
    p.drawString(4.5*inch, 11.4*inch, "AGE                              : " + str(header['age']))
    p.drawString(7*inch, 11.4*inch, "DATE         : " + soa_date)
    if len(header['address']) < 35:
        p.drawString(0.3*inch, 11.2*inch, "ADDRESS                           : " + header['address'])
    else:
        p.drawString(0.3*inch, 11.2*inch, "ADDRESS                           : " + header['address'][:31])
        p.drawString(1.75*inch, 11*inch, header['address'][31:])
    p.drawString(4.5*inch, 11.2*inch, "BIRTHDATE               : " + header['patient'][0]['bday'])

    if toecode == 'IN-PATIENT':
        if header['details'][0]['date_discharged']:
            p.drawString(7*inch, 11.2*inch, "No. of Days: " + str(header['details'][0]['no_day']) + " day/s") 
        else:
            if header['details'][0]['no_days'] is not None:
                p.drawString(7*inch, 11.2*inch, "No. of Days: " + str(header['details'][0]['no_days']) + " day/s")   
            else:
                p.drawString(7*inch, 11.2*inch, "No. of Days:")   
    

    p.drawString(4.5*inch, 11*inch, "DATE ADMITTED     : " + header['details'][0]['date_admitted'])
    p.drawString(0.3*inch, 10.8*inch, "FINAL DIAGNOSIS           : ")
    p.setFont("Times-Roman", 7, leading=None)
    try:
        if len(final_diagnosis) < 45:
            p.drawString(1.8*inch, 10.8*inch, final_diagnosis)
        elif len(final_diagnosis) < 45 and len(final_diagnosis) > 85:
            p.drawString(1.8*inch, 10.8*inch, final_diagnosis[:46])
            p.drawString(1.75*inch, 10.6*inch, final_diagnosis[46:85])
        elif len(final_diagnosis) < 45 and len(final_diagnosis) <= 125:
            p.drawString(1.8*inch, 10.8*inch, final_diagnosis[:46])
            p.drawString(0.3*inch, 10.6*inch, final_diagnosis[46:120])
        else:
            p.drawString(1.8*inch, 10.8*inch, final_diagnosis[:46])
            p.drawString(0.3*inch, 10.6*inch, final_diagnosis[46:120] + "...")
    except:
        pass
    p.setFont("Times-Roman", 9, leading=None)
    if header['details'][0]['date_discharged']:
        p.drawString(4.5*inch, 10.8*inch, "DATE DISCHARGED: " + header['details'][0]['date_discharged'][:11])
    else:
        p.drawString(4.5*inch, 10.8*inch, "DATE DISCHARGED: " + datetime.strftime(today, "%b %d, %Y"))
    if str(firstcase) == "None":
        p.drawString(4.5*inch, 10.6*inch, "1ST CASE                   : ")
    else:
        p.drawString(4.5*inch, 10.6*inch, "1ST CASE                   : " + str(firstcase))
    p.drawString(0.3*inch, 10.4*inch, "OTHER DIAGNOSIS          : ")
    p.setFont("Times-Roman", 7, leading=None)
    if len(other_diagnosis) < 50:
        p.drawString(1.8*inch, 10.4*inch, other_diagnosis)
    else:
        p.drawString(1.8*inch, 10.4*inch, other_diagnosis[:51])
        p.drawString(1.75*inch, 10.2*inch, other_diagnosis[51:])
    p.setFont("Times-Roman", 9, leading=None)
    if str(secondcase) == "None":
        p.drawString(4.5*inch, 10.4*inch, "2nd CASE                    : ")
    else:
        p.drawString(4.5*inch, 10.4*inch, "2nd CASE                    : " + str(secondcase))
    if toecode == 'IN-PATIENT':
        if len(header['room_assign'][0]['wardname']) < 16:
            p.drawString(6.5*inch, 10.4*inch, "WARD     : " + header['room_assign'][0]['wardname'])
        elif len(header['room_assign'][0]['wardname']) < 30:
            p.drawString(6.5*inch, 10.4*inch, "WARD     : " + header['room_assign'][0]['wardname'][:14])
            p.drawString(7.1*inch, 10.2*inch, header['room_assign'][0]['wardname'][14:29])
        else: 
            p.drawString(6.5*inch, 10.4*inch, "WARD     : " + header['room_assign'][0]['wardname'][:14])
            p.drawString(7.1*inch, 10.2*inch, header['room_assign'][0]['wardname'][14:] + "...")
    try:
        if header['mss'][0]['mssdesc']:
            p.drawString(4.5*inch, 10.2*inch, "MSS CLASS                : " + header['mss'][0]['mssdesc'])
        else:
            p.drawString(4.5*inch, 10.2*inch, "MSS CLASS                : ")
    except:
        p.drawString(4.5*inch, 10.2*inch, "MSS CLASS                : ")
        pass
    p.drawString(6.5*inch, 10.6*inch, "HOSP.NO.: " + header['patient'][0]['hpercode'])  
    try:
        p.drawString(0.3*inch, 10*inch, "ATTENDING PHYSICIAN : " + physician)
    except:
        p.drawString(0.3*inch, 10*inch, "ATTENDING PHYSICIAN : ")
    if firstcase == "":
        p.drawString(4.5*inch, 10*inch, "PHILHEALTH             : ")
        p.drawString(4.5*inch, 9.8*inch, "PHILHEALTH NO      : ")
    else:
        p.drawString(4.5*inch, 10*inch, "PHILHEALTH             : " + mem_type)
        p.drawString(4.5*inch, 9.8*inch, "PHILHEALTH NO      : " + phicnum)
    
    p.setFont("Times-Bold", 9, leading=None)
    #TABLES HOSPITAL CHARGES
    styleN = styles["BodyText"]
    styleN.alignment = TA_CENTER
    styleN.fontSize = 8 
    styleN.fontName = "Times-Bold"
    h_particulars = Paragraph('PARTICULARS', styleN)
    h_sc_pwd = Paragraph('Mandatory Discount SC/PWD', styleN)
    h_actual = Paragraph('Actual Charges', styleN)
    h_phil = Paragraph('Philhealth', styleN)
    h_pcso = Paragraph('PCSO', styleN)
    h_dswd = Paragraph('OP-SCPF', styleN)
    h_maip = Paragraph('MAIP', styleN)
    h_qfs = Paragraph('Hospital QFS', styleN)
    h_out = Paragraph('Out of the Pocket Expense', styleN)
    h_hci = Paragraph('HCI FEES', styleN)
    h_prof = Paragraph('PROFESSIONAL FEE/S', styleN)
    h_summ_fee = Paragraph('SUMMARY OF FEES', styleN)
    h_caseone = Paragraph('1st Case', styleN)
    h_casetwo = Paragraph('2nd Case', styleN)


    style_td = styles2["BodyText"]
    style_td.alignment = TA_LEFT
    style_td.fontSize = 8 
    style_td.fontName = "Times-Roman"

    style_amt = styles3["BodyText"]
    style_amt.alignment = TA_RIGHT
    style_amt.fontSize = 8 
    style_amt.fontName = "Times-Roman"
    hci_fee_cols = 0
    table_data = [
        [h_particulars, h_actual, h_sc_pwd, h_phil, h_phil, h_pcso, h_maip, h_dswd, h_qfs, h_out],
        ['','','',h_caseone, h_casetwo],
        [h_hci]
    ]

    if header['rnb']:
        table_data.append([Paragraph('Room and Board', style_td), Paragraph(str("{:,.2f}".format(header['rnb'])), style_amt)])
        hci_fee_cols += 1
    if header['meds']:
        table_data.append([Paragraph('Drugs and Medicines', style_td), Paragraph(str("{:,.2f}".format(header['meds'])), style_amt)])
        hci_fee_cols += 1
    if header['medsup']:
        table_data.append([Paragraph('Medical Supplies', style_td), Paragraph(str("{:,.2f}".format(header['medsup'])), style_amt)])
        hci_fee_cols += 1
    if header['lab']:
        table_data.append([Paragraph('Laboratory', style_td), Paragraph(str("{:,.2f}".format(header['lab'])), style_amt)])
        hci_fee_cols += 1
    if header['rad']:
        table_data.append([Paragraph('Xray/Ultrasound/2D Echo', style_td), Paragraph(str("{:,.2f}".format(header['rad'])), style_amt)])
        hci_fee_cols += 1
    if header['mrict']:
        table_data.append([Paragraph('CT Scan/MRI', style_td), Paragraph(str("{:,.2f}".format(header['mrict'])), style_amt)])
        hci_fee_cols += 1
    if header['er']:
        table_data.append([Paragraph('ER Fee', style_td), Paragraph(str("{:,.2f}".format(header['er'])), style_amt)])
        hci_fee_cols += 1
    if header['ordr']:
        table_data.append([Paragraph('OR/DR Fee', style_td), Paragraph(str("{:,.2f}".format(header['ordr'])), style_amt)])
        hci_fee_cols += 1
    if header['nursing']:
        table_data.append([Paragraph('Nursing Care Procedure', style_td), Paragraph(str("{:,.2f}".format(header['nursing'])), style_amt)])
        hci_fee_cols += 1
    if header['ecg']:
        table_data.append([Paragraph('ECG', style_td), Paragraph(str("{:,.2f}".format(header['ecg'])), style_amt)])
        hci_fee_cols += 1
    if header['pt']:
        table_data.append([Paragraph('Physical Therapy', style_td), Paragraph(str("{:,.2f}".format(header['pt'])), style_amt)])
        hci_fee_cols += 1
    if header['dialysis']:
        table_data.append([Paragraph('Hemodialysis', style_td), Paragraph(str("{:,.2f}".format(header['dialysis'])), style_amt)])
        hci_fee_cols += 1
    try:
        if header['abtc']:
            table_data.append([Paragraph('ABTC', style_td), Paragraph(str("{:,.2f}".format(header['abtc'][0]['pcchrgamt'])), style_amt)])
            hci_fee_cols += 1
    except:
        pass
    try:
        if header['nbs']:
            table_data.append([Paragraph('New Born Screening', style_td), Paragraph(str("{:,.2f}".format(header['nbs'][0]['pcchrgamt'])), style_amt)])
            hci_fee_cols += 1
    except:
        pass
    try:
        if header['nbh']:
            table_data.append([Paragraph('New Born Hearing', style_td), Paragraph(str("{:,.2f}".format(header['nbh'][0]['pcchrgamt'])), style_amt)])
            hci_fee_cols += 1
    except:
        pass

    try:
        if header['amb']:
            table_data.append([Paragraph('Ambulance Fee', style_td), Paragraph(str("{:,.2f}".format(header['amb'][0]['pcchrgamt'])), style_amt)])
            hci_fee_cols += 1
    except:
        pass

    #HCI SUMMARY
    table_data.append([
        Paragraph('TOTAL(HCI Fees)', style_td), 
        Paragraph(str("{:,.2f}".format(hosp_summary)), style_amt), 
        Paragraph(str("{:,.2f}".format(sc_pwd)), style_amt),
        Paragraph(str("{:,.2f}".format(caseone)), style_amt),
        Paragraph(str("{:,.2f}".format(casetwo)), style_amt),
        Paragraph(str("{:,.2f}".format(pcso)), style_amt),
        Paragraph(str("{:,.2f}".format(maip)), style_amt),
        Paragraph(str("{:,.2f}".format(op)), style_amt),
        Paragraph(str("{:,.2f}".format(qfs)), style_amt),
        Paragraph(str("{:,.2f}".format(bal)), style_amt),
    ])
    hci_fee_cols += 1
    prof_header_cols = hci_fee_cols + 3
    #PROFFEE

    if header['prof']:
        table_data.append([h_prof])
        for i in header['prof']:
            if i['balance']:
                prof_balance = i['balance']
            else:
                prof_balance = 0.00
            if i['phicamount'] is not None:
                phicamount =  i['phicamount']
            else:
                phicamount = 0
            if i['pfsenior'] is not None:
                pfsc = i['pfsenior']
            else:
                pfsc = 0.00
            table_data.append([
                Paragraph(i['physician'], style_td),
                Paragraph(str("{:,.2f}".format(i['pfamt'])), style_amt),
                Paragraph(str("{:,.2f}".format(pfsc)), style_amt), 
                Paragraph(str("{:,.2f}".format(caseonepf)), style_amt), 
                Paragraph(str("{:,.2f}".format(casetwopf)), style_amt), 
                Paragraph(str(0.00), style_amt), 
                Paragraph(str(0.00), style_amt), 
                Paragraph(str(0.00), style_amt), 
                Paragraph(str("{:,.2f}".format(i['pfdisc'])), style_amt), 
                Paragraph(str("{:,.2f}".format(prof_balance)), style_amt)
            ])
        table_data.append([
            Paragraph('TOTAL(Prof Fee)', style_td), 
            Paragraph(str("{:,.2f}".format(prof_summary)), style_amt), 
            Paragraph(str("{:,.2f}".format(prof_sc)), style_amt),
            Paragraph(str("{:,.2f}".format(caseonepf)), style_amt),
            Paragraph(str("{:,.2f}".format(casetwopf)), style_amt),
            Paragraph(str(0.00), style_amt), 
            Paragraph(str(0.00), style_amt), 
            Paragraph(str(0.00), style_amt), 
            Paragraph(str("{:,.2f}".format(prof_qfs)), style_amt), 
            Paragraph(str("{:,.2f}".format(prof_sum_bal)), style_amt),
        ])
            

    #SUMMARY OF FEES
    table_data.append([h_summ_fee])
    table_data.append(
        [h_particulars, h_actual, h_sc_pwd, h_caseone, h_casetwo, h_pcso, h_maip, h_dswd, h_qfs, h_out]
    )

    table_data.append([
        Paragraph('TOTAL(HCI Fees)', style_td), 
        Paragraph(str("{:,.2f}".format(hosp_summary)), style_amt), 
        Paragraph(str("{:,.2f}".format(sc_pwd)), style_amt),
        Paragraph(str("{:,.2f}".format(caseone)), style_amt),
        Paragraph(str("{:,.2f}".format(casetwo)), style_amt),
        Paragraph(str("{:,.2f}".format(pcso)), style_amt),
        Paragraph(str("{:,.2f}".format(maip)), style_amt),
        Paragraph(str("{:,.2f}".format(op)), style_amt),
        Paragraph(str("{:,.2f}".format(qfs)), style_amt),
        Paragraph(str("{:,.2f}".format(bal)), style_amt),
    ])

    table_data.append([
            Paragraph('TOTAL(Prof Fee)', style_td), 
            Paragraph(str("{:,.2f}".format(prof_summary)), style_amt), 
            Paragraph(str("{:,.2f}".format(prof_sc)), style_amt),
            Paragraph(str("{:,.2f}".format(caseonepf)), style_amt),
            Paragraph(str("{:,.2f}".format(casetwopf)), style_amt),
            Paragraph(str("{:,.2f}".format(0)), style_amt), 
            Paragraph(str("{:,.2f}".format(0)), style_amt), 
            Paragraph(str("{:,.2f}".format(0)), style_amt), 
            Paragraph(str("{:,.2f}".format(prof_qfs)), style_amt), 
            Paragraph(str("{:,.2f}".format(prof_sum_bal)), style_amt),
    ])

    table_data.append([
            Paragraph('GRAND TOTAL', style_td), 
            Paragraph(str("{:,.2f}".format(hosp_summary + prof_summary)), style_amt), 
            Paragraph(str("{:,.2f}".format(sc_pwd + prof_sc)), style_amt),
            Paragraph(str("{:,.2f}".format(caseone + caseonepf)), style_amt),
            Paragraph(str("{:,.2f}".format(casetwo + casetwopf)), style_amt),
            Paragraph(str("{:,.2f}".format(pcso)), style_amt),
            Paragraph(str("{:,.2f}".format(maip)), style_amt),
            Paragraph(str("{:,.2f}".format(op)), style_amt),
            Paragraph(str("{:,.2f}".format(qfs + prof_qfs)), style_amt),
            Paragraph(str("{:,.2f}".format(bal + prof_sum_bal)), style_amt),
        ])
    
    t = Table(table_data, colWidths=[1.5*inch, 0.7*inch, 0.8*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.8*inch])
    #locate column
    t.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONT', (0, 0), (-1, -1), 'Times-Roman', 8),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ADD8E6')),
        ('SPAN', (0, 2), (-1, 2)),
        ('SPAN', (3, 0), (4, 0)),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#e8f4f8')),
        ('BACKGROUND', (0, hci_fee_cols + 2), (-1, hci_fee_cols + 2), colors.HexColor('#ADD8E6')),
        ('SPAN', (0, prof_header_cols), (-1, prof_header_cols)),
        ('BACKGROUND', (0, prof_header_cols), (-1, prof_header_cols), colors.HexColor('#d4ebf2')),
        ('SPAN', (0, len(table_data) - 5 ), (-1, len(table_data) - 5)),
        ('BACKGROUND', (0, len(table_data) - 6 ), (-1, len(table_data) - 6), colors.HexColor('#d4ebf2')),
        ('BACKGROUND', (0, len(table_data) - 5 ), (-1, len(table_data) - 5), colors.HexColor('#e8f4f8')),
        ('BACKGROUND', (0, len(table_data) - 4 ), (-1, len(table_data) - 4), colors.HexColor('#ADD8E6')),
        ('BACKGROUND', (0, len(table_data) - 1 ), (-1, len(table_data) - 1), colors.HexColor('#d4ebf2')),
        ]))
    t.wrapOn(p, 0, 0)
    table_len = (len(table_data) * 0.2) + 1.4

    t.drawOn(p, 0.3*inch, (9 - table_len)*inch)

    p.setFont("Times-Roman", 9, leading=None)
    starting = 9 - table_len
    if phictype == "P" or phictype == "I":
        p.setFont("Times-Bold", 9, leading=None)
        p.setFillColor("red")
        p.drawString(6.8*inch, (starting - 0.15)*inch, "NO BALANCE BILLING")
        p.setFillColor("black")
        p.setFont("Times-Roman", 9, leading=None)
    p.drawString(1*inch, (starting - 0.3)*inch, "Please pay the amount of: ________________________________________________________________________________________")
    if bal + prof_sum_bal != 0:
        p.drawString(2.35*inch, (starting - 0.3)*inch, num2words(round(bal + prof_sum_bal, 2)).upper() + " PESOS ONLY")
    else:
        p.drawString(2.35*inch, (starting - 0.3)*inch, " xxx ")
    p.setFont("Times-Roman", 8, leading=None)

    p.drawString(5.5*inch, (starting - 0.6)*inch, "Official Receipt No.: _________________________")
    p.drawString(5.5*inch, (starting - 0.8)*inch, "Payment in Php       : _________________________")
    p.drawString(5.5*inch, (starting - 1)*inch, "Date                         : _________________________")
    p.setFont("Times-Bold", 9, leading=None)
    p.drawString(0.3*inch, (starting - 1.2)*inch, "PREPARED BY:")
    p.line(0.3*inch, (starting - 1.6) *inch, 3*inch, (starting - 1.6) *inch) #(x1, y1, x2, y2)
    p.drawString(5*inch, (starting - 1.2)*inch, "CONFORME:")
    p.line(5*inch, (starting - 1.6) *inch, 8*inch, (starting - 1.6) *inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 9, leading=None)
    p.drawString(1.3*inch, (starting - 1.8)*inch, "Billing Staff")
    p.drawString(0.9*inch, (starting - 1.55)*inch, request.session.get("name"))
    p.drawString(0.9*inch, (starting - 1.95)*inch, "(Signature over Printed Name)")

    p.drawString(0.3*inch, (starting - 2.2)*inch, "Contact Number : (054) 881-1033 Loc.304")
    p.drawString(0.3*inch, (starting - 2.4)*inch, "Date Signed        : " + soa_date)
    if conf_type == "":
        p.drawString(5.2*inch, (starting - 1.8)*inch, "Philhealth Member/Patient/Authorized Representative")
    elif conf_type == "PATIENT":
        p.drawString(6.3*inch, (starting - 1.8)*inch, "Patient")
    elif conf_type == "PHIC":
        p.drawString(6*inch, (starting - 1.8)*inch, "Philhealth Member")
    elif conf_type == "REP":
        p.drawString(5.9*inch, (starting - 1.8)*inch, "Authorized Representative")
        if conf_relation == '1':
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient : Spouse")
        elif conf_relation == '2':
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient : Child")
        elif conf_relation == '3':
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient : Parent")
        elif conf_relation == '4':
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient : Sibling")
        elif conf_relation == '5':
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient : Other")
        elif conf_relation == '6':
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient : Member")
        else:
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient: ")
    if conf_name != "":
        p.drawString(5.3*inch, (starting - 1.55)*inch, conf_name)    
    p.drawString(5.8*inch, (starting - 1.95)*inch, "(Signature over Printed Name)")
    p.drawString(5*inch, (starting - 2.4)*inch, "Contact Number                   : " + conf_contact)
    p.drawString(5*inch, (starting - 2.6)*inch, "Date Signed                          : " + conf_date_signed)

    p.line(0, 0.30*inch, 1000, 0.30*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Italic", 10, leading=None)
    p.drawString(0.3*inch, 0.15*inch, "BRGHGMC-F-FS-BIL-001")
    p.drawString(2.6*inch, 0.15*inch, "Rev. 9")
    p.drawString(3.8*inch, 0.15*inch, "Effectivity Date: May 02, 2023")
    p.drawImage(pagpadabalogo, 7.2*inch, 0.05*inch, mask='auto', width=80, height=13)
    p.setTitle("STATEMENT OF ACCOUNT")
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def print_dialy_detailed_patient_bill(request, enctr):
    # DATA #
    today = date.today()
    styles = getSampleStyleSheet()
    styles2 = getSampleStyleSheet()
    styles3 = getSampleStyleSheet()
    styles4 = getSampleStyleSheet()
    enctr = enctr.replace('-', '/')
    if request.session.get('employee_id') is not None:
        style_header = styles4["BodyText"]
        style_header = styles["BodyText"]
        style_header.alignment = TA_LEFT
        style_header.fontSize = 8 
        style_header.fontName = "Times-Roman"
        header_response = requests.post(detailed_soa_header_api, data={'enctr': enctr})
        header_json_response = header_response.json()
        if header_json_response['status'] == 'success':
            if header_json_response['data'] is None:
                enctr = enctr.replace('-', '/')
                header_response = requests.post(detailed_soa_header_api, data={'enctr': enctr})
                header_json_response = header_response.json()
                if header_json_response['status'] == 'success':
                    header = header_json_response['data']
            else:
                header = header_json_response['data']
        try:
            if header['patient'][0]['patsuffix']:
                suffix = header['patient'][0]['patsuffix']
            else:
                suffix = ""
        except:
            suffix = ""
            pass

        try:
            if header['diagnosis']:
                for i in header['diagnosis']:
                    if i['primediag'] == 'Y':
                        final_diagnosis = i['diagtext'].upper()
                        physician = i['physician']
                    else:
                        final_diagnosis = ""
                        physician = ""

                    if i['tdcode'] == 'OTHER':
                        other_diagnosis = i['diagtext']
                    else:
                        other_diagnosis = ""
        except:
            final_diagnosis = ""
            other_diagnosis = ""
            physician = ""
            pass

        try: 
            if header['philhealth']:
                firstcase = header['philhealth'][0]['firstcase']
                secondcase = header['philhealth'][0]['secondcase']
            else:
                firstcase = ""
                secondcase = ""
        except:
            firstcase = ""
            secondcase = ""
            pass
        try:
            if header['member_type']:
                phicnum = header['member_type'][0]['phicnum']
                mem_type = header['member_type'][0]['typedesc']
                phictype = header['member_type'][0]['phictypemem']
            else:
                phicnum = ""
                mem_type = ""
                phictype = ""
        except:
            phicnum = ""
            mem_type = ""
            phictype = ""
            pass

        toecode = ''
        if header['toecode'] == 'OPD':
            toecode = 'OUT-PATIENT'
        elif header['toecode'] == 'OPDAD':
            toecode = 'OUT-PATIENT'
        elif header['toecode'] == 'ER':
            toecode = 'EMERGENCY'
        elif header['toecode'] == 'ERADM':
            toecode = 'EMERGENCY'
        elif header['toecode'] == 'ADM':
            toecode = 'IN-PATIENT'

        try:
            soa_no = header['oth'][0]['soa_no']
            soa_date = header['oth'][0]['soa_date']
            conf_type = header['oth'][0]['conforme_type']
            conf_name = header['oth'][0]['conforme_name']
            conf_date_signed = header['oth'][0]['conforme_date_signed']
            conf_contact = header['oth'][0]['conforme_contact']
            conf_relation = header['oth'][0]['fsoarelto']
        except:
            soa_no = ""
            soa_date = datetime.today().strftime('%m-%d-%Y')
            conf_type = ""
            conf_name = ""
            conf_date_signed = ""
            conf_contact = ""
            conf_relation = ""
            pass

    # END DATA #
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
    p.drawString(2.7*inch, 11.8*inch, "DETAILED STATEMENT OF ACCOUNT")

    p.setFont("Times-Roman", 9, leading=None)
    
    p.drawString(7*inch, 11.6*inch, "SOA NO.    : " + soa_no)
    p.drawString(0.3*inch, 11.4*inch, "NAME OF PATIENT          : " + header['patient'][0]['patlast'] + ", " + header['patient'][0]['patfirst'] + " " + header['patient'][0]['patmiddle'] + " " + suffix)
    p.drawString(4.5*inch, 11.4*inch, "AGE                              : " + str(header['age']))
    p.drawString(7*inch, 11.4*inch, "DATE         : " + soa_date)
    if len(header['address']) < 35:
        p.drawString(0.3*inch, 11.2*inch, "ADDRESS                           : " + header['address'])
    else:
        p.drawString(0.3*inch, 11.2*inch, "ADDRESS                           : " + header['address'][:31])
        p.drawString(1.75*inch, 11*inch, header['address'][31:])
    p.drawString(4.5*inch, 11.2*inch, "BIRTHDATE               : " + header['patient'][0]['bday'])

    if toecode == 'IN-PATIENT':
        if header['details'][0]['date_discharged']:
            p.drawString(7*inch, 11.2*inch, "No. of Days: " + str(header['details'][0]['no_day']) + " day/s") 
        else:
            if header['details'][0]['no_days'] is not None:
                p.drawString(7*inch, 11.2*inch, "No. of Days: " + str(header['details'][0]['no_days']) + " day/s")   
            else:
                p.drawString(7*inch, 11.2*inch, "No. of Days:")   
    

    p.drawString(4.5*inch, 11*inch, "DATE ADMITTED     : " + header['details'][0]['date_admitted'])
    p.drawString(0.3*inch, 10.8*inch, "FINAL DIAGNOSIS           : ")
    p.setFont("Times-Roman", 7, leading=None)
    if len(final_diagnosis) < 45:
        p.drawString(1.8*inch, 10.8*inch, final_diagnosis)
    elif len(final_diagnosis) < 45 and len(final_diagnosis) > 85:
        p.drawString(1.8*inch, 10.8*inch, final_diagnosis[:46])
        p.drawString(1.75*inch, 10.6*inch, final_diagnosis[46:85])
    elif len(final_diagnosis) < 45 and len(final_diagnosis) <= 125:
        p.drawString(1.8*inch, 10.8*inch, final_diagnosis[:46])
        p.drawString(0.3*inch, 10.6*inch, final_diagnosis[46:120])
    else:
        p.drawString(1.8*inch, 10.8*inch, final_diagnosis[:46])
        p.drawString(0.3*inch, 10.6*inch, final_diagnosis[46:120] + "...")
    p.setFont("Times-Roman", 9, leading=None)
    if header['details'][0]['date_discharged']:
        p.drawString(4.5*inch, 10.8*inch, "DATE DISCHARGED: " + header['details'][0]['date_discharged'][:11])
    else:
        p.drawString(4.5*inch, 10.8*inch, "DATE DISCHARGED: " + datetime.strftime(today, "%b %d, %Y"))
    if str(firstcase) == "None":
        p.drawString(4.5*inch, 10.6*inch, "1ST CASE                   : ")
    else:
        p.drawString(4.5*inch, 10.6*inch, "1ST CASE                   : " + str(firstcase))
    p.drawString(0.3*inch, 10.4*inch, "OTHER DIAGNOSIS          : ")
    p.setFont("Times-Roman", 7, leading=None)
    if len(other_diagnosis) < 50:
        p.drawString(1.8*inch, 10.4*inch, other_diagnosis)
    else:
        p.drawString(1.8*inch, 10.4*inch, other_diagnosis[:51])
        p.drawString(1.75*inch, 10.2*inch, other_diagnosis[51:])
    p.setFont("Times-Roman", 9, leading=None)
    if str(secondcase) == "None":
        p.drawString(4.5*inch, 10.4*inch, "2nd CASE                    : ")
    else:
        p.drawString(4.5*inch, 10.4*inch, "2nd CASE                    : " + str(secondcase))
    if toecode == 'IN-PATIENT':
        if len(header['room_assign'][0]['wardname']) < 16:
            p.drawString(6.5*inch, 10.4*inch, "WARD     : " + header['room_assign'][0]['wardname'])
        elif len(header['room_assign'][0]['wardname']) < 30:
            p.drawString(6.5*inch, 10.4*inch, "WARD     : " + header['room_assign'][0]['wardname'][:14])
            p.drawString(7.1*inch, 10.2*inch, header['room_assign'][0]['wardname'][14:29])
        else: 
            p.drawString(6.5*inch, 10.4*inch, "WARD     : " + header['room_assign'][0]['wardname'][:14])
            p.drawString(7.1*inch, 10.2*inch, header['room_assign'][0]['wardname'][14:] + "...")
    try:
        if header['mss'][0]['mssdesc']:
            p.drawString(4.5*inch, 10.2*inch, "MSS CLASS                : " + header['mss'][0]['mssdesc'])
        else:
            p.drawString(4.5*inch, 10.2*inch, "MSS CLASS                : ")
    except:
        p.drawString(4.5*inch, 10.2*inch, "MSS CLASS                : ")
        pass
    p.drawString(6.5*inch, 10.6*inch, "HOSP.NO.: " + header['patient'][0]['hpercode'])  

    p.drawString(0.3*inch, 10*inch, "ATTENDING PHYSICIAN : " + physician)
    if firstcase == "":
        p.drawString(4.5*inch, 10*inch, "PHILHEALTH             : ")
        p.drawString(4.5*inch, 9.8*inch, "PHILHEALTH NO      : ")
    else:
        p.drawString(4.5*inch, 10*inch, "PHILHEALTH             : " + mem_type)
        p.drawString(4.5*inch, 9.8*inch, "PHILHEALTH NO      : " + phicnum)
    
    p.setFont("Times-Bold", 9, leading=None)
    #TABLES HOSPITAL CHARGES
    styleN = styles["BodyText"]
    styleN.alignment = TA_CENTER
    styleN.fontSize = 8 
    styleN.fontName = "Times-Bold"
    h_particulars = Paragraph('PARTICULARS', styleN)
    h_sc_pwd = Paragraph('Qty', styleN)
    h_actual = Paragraph('Unit Price', styleN)
    h_phil = Paragraph('Amount', styleN)

    style_td = styles2["BodyText"]
    style_td.alignment = TA_LEFT
    style_td.fontSize = 8 
    style_td.fontName = "Times-Roman"

    style_amt = styles3["BodyText"]
    style_amt.alignment = TA_RIGHT
    style_amt.fontSize = 8 
    style_amt.fontName = "Times-Roman"
    hci_fee_cols = 0
    table_data = [
        [h_particulars, h_actual, h_sc_pwd, h_phil]
    ]

    hci_fee_cols += 1
    try:
        if header['prof']:
            for i in header['prof']:
                table_data.append([Paragraph("PROFESSIONAL FEE (" + i['physician'] + ")", style_td), Paragraph(str("{:,.2f}".format(i['pfamt'])), style_amt), 1, Paragraph(str("{:,.2f}".format(i['pftotamt'])), style_amt)])
                hci_fee_cols += 1   
    except:
        pass

    try:
        if header['meds']:
            for i in header['meds']:
                if len(i['gendesc']) > 50:
                    particular = i['gendesc'][:50] + "..."
                else:
                    particular = i['gendesc']
                table_data.append([Paragraph(particular, style_td), Paragraph(str("{:,.2f}".format(i['pchrgup'])), style_amt), i['pchrgqty'], Paragraph(str("{:,.2f}".format(i['pcchrgamt'])), style_amt)])
                hci_fee_cols += 1    
    except:
        pass
    
    try:
        if header['medsup']:
            for i in header['medsup']:
                if len(i['cl2desc']) > 80:
                    particular = i['cl2desc'][:80] + "..."
                else:
                    particular = i['cl2desc']
                table_data.append([Paragraph(particular, style_td), Paragraph(str("{:,.2f}".format(i['pchrgup'])), style_amt), i['pchrgqty'], Paragraph(str("{:,.2f}".format(i['pcchrgamt'])), style_amt)])
                hci_fee_cols += 1    
    except:
        pass

    
    t = Table(table_data, colWidths=[5*inch, 1*inch, 1*inch, 1*inch])
    #locate column
    t.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONT', (0, 0), (-1, -1), 'Times-Roman', 8),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ADD8E6')),
        ('BACKGROUND', (0, hci_fee_cols -1), (-1, hci_fee_cols -1), colors.HexColor('#ADD8E6'))
        ]))
    t.wrapOn(p, 0, 0)
    table_len = (len(table_data) * 0.2) + 1.4

    t.drawOn(p, 0.3*inch, (10.5 - table_len)*inch)

    p.setFont("Times-Roman", 9, leading=None)
    starting = 9 - table_len
   
    p.setFont("Times-Roman", 8, leading=None)

    p.setFont("Times-Bold", 9, leading=None)
    p.drawString(0.3*inch, (starting - 1.2)*inch, "PREPARED BY:")
    p.line(0.3*inch, (starting - 1.6) *inch, 3*inch, (starting - 1.6) *inch) #(x1, y1, x2, y2)
    p.drawString(5*inch, (starting - 1.2)*inch, "CONFORME:")
    p.line(5*inch, (starting - 1.6) *inch, 8*inch, (starting - 1.6) *inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 9, leading=None)
    p.drawString(1.3*inch, (starting - 1.8)*inch, "Billing Staff")
    p.drawString(0.9*inch, (starting - 1.55)*inch, request.session.get("name"))
    p.drawString(0.9*inch, (starting - 1.95)*inch, "(Signature over Printed Name)")

    p.drawString(0.3*inch, (starting - 2.2)*inch, "Contact Number : (054) 881-1033 Loc.304")
    p.drawString(0.3*inch, (starting - 2.4)*inch, "Date Signed        : " + soa_date)
    if conf_type == "":
        p.drawString(5.2*inch, (starting - 1.8)*inch, "Philhealth Member/Patient/Authorized Representative")
    elif conf_type == "PATIENT":
        p.drawString(6.3*inch, (starting - 1.8)*inch, "Patient")
    elif conf_type == "PHIC":
        p.drawString(6*inch, (starting - 1.8)*inch, "Philhealth Member")
    elif conf_type == "REP":
        p.drawString(5.9*inch, (starting - 1.8)*inch, "Authorized Representative")
        if conf_relation == '1':
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient : Spouse")
        elif conf_relation == '2':
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient : Child")
        elif conf_relation == '3':
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient : Parent")
        elif conf_relation == '4':
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient : Sibling")
        elif conf_relation == '5':
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient : Other")
        elif conf_relation == '6':
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient : Member")
        else:
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient: ")
    if conf_name != "":
        p.drawString(5.3*inch, (starting - 1.55)*inch, conf_name)    
    p.drawString(5.8*inch, (starting - 1.95)*inch, "(Signature over Printed Name)")
    p.drawString(5*inch, (starting - 2.4)*inch, "Contact Number                   : " + conf_contact)
    p.drawString(5*inch, (starting - 2.6)*inch, "Date Signed                          : " + conf_date_signed)

    p.setTitle("STATEMENT OF ACCOUNT")
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def print_dialysis_patient_bill(request, enctr):
    # DATA #
    encounter = enctr
    height, width = A4
    today = date.today()
    styles = getSampleStyleSheet()
    styles2 = getSampleStyleSheet()
    styles3 = getSampleStyleSheet()
    styles4 = getSampleStyleSheet()
    enctr = enctr.replace('-', '/')
    if request.session.get('employee_id') is not None:
        style_header = styles4["BodyText"]
        style_header = styles["BodyText"]
        style_header.alignment = TA_LEFT
        style_header.fontSize = 8 
        style_header.fontName = "Times-Roman"
        sc_pwd = 0
        qfs = 0
        maip = 0
        pcso = 0
        dswd = 0
        op = 0
        phiccase = 0
        phiccasepf = 0
        header_response = requests.post(soa_header_api, data={'enctr': enctr})
        header_json_response = header_response.json()
        if header_json_response['status'] == 'success':
            if header_json_response['data'] is None:
                enctr = enctr.replace('-', '/')
                header_response = requests.post(soa_header_api, data={'enctr': enctr})
                header_json_response = header_response.json()
                if header_json_response['status'] == 'success':
                    header = header_json_response['data']
            else:
                header = header_json_response['data']

        try:
            if header['abtc']:
                abtc = header['abtc'][0]['pcchrgamt'] 
            else:
                abtc = 0
        except:
            abtc = 0

        try:
            if header['nbs']:
                nbs = header['nbs'][0]['pcchrgamt'] 
            else:
                nbs = 0                
        except:
            nbs = 0

        try:
            if header['nbh']:
                nbh = header['nbh'][0]['pcchrgamt']
            else:
                nbh = 0
        except:
            nbh = 0
        
        try:
            if header['amb']:
                amb = header['amb'][0]['pcchrgamt']
            else:
                amb = 0
        except:
            amb = 0

        hosp_summary = add(header['rnb'], header['meds'], header['medsup'], header['lab'], header['rad'], header['mrict'], header['er'], header['ordr'], header['nursing'], header['ecg'], header['pt'], header['dialysis'], abtc, nbs, nbh, amb) 
        bal = hosp_summary
        
        prof_summary = 0
        prof_sc = 0
        prof_qfs = 0
        prof_bal = 0
        prof_sum_bal = 0
        prof_phic = 0
        phic_summary = 0
        if header['prof']:
            for i in header['prof']:
                prof_summary += i['pfamt']
                prof_qfs += i['pfdisc']
                if i['pfsenior'] is not None:
                    prof_sc += i['pfsenior']
                # prof_sum_bal += add(i['balance'])
                if i['phicamount'] is not None:
                    prof_phic += i['phicamount']
            prof_sum_bal = prof_summary - (prof_qfs + prof_sc + prof_phic)
            if prof_sum_bal < 0:
                prof_sum_bal = 0
        else:
            prof_summary = 0


        try:
            if header['disc']:
                for i in header['disc']:
                    sc_pwd += bal * 0.2
                    bal -= bal * 0.2 
        except:
            pass
        caseone = 0
        casetwo = 0
        caseonepf = 0
        casetwopf = 0  
        try:
            if header['philhealth']:
                phiccase = header['philhealth'][0]['amthosp1']
                caseone = header['philhealth'][0]['amthosp1']
                if header['philhealth'][0]['amt2']:
                    casetwo = header['philhealth'][0]['amthosp2']
                    phiccase += header['philhealth'][0]['amthosp2']
                phiccasepf = header['philhealth'][0]['amtpf1']
                caseonepf = header['philhealth'][0]['amtpf1']
                if header['philhealth'][0]['amtpf2']:
                    phiccasepf += header['philhealth'][0]['amtpf2']
                    casetwopf = header['philhealth'][0]['amtpf2']
                bal -= phiccase
                prof_bal -= phiccasepf
        except:
            caseone = 0
            casetwo = 0
            caseonepf = 0
            casetwopf = 0 

        if phiccase is None:
            phiccase = 0
            
        try:
            if header['othdisc']:
                for i in header['othdisc']:
                    bal -= i['amount']
                    if i['disccode'] == 'QFS':
                        qfs = i['amount']
        except:
            pass
        try:
            if header['pdaf']:
                for i in header['pdaf']:
                    bal -= i['amount']
                    if i['fundcode'].strip() == 'MAP':
                        maip = i['amount']
                    elif i['fundcode'].strip() == 'DSWD':
                        dswd = i['amount']
                    elif i['fundcode'].strip() == 'PCSO':
                        pcso = i['amount']
                    elif i['fundcode'].strip() == 'OP':
                        op = i['amount']
        except:
            pass
        
        try:
            if header['patient'][0]['patsuffix']:
                suffix = header['patient'][0]['patsuffix']
            else:
                suffix = ""
        except:
            suffix = ""
            pass

        try:
            if header['diagnosis']:
                for i in header['diagnosis']:
                    if i['primediag'] == "Y":
                        final_diagnosis = i['diagtext'].upper()
                        physician = i['physician']

                    if i['tdcode'] == 'OTHER':
                        other_diagnosis = i['diagtext']
                    else:
                        other_diagnosis = ""
        except:
            final_diagnosis = ""
            other_diagnosis = ""
            physician = ""
            pass
        
        try: 
            if header['philhealth']:
                firstcase = header['philhealth'][0]['firstcase']
                secondcase = header['philhealth'][0]['secondcase']
            else:
                firstcase = ""
                secondcase = ""
        except:
            firstcase = ""
            secondcase = ""
            pass
        try:
            if header['member_type']:
                phicnum = header['member_type'][0]['phicnum']
                mem_type = header['member_type'][0]['typedesc']
                phictype = header['member_type'][0]['phictypemem']
            else:
                phicnum = ""
                mem_type = ""
                phictype = ""
        except:
            phicnum = ""
            mem_type = ""
            phictype = ""
            pass

        if bal < 0:
            bal = 0
        if prof_bal < 0:
            prof_bal = 0

        toecode = ''
        if header['toecode'] == 'OPD':
            toecode = 'OUT-PATIENT'
        elif header['toecode'] == 'OPDAD':
            toecode = 'OUT-PATIENT'
        elif header['toecode'] == 'ER':
            toecode = 'EMERGENCY'
        elif header['toecode'] == 'ERADM':
            toecode = 'EMERGENCY'
        elif header['toecode'] == 'ADM':
            toecode = 'IN-PATIENT'

        try:
            soa_no = header['oth'][0]['soa_no']
            soa_date = header['oth'][0]['soa_date']
            conf_type = header['oth'][0]['conforme_type']
            conf_name = header['oth'][0]['conforme_name']
            conf_date_signed = header['oth'][0]['conforme_date_signed']
            conf_contact = header['oth'][0]['conforme_contact']
            conf_relation = header['oth'][0]['fsoarelto']
        except:
            soa_no = ""
            soa_date = datetime.today().strftime('%m-%d-%Y')
            conf_type = ""
            conf_name = ""
            conf_date_signed = ""
            conf_contact = ""
            conf_relation = ""
            pass

    # END DATA #
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
    p.drawString(3.1*inch, 11.8*inch, "STATEMENT OF ACCOUNT")

    p.setFont("Times-Roman", 9, leading=None)
    
    p.drawString(7*inch, 11.6*inch, "SOA NO.    : " + soa_no)
    p.drawString(0.3*inch, 11.4*inch, "NAME OF PATIENT          : " + header['patient'][0]['patlast'] + ", " + header['patient'][0]['patfirst'] + " " + header['patient'][0]['patmiddle'] + " " + suffix)
    p.drawString(4.5*inch, 11.4*inch, "AGE                              : " + str(header['age']))
    p.drawString(7*inch, 11.4*inch, "DATE         : " + soa_date)
    if len(header['address']) < 35:
        p.drawString(0.3*inch, 11.2*inch, "ADDRESS                           : " + header['address'])
    else:
        p.drawString(0.3*inch, 11.2*inch, "ADDRESS                           : " + header['address'][:31])
        p.drawString(1.75*inch, 11*inch, header['address'][31:])
    p.drawString(4.5*inch, 11.2*inch, "BIRTHDATE               : " + header['patient'][0]['bday'])

    if toecode == 'IN-PATIENT':
        if header['details'][0]['date_discharged']:
            p.drawString(7*inch, 11.2*inch, "No. of Days: " + str(header['details'][0]['no_day']) + " day/s") 
        else:
            if header['details'][0]['no_days'] is not None:
                p.drawString(7*inch, 11.2*inch, "No. of Days: " + str(header['details'][0]['no_days']) + " day/s")   
            else:
                p.drawString(7*inch, 11.2*inch, "No. of Days:")   
    
    p.drawString(4.5*inch, 11*inch, "DATE ADMITTED     : " + header['details'][0]['date_admitted'])
    p.drawString(0.3*inch, 10.8*inch, "FINAL DIAGNOSIS           : ")
    p.setFont("Times-Roman", 7, leading=None)
    try:
        if len(final_diagnosis) < 45:
            p.drawString(1.8*inch, 10.8*inch, final_diagnosis)
        elif len(final_diagnosis) < 45 and len(final_diagnosis) > 85:
            p.drawString(1.8*inch, 10.8*inch, final_diagnosis[:46])
            p.drawString(1.75*inch, 10.6*inch, final_diagnosis[46:85])
        elif len(final_diagnosis) < 45 and len(final_diagnosis) <= 125:
            p.drawString(1.8*inch, 10.8*inch, final_diagnosis[:46])
            p.drawString(0.3*inch, 10.6*inch, final_diagnosis[46:120])
        else:
            p.drawString(1.8*inch, 10.8*inch, final_diagnosis[:46])
            p.drawString(0.3*inch, 10.6*inch, final_diagnosis[46:120] + "...")
    except:
        pass
    p.setFont("Times-Roman", 9, leading=None)
    if header['details'][0]['date_discharged']:
        p.drawString(4.5*inch, 10.8*inch, "DATE DISCHARGED: " + header['details'][0]['date_discharged'][:11])
    else:
        p.drawString(4.5*inch, 10.8*inch, "DATE DISCHARGED: " + datetime.strftime(today, "%b %d, %Y"))
    if str(firstcase) == "None":
        p.drawString(4.5*inch, 10.6*inch, "1ST CASE                   : ")
    else:
        p.drawString(4.5*inch, 10.6*inch, "1ST CASE                   : " + str(firstcase))
    p.drawString(0.3*inch, 10.4*inch, "OTHER DIAGNOSIS          : ")
    p.setFont("Times-Roman", 7, leading=None)
    if len(other_diagnosis) < 50:
        p.drawString(1.8*inch, 10.4*inch, other_diagnosis)
    else:
        p.drawString(1.8*inch, 10.4*inch, other_diagnosis[:51])
        p.drawString(1.75*inch, 10.2*inch, other_diagnosis[51:])
    p.setFont("Times-Roman", 9, leading=None)
    if str(secondcase) == "None":
        p.drawString(4.5*inch, 10.4*inch, "2nd CASE                    : ")
    else:
        p.drawString(4.5*inch, 10.4*inch, "2nd CASE                    : " + str(secondcase))
    if toecode == 'IN-PATIENT':
        if len(header['room_assign'][0]['wardname']) < 16:
            p.drawString(6.5*inch, 10.4*inch, "WARD     : " + header['room_assign'][0]['wardname'])
        elif len(header['room_assign'][0]['wardname']) < 30:
            p.drawString(6.5*inch, 10.4*inch, "WARD     : " + header['room_assign'][0]['wardname'][:14])
            p.drawString(7.1*inch, 10.2*inch, header['room_assign'][0]['wardname'][14:29])
        else: 
            p.drawString(6.5*inch, 10.4*inch, "WARD     : " + header['room_assign'][0]['wardname'][:14])
            p.drawString(7.1*inch, 10.2*inch, header['room_assign'][0]['wardname'][14:] + "...")
    try:
        if header['mss'][0]['mssdesc']:
            p.drawString(4.5*inch, 10.2*inch, "MSS CLASS                : " + header['mss'][0]['mssdesc'])
        else:
            p.drawString(4.5*inch, 10.2*inch, "MSS CLASS                : ")
    except:
        p.drawString(4.5*inch, 10.2*inch, "MSS CLASS                : ")
        pass
    p.drawString(6.5*inch, 10.6*inch, "HOSP.NO.: " + header['patient'][0]['hpercode'])  
    try:
        p.drawString(0.3*inch, 10*inch, "ATTENDING PHYSICIAN : " + physician)
    except:
        p.drawString(0.3*inch, 10*inch, "ATTENDING PHYSICIAN : ")
    if firstcase == "":
        p.drawString(4.5*inch, 10*inch, "PHILHEALTH             : ")
        p.drawString(4.5*inch, 9.8*inch, "PHILHEALTH NO      : ")
    else:
        p.drawString(4.5*inch, 10*inch, "PHILHEALTH             : " + mem_type)
        p.drawString(4.5*inch, 9.8*inch, "PHILHEALTH NO      : " + phicnum)
    
    p.setFont("Times-Bold", 9, leading=None)
    #TABLES HOSPITAL CHARGES
    styleN = styles["BodyText"]
    styleN.alignment = TA_CENTER
    styleN.fontSize = 8 
    styleN.fontName = "Times-Bold"
    h_particulars = Paragraph('PARTICULARS', styleN)
    h_sc_pwd = Paragraph('Mandatory Discount SC/PWD', styleN)
    h_actual = Paragraph('Actual Charges', styleN)
    h_phil = Paragraph('Philhealth', styleN)
    h_pcso = Paragraph('PCSO', styleN)
    h_dswd = Paragraph('OP-SCPF', styleN)
    h_maip = Paragraph('MAIP', styleN)
    h_qfs = Paragraph('Hospital QFS', styleN)
    h_out = Paragraph('Out of the Pocket Expense', styleN)
    h_hci = Paragraph('HCI FEES', styleN)
    h_prof = Paragraph('PROFESSIONAL FEE/S', styleN)
    h_summ_fee = Paragraph('SUMMARY OF FEES', styleN)
    h_caseone = Paragraph('1st Case', styleN)
    h_casetwo = Paragraph('2nd Case', styleN)


    style_td = styles2["BodyText"]
    style_td.alignment = TA_LEFT
    style_td.fontSize = 8 
    style_td.fontName = "Times-Roman"

    style_amt = styles3["BodyText"]
    style_amt.alignment = TA_RIGHT
    style_amt.fontSize = 8 
    style_amt.fontName = "Times-Roman"
    hci_fee_cols = 0
    table_data = [
        [h_particulars, h_actual, h_sc_pwd, h_phil, h_phil, h_pcso, h_maip, h_dswd, h_qfs, h_out],
        ['','','',h_caseone, h_casetwo],
        [h_hci]
    ]
    try:
        table_data.append([Paragraph('Dialysis Package', style_td), Paragraph(str("{:,.2f}".format(header['total'])), style_amt)])
    except:
        table_data.append([Paragraph('Dialysis Package', style_td), Paragraph(str("{:,.2f}".format(0)), style_amt)])
    hci_fee_cols += 1
    

    #HCI SUMMARY
    try:
        table_data.append([
            Paragraph('TOTAL(HCI Fees)', style_td), 
            Paragraph(str("{:,.2f}".format(header['total'])), style_amt), 
            Paragraph(str("{:,.2f}".format(sc_pwd)), style_amt),
            Paragraph(str("{:,.2f}".format(caseone)), style_amt),
            Paragraph(str("{:,.2f}".format(casetwo)), style_amt),
            Paragraph(str("{:,.2f}".format(pcso)), style_amt),
            Paragraph(str("{:,.2f}".format(maip)), style_amt),
            Paragraph(str("{:,.2f}".format(op)), style_amt),
            Paragraph(str("{:,.2f}".format(qfs)), style_amt),
            Paragraph(str("{:,.2f}".format(bal)), style_amt),
        ])
    except:
        table_data.append([
            Paragraph('TOTAL(HCI Fees)', style_td), 
            Paragraph(str("{:,.2f}".format(header['total'])), style_amt), 
            Paragraph(str("{:,.2f}".format(sc_pwd)), style_amt),
            Paragraph("0.00", style_amt),
            Paragraph(str("{:,.2f}".format(casetwo)), style_amt),
            Paragraph(str("{:,.2f}".format(pcso)), style_amt),
            Paragraph(str("{:,.2f}".format(maip)), style_amt),
            Paragraph(str("{:,.2f}".format(op)), style_amt),
            Paragraph(str("{:,.2f}".format(qfs)), style_amt),
            Paragraph(str("{:,.2f}".format(bal)), style_amt),
        ])

    hci_fee_cols += 1
    prof_header_cols = hci_fee_cols + 3
    #PROFFEE

    if header['prof']:
        table_data.append([h_prof])
        for i in header['prof']:
            if i['balance']:
                prof_balance = i['balance']
            else:
                prof_balance = 0.00
            if i['phicamount'] is not None:
                phicamount =  i['phicamount']
            else:
                phicamount = 0
            if i['pfsenior'] is not None:
                pfsc = i['pfsenior']
            else:
                pfsc = 0.00
            table_data.append([
                Paragraph(i['physician'], style_td),
                Paragraph(str("{:,.2f}".format(i['pfamt'])), style_amt),
                Paragraph(str("{:,.2f}".format(pfsc)), style_amt), 
                Paragraph(str("{:,.2f}".format(caseonepf)), style_amt), 
                Paragraph(str("{:,.2f}".format(casetwopf)), style_amt), 
                Paragraph(str(0.00), style_amt), 
                Paragraph(str(0.00), style_amt), 
                Paragraph(str(0.00), style_amt), 
                Paragraph(str("{:,.2f}".format(i['pfdisc'])), style_amt), 
                Paragraph(str("{:,.2f}".format(prof_balance)), style_amt)
            ])
        table_data.append([
            Paragraph('TOTAL(Prof Fee)', style_td), 
            Paragraph(str("{:,.2f}".format(prof_summary)), style_amt), 
            Paragraph(str("{:,.2f}".format(prof_sc)), style_amt),
            Paragraph(str("{:,.2f}".format(caseonepf)), style_amt),
            Paragraph(str("{:,.2f}".format(casetwopf)), style_amt),
            Paragraph(str(0.00), style_amt), 
            Paragraph(str(0.00), style_amt), 
            Paragraph(str(0.00), style_amt), 
            Paragraph(str("{:,.2f}".format(prof_qfs)), style_amt), 
            Paragraph(str("{:,.2f}".format(prof_sum_bal)), style_amt),
        ])

    #SUMMARY OF FEES
    table_data.append([h_summ_fee])
    table_data.append(
        [h_particulars, h_actual, h_sc_pwd, h_caseone, h_casetwo, h_pcso, h_maip, h_dswd, h_qfs, h_out]
    )

    table_data.append([
        Paragraph('TOTAL(HCI Fees)', style_td), 
        Paragraph(str("{:,.2f}".format(header['total'])), style_amt), 
        Paragraph(str("{:,.2f}".format(sc_pwd)), style_amt),
        Paragraph(str("{:,.2f}".format(caseone)), style_amt),
        Paragraph(str("{:,.2f}".format(casetwo)), style_amt),
        Paragraph(str("{:,.2f}".format(pcso)), style_amt),
        Paragraph(str("{:,.2f}".format(maip)), style_amt),
        Paragraph(str("{:,.2f}".format(op)), style_amt),
        Paragraph(str("{:,.2f}".format(qfs)), style_amt),
        Paragraph(str("{:,.2f}".format(bal)), style_amt),
    ])

    table_data.append([
            Paragraph('TOTAL(Prof Fee)', style_td), 
            Paragraph(str("{:,.2f}".format(prof_summary)), style_amt), 
            Paragraph(str("{:,.2f}".format(prof_sc)), style_amt),
            Paragraph(str("{:,.2f}".format(caseonepf)), style_amt),
            Paragraph(str("{:,.2f}".format(casetwopf)), style_amt),
            Paragraph(str("{:,.2f}".format(0)), style_amt), 
            Paragraph(str("{:,.2f}".format(0)), style_amt), 
            Paragraph(str("{:,.2f}".format(0)), style_amt), 
            Paragraph(str("{:,.2f}".format(prof_qfs)), style_amt), 
            Paragraph(str("{:,.2f}".format(prof_sum_bal)), style_amt),
    ])

    table_data.append([
            Paragraph('GRAND TOTAL', style_td), 
            Paragraph(str("{:,.2f}".format(header['total'] + prof_summary)), style_amt), 
            Paragraph(str("{:,.2f}".format(sc_pwd + prof_sc)), style_amt),
            Paragraph(str("{:,.2f}".format(caseone + caseonepf)), style_amt),
            Paragraph(str("{:,.2f}".format(casetwo + casetwopf)), style_amt),
            Paragraph(str("{:,.2f}".format(pcso)), style_amt),
            Paragraph(str("{:,.2f}".format(maip)), style_amt),
            Paragraph(str("{:,.2f}".format(op)), style_amt),
            Paragraph(str("{:,.2f}".format(qfs + prof_qfs)), style_amt),
            Paragraph(str("{:,.2f}".format(bal + prof_sum_bal)), style_amt),
        ])
    
    t = Table(table_data, colWidths=[1.5*inch, 0.7*inch, 0.8*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.8*inch])
    #locate column
    t.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONT', (0, 0), (-1, -1), 'Times-Roman', 8),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ADD8E6')),
        ('SPAN', (0, 2), (-1, 2)),
        ('SPAN', (3, 0), (4, 0)),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#e8f4f8')),
        ('BACKGROUND', (0, hci_fee_cols + 2), (-1, hci_fee_cols + 2), colors.HexColor('#ADD8E6')),
        ('SPAN', (0, prof_header_cols), (-1, prof_header_cols)),
        ('BACKGROUND', (0, prof_header_cols), (-1, prof_header_cols), colors.HexColor('#d4ebf2')),
        ('SPAN', (0, len(table_data) - 5 ), (-1, len(table_data) - 5)),
        ('BACKGROUND', (0, len(table_data) - 6 ), (-1, len(table_data) - 6), colors.HexColor('#d4ebf2')),
        ('BACKGROUND', (0, len(table_data) - 5 ), (-1, len(table_data) - 5), colors.HexColor('#e8f4f8')),
        ('BACKGROUND', (0, len(table_data) - 4 ), (-1, len(table_data) - 4), colors.HexColor('#ADD8E6')),
        ('BACKGROUND', (0, len(table_data) - 1 ), (-1, len(table_data) - 1), colors.HexColor('#d4ebf2')),
        ]))
    t.wrapOn(p, 0, 0)
    table_len = (len(table_data) * 0.2) + 1.4

    t.drawOn(p, 0.3*inch, (9 - table_len)*inch)

    p.setFont("Times-Roman", 9, leading=None)
    starting = 9 - table_len
    if phictype == "P" or phictype == "I":
        p.setFont("Times-Bold", 9, leading=None)
        p.setFillColor("red")
        p.drawString(6.8*inch, (starting - 0.15)*inch, "NO BALANCE BILLING")
        p.setFillColor("black")
        p.setFont("Times-Roman", 9, leading=None)
    p.drawString(1*inch, (starting - 0.3)*inch, "Please pay the amount of: ________________________________________________________________________________________")
    if bal + prof_sum_bal != 0:
        p.drawString(2.35*inch, (starting - 0.3)*inch, num2words(round(bal + prof_sum_bal, 2)).upper() + " PESOS ONLY")
    else:
        p.drawString(2.35*inch, (starting - 0.3)*inch, " xxx ")
    p.setFont("Times-Roman", 8, leading=None)

    p.drawString(5.5*inch, (starting - 0.6)*inch, "Official Receipt No.: _________________________")
    p.drawString(5.5*inch, (starting - 0.8)*inch, "Payment in Php       : _________________________")
    p.drawString(5.5*inch, (starting - 1)*inch, "Date                         : _________________________")
    p.setFont("Times-Bold", 9, leading=None)
    p.drawString(0.3*inch, (starting - 1.2)*inch, "PREPARED BY:")
    p.line(0.3*inch, (starting - 1.6) *inch, 3*inch, (starting - 1.6) *inch) #(x1, y1, x2, y2)
    p.drawString(5*inch, (starting - 1.2)*inch, "CONFORME:")
    p.line(5*inch, (starting - 1.6) *inch, 8*inch, (starting - 1.6) *inch) #(x1, y1, x2, y2)
    p.setFont("Times-Roman", 9, leading=None)
    p.drawString(1.3*inch, (starting - 1.8)*inch, "Billing Staff")
    p.drawString(0.9*inch, (starting - 1.55)*inch, request.session.get("name"))
    p.drawString(0.9*inch, (starting - 1.95)*inch, "(Signature over Printed Name)")

    p.drawString(0.3*inch, (starting - 2.2)*inch, "Contact Number : (054) 881-1033 Loc.304")
    p.drawString(0.3*inch, (starting - 2.4)*inch, "Date Signed        : " + soa_date)
    if conf_type == "":
        p.drawString(5.2*inch, (starting - 1.8)*inch, "Philhealth Member/Patient/Authorized Representative")
    elif conf_type == "PATIENT":
        p.drawString(6.3*inch, (starting - 1.8)*inch, "Patient")
    elif conf_type == "PHIC":
        p.drawString(6*inch, (starting - 1.8)*inch, "Philhealth Member")
    elif conf_type == "REP":
        p.drawString(5.9*inch, (starting - 1.8)*inch, "Authorized Representative")
        if conf_relation == '1':
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient : Spouse")
        elif conf_relation == '2':
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient : Child")
        elif conf_relation == '3':
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient : Parent")
        elif conf_relation == '4':
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient : Sibling")
        elif conf_relation == '5':
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient : Other")
        elif conf_relation == '6':
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient : Member")
        else:
            p.drawString(5*inch, (starting - 2.2)*inch, "Relation to Member/Patient: ")
    if conf_name != "":
        p.drawString(5.3*inch, (starting - 1.55)*inch, conf_name)    
    p.drawString(5.8*inch, (starting - 1.95)*inch, "(Signature over Printed Name)")
    p.drawString(5*inch, (starting - 2.4)*inch, "Contact Number                   : " + conf_contact)
    p.drawString(5*inch, (starting - 2.6)*inch, "Date Signed                          : " + conf_date_signed)

    p.line(0, 0.30*inch, 1000, 0.30*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Italic", 10, leading=None)
    p.drawString(0.3*inch, 0.15*inch, "BRGHGMC-F-FS-BIL-001")
    p.drawString(2.6*inch, 0.15*inch, "Rev. 9")
    p.drawString(3.8*inch, 0.15*inch, "Effectivity Date: May 02, 2023")
    p.drawImage(pagpadabalogo, 7.2*inch, 0.05*inch, mask='auto', width=80, height=13)
    p.setTitle("STATEMENT OF ACCOUNT")
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def print_patient_detailed_bill(request, enctr):
    encounter = enctr
    enctr = enctr.replace('-', '/')
    header_response = requests.post(detailed_soa_header_api, data={'enctr': enctr})
    header_json_response = header_response.json()
    if header_json_response['status'] == 'success':
        if header_json_response['data'] is None:
            enctr = enctr.replace('-', '/')
            header_response = requests.post(detailed_soa_header_api, data={'enctr': enctr})
            header_json_response = header_response.json()
            if header_json_response['status'] == 'success':
                header = header_json_response['data']
        else:
            header = header_json_response['data']

    if header['typecode'] == '027':
        return HttpResponseRedirect('/' + encounter + '/dialysisbill')

    final_diagnosis = ""
    other_diagnosis = ""
    physician = ""
    try:
        if header['patient'][0]['patsuffix']:
            suffix = header['patient'][0]['patsuffix']
        else:
            suffix = ""
    except:
        suffix = ""
        pass

    try:
        if header['diagnosis']:
            for i in header['diagnosis']:
                if i['primediag'] == 'Y':
                    final_diagnosis = i['diagtext'].upper()
                    physician = i['physician']
                else:
                    final_diagnosis = ""
                    physician = ""

                if i['tdcode'] == 'OTHER':
                    other_diagnosis = i['diagtext']
                else:
                    other_diagnosis = ""
    except:
        final_diagnosis = ""
        other_diagnosis = ""
        physician = ""
        pass

    try: 
        if header['philhealth']:
            firstcase = header['philhealth'][0]['firstcase']
            secondcase = header['philhealth'][0]['secondcase']
        else:
            firstcase = ""
            secondcase = ""
    except:
        firstcase = ""
        secondcase = ""
        pass
    try:
        if header['member_type']:
            phicnum = header['member_type'][0]['phicnum']
            mem_type = header['member_type'][0]['typedesc']
            phictype = header['member_type'][0]['phictypemem']
        else:
            phicnum = ""
            mem_type = ""
            phictype = ""
    except:
        phicnum = ""
        mem_type = ""
        phictype = ""
        pass

    toecode = ''
    if header['toecode'] == 'OPD':
        toecode = 'OUT-PATIENT'
    elif header['toecode'] == 'OPDAD':
        toecode = 'OUT-PATIENT'
    elif header['toecode'] == 'ER':
        toecode = 'EMERGENCY'
    elif header['toecode'] == 'ERADM':
        toecode = 'EMERGENCY'
    elif header['toecode'] == 'ADM':
        toecode = 'IN-PATIENT'

    try:
        soa_no = header['oth'][0]['soa_no']
        soa_date = header['oth'][0]['soa_date']
    except:
        soa_no = ""
        soa_date = datetime.today().strftime('%m-%d-%Y')
        pass 


    pdf = HtmlPdf()
    pdf.add_page()

    ext_final_diagnosis = ""

    page_header = """<table border='0' width='100%'>"""
    page_header += """<tr><td width='100%' align='center'><img height='80' width='550' src='http://173.10.7.2/medsys-static-files/integrated/img/page_header.png'></td></tr>"""
    page_header += """<tr><td width='100%'  align='center'><font size='9'><b>DETAILED STATEMENT OF ACCOUNT<b></font></td></tr>"""
    page_header += "<tr><td width='100%' align='right'><font size='8'>SOA No.: "+ soa_no +"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</font></td></tr>"
    page_header += "<tr><td width='60%' align='left'><font size='8'>NAME OF PATIENT &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: " + header['patient'][0]['patlast'] + ", " + header['patient'][0]['patfirst'] + " " +  header['patient'][0]['patmiddle'] + " " + suffix + "</font></td><td width='30%' align='left'><font size='8'>AGE &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; : " +  str(header['age']) + "</font></td><td width='10%' align='left'><font size='8'>DATE: "+ soa_date +"</font></td></tr>"
    page_header += "<tr><td width='60%' align='left'><font size='8'>ADDRESS &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: " + header['address'] + "</font></td><td width='30%' align='left'><font size='8'>BIRTHDATE &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: " +  str(header['patient'][0]['bday']) + "</font></td>"
    if toecode == 'IN-PATIENT':
        if header['details'][0]['date_discharged']:
            page_header += "<td width='10%' align='left'><font size='8'>No. of day/s:" + str(header['details'][0]['no_day']) + "</font></td></tr>"
        else:
            if header['details'][0]['no_days'] is not None:
                page_header += "<td width='10%' align='left'><font size='8'>No. of day/s: "+str(header['details'][0]['no_days'])+" days</font></td></tr>"   
            else:
                page_header += "<td width='10%' align='left'><font size='8'>No. of day/s:</font></td></tr>"
    page_header += "<tr><td width='60%' align='left'><font size='8'>&#09;</font></td><td width='40%' align='left'><font size='8'>DATE ADMITTED &nbsp&nbsp&nbsp: "+ header['details'][0]['date_admitted'] +" </font></td></tr>"
    if len(final_diagnosis) <= 45:
        page_header += "<tr><td width='60%' align='left'><font size='8'>FINAL DIAGNOSIS &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: "+ final_diagnosis +"</font></td>"
    else:
        page_header += "<tr><td width='60%' align='left'><font size='8'>FINAL DIAGNOSIS &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: "+ final_diagnosis[:45]+"...</font></td>"
        ext_final_diagnosis = final_diagnosis[46:]
    if header['details'][0]['date_discharged']:
        page_header += "<td width='40%' align='left'><font size='8'>DATE DISCHARGED: "+header['details'][0]['date_discharged'][:11]+"</font></td></tr>"
    else:
        x = datetime.now()
        page_header += "<td width='40%' align='left'><font size='8'>DATE DISCHARGED: "+ x.strftime("%b %d, %Y") +"</font></td></tr>"
    if ext_final_diagnosis != "":
        page_header += "<tr><td width='60%' align='left'><font size='8'>"+ext_final_diagnosis[:60]+"</font></td><td width='20%' align='left'><font size='8'>1ST CASE: "+ firstcase +"</font></td> <td width='20%' align='left'><font size='8'>HOSP. NO.: "+ header['patient'][0]['hpercode'] +"</font></td></tr>"
    else:
        page_header += "<tr><td width='60%' align='left'><font size='8'>&#09;</font></td><td width='20%' align='left'><font size='8'>1ST CASE &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:"+ firstcase +"</font></td> <td width='20%' align='left'><font size='9'>HOSP. NO.: "+ header['patient'][0]['hpercode'] +"</font></td></tr>"
    try:
        page_header += "<tr><td width='60%' align='left'><font size='8'>OTHER DIAGNOSIS &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:"+ other_diagnosis[:51] +"</font></td><td width='20%' align='left'><font size='8'>2ND CASE &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:"+ secondcase +"</font></td>"
    except:
        page_header += "<tr><td width='60%' align='left'><font size='8'>OTHER DIAGNOSIS &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:</font></td><td width='20%' align='left'><font size='8'>2ND CASE &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:</font></td>"
        pass
    if toecode == 'IN-PATIENT':
        if len(header['room_assign'][0]['wardname']) <= 15:
            page_header += "<td width='20%' align='left'><font size='8'>WARD &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: "+ header['room_assign'][0]['wardname'] +" </font></td>"
        else:
            page_header += "<td width='20%' align='left'><font size='8'>WARD &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: "+ header['room_assign'][0]['wardname'][:15] +"...</font></td>"
    else:
        page_header += "<td width='20%' align='left'><font size='8'>WARD &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: </font></td>"
    page_header += "</tr>"
    try:
        if header['mss'][0]['mssdesc']:
            page_header += "<tr><td width='60%' align='left'><font size='8'>&#09;</font></td><td width='20%' align='left'><font size='8'>MSS CLASS &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:"+ header['mss'][0]['mssdesc'] +"</font></td> <td width='20%' align='left'><font size='9'></font></td></tr>"
        else:
            page_header += "<tr><td width='60%' align='left'><font size='8'>&#09;</font></td><td width='20%' align='left'><font size='8'>MSS CLASS &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:</font></td> <td width='20%' align='left'><font size='9'></font></td></tr>"
    except:
        page_header += "<tr><td width='60%' align='left'><font size='8'>&#09;</font></td><td width='20%' align='left'><font size='8'>MSS CLASS &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:</font></td> <td width='20%' align='left'><font size='8'></font></td></tr>"
    page_header += "<tr><td width='60%' align='left'><font size='8'>ATTENDING PHYSICIAN  :"+ physician +"</font></td><td width='20%' align='left'><font size='8'>PHILHEALTH &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:"+ mem_type +"</font></td></tr>"
    page_header += "<tr><td width='60%' align='left'><font size='8'>&#09;</font></td><td width='20%' align='left'><font size='8'>PHILHEALTH NO. &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:"+ phicnum +"</font></td></tr>"
    page_header += """</table>"""

    overall = 0
    pdf.write_html(page_header)

    try:
        if header['rnb']:
            total_rm = 0
            rnb_table = '<font size="8">'
            rnb_table += """ <table border="1" cellpadding="5px">  <tr> <th width=120>Date</th> <th width=200>Charge Slip No.</th> <th width=100>Days</th> <th width=480>Particulars</th> <th width=130>Unit Cost</th> <th width=130>Amount</th></tr><tr><th align=left colspan='7'>Room and Board</th></tr>
            """
            for i in header['rnb']:
                if i['rmcharge'] is not None:
                    total_rm += i['rmcharge']
                if i['days'] is None:
                    days = '-'
                else:
                    days = str(i['days'])
             
                if i['rmrate'] is not None:
                    rate = str("{:,.2f}".format(i['rmrate']))
                else:
                    rate = '0'

                if i['rmcharge'] is not None:
                    charge = str("{:,.2f}".format(i['rmcharge']))
                else:
                    charge = '0'
                rnb_table += '<tr> <td width=120 align=center><font size="8">' + i['date'] + '</font></td> <td width=200 align=center><font size="8">-</font></td> <td width=100 align=center><font size="8">'+ days +'</font></td> <td width=480><font size="8">' + i['wardname'] + '</font></td> <td width=130 align=right><font size="8">'+ rate + '</font></td> <td width=130 align=right><font size="8">'+ charge +'</font></td> </tr>'
            rnb_table += '<tr> <td width=120>&nbsp</td> <td width=200>&nbsp</td> <td width=100>&nbsp</td> <td width=480>&nbsp</td> <td width=130 align=right><font size="9"><b>Total</b></font></td> <td width=130 align=right><font size="9"><b>'+ str("{:,.2f}".format(total_rm)) +'</b></font></td></tr></table>'
            pdf.write_html(rnb_table)
            overall += total_rm
    except:
        pass 

    try:
        if header['meds']:
            meds = []
            total_meds = 0
            meds_table = '<font size="8">'
            meds_table += """ <table border="1" cellpadding="5px">  <tr> <th width=120>Date</th> <th width=200>Charge Slip No.</th> <th width=100>Qty.</th> <th width=480>Particulars</th> <th width=130>Unit Cost</th> <th width=130>Amount</th> </tr> <tr><th align=left colspan='7'>Drugs and Medicine</th></tr>"""
            for i in header['meds']:
                if i not in meds:
                    meds.append(i)
            for i in meds:
                total_meds += i['pcchrgamt']
                if len(i['gendesc']) > 60:
                    particular = i['gendesc'][:60] + "..."
                else:
                    particular = i['gendesc']
                meds_table += '<tr> <td width=120 align=center><font size="8">' + i['date'] + '</font></td> <td width=200 align=center><font size="8">' + i['pcchrgcod'] +'</font></td> <td width=100 align=center><font size="8">'+ str(i['pchrgqty']) +'</font></td> <td width=480><font size="8">' + i['gendesc'] + '</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pchrgup'])) +'</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pcchrgamt'])) +'</font></td> </tr>'
            meds_table += '<tr> <td width=120>&nbsp</td> <td width=200>&nbsp</td> <td width=100>&nbsp</td> <td width=480>&nbsp</td> <td width=130 align=right><font size="9"><b>Total</b></font></td> <td width=130 align=right><font size="9"><b>' + str("{:,.2f}".format(total_meds)) + '</b></font></td></tr></table>'
            pdf.write_html(meds_table)
            overall += total_meds
    except:
        pass
    
    try:
        if header['medsup2']:
            total_medsup = 0
            medsup_table = '<font size="8">'
            medsup_table += """ <table border="1" cellpadding="5px"> <tr> <th width=120>Date</th> <th width=200>Charge Slip No.</th> <th width=100>Qty.</th> <th width=480>Particulars</th> <th width=130>Unit Cost</th> <th width=130>Amount</th> </tr> <tr><th align=left colspan='7'>Medical Supply</th></tr>"""
            for i in header['medsup2']:
                total_medsup += i['pcchrgamt']
                if len(i['cl2desc']) > 60:
                    particular = i['cl2desc'][:60] + "..."
                else:
                    particular = i['cl2desc'] 
                medsup_table += '<tr> <td width=120 align=center><font size="8">' + i['date'] + '</font></td> <td width=200 align=center><font size="8">' + i['pcchrgcod'] +'</font></td> <td width=100 align=center><font size="8">'+ str(i['pchrgqty']) +'</font></td> <td width=480><font size="8">' + particular + '</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pchrgup'])) +'</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pcchrgamt'])) +'</font></td> </tr>'
            medsup_table += '<tr> <td width=120>&nbsp</td> <td width=200>&nbsp</td> <td width=100>&nbsp</td> <td width=480>&nbsp</td> <td width=130 align=right><font size="9"><b>Total</b></font></td> <td width=130 align=right><font size="9"><b>' + str("{:,.2f}".format(total_medsup)) + '</b></font></td></tr></table>'
            pdf.write_html(medsup_table)
            overall += total_medsup
    except:
        pass
    try:
        if header['lab']:
            total_lab = 0
            lab_table = '<font size="8">'
            lab_table += """ <table border="1" cellpadding="5px">  <tr> <th width=120>Date</th> <th width=200>Charge Slip No.</th> <th width=100>Qty.</th> <th width=480>Particulars</th> <th width=130>Unit Cost</th> <th width=130>Amount</th> </tr> <tr><th align=left colspan='7'>Laboratory</th></tr>"""
            for i in header['lab']:
                total_lab += i['pcchrgamt']
                if len(i['procdesc']) > 60:
                    particular = i['procdesc'][:60] + "..."
                else:
                    particular = i['procdesc'] 
                lab_table += '<tr> <td width=120 align=center><font size="8">' + i['date'] + '</font></td> <td width=200 align=center><font size="8">' + i['pcchrgcod'] +'</font></td> <td width=100 align=center><font size="8">'+ str(i['pchrgqty']) +'</font></td> <td width=480><font size="8">' + particular + '</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pchrgup'])) +'</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pcchrgamt'])) +'</font></td> </tr>'
            lab_table += '<tr> <td width=120>&nbsp</td> <td width=200>&nbsp</td> <td width=100>&nbsp</td> <td width=480>&nbsp</td> <td width=130 align=right><font size="9"><b>Total</b></font></td> <td width=130 align=right><font size="9"><b>' + str("{:,.2f}".format(total_lab)) + '</b></font></td></tr></table>'
            pdf.write_html(lab_table)
            overall += total_lab
    except:
        pass
    try:
        if header['rad']:
            total_rad = 0
            rad_table = '<font size="8">'
            rad_table += """ <table border="1" cellpadding="5px"> <tr>  <th width=120>Date</th> <th width=200>Charge Slip No.</th> <th width=100>Qty.</th> <th width=480>Particulars</th> <th width=130>Unit Cost</th> <th width=130>Amount</th> </tr> <tr><th align=left colspan='7'>Xray/Ultrasound/2D Echo</th></tr><tr>"""
            for i in header['rad']:
                total_rad += int(i['pcchrgamt'])
                if len(i['procdesc']) > 60:
                    particular = i['procdesc'][:60] + "..."
                else:
                    particular = i['procdesc'] 
                rad_table += '<tr> <td width=120 align=center><font size="8">' + i['date'] + '</font></td> <td width=200 align=center><font size="8">' + i['pcchrgcod'] +'</font></td> <td width=100 align=center><font size="8">'+ str(i['pchrgqty']) +'</font></td> <td width=480><font size="8">' + particular + '</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pchrgup'])) +'</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pcchrgamt'])) +'</font></td> </tr>'
            rad_table += '<tr> <td width=120>&nbsp</td> <td width=200>&nbsp</td> <td width=100>&nbsp</td> <td width=480>&nbsp</td> <td width=130 align=right><font size="9"><b>Total</b></font></td> <td width=130 align=right><b><font size="9">' + str("{:,.2f}".format(total_rad)) + '</font></b></td></tr></table>'
            pdf.write_html(rad_table)
            overall += total_rad
    except:
        pass

    try:
        if header['mrict']:
            total_mrict = 0
            mrict_table = '<font size="8">'
            mrict_table += """ <table border="1" cellpadding="5px">  <tr> <th width=120>Date</th> <th width=200>Charge Slip No.</th> <th width=100>Qty.</th> <th width=480>Particulars</th> <th width=130>Unit Cost</th> <th width=130>Amount</th> </tr><tr><th align=left colspan='7'>MRI/CT Scan</th></tr>"""
            for i in header['mrict']:
                total_mrict += int(i['pcchrgamt'])
                if len(i['procdesc']) > 60:
                    particular = i['procdesc'][:60] + "..."
                else:
                    particular = i['procdesc'] 
                mrict_table += '<tr> <td width=120 align=center><font size="8">' + i['date'] + '</font></td> <td width=200 align=center><font size="8">' + i['pcchrgcod'] +'</font></td> <td width=100 align=center><font size="8">'+ str(i['pchrgqty']) +'</font></td> <td width=480><font size="8">' + particular + '</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pchrgup'])) +'</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pcchrgamt'])) +'</font></td> </tr>'
            mrict_table += '<tr> <td width=120>&nbsp</td> <td width=200>&nbsp</td> <td width=100>&nbsp</td> <td width=480>&nbsp</td> <td width=130 align=right><font size="9"><b>Total</b></font></td> <td width=130 align=right><font size="9"><b>' + str("{:,.2f}".format(total_mrict)) + '</b></font></td></tr></table>'
            pdf.write_html(mrict_table)
            overall += total_mrict
    except:
        pass

    try:
        if header['er']:
            total_er = 0
            er_table = '<font size="8">'
            er_table += """ <table border="1" cellpadding="5px">  <tr> <th width=120>Date</th> <th width=200>Charge Slip No.</th> <th width=100>Qty.</th> <th width=480>Particulars</th> <th width=130>Unit Cost</th> <th width=130>Amount</th> </tr><tr><th align=left colspan='7'>Emergency Room</th></tr>"""
            for i in header['er']:
                total_er += int(i['pcchrgamt'])
                if len(i['procdesc']) > 60:
                    particular = i['procdesc'][:60] + "..."
                else:
                    particular = i['procdesc'] 
                er_table += '<tr> <td width=120 align=center><font size="8">' + i['date'] + '</font></td> <td width=200 align=center><font size="8">' + i['pcchrgcod'] +'</font></td> <td width=100 align=center><font size="8">'+ str(i['pchrgqty']) +'</font></td> <td width=480><font size="8">' + particular + '</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pchrgup'])) +'</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pcchrgamt'])) +'</font></td> </tr>'
            er_table += '<tr> <td width=120>&nbsp</td> <td width=200>&nbsp</td> <td width=100>&nbsp</td> <td width=480>&nbsp</td> <td width=130 align=right><font size="9"><b>Total</b></font></td> <td width=130 align=right><font size="9"><b>' + str("{:,.2f}".format(total_er)) + '</b></font></td></tr></table>'
            pdf.write_html(er_table)
            overall += total_er
    except:
        pass
    
    try:
        if header['ordr']:
            total_ordr = 0
            or_table = '<font size="8">'
            or_table += """ <table border="1" cellpadding="5px">  <tr> <th width=120>Date</th> <th width=200>Charge Slip No.</th> <th width=100>Qty.</th> <th width=480>Particulars</th> <th width=130>Unit Cost</th> <th width=130>Amount</th> </tr><tr><th align=left colspan='7'>Operating/Emergency Room</th></tr>"""
            for i in header['ordr']:
                total_ordr += int(i['pcchrgamt'])
                if len(i['procdesc']) > 60:
                    particular = i['procdesc'][:60] + "..."
                else:
                    particular = i['procdesc'] 
                or_table += '<tr> <td width=120 align=center><font size="8">' + i['date'] + '</font></td> <td width=200 align=center><font size="8">' + i['pcchrgcod'] +'</font></td> <td width=100 align=center><font size="8">'+ str(i['pchrgqty']) +'</font></td> <td width=480><font size="8">' + particular + '</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pchrgup'])) +'</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pcchrgamt'])) +'</font></td> </tr>'
            or_table += '<tr> <td width=120>&nbsp</td> <td width=200>&nbsp</td> <td width=100>&nbsp</td> <td width=480>&nbsp</td> <td width=130 align=right><font size="9"><b>Total</b></font></td> <td width=130 align=right><font size="9"><b>' + str("{:,.2f}".format(total_ordr)) + '</b></font></td></tr></table>'
            pdf.write_html(or_table)
            overall += total_ordr
    except:
        pass
    try:
        if header['nursing']:
            total_nursing = 0
            nursing_table = '<font size="9">'
            nursing_table += """ <table border="1" cellpadding="5px">  <tr> <th width=120>Date</th> <th width=200>Charge Slip No.</th> <th width=100>Qty.</th> <th width=480>Particulars</th> <th width=130>Unit Cost</th> <th width=130>Amount</th> </tr><tr><th align=left colspan='7'>Nursing Care Procedure</th></tr>"""
            for i in header['nursing']:
                total_nursing += int(i['pcchrgamt'])
                if len(i['procdesc']) > 60:
                    particular = i['procdesc'][:60] + "..."
                else:
                    particular = i['procdesc'] 
                nursing_table += '<tr> <td width=120 align=center><font size="8">' + i['date'] + '</font></td> <td width=200 align=center><font size="8">' + i['pcchrgcod'] +'</font></td> <td width=100 align=center><font size="8">'+ str(i['pchrgqty']) +'</font></td> <td width=480><font size="8">' + particular + '</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pchrgup'])) +'</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pcchrgamt'])) +'</font></td> </tr>'
            nursing_table += '<tr> <td width=120>&nbsp</td> <td width=200>&nbsp</td> <td width=100>&nbsp</td> <td width=480>&nbsp</td> <td width=130 align=right><font size="9"><b>Total</b></font></td> <td width=130 align=right><font size="9"><b>' + str("{:,.2f}".format(total_nursing)) + '</b></font></td></tr></table>'
            pdf.write_html(nursing_table)
            overall += total_nursing
    except:
        pass
        
    try:
        if header['ecg']:
            total_ecg = 0
            ecg_table = '<font size="8">'
            ecg_table += """ <table border="1" cellpadding="5px">  <tr> <th width=120>Date</th> <th width=200>Charge Slip No.</th> <th width=100>Qty.</th> <th width=480>Particulars</th> <th width=130>Unit Cost</th> <th width=130>Amount</th> </tr><tr><th align=left colspan='7'>ECG</th></tr>"""
            for i in header['ecg']:
                total_ecg += int(i['pcchrgamt'])
                if len(i['procdesc']) > 60:
                    particular = i['procdesc'][:60] + "..."
                else:
                    particular = i['procdesc'] 
                ecg_table += '<tr> <td width=120 align=center><font size="8">' + i['date'] + '</font></td> <td width=200 align=center><font size="8">' + i['pcchrgcod'] +'</font></td> <td width=100 align=center><font size="8">'+ str(i['pchrgqty']) +'</font></td> <td width=480><font size="8">' + particular + '</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pchrgup'])) +'</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pcchrgamt'])) +'</font></td> </tr>'
            ecg_table += '<tr> <td width=120>&nbsp</td> <td width=200>&nbsp</td> <td width=100>&nbsp</td> <td width=480>&nbsp</td> <td width=130 align=right><font size="9"><b>Total</b></font></td> <td width=130 align=right><font size="8"><b>' + str("{:,.2f}".format(total_ecg)) + '</b></font></td></tr></table>'
            pdf.write_html(ecg_table)
            overall += total_ecg
    except:
        pass
        
    try:
        if header['pt']:
            total_pt = 0
            pt_table = '<font size="8">'
            pt_table += """ <table border="1" cellpadding="5px">  <tr> <th width=120>Date</th> <th width=200>Charge Slip No.</th> <th width=100>Qty.</th> <th width=480>Particulars</th> <th width=130>Unit Cost</th> <th width=130>Amount</th> </tr><tr><th align=left colspan='7'>Physical Therapy</th></tr>"""
            for i in header['pt']:
                total_pt += int(i['pcchrgamt'])
                if len(i['procdesc']) > 60:
                    particular = i['procdesc'][:60] + "..."
                else:
                    particular = i['procdesc'] 
                pt_table += '<tr> <td width=120 align=center><font size="8">' + i['date'] + '</font></td> <td width=200 align=center><font size="8">' + i['pcchrgcod'] +'</font></td> <td width=100 align=center><font size="8">'+ str(i['pchrgqty']) +'</font></td> <td width=480><font size="8">' + particular + '</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pchrgup'])) +'</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pcchrgamt'])) +'</font></td> </tr>'
            pt_table += '<tr> <td width=120>&nbsp</td> <td width=200>&nbsp</td> <td width=100>&nbsp</td> <td width=480>&nbsp</td> <td width=130 align=right><font size="9"><b>Total</b></font></td> <td width=130 align=right><font size="8"><b>' + str("{:,.2f}".format(total_pt)) + '</b></font></td></tr></table>'
            pdf.write_html(pt_table)
            overall += total_pt
    except:
        pass

        
    try:
        if header['dialysis']:
            total_dialysis = 0
            dialysis_table = '<font size="8">'
            dialysis_table += """ <table border="1" cellpadding="5px">  <tr> <th width=120>Date</th> <th width=200>Charge Slip No.</th> <th width=100>Qty.</th> <th width=480>Particulars</th> <th width=130>Unit Cost</th> <th width=130>Amount</th> </tr><tr><th align=left colspan='7'>Nursing Care Procedure</th></tr>"""
            for i in header['dialysis']:
                total_dialysis += int(i['pcchrgamt'])
                if len(i['procdesc']) > 60:
                    particular = i['procdesc'][:60] + "..."
                else:
                    particular = i['procdesc'] 
                dialysis_table += '<tr> <td width=120 align=center><font size="8">' + i['date'] + '</font></td> <td width=200 align=center><font size="8">' + i['pcchrgcod'] +'</font></td> <td width=100 align=center><font size="8">'+ str(i['pchrgqty']) +'</font></td> <td width=480><font size="8">' + particular + '</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pchrgup'])) +'</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pcchrgamt'])) +'</font></td> </tr>'
            dialysis_table += '<tr> <td width=120>&nbsp</td> <td width=200>&nbsp</td> <td width=100>&nbsp</td> <td width=480>&nbsp</td> <td width=130 align=right><font size="9"><b>Total</b></font></td> <td width=130 align=right><font size="9"><b>' + str("{:,.2f}".format(total_dialysis)) + '</b></font></td></tr></table>'
            pdf.write_html(dialysis_table)
            overall += total_dialysis
    except:
        pass

    try:
        if header['abtc']:
            total_abtc = 0
            abtc_table = '<font size="8">'
            abtc_table += """ <table border="1" cellpadding="5px">  <tr> <th width=120>Date</th> <th width=200>Charge Slip No.</th> <th width=100>Qty.</th> <th width=480>Particulars</th> <th width=130>Unit Cost</th> <th width=130>Amount</th> </tr><tr><th align=left colspan='7'>ABTC</th></tr>"""
            for i in header['abtc']:
                total_abtc += int(i['pcchrgamt'])
                if len(i['procdesc']) > 60:
                    particular = i['procdesc'][:60] + "..."
                else:
                    particular = i['procdesc'] 
                abtc_table += '<tr> <td width=120 align=center><font size="8">' + i['date'] + '</font></td> <td width=200 align=center><font size="8">' + i['pcchrgcod'] +'</font></td> <td width=100 align=center><font size="8">'+ str(i['pchrgqty']) +'</font></td> <td width=480><font size="8">' + particular + '</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pchrgup'])) +'</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pcchrgamt'])) +'</font></td> </tr>'
            abtc_table += '<tr> <td width=120>&nbsp</td> <td width=200>&nbsp</td> <td width=100>&nbsp</td> <td width=480>&nbsp</td> <td width=130 align=right><font size="9"><b>Total</b></font></td> <td width=130 align=right><font size="9"><b>' + str("{:,.2f}".format(total_abtc)) + '</b></font></td></tr></table>'
            pdf.write_html(abtc_table)
            overall += total_abtc
    except:
        pass

    try:
        if header['nbs']:
            total_nbs = 0
            nbs_table = '<font size="8">'
            nbs_table += """ <table border="1" cellpadding="5px">  <tr> <th width=120>Date</th> <th width=200>Charge Slip No.</th> <th width=100>Qty.</th> <th width=480>Particulars</th> <th width=130>Unit Cost</th> <th width=130>Amount</th> </tr><tr><th align=left colspan='7'>New Born Screening</th></tr>"""
            for i in header['nbs']:
                total_nbs += int(i['pcchrgamt'])
                if len(i['procdesc']) > 60:
                    particular = i['procdesc'][:60] + "..."
                else:
                    particular = i['procdesc'] 
                nbs_table += '<tr> <td width=120 align=center><font size="8">' + i['date'] + '</font></td> <td width=200 align=center><font size="8">' + i['pcchrgcod'] +'</font></td> <td width=100 align=center><font size="8">'+ str(i['pchrgqty']) +'</font></td> <td width=480><font size="8">' + particular + '</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pchrgup'])) +'</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pcchrgamt'])) +'</font></td> </tr>'
            nbs_table += '<tr> <td width=120>&nbsp</td> <td width=200>&nbsp</td> <td width=100>&nbsp</td> <td width=480>&nbsp</td> <td width=130 align=right><font size="9"><b>Total</b></font></td> <td width=130 align=right><font size="9"><b>' + str("{:,.2f}".format(total_nbs)) + '</b></font></td></tr></table>'
            pdf.write_html(nbs_table)
            overall += total_nbs
    except:
        pass

    try:
        if header['nbh']:
            total_nbh = 0
            nbh_table = '<font size="8">'
            nbh_table += """ <table border="1" cellpadding="5px">  <tr> <th width=120>Date</th> <th width=200>Charge Slip No.</th> <th width=100>Qty.</th> <th width=480>Particulars</th> <th width=130>Unit Cost</th> <th width=130>Amount</th> </tr><tr><th align=left colspan='7'>New Born Hearing Test</th></tr>"""
            for i in header['nbh']:
                total_nbh += int(i['pcchrgamt'])
                if len(i['procdesc']) > 60:
                    particular = i['procdesc'][:60] + "..."
                else:
                    particular = i['procdesc'] 
                nbh_table += '<tr> <td width=120 align=center><font size="8">' + i['date'] + '</font></td> <td width=200 align=center><font size="8">' + i['pcchrgcod'] +'</font></td> <td width=100 align=center><font size="8">'+ str(i['pchrgqty']) +'</font></td> <td width=480><font size="8">' + particular + '</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pchrgup'])) +'</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pcchrgamt'])) +'</font></td> </tr>'
            nbh_table += '<tr> <td width=120>&nbsp</td> <td width=200>&nbsp</td> <td width=100>&nbsp</td> <td width=480>&nbsp</td> <td width=130 align=right><font size="9"><b>Total</b></font></td> <td width=130 align=right><font size="9"><b>' + str("{:,.2f}".format(total_nbh)) + '</b></font></td></tr></table>'
            pdf.write_html(nbh_table)
            overall += total_nbh
    except:
        pass

    try:
        if header['amb']:
            total_amb = 0
            amb_table = "<font size='8'>"
            amb_table += """ <table border="1" cellpadding="5px">  <tr> <th width=120>Date</th> <th width=200>Charge Slip No.</th> <th width=100>Qty.</th> <th width=480>Particulars</th> <th width=130>Unit Cost</th> <th width=130>Amount</th> </tr><tr><th align=left colspan='7'>Ambulance Fee</th></tr>"""
            for i in header['amb']:
                total_amb += int(i['pcchrgamt'])
                if len(i['procdesc']) > 60:
                    particular = i['procdesc'][:60] + "..."
                else:
                    particular = i['procdesc'] 
                amb_table += '<tr> <td width=120 align=center><font size="8">' + i['date'] + '</font></td> <td width=200 align=center><font size="8">' + i['pcchrgcod'] +'</font></td> <td width=100 align=center><font size="8">'+ str(i['pchrgqty']) +'</font></td> <td width=480><font size="8">' + particular + '</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pchrgup'])) +'</font></td> <td width=130 align=right><font size="8">'+ str("{:,.2f}".format(i['pcchrgamt'])) +'</font></td> </tr>'
            amb_table += '<tr> <td width=120>&nbsp</td> <td width=200>&nbsp</td> <td width=100>&nbsp</td> <td width=480>&nbsp</td> <td width=130 align=right><font size="9"><b>Total</b></font></td> <td width=130 align=right><font size="9"><b>' + str("{:,.2f}".format(total_amb)) + '</b></font></td></tr></table>'
            pdf.write_html(amb_table)
            overall += total_amb
    except:
        pass

    total = "<table border='0' width='100%'><tr><td width='60%'><font size='9'>&nbsp</font></td> <td width='20%' align='right'><font size='10'><b>Total</b></font></td> <td width='20%' align='right'><font size='10'><b>"+str("{:,.2f}".format(overall))+"</b></font></td></tr></table>"
    pdf.write_html(total)
    
    footer = "<table border='0' width='100%'><tr><td width='20%'><font size='9'>Prepared by:</font></td> <td width='80%'>&nbsp</td></tr>"
    footer += "<tr><td width='20%'>&nbsp</td><td width='80%'><font size='9'></font></td></tr>"
    #footer += "<tr><td width='20%'>&nbsp</td><td width='80%'><font size='9'>" + request.session.get("name") + "</font></td></tr>"
    footer += "</table>"
    pdf.write_html(footer)
    response = HttpResponse(pdf.output(dest='S').encode('latin-1'))
    response['Content-Type'] = 'application/pdf'
    return response

def discounts(request):
    if request.session.get('employee_id') is not None:
        patient_response = requests.get(all_patients_api)
        patient_json_response = patient_response.json()
        if patient_json_response['status'] == 'success':
            for i in patient_json_response['data']:
                i['enccode'] = i['enccode'].replace('/', '-')
            patients = patient_json_response['data']
        return render(request, 'integrated/discount/discount.html', {'page': 'Patient Discount', 'user_level': request.session['user_level'], 'name': request.session['name'], 'patients': patients})
    else:
        return render(request, 'integrated/login/html', {'page': 'Login'})

def add(*p):
    return sum(filter(None, p))

def patient_discount(request, enctr):
    enctr = enctr.replace('-', '/')
    encounter = enctr.replace('/', '-')
    if request.session.get('employee_id') is not None:
        header_response = requests.post(soa_header_api, data={'enctr': enctr})
        header_json_response = header_response.json()
        if header_json_response['status'] == 'success':
            if header_json_response['data'] is None:
                enctr = enctr.replace('-', '/')
                header_response = requests.post(soa_header_api, data={'enctr': enctr})
                header_json_response = header_response.json()
                if header_json_response['status'] == 'success':
                    header = header_json_response['data']
            else:
                header = header_json_response['data']
        hosp_summary = add(header['rnb'], header['meds'], header['medsup'], header['lab'], header['rad'], header['mrict'], header['er'], header['ordr'], header['nursing'], header['ecg'], header['pt'], header['dialysis']) 
        prof_summary = 0
        srdisc = 0
        qfsdisc = 0
        if header['prof']:
            for i in header['prof']:
                prof_summary += i['pftotamt']
                if i['pfsenior'] is not None:
                    srdisc += i['pfsenior']
                qfsdisc += i['pfdisc']
        else:
            prof_summary = 0
        prof_bal = prof_summary

        bal = hosp_summary

        try:
            if header['philhealth']:
                bal -= header['philhealth'][0]['amthosp1']
                prof_bal -= header['philhealth'][0]['amtpf1']
        except:
            pass
        prof_bal -= srdisc
        prof_bal -= qfsdisc
        try:
            if header['disc']:
                for i in header['disc']:
                    bal -= bal * 0.2
        except:
            pass
        try:
            if header['othdisc']:
                for i in header['othdisc']:
                    bal -= i['amount']
        except:
            pass
        try:
            if header['pdaf']:
                for i in header['pdaf']:
                    bal -= i['amount']
        except:
            pass
        
        return render(request, 'integrated/discount/patient_discount.html', {'page': 'Patient Discount', 'user_level': request.session['user_level'], 'name': request.session['name'], 'header': header, 'summ': hosp_summary, 'prof_summ': prof_summary, 'enctr': encounter, 'bal': bal, 'prof_bal': prof_bal, 'prof': header['prof']})
    else:
        return render(request, 'integrated/login/html', {'page': 'Login'})

def add_discount(request, enctr, hpercode):
    if request.method == 'POST':
        enctr = enctr.replace('-', '/')
        disc_type = request.POST.get("disc-type")
        disc_amount = request.POST.get("disc-amount")
        response = requests.post(add_discount_api, data={'enccode': enctr, 'hpercode': hpercode, 'type': disc_type, 'amount': disc_amount, 'encoder': request.session.get('employee_id')})
        return HttpResponseRedirect('/' + enctr.replace('/', '-') + '/patient_discount')

def add_pf_discount(request, enctr):
    licno = request.POST.get('physician')
    disc_type = request.POST.get('disc-type')
    disc_amount = request.POST.get('disc-amount') 
    response = requests.post(add_pf_discount_api, data={'enccode': enctr, 'licno': licno, 'type': disc_type, 'amount': disc_amount}).json()
    return HttpResponseRedirect('/' + enctr.replace('/', '-') + '/patient_discount')

def del_pf_discount(request, enctr, licno, type):
    response = requests.post(delete_pf_discount_api, data={'enccode': enctr, 'licno': licno, 'type': type}).json()
    return HttpResponseRedirect('/' + enctr.replace('/', '-') + '/patient_discount')

def delete_discount(request, enctr, disc_type):
    if request.session.get('employee_id') is not None:
        enctr = enctr.replace('-', '/')
        response = requests.post(delete_discount_api, data={'enccode': enctr, 'type': disc_type})
        response_json = response.json()
        return HttpResponseRedirect('/' + enctr.replace('/', '-') + '/patient_discount')
    else:
        return HttpResponseRedirect('/')

def patient_encounter(request, hpercode, page):
    if request.session.get('employee_id') is not None:
        response = requests.post(consultation_list_api, data={'hospital_no': hpercode})
        response_json = response.json()
        if response_json['status'] == 'success':
            for i in response_json['data']:
                i['date'] =  datetime.strptime(i['date'][:10], '%Y-%m-%d')
                i['enccode'] = i['enccode'].replace('/', '-')
            encounters = response_json['data']
        else:
            encounters = []
        if page == 'Billing':
            return render(request, 'integrated/encounter_list.html', {'page': 'Billing', 'user_level': request.session['user_level'], 'name': request.session['name'], 'encounters': encounters, 'page': page})
        elif page == 'Radiology':
            return render(request, 'integrated/encounter_list.html', {'page': 'Radiology', 'user_level': request.session['user_level'], 'name': request.session['name'], 'encounters': encounters, 'page': page})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def patient_diagnosis(request, enctr):
    if request.session.get('employee_id') is not None:
        encounter = enctr.replace('-', '/')
        diagnosis = []
        if request.method == 'POST':
            diag_type = request.POST.get('diag-type')
            diagnosis = request.POST.get('diagnosis')
            physician = request.POST.get('physician')
            primary = request.POST.get('primary')
            remarks = request.POST.get('remarks')
            add_diagnosis = requests.post(add_diagnosis_api, data={'enccode': encounter, 'type': diag_type, 'diagnosis': diagnosis, 'physician': physician, 'primary': primary, 'remarks': remarks, 'encoder': request.session.get('employee_id')})
            diag_response = add_diagnosis.json()
        response = requests.post(patient_diagnosis_api, data={'encounter_no': encounter})
        json_response = response.json()
        if json_response['status'] == 'success':
            if json_response['data'] is None:
                encounter = enctr
                response = requests.post(patient_diagnosis_api, data={'encounter_no': encounter})
                json_response = response.json()
                if json_response['status'] == 'success':
                    diagnosis = json_response['data']
            else:
                diagnosis = json_response['data']
        doctor_response = requests.get(doctors_list_api)
        doctor_json_response = doctor_response.json()
        if doctor_json_response['status'] == 'success':
            doctor_list = doctor_json_response['data']
        else:
            doctor_list = []
        patient_details = requests.post(patient_details_by_enc_api, data={'enccode': encounter}).json()["data"]
        return render(request, 'integrated/patient_diagnosis.html', {'page': 'Patient Diagnosis', 'user_level': request.session['user_level'], 'name': request.session['name'], 'encounters': enctr, 'diagnosis': diagnosis, 'doctor_list': doctor_list, 'patient': patient_details})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def delete_diagnosis(request, enctr, uid):
    delete = requests.post(delete_diagnosis_api, data={'enccode': enctr, 'uid': uid}).json()["status"]
    if delete == 'success':
        return HttpResponseRedirect('/' + enctr + '/diagnosis')

def caserate(request, enctr):
    if request.session.get('employee_id') is not None:
        encounter = enctr.replace('-', '/')
        msg = ""
        if request.method == 'POST':
            caserate = request.POST.get("caserate")
            typ = request.POST.get("type")
            addcase = requests.post(add_case_rate_api, data={'enccode': encounter, 'type': typ, 'caserate': caserate})
            response = addcase.json()
            if response["status"] == "success":
                msg = "Case Rate added"
            else:
                msg = response["message"]
        patient_details = requests.post(patient_details_by_enc_api, data={'enccode': encounter}).json()["data"]
        patient_case_rate = requests.post(patient_case_rate_api, data={'enccode': encounter}).json()["data"]
        first_case_rate = requests.post(first_case_api).json()["data"]
        second_case_rate = requests.post(second_case_api).json()["data"]
        return render(request, 'integrated/caserate.html', {'page': 'Case Rate', 'user_level': request.session['user_level'], 'name': request.session['name'], 'patient': patient_details, 'patient_case_rate': patient_case_rate, 'first_case_rate': first_case_rate, 'second_case_rate': second_case_rate, 'encounter': enctr, 'msg': msg})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def deletecaserate(request, enctr, typ):
    if request.session.get('employee_id') is not None:
        encounter = enctr.replace('-', '/')
        deletecase = requests.post(delete_case_rate_api, data={'enccode': encounter, 'type': typ}).json()
        return HttpResponseRedirect('/' + enctr + '/caserate')
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def proffee(request, enctr):
    if request.session.get('employee_id') is not None:
        encounter = enctr.replace('-', '/')
        msg = ""
        if request.method == 'POST':
            caserate = request.POST.get("caserate")
            typ = request.POST.get("type")
            addcase = requests.post(add_case_rate_api, data={'enccode': encounter, 'type': typ, 'caserate': caserate})
            response = addcase.json()
            if response["status"] == "success":
                msg = "Case Rate added"
            else:
                msg = response["message"]
        patient_details = requests.post(patient_details_by_enc_api, data={'enccode': encounter}).json()["data"]
        profee = requests.post(patient_proffee_api, data={'enccode': encounter}).json()["data"]
        return render(request, 'integrated/proffee.html', {'page': 'Professiona Fee', 'user_level': request.session['user_level'], 'name': request.session['name'], 'patient': patient_details, 'msg': msg, 'proffee': profee, 'encounter': enctr})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def addProffee(request, enctr):
    if request.session.get('employee_id') is not None:
        encounter = enctr.replace('-', '/')
        amount = 0
        msg = ""
        if request.method == 'POST':
            physician = request.POST.get("physician")
            amount = request.POST.get("amount")
            add_proffee = requests.post(add_proffee_api, data={'enccode': encounter, 'licno': physician, 'amount': amount, 'employeeid': request.session['employee_id']}).json()["status"]
            if add_proffee == 'success':
                msg = "Data added successfully"
                return HttpResponseRedirect('/' + enctr + '/proffee')
            else:
                msg = "Database error occured"
        patient_details = requests.post(patient_details_by_enc_api, data={'enccode': encounter}).json()["data"]
        patient_case_rate = requests.post(patient_case_rate_api, data={'enccode': encounter}).json()["data"]
        physician = requests.get(doctors_list_api).json()["data"]
        for i in patient_case_rate:
            amount = i['amtpf1'] + i['amtpf2']
        return render(request, 'integrated/add_proffee.html', {'page': 'Professional Fee', 'user_level': request.session['user_level'], 'name': request.session['name'], 'patient': patient_details, 'msg': msg, 'physician': physician, 'encounter': enctr, 'amount': amount})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def deleteProffee(request, enctr, licno):
    if request.session.get('employee_id') is not None:
        encounter = enctr.replace('-', '/')
        delete = requests.post(delete_proffee_api, data={'enccode': encounter, 'licno': licno}).json()["status"]
        if delete == 'success':
            return HttpResponseRedirect('/' + enctr + '/proffee')
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def charges(request, enctr):
    encounter = enctr
    enctr = enctr.replace('-', '/')
    if request.session.get('employee_id') is not None:
        header_response = requests.post(detailed_soa_header_api, data={'enctr': enctr})
        header_json_response = header_response.json()
        if header_json_response['status'] == 'success':
            if header_json_response['data'] is None:
                enctr = enctr.replace('-', '/')
                header_response = requests.post(detailed_soa_header_api, data={'enctr': enctr})
                header_json_response = header_response.json()
                if header_json_response['status'] == 'success':
                    header = header_json_response['data']
            else:
                header = header_json_response['data']
    
        try:
            if header['abtc']:
                abtc = header['abtc'][0]['pcchrgamt'] 
            else:
                abtc = 0
        except:
            abtc = 0


        try:
            if header['nbs']:
                nbs = header['nbs'][0]['pcchrgamt'] 
            else:
                nbs = 0                
        except:
            nbs = 0

        try:
            if header['nbh']:
                nbh = header['nbh'][0]['pcchrgamt']
            else:
                nbh = 0
        except:
            nbh = 0

        try:
            if header['amb']:
                amb = header['amb'][0]['pcchrgamt']
            else:
                amb = 0
        except:
            amb = 0

        toecode = ''
        if header['toecode'] == 'OPD':
            toecode = 'OUT-PATIENT'
        elif header['toecode'] == 'OPDAD':
            toecode = 'OUT-PATIENT'
        elif header['toecode'] == 'ER':
            toecode = 'EMERGENCY'
        elif header['toecode'] == 'ERADM':
            toecode = 'EMERGENCY'
        elif header['toecode'] == 'ADM':
            toecode = 'IN-PATIENT'
        
        try:
            if header['rad']:
                for i in header['rad']:
                    i['enccode'] = i['enccode'].replace('/', '-')
        except:
            pass

        try:
            if header['meds']:
                for i in header['meds']:
                    i['enccode'] = i['enccode'].replace('/', '-')
        except:
            pass

        try:
            if header['medsup']:
                for i in header['medsup']:
                    i['enccode'] = i['enccode'].replace('/', '-')
        except:
            pass

        try:
            if header['lab']:
                for i in header['lab']:
                    i['enccode'] = i['enccode'].replace('/', '-')
        except:
            pass

        try:
            if header['ultra']:
                for i in header['ultra']:
                    i['enccode'] = i['enccode'].replace('/', '-')
        except:
            pass

        try:
            if header['echo']:
                for i in header['echo']:
                    i['enccode'] = i['enccode'].replace('/', '-')
        except:
            pass

        try:
            if header['nursing']:
                for i in header['nursing']:
                    i['enccode'] = i['enccode'].replace('/', '-')
        except:
            pass

        try:
            if header['misc']:
                for i in header['misc']:
                    i['enccode'] = i['enccode'].replace('/', '-')
        except:
            pass

        try:
            if header['mrict']:
                for i in header['mrict']:
                    i['enccode'] = i['enccode'].replace('/', '-')
        except:
            pass

        try:
            if header['er']:
                for i in header['er']:
                    i['enccode'] = i['enccode'].replace('/', '-')
        except:
            pass

        try:
            if header['ordr']:
                for i in header['ordr']:
                    i['enccode'] = i['enccode'].replace('/', '-')
        except:
            pass

        try:
            if header['ecg']:
                for i in header['ecg']:
                    i['enccode'] = i['enccode'].replace('/', '-')
        except:
            pass

        try:
            if header['pt']:
                for i in header['pt']:
                    i['enccode'] = i['enccode'].replace('/', '-')
        except:
            pass

        try:
            if header['dialysis']:
                for i in header['dialysis']:
                    i['enccode'] = i['enccode'].replace('/', '-')
        except:
            pass

        try:
            if header['abtc']:
                for i in header['abtc']:
                    i['enccode'] = i['enccode'].replace('/', '-')
        except:
            pass

        try:
            if header['nbs']:
                for i in header['nbs']:
                    i['enccode'] = i['enccode'].replace('/', '-')
        except:
            pass

        try:
            if header['nbh']:
                for i in header['nbh']:
                    i['enccode'] = i['enccode'].replace('/', '-')
        except:
            pass
        return render(request, 'integrated/billing/charges.html', {'page': 'Billing', 'user_level': request.session['user_level'], 'name': request.session['name'], 'header': header, 'encounter': encounter, 'toecode': toecode})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def editcharges(request, chargecode, type, enctr):
    encounter = enctr
    msg = ''
    enctr = enctr.replace('-', '/')
    if request.session.get('employee_id') is not None:
        if request.method == "POST":
            qty = request.POST.get('qty')
            amount = request.POST.get('amount')
            update = requests.post(update_charges_api, data={'chargecode': chargecode, 'enccode': enctr, 'qty': qty, 'amount': amount}).json()
            msg = "Charges updated successfully"
        data = requests.post(get_charges_api, data={'chargecode': chargecode, 'type': type, 'enccode': enctr}).json()
        if data['status'] == "success":
            charges = data['data']['result']
        else:
            charges = []
        return render(request, 'integrated/billing/edit_charges.html', {'page': 'Billing', 'user_level': request.session['user_level'], 'name': request.session['name'], 'chargecode': chargecode, 'charges': charges, 'type': type, 'enctr': encounter, 'msg': msg})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def deletecharges(request, chargecode, enctr):
    encounter = enctr
    enctr = enctr.replace('-', '/')
    if request.session.get('employee_id') is not None:
        delete = requests.post(delete_charges_api,data={'enccode': enctr, 'chargecode': chargecode}).json()
        if delete['status'] == "success":
            return HttpResponseRedirect('/' + encounter + "/charges")
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def newcharges(request, enctr):
    encounter = enctr
    enctr = enctr.replace('-', '/')
    if request.session.get('employee_id') is not None:
        items = requests.post(get_chargelist_api).json()['data']
        patient_details = requests.post(patient_details_by_enc_api, data={'enccode': enctr}).json()["data"]
        charges = requests.post(load_charges_api, data={'enccode': enctr}).json()["data"]
        return render(request, 'integrated/billing/new_charges.html', {'page': 'Billing', 'user_level': request.session['user_level'], 'name': request.session['name'], 'enctr': encounter, 'patient_details': patient_details, 'items': items, 'charges': charges})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def addCharges(request):
    ex = request.GET.get("exam", None)
    enctr = request.GET.get("enctr", None)
    rate = request.GET.get("rate", None)
    add = requests.post(add_charges_api, data={'enc': enctr, 'exam': ex, 'encoder': request.session['employee_id'], 'rate': rate}).json()["status"]
    return HttpResponse(json.dumps(add))

def load_all_charges(request, enctr):
    charges = requests.post(load_charges_api, data={'enccode': enctr}).json()["data"]
    return render(request, 'integrated/billing/reload_charges.html', {'charges': charges, 'enctr': enctr})

def delCharges(request):
    docint = request.GET.get("intkey", None)
    delete = requests.post(del_charges_api, data={'docintkey': docint}).json()["status"]
    return HttpResponse(json.dumps(delete))

def pharmacy(request):
    if request.session.get('employee_id') is not None:
        patient_list = requests.post(pha_patient_api).json()["data"]
        plist = []
        for i in patient_list:
            i['enccode'] = i['enccode'].replace('/', '-')
            if i not in plist:
                plist.append(i)
        return render(request, 'integrated/pharmacy/index.html', {'page': 'Pharmacy', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': plist})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def load_prescription(request, enctr):
    prescription = requests.post(pha_prescription_api, data={'enccode': enctr}).json()["data"]
    return render(request, 'integrated/pharmacy/prescription.html', {'list': prescription, 'enctr': enctr})

def release_meds(request):
    uid = request.GET.getlist("arr[]")
    release = requests.post(pha_release_prescription_api, data={'uids': uid, 'len': len(uid)}).json()["status"]
    return HttpResponse(json.dumps(release))

def undo_meds(request):
    uid = request.GET.get("uid")
    undo = requests.post(pha_undo_prescription_api, data={'uid': uid}).json()["status"]
    return HttpResponse(json.dumps(undo))

def print_prescription(request, enctr):
    enctr = enctr.replace('-', '/')
    patient_details = requests.post(patient_details_by_enc_api, data={'enccode': enctr}).json()["data"]
    patient_address = requests.post(patient_address_api, data={'no': patient_details[0]['hpercode']}).json()["data"]
    age = requests.post(age_api, data={'enccode': enctr, 'toecode': patient_details[0]['toecode']}).json()["data"]
    md = requests.post(pres_md_api, data={'enccode': enctr}).json()["data"]
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    #logo = ImageReader(static_root + '/static/integrated/img/brghgmclogo.png')
    response = HttpResponse(content_type='application/pdf')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setPageSize((8.5*inch, 6.5*inch))
    #p.drawImage(logo, 0.5*inch, 5.6*inch, mask='auto', width=64, height=64)
    p.setFont("Times-Roman", 11, leading=None)
    p.setFillColor("green")
    p.drawString(2.5*inch, 6.3*inch, "Bicol Region General Hospital and Geriatric Medical Center")
    p.drawString(3.3*inch, 6.15*inch, "(Formely BICOL SANITARIUM)")
    p.setFont("Times-Roman", 10, leading=None)
    p.setFillColor("black")
    p.drawString(3.4*inch, 6*inch, "San Pedro, Cabusao Camarines Sur")
    p.drawString(2.6*inch, 5.85*inch, "Telephone Nos.: (054) 473-2244, 472-4422, 881-1033, 881-1761")
    p.drawString(2.7*inch, 5.7*inch, "E-mail Address: bicolsan@gmail.com, brghgmc@gmail.com")
    p.line(0, 5.6*inch, 1000, 5.6*inch) #(x1, y1, x2, y2)
    p.drawString(3.8*inch, 5.45*inch, "PRESCRIPTION")
    p.drawString(6.8*inch, 5.2*inch, "Date:________________")
    p.drawString(0.2*inch, 5*inch, "Patient's Name:_____________________________________________________________________________")
    p.drawString(1.1*inch, 5*inch, patient_details[0]['patlast'] + ", " + patient_details[0]['patfirst'] + " " + patient_details[0]['patmiddle'])
    p.drawString(6.5*inch, 5*inch, "Age:_________")
    p.drawString(7*inch, 5*inch, str(age))
    p.drawString(7.5*inch, 5*inch, "Sex:_________")
    p.drawString(8*inch, 5*inch, patient_details[0]['patsex'])
    p.drawString(0.2*inch, 4.8*inch, "Address:________________________________________________")
    p.setFont("Times-Roman", 7, leading=None)
    p.drawString(0.75*inch, 4.8*inch, patient_address[0]['address'])
    p.setFont("Times-Roman", 10, leading=None)
    if patient_details[0]['toecode'] == 'ER':
        p.rect(4.1*inch, 4.8*inch, 10, 10, stroke=1, fill=1)#ER
    else:
        p.rect(4.1*inch, 4.8*inch, 10, 10, stroke=1, fill=0)#ER
    p.drawString(4.25*inch, 4.8*inch, "ER")
    if patient_details[0]['toecode'] == 'OPD':
        p.rect(4.5*inch, 4.8*inch, 10, 10, stroke=1, fill=1)#OPD
    else:
        p.rect(4.5*inch, 4.8*inch, 10, 10, stroke=1, fill=0)#OPD
    p.drawString(4.65*inch, 4.8*inch, "OPD")
    if patient_details[0]['toecode'] == 'ADM':
        p.rect(5*inch, 4.8*inch, 10, 10, stroke=1, fill=1)#WARD
    else:
        p.rect(5*inch, 4.8*inch, 10, 10, stroke=1, fill=0)#WARD
        p.drawString(5.8*inch, 4.8*inch, "N/A")
        p.drawString(7.1*inch, 4.8*inch, "N/A")
        p.drawString(8.05*inch, 4.8*inch, "N/A")
    p.drawString(5.15*inch, 4.8*inch, "Ward______________")
    p.drawString(6.5*inch, 4.8*inch, "Rom No._______")
    p.drawString(7.5*inch, 4.8*inch, "Bed No.______")
    p.setTitle("PRESCRIPTION")
    #p.drawImage(ImageReader(static_root + '/static/integrated/img/rx.png'), 0.3*inch, 4.3*inch, mask='auto', width=32, height=32)
    p.drawString(1*inch, 4.3*inch, "Generic Name of Drug(s)/Form")
    p.drawString(3.9*inch, 4.3*inch, "Dose & Frequency")
    p.drawString(6.1*inch, 4.3*inch, "Duration")
    p.drawString(7.6*inch, 4.3*inch, "Qty.")
    
    #prescription
    styles = getSampleStyleSheet()
    styles2 = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleN.alignment = TA_CENTER
    styleN.fontSize = 8 
    styleN.fontName = "Times-Bold"

    style_td = styles2["BodyText"]
    style_td.alignment = TA_LEFT
    style_td.fontSize = 8 
    style_td.alignment = TA_CENTER
    style_td.fontName = "Times-Roman"
    prescription = requests.post(pha_prescription_api, data={'enccode': enctr}).json()["data"]
    table_data = []
    count = 0
    for i in prescription:
        if i['status'] == '0':
            count += 1
            li = i['prescription'].split("_")
            if li[0]:
                gen = li[0]
            else: 
                gen = "--------"
            if li[1]:
                dose = li[1]
            else: 
                dose = "-------"
            if li[2]:
                duration = li[2]
            else: 
                duration = "----"
            if li[3]:
                qty = li[3]
            else: 
                qty = "----"
            table_data.append([Paragraph(gen, style_td), Paragraph(dose, style_td), Paragraph(duration, style_td), Paragraph(qty, style_td)])
    if table_data:
        t = Table(table_data, colWidths=[3.1*inch, 2.3*inch, 1.5*inch, 1.2*inch])
        t.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONT', (0, 0), (-1, -1), 'Times-Roman', 8)
        ]))
        t.wrapOn(p, 0, 0)

        if count == 1:
            t.drawOn(p, 0.2*inch, 3.9*inch)
        elif count == 2:
            t.drawOn(p, 0.2*inch, 3.7*inch)
        elif count == 3:
            t.drawOn(p, 0.2*inch, 3.5*inch)
        elif count == 4:
            t.drawOn(p, 0.2*inch, 3.2*inch)
        elif count == 5:
            t.drawOn(p, 0.2*inch, 3*inch)
        elif count == 6:
            t.drawOn(p, 0.2*inch, 2.7*inch)
        elif count == 7:
            t.drawOn(p, 0.2*inch, 2.5*inch)
        elif count == 8:
            t.drawOn(p, 0.2*inch, 2.2*inch)
        elif count == 9:
            t.drawOn(p, 0.2*inch, 2*inch)
        elif count == 10:
            t.drawOn(p, 0.2*inch, 1.7*inch)
        elif count == 11:
            t.drawOn(p, 0.2*inch, 1.5*inch)
        elif count == 12:
            t.drawOn(p, 0.2*inch, 1.2*inch)
        elif count == 13:
            t.drawOn(p, 0.2*inch, 1*inch)
        elif count == 14:
            t.drawOn(p, 0.2*inch, 0.8*inch)

    p.setFont("Times-Roman", 7, leading=None)
    p.drawString(0.45*inch, 0.55*inch, "Brand prescribing and unathorized use of NON-PNDF/PNF drugs in")
    p.drawString(0.4*inch, 0.44*inch, "BRGHGMC are violations of the Universally Accessible Cheaper and Quality")
    p.drawString(0.45*inch, 0.33*inch, "Medicines Act of 2008(RA 9502) and PhilHealth rules and regulations.")
    p.rect(0.3*inch, 0.25*inch, 3.2*inch, 0.45*inch, stroke=1, fill=0)

    p.setFont("Times-Roman", 10, leading=None)
    p.drawString(4.5*inch, 0.7*inch, "Printed Name / Signature: ________________________________")
    if md:
        p.drawString(6*inch, 0.7*inch, md[0]['firstname'] + " " + md[0]['middlename'][:1] + " " + md[0]['lastname'] + ", MD")
    p.drawString(5*inch, 0.5*inch, "License Number: ________________________")
    if md:
        p.drawString(6.2*inch, 0.5*inch, md[0]['licno'])
    p.drawString(5.05*inch, 0.3*inch, "S2 Lic. Number: ________________________")

    p.line(0, 0.2*inch, 1000, 0.2*inch) #(x1, y1, x2, y2)
    p.setFont("Times-Italic", 7, leading=None)
    p.drawString(0.1*inch, 0.1*inch, "BRGHGMC-F-MS-001")
    p.drawString(4.2*inch, 0.1*inch, "Rev 3")
    p.drawString(7.1*inch, 0.1*inch, "Effectivity Date: January 6, 2020")
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def profile(request):
    if request.session.get('employee_id') is not None:
        if request.method == 'POST':
            email = request.POST.get("email")
            contact = request.POST.get("contact")
            update = requests.post(update_user_api, data={'email': email, 'contact': contact, 'employeeid': request.session['employee_id']}).json()["status"]
            if update == 'success':
                request.session['email'] = email
                request.session['contactno'] = contact
        return render(request, 'integrated/profile/index.html', {'page': 'Profile', 'user_level': request.session['user_level'], 'name': request.session['name'], 'userid': request.session['userid'], 'position': request.session['position'], 'contactno': request.session['contactno'], 'email': request.session['email']})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def changepw(request):
    if request.session.get('employee_id') is not None:
        msg = ""
        if request.method == 'POST':
            oldpw = request.POST.get("old")
            newpw = request.POST.get("new")
            update = requests.post(update_user_pw_api, data={'employeeid': request.session['userid'], 'oldpw': oldpw, 'newpw': newpw}).json()["status"]
            if update == 'failed':
                msg = "Incorrect Old Password"
            else:
                msg = "Password updated"
        return render(request, 'integrated/profile/changepw.html', {'page': 'Profile', 'user_level': request.session['user_level'], 'name': request.session['name'], 'msg':msg})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def cashier(request):
    if request.session.get('employee_id') is not None:
        return render(request, 'integrated/cashier/index.html', {'page': 'Cashier', 'user_level': request.session['user_level'], 'name': request.session['name']})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def rfid(request, no):
    if request.session.get('employee_id') is not None:
        msg = ''
        if request.method == 'POST':
            rfid = request.POST.get("rfid")
            updaterfid = requests.post(update_patient_rfid_api, data={'hospital_no': no, 'rfid': rfid}).json()
            if updaterfid['status'] == "success":
                msg = "success"
            else:
                msg = "failed"
        details_response = requests.post(patient_details_api, data={'hospital_no': no})
        details_json_response = details_response.json()
        if details_json_response['status'] == 'success':
            details = details_json_response['data']
            details['details'][0]['patbdate'] = details['details'][0]['patbdate'][:10]
        return render(request, 'integrated/rfid/index.html', {'page': 'RFID', 'user_level': request.session['user_level'], 'name': request.session['name'], 'no': no, 'details': details, 'msg': msg})
    else:
        return HttpResponseRedirect('/')

def dialysis(request):
    if request.session.get('employee_id') is not None:
        patientlist = requests.post(dial_pat_list_api).json()["data"]
        return render(request, 'integrated/dialysis/index.html', {'page': 'Dialysis','user_level': request.session['user_level'], 'name': request.session['name'], 'list': patientlist})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def dialysisenrollment(request, no):
    if request.session.get('employee_id') is not None:
        msg = ""
        if request.method == "POST":
            tscode = request.POST.get("service")
            mssikey = request.POST.get("mss")
            enroll = requests.post(dial_enrollment_api, data={'hpercode': no, 'tscode': tscode, 'mssikey': mssikey}).json()["status"]
            msg = enroll
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
        mss_class = requests.get(get_mss_class_api).json()["data"]
        return render(request, 'integrated/dialysis/enrollment.html', {'page': 'Emergency Room', 'user_level': request.session['user_level'], 'name': request.session['name'], 'no':no, 'details': details, 'now': now, 'addr': addr, 'mss': mss_class, 'msg': msg})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def dialysisenrolled(request, no):
    if request.session.get('employee_id') is not None:
        msg = ""
        if request.method == "POST":
            tscode = request.POST.get("service")
            mssikey = request.POST.get("mss")
            enroll = requests.post(dial_update_patient_api, data={'hpercode': no, 'tscode': tscode, 'mssikey': mssikey}).json()["status"]
            msg = enroll
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
        mss_class = requests.get(get_mss_class_api).json()["data"]
        record = requests.post(dial_enrolled_api, data={'no': no}).json()["data"]
        return render(request, 'integrated/dialysis/enrolled_details.html', {'page': 'Emergency Room', 'user_level': request.session['user_level'], 'name': request.session['name'], 'no':no, 'details': details, 'now': now, 'addr': addr, 'mss': mss_class, 'msg': msg, 'record': record})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def dialysislog(request):
    if request.session.get('employee_id') is not None:
        msg = ""
        if request.method == "POST":
            rfid = request.POST.get('rfid')
            addlog = requests.post(dial_add_api, data={'rfid': rfid, 'entryby': request.session['employee_id']})
            msg = "success"
        log = requests.post(dial_log_api).json()["data"]
        for i in log:
            i['enccode'] = i['enccode'].replace('/', '-')
        return render(request, 'integrated/dialysis/log.html', {'page': 'Dialysis','user_level': request.session['user_level'], 'name': request.session['name'], 'list': log, 'msg': msg})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def dialysisConsultation(request, enctr):
    if request.session.get('employee_id') is not None:
        msg = ""
        encounter_no = enctr
        encounter = ""
        today = datetime.today()
        no = ""
        if request.method == "POST":
            height = request.POST.get('height')
            weight = request.POST.get('weight')
            temp = request.POST.get('temp')
            pulse = request.POST.get('pulse')
            bp = request.POST.get('bp')
            resp = request.POST.get('resp')
            diatype = request.POST.get('dia-type')
            disposition = request.POST.get('disposition')
            discharged_date = request.POST.get('discharged_date')
            discharged_time = request.POST.get('discharged_time')
            complaint = request.POST.get('chief_complaint')
            diagnosis = request.POST.get('diagnosis')
            discharge = discharged_date + " " + discharged_time
            #add VS
            addVS = requests.post(dial_add_vs_api, data={'enccode': encounter_no, 'height': height, 'weight': weight, 'temp': temp, 'pulse': pulse, 'bp': bp, 'resp': resp}).json()["status"]
            if(addVS == "success"):
                msg = "success"
            else:
                msg = "failed"
            update = requests.post(dial_update_api, data={'enccode': encounter_no, 'dialyzer': diatype, 'discharged_dt': discharge, 'disposition': disposition, 'complaint': complaint, 'diagnosis': diagnosis, 'entryby': request.session['employee_id']}).json()["status"]
        #This is for OPD Consultation Records
        response = requests.post(opd_record_api, data={'encounter_no': enctr})
        json_response = response.json()
        if json_response['status'] == 'success':
            if not json_response['data']:
                enctr = enctr.replace('-', '/')
                response = requests.post(opd_record_api, data={'encounter_no': enctr})
                json_response = response.json()
                if json_response['status'] == 'success':
                    encounter = enctr
                    for i in json_response['data']:
                        i['opddate'] = datetime.strptime(i['opddate'][:10], "%Y-%m-%d")
                        i['birthdate'] = datetime.strptime(i['birthdate'][:10], "%Y-%m-%d")
                        no = i['hpercode']
                        if i['opddtedis'] is not None:
                            i['disdate'] = datetime.strptime(i['opddtedis'][:10], "%Y-%m-%d")
                            i['distime'] = datetime.strptime(i['opddtedis'][11:19], "%H:%M:%S")
                    record = json_response['data']
            else:
                encounter = enctr
                for i in json_response['data']:
                    i['opddate'] = datetime.strptime(i['opddate'][:10], "%Y-%m-%d")
                    i['birthdate'] = datetime.strptime(i['birthdate'][:10], "%Y-%m-%d")
                    no = i['hpercode']
                record = json_response['data']
        vital_response = requests.post(vital_sign_api, data={'encounter_no': encounter})
        vital_json_response = vital_response.json()
        if vital_json_response['status'] == 'success':
            vitals = vital_json_response['data']
        else:
            vitals = []
        hw_response = requests.post(height_weight_api, data={'encounter_no': enctr})
        hw_json_response = hw_response.json()
        if hw_json_response['status'] == 'success':
            hw = hw_json_response['data']
        else:
            hw = []
        addr_response = requests.post(patient_address_api, data={'no': no})
        addr_json_response = addr_response.json()
        if addr_json_response['status'] == 'success':
            addr = addr_json_response['data']
        else:
            addr = []
        illness_response = requests.post(present_illlness_api, data={'encounter_no': enctr})
        illness_json_response = illness_response.json()
        if illness_json_response['status'] == 'success':
            illness = illness_json_response['data']
        else:
            illness = []
        complaint_response = requests.post(complaint_api, data={'encounter_no': enctr})
        complaint_json_response = complaint_response.json()
        if complaint_json_response['status'] == 'success':
            complaint = complaint_json_response['data']
        else:
            complaint = []
        diagnosis_response = requests.post(diagnosis_api, data={'encounter_no': enctr})
        diagnosis_json_response = diagnosis_response.json()
        if diagnosis_json_response['status'] == 'success':
            diagnosis = diagnosis_json_response['data']
        else:
            diagnosis = []
        dialysis_details = requests.post(dial_details_api, data={'enccode': enctr}).json()["data"]
        return render(request, 'integrated/dialysis/opd_consultation_details.html', {'page': 'Consultations', 'user_level': request.session['user_level'], 'name': request.session['name'], 'record': record, 'today': today, 'vitals': vitals, 'hw': hw, 'addr': addr, 'illness': illness, 'complaint': complaint, 'diagnosis': diagnosis, 'enctr': encounter_no, 'msg': msg, 'dialysis_details': dialysis_details, 'no': no})

    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})


def dialysisDischarged(request, enctr):
    if request.session.get('employee_id') is not None:
        encounter_no = enctr
        no = ""
        if request.method == "POST":
            height = request.POST.get('height')
            weight = request.POST.get('weight')
            temp = request.POST.get('temp')
            pulse = request.POST.get('pulse')
            bp = request.POST.get('bp')
            resp = request.POST.get('resp')
            diatype = request.POST.get('dia-type')
            disposition = request.POST.get('disposition')
            discharged_date = request.POST.get('discharged_date')
            discharged_time = request.POST.get('discharged_time')
            complaint = request.POST.get('chief_complaint')
            diagnosis = request.POST.get('diagnosis')
            discharge = discharged_date + " " + discharged_time
            #add VS
            addVS = requests.post(dial_add_vs_api, data={'enccode': encounter_no, 'height': height, 'weight': weight, 'temp': temp, 'pulse': pulse, 'bp': bp, 'resp': resp}).json()["status"]
            update = requests.post(dial_discharged_api, data={'enccode': encounter_no, 'dialyzer': diatype, 'discharged_dt': discharge, 'disposition': disposition, 'complaint': complaint, 'diagnosis': diagnosis, 'entryby': request.session['employee_id']}).json()["status"]
            return HttpResponseRedirect('/dialysislog')
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})


def login(request):
    if request.session.get('employee_id') is None:
        if request.method == 'POST':
            userid = request.POST.get("userid").upper()
            password = request.POST.get("password")
            login_response = requests.post(login_api, data={'username': userid, 'password': password})
            login_json_response = login_response.json()
            if login_json_response['status'] == 'success':
                if json.dumps(login_json_response['data']) == "[]":
                    messages.warning(request, "Invalid Username or Password")  
                    return render(request, 'integrated/login.html', {'page': 'Login'})
                else:
                    request.session['employee_id'] = login_json_response['data'][0]['employeeid']
                    request.session['user_level'] = login_json_response['data'][0]['user_level']
                    request.session['name'] = login_json_response['data'][0]['name']
                    request.session['position'] = login_json_response['data'][0]['postitle']
                    request.session['contactno'] = login_json_response['data'][0]['contactno']
                    request.session['email'] = login_json_response['data'][0]['email']
                    request.session['userid'] = userid
                    if login_json_response['data'][0]['user_level'] == 1:#ADMIN
                        return HttpResponseRedirect('/')
                    elif login_json_response['data'][0]['user_level'] == 15:#BILLING
                        return HttpResponseRedirect('/')
                    elif login_json_response['data'][0]['user_level'] == 3:#LABORATORY
                        return HttpResponseRedirect('/')
                    elif login_json_response['data'][0]['user_level'] == 4:#RADIOLOGY
                        return HttpResponseRedirect('/')
                    elif login_json_response['data'][0]['user_level'] == 5:#PHARMACY
                        return HttpResponseRedirect('/')
                    elif login_json_response['data'][0]['user_level'] == 6:#PHILHEATH
                        return HttpResponseRedirect('/')
                    elif login_json_response['data'][0]['user_level'] == 16:#CASHIERING
                        return HttpResponseRedirect('/')
                    elif login_json_response['data'][0]['user_level'] == 2:#NURSING
                        return HttpResponseRedirect('/')
                    elif login_json_response['data'][0]['user_level'] == 11:#CSSR
                        return HttpResponseRedirect('/')
                    else:
                        messages.error(request, "Access Denied! Please contact the system administrator")
                        return render(request, 'integrated/login.html', {'page': 'Login'})
            else:
                messages.warning(request, "Invalid Username or Password")  
                return render(request, 'integrated/login.html', {'page': 'Login'})

        else:
            return render(request, 'integrated/login.html', {'page': 'Login'})
    else:
        return HttpResponseRedirect('/')

def social_service(request):
    patient_list = requests.post(get_mss_patient_list_api).json()["data"]
    return render(request, 'integrated/mss/index.html', {'page': 'Social Service', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': patient_list})

def patient_search_mss(request):
    if request.session.get('employee_id') is not None:
        if request.method == 'POST':
            today = datetime.today()
            hospital_no = request.POST.get("hospital_no")
            lastname = request.POST.get("lastname").upper()
            firstname = request.POST.get("firstname").upper()
            middlename = request.POST.get("middlename").upper()
            no = 't'
            search_response = requests.post(patient_search_api, data={'no': hospital_no, 'lastname': lastname, 'firstname': firstname, 'middlename': middlename})
            search_json_response = search_response.json()
            if search_json_response['status'] == 'success':
                for i in search_json_response['data']:
                    i['dob'] = datetime.strptime(i['dob'][:11], "%b %d %Y")
                return render(request, 'integrated/mss/patient_search_result.html', {'result': search_json_response['data'], 'user_level': request.session['user_level'], 'name': request.session['name'], 'today': today, 'no': no})
            else:
                msg = "Record not found"
                return render(request, 'integrated/mss/patient_search_result.html', {'page': 'Search Result', 'msg': msg, 'user_level': request.session['user_level'], 'name': request.session['name']})
        else:
            msg = "Incorrect Search Procedure, Please ask for assistance"
            return render(request, 'integrated/opd/patient_search_result.html', {'page': 'Search Result', 'msg': msg, 'user_level': request.session['user_level'], 'name': request.session['name']})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def mss_patient_encounter(request, hpercode):
    if request.session.get('employee_id') is not None:
        response = requests.post(consultation_list_api, data={'hospital_no': hpercode})
        response_json = response.json()
        if response_json['status'] == 'success':
            for i in response_json['data']:
                i['date'] =  datetime.strptime(i['date'][:10], '%Y-%m-%d')
                i['enccode'] = i['enccode'].replace('/', '-')
            encounters = response_json['data']
        else:
            encounters = []
        return render(request, 'integrated/mss/encounter_list.html', {'page': 'Social Service', 'user_level': request.session['user_level'], 'name': request.session['name'], 'encounters': encounters})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def mss_patient_details(request, enctr):
    if request.session.get('employee_id') is not None:
        msg = ""
        if request.method == 'POST':
            mssclass = request.POST.get('mss')
            remarks = request.POST.get('remarks')
            addClass = requests.post(add_patient_mss_class_api, data={'enccode': enctr, 'mssikey': mssclass, 'remarks': remarks, 'user': request.session.get('employee_id'), 'informant': request.session.get('employee_id')}).json()["status"]
            msg = addClass
        patient_details = requests.post(patient_details_by_enc_api, data={'enccode': enctr}).json()["data"]
        no = patient_details[0]['hpercode']
        toe = patient_details[0]['toecode']
        patient_service = requests.post(get_patient_typser_api, data={'enc': enctr, 'toe': toe}).json()["data"]
        service = patient_service[0]['tsdesc']
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
        mss_patient_details = requests.post(get_patient_mss_api, data={'enccode': enctr}).json()["data"]
        mss_class = requests.get(get_mss_class_api).json()["data"]
        return render(request, 'integrated/mss/patient_mss_class.html', {'page': 'Social Service', 'user_level': request.session['user_level'], 'name': request.session['name'], 'no':no, 'details': details, 'now': now, 'addr': addr, 'mss': mss_class, 'msg': msg, 'toe': toe, 'service': service, 'enctr': enctr, 'mss_patient_details': mss_patient_details})
    else:
        return render(request, 'integrated/login.html', {'page': 'Login'})

def reports(request):
    return render(request, 'integrated/reports/index.html', {'page': 'Reports', 'user_level': request.session['user_level'], 'name': request.session['name']})

def re_er_referral(request):
    services = requests.post(get_er_services_api).json()['data']
    li = []
    if request.method == 'POST':
        start = request.POST.get('start')
        end = request.POST.get('end')
        tscode = request.POST.get('services')
        li = requests.post(rep_er_referral, data={'start':start, 'end': end, 'tscode': tscode}).json()['data']
    return render(request, 'integrated/reports/er_referral.html', {'page': 'Reports', 'user_level': request.session['user_level'], 'name': request.session['name'], 'services': services, 'list': li})

def re_er_incoming(request):
    li = []
    if request.method == 'POST':
        start = request.POST.get('start')
        end = request.POST.get('end')
        li = requests.post(rep_er_incoming_referral, data={'start':start, 'end': end}).json()['data']
        for i in li:
            i['date'] = datetime.strptime(i['erdate'][:10], '%Y-%m-%d')
            i['time'] = datetime.strptime(i['erdate'][11:19], '%H:%M:%S')
    return render(request, 'integrated/reports/er_incoming_referral.html', {'page': 'Reports', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': li})

def re_refer_outgoing(request):
    li = []
    if request.method == 'POST':
        start = request.POST.get('start')
        end = request.POST.get('end')
        li = requests.post(rep_er_outgoing_referral, data={'start':start, 'end': end}).json()['data']
        for i in li:
            i['date'] = datetime.strptime(i['erdate'][:10], '%Y-%m-%d')
            i['time'] = datetime.strptime(i['erdate'][11:19], '%H:%M:%S')
    return render(request, 'integrated/reports/referral_outgoing_referral.html', {'page': 'Reports', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': li})

def re_daily_movement(request):
    li = []
    if request.method == 'POST':
        start = request.POST.get('start')
        end = request.POST.get('end')
        li = requests.post(daily_movement_api, data={'start':start, 'end': end}).json()['data']
        no = 0
        for i in li:
            no += 1
            i['no'] = no
            i['admdate'] = datetime.strptime(i['admdate'][:10], '%Y-%m-%d')
            if i['disdate'] != '':
                i['disdate'] = datetime.strptime(i['disdate'][:10], '%Y-%m-%d')
            if i['dispcode'] == '':
                i['dispcode'] = ''
            if i['condcode'] == '':
                i['condcode'] = ''
    return render(request, 'integrated/reports/dailyMovement.html', {'page': 'Reports', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': li})

def re_bills_rendered(request):
    li = []
    if request.method == 'POST':
        start = request.POST.get('start')
        end = request.POST.get('end')
        li = requests.post(bill_rendered_api, data={'start':start, 'end': end}).json()['data']
        no = 0
        for i in li:
            no += 1
            i['no'] = no
            i['admdate'] = datetime.strptime(i['admdate'][:10], '%Y-%m-%d')
            if i['disdate'] != '':
                i['disdate'] = datetime.strptime(i['disdate'][:10], '%Y-%m-%d')
            if i['dispcode'] == '':
                i['dispcode'] = ''
            if i['condcode'] == '':
                i['condcode'] = ''
    return render(request, 'integrated/reports/billsRendered.html', {'page': 'Reports', 'user_level': request.session['user_level'], 'name': request.session['name'], 'list': li})

def logout(request):
    try:
        del request.session['employee_id']
        del request.session['user_level']
        del request.session['name']
    except KeyError:
        pass
    return HttpResponseRedirect('/login')