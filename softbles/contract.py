from openerp.osv import fields, osv

class hr_contract_type(osv.osv):
    _name = 'hr.contract.type'
    _inherit= 'hr.contract.type'
    
    _columns = {
        "jht_tk":fields.float('JHT Karyawan (%)'),
        "jht_pr":fields.float('JHT Perusahaan (%)'),
        "jkk":fields.float('JKK (%)'),
        "jkm":fields.float('JKM (%)'),
        "jpk_single":fields.float('JPK Single',size=1),
        "jpk_menikah":fields.float('JPK Menikah',size=1),
        "tunjangan_jabatan":fields.float('Tunjangan Jabatan Jabatan (%)',size=1),
        "max_tunj_jabatan":fields.float('Nominal Max (Rp)'),
        "bpjs_pr":fields.float('Kontribusi Perusahaan (%)'),
        'bpjs_tk':fields.float('Kontribusi Karyawan (%)'),
        'max_bpjs':fields.float('Batas Max BPJS'),
        'min_bpjs':fields.float('Batas Min BPJS'), 
     } 
hr_contract_type()

class hr_contract(osv.osv):
    _name       = 'hr.contract'
    _inherit    = 'hr.contract'

    _columns    = {
        "tunj_makan"        : fields.float("Tunjangan Makan (Perhari)"),
        "tunj_makan_bulanan": fields.float("Tunjangan Makan (Bulanan)"),
        "tunj_transport"   : fields.float("Tunjangan Transport (perbulan)"),
        "tunj_lembur"       : fields.float("Tunjangan lembur (perhari)"),
        "tunj_komunikasi"   : fields.float("Tunjangan Komunikasi (Perbulan)"),

    }
hr_contract()

class pkp(osv.osv):
    _name="hr.pkp"
    _rec_name="kode"
    
    _columns = {
        "kode":fields.char('Kode',size=5,required=True),
        "nominal_min" : fields.float("Nominal Min",required=True),
        "nominal_max" : fields.float("Nominal Max",required=True),
        "pajak":fields.float('Pajak (%)',size=2,required=True),
    }

    _sql_constraints = [('kode_uniq', 'unique(kode)','Kode tidak boleh sama!')]
    _sql_constraints = [('pajak_uniq', 'unique(pajak)','Besaran % pajak tidak boleh sama!')]
           
pkp() 

class ptkp(osv.osv):
    _name="hr.ptkp"
    _rec_name="kode"
    
    _columns = {
        "kode":fields.char('Kode',size=5,required=True),
        "nominal_bulan" : fields.float("Nominal Perbulan",required=True),
        "nominal_tahun" : fields.float("Nominal Pertahun"),
    }
    def onchange_kali(self, cr, uid, ids, nominal_bulan, nominal_tahun, context=None):
        v = {'nominal_tahun_': (nominal_bulan ) * 12}
        return {'value': v}

    def onchange_bagi(self, cr, uid, ids, nominal_bulan, nominal_tahun, context=None):
        v = {'nominal_bulan': (nominal_tahun ) /12}
        return {'value': v}
        
    _sql_constraints = [('kode_uniq', 'unique(kode)','Kode tidak boleh sama!')]
           
ptkp()

class hr_employee(osv.osv):
    _name = "hr.employee"
    _inherit = "hr.employee"

    _columns = {
        "ptkp_id" : fields.many2one("hr.ptkp","PTKP",required=True),
        "skypee_id" : fields.char("Skype ID"),
        "gtalk_id" : fields.char("Gtalk ID"),
        "no_hp" : fields.char("No Handphone"),
        "other" : fields.char("Other"),
        "no_ktp" : fields.char("KTP Number"),
        "fingerprint_code" : fields.char("NIK"),
    }

hr_employee()