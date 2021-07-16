from openerp.osv import fields, osv

class pajak(osv.osv):
	_name = "hr.pajak"
	_description = "Report pajak karyawan"

	_columns = {
		"employee_id" : fields.many2one('hr.employee','Employee'),
		'date' : fields.date('Per Bulan'),
		"income" : fields.float('Gaji Bersih'),
		"pajak" : fields.float('Pph 21'),
	}
pajak()

class asuransi(osv.osv):
	_name = "hr.asuransi"
	_description ="Report Asuransi Perusahaan"

	_columns = {
		"employee_id" :fields.many2one('hr.employee', 'Employee'),
		"date" : fields.date('per Bulan'),
		"jht_tk" : fields.float('JHT Karyawan'),
		"jht_pr" : fields.float('JHT Perusahaan'),
		"jkk" : fields.float('Iuran JKK'),
		"jkm" : fields.float('Iuran JKM'),
		"bpjs_tk" : fields.float('Iuran BPJS Karyawan'),
		"bpjs_pr" : fields.float('Iuran BPJS Perusahaan'),
		"bpjs_ketenagakerjaan_tk" :fields.float("Jamsostek Dibayar Karyawan"),
        "bpjs_ketenagakerjaan_pr" :fields.float("Jamsostek Dibayar Perusahaan"),
        "total_bpjs_ketenagakerjaan" :fields.float("total Jamsostek"),
		'total_bpjs' :fields.float('Total BPJS'),
	}
asuransi()