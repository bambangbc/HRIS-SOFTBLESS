import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import netsvc
from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

from openerp.tools.safe_eval import safe_eval as eval
import pprint

class hr_payslip(osv.osv):
    '''
    PPI Pay Slip
    '''

    _name = 'hr.payslip'
    _inherit = 'hr.payslip'
    _description = 'Pay Slip Inheriteed Lucas Marin'

    def get_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, context=None):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        def was_on_leave(employee_id, datetime_day, context=None):
            res = False
            day = datetime_day.strftime("%Y-%m-%d")
            holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state','=','validate'),('employee_id','=',employee_id),('type','=','remove'),('date_from','<=',day),('date_to','>=',day)])
            if holiday_ids:
                res = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].holiday_status_id.name
            return res

        res = []
        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            if not contract.working_hours:
                #fill only if the contract as a working schedule linked
                continue
            attendances = {
                 'name': _("Normal Working Days paid at 100%"),
                 'sequence': 1,
                 'code': 'WORK100',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }

            presences = {
                 'name': _("Kehadiran"),
                 'sequence': 2,
                 'code': 'PRESENCES',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }

            terlambat = {
                 'name': _("terlambat"),
                 'sequence': 2,
                 'code': 'TERLAMBAT',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }

            lembur = {
                 'name': _("Lembur"),
                 'sequence': 3,
                 'code': 'LEMBUR',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }
            leaves = {}
            day_from = datetime.strptime(date_from,"%Y-%m-%d")
            day_to = datetime.strptime(date_to,"%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1
            for day in range(0, nb_of_days):
                working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
                date = (day_from + timedelta(days=day))
                isNonWorkingDay = date.isoweekday()==6 or date.isoweekday()==7
                if working_hours_on_day:
                    leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day), context=context)
                    if leave_type:
                        #if he was on leave, fill the leaves dict
                        if leave_type in leaves:
                            leaves[leave_type]['number_of_days'] += 1.0
                            leaves[leave_type]['number_of_hours'] += working_hours_on_day
                        else:
                            leaves[leave_type] = {
                                'name': leave_type,
                                'sequence': 5,
                                'code': leave_type,
                                'number_of_days': 1.0,
                                'number_of_hours': working_hours_on_day,
                                'contract_id': contract.id,
                            }
                    else:
                        real_working_hours_on_day = self.pool.get('hr.attendance').real_working_hours_on_day(cr,uid, contract.employee_id.id, day_from + timedelta(days=day),context)
                        if real_working_hours_on_day >= 0.000000000000000001 and not isNonWorkingDay :
                            presences['number_of_days'] += 1.0
                            presences['number_of_hours'] += working_hours_on_day
                        #add the input vals to tmp (increment if existing)
                        attendances['number_of_days'] += 1.0
                        attendances['number_of_hours'] += working_hours_on_day
            leaves = [value for key,value in leaves.items()]
            res += [attendances] + [presences] + [terlambat] + [lembur] + leaves 
        return res

    def compute_sheet(self, cr, uid, ids, context=None):
        slip_line_pool = self.pool.get('hr.payslip.line')
        sequence_obj = self.pool.get('ir.sequence')
        for payslip in self.browse(cr, uid, ids, context=context):
            number = payslip.number or sequence_obj.get(cr, uid, 'salary.slip')
            #delete old payslip lines
            old_slipline_ids = slip_line_pool.search(cr, uid, [('slip_id', '=', payslip.id)], context=context)
#            old_slipline_ids
            if old_slipline_ids:
                slip_line_pool.unlink(cr, uid, old_slipline_ids, context=context)
            if payslip.contract_id:
                #set the list of contract for which the rules have to be applied
                contract_ids = [payslip.contract_id.id]
            else:
                #if we don't give the contract, then the rules to apply should be for all current contracts of the employee
                contract_ids = self.get_contract(cr, uid, payslip.employee_id, payslip.date_from, payslip.date_to, context=context)
            #find denda
            for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context):
                if line['code'] == 'B/T' :
                    bonus = line['amount']
            #find BPJS 
            for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context):
                # find bpjs Kesehatan
                if line['code'] == 'TAX' :
                    tax = line['amount']
                if line['code'] == 'BPJS_KESEHATAN' :
                    bpjs_tk = line['amount']
                if line['code'] == 'JAMSOSTEK_KARYAWAN' :
                    JAMSOSTEK_KARYAWAN = line['amount']
            for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context):
                if line['code'] == 'NET' :
                    net = line['amount']
                    net_bpjs = line['amount'] - bonus - tax - bpjs_tk - JAMSOSTEK_KARYAWAN 
                    if net_bpjs >= payslip.contract_id.type_id.max_bpjs :
                        bpjs = payslip.contract_id.type_id.max_bpjs
                    elif net_bpjs <= payslip.contract_id.type_id.min_bpjs :
                        bpjs = payslip.contract_id.type_id.min_bpjs
                    else :
                        bpjs = net_bpjs
                    self.write(cr,uid,ids,{'bpjs_tk':bpjs},context=context)
            net = net-tax-bpjs_tk-JAMSOSTEK_KARYAWAN 

            #####kalkulasi jamsostek ketenagakerjaan#######
            bpjs_ketenagakerjaan = (net_bpjs*payslip.contract_id.type_id.jht_tk)/100
            self.write(cr,uid,ids,{'bpjs_ketenagakerjaan_tk':bpjs_ketenagakerjaan},context=context)
            ##########################################

            #find pajak
            for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context):
                if line['code'] == "B/T" :
                    bonus = line['amount']
                net_setahun = (net)*12
            ptkp = payslip.employee_id.ptkp_id.nominal_tahun
            tunj_jabatan = (net*12)*(payslip.contract_id.type_id.tunjangan_jabatan/100)
            if tunj_jabatan >= payslip.contract_id.type_id.max_tunj_jabatan :
                tunj_jabatan = payslip.contract_id.type_id.max_tunj_jabatan      
            pkp = net_setahun - ptkp - tunj_jabatan
            obj_pkp = self.pool.get('hr.pkp')
            src_pkp = obj_pkp.search(cr,uid,[])
            pjk = 0
            # for pkp_21 in obj_pkp.browse(cr,uid,src_pkp) :
            #     pajak = 0 
            #     percent = pkp_21.pajak
            #     if pkp > pkp_21.nominal_max :
            #         total_pkp = pkp_21.nominal_max - pkp_21.nominal_min
            #         pajak = (total_pkp * percent)/100
            #     elif pkp <= pkp_21.nominal_max and pkp >= pkp_21.nominal_min :
            #         pajak_tampung = pkp - pkp_21.nominal_min
            #         pajak = (pajak_tampung*percent)/100
            #     pjk += pajak 
            #pajak = pjk/12
            for pkp_21 in obj_pkp.browse(cr,uid,src_pkp) :
                percent = pkp_21.pajak
                pjk = (pkp * percent)/100
                break
            pajak = pjk/12
            if pajak > 0 :
                self.write(cr,uid,ids,{'pjk':pajak},context=context)
            else :
                self.write(cr,uid,ids,{'pjk':0},context=context)
            #menentukan Gaji bersih
            for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context):
                if line['code'] == 'NET' :
                    net = line['amount']
                    self.write(cr,uid,ids,{'income':net},context=context)
            lines = [(0,0,line) for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context)]
            self.write(cr, uid, [payslip.id], {'line_ids': lines, 'number': number,}, context=context)
        return True 

    def hr_verify_sheet(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'verify'}, context=context)

    _columns = {
        "bpjs_tk" : fields.float("BPJS_TK"),
        "bpjs_pr" : fields.float("BPJS PR"),
        'total_bpjs' :fields.float("Total BPJS"),
        "bpjs_ketenagakerjaan_tk" :fields.integer("BPJS_ketenagakerjaan"),
        "bpjs_ketenagakerjaan_pr" :fields.integer("BPJS_ketenagakerjaan_Pr"),
        "total_bpjs_ketenagakerjaan" :fields.float("total BPJS_ketenagakerjaan"),
        "pjk" : fields.integer("PAJAK"),
        "income":fields.float("income"),
    }

hr_payslip()

class hr_attendance(osv.osv):
    _name = "hr.attendance"
    _inherit = "hr.attendance"
    _description = "Attendance SOFTBLESS"

    def real_working_hours_on_day(self, cr, uid, employee_id, datetime_day, context=None):
        day = datetime_day.strftime("%Y-%m-%d 00:00:00")
        day2 = datetime_day.strftime("%Y-%m-%d 24:00:00")

        pprint.pprint(day)


        #employee attendance
        atts_ids = self.search(cr, uid, [('employee_id', '=', employee_id), ('name', '>', day), ('name', '<', day2)], limit=2, order='name asc' )
        
        time1=0
        time2=0

        for att in self.browse(cr, uid, atts_ids, context=context):
            if att.action == 'sign_in':
                pprint.pprint('sign_in')
                pprint.pprint(att.name)
                time1 = datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")
            else:
                pprint.pprint('sign_out')
                pprint.pprint(att.name)
                time2 = datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")
        
        if time2 and time1:
            delta = (time2 - time1).seconds / 3600.00
        else:
            delta = 0

        pprint.pprint(delta)        
        return delta

    def _altern_si_so(self, cr, uid, ids, context=None):
        """ Alternance sign_in/sign_out check.
            Previous (if exists) must be of opposite action.
            Next (if exists) must be of opposite action.

            PPI: skip _constraints supaya bisa import dari CSV
        """
        return True

hr_attendance()