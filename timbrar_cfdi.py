from facturacion_electronica.CFDI import CFDIv40
import sys
import json

if __name__ == '__main__':

  if len(sys.argv) != 6:
    print("[ER] Syntax: timbrar_cfdi.py <json_file> <cer_file> <key_file> <password> <output_xml>")
  else:

    tmp_json = sys.argv[1]
    tmp_cer = sys.argv[2]
    tmp_key = sys.argv[3]
    tmp_passwd = sys.argv[4]
    tmp_xml = sys.argv[5]
    tmp_pem = f'{tmp_key}.pem'

    # Read JSON File.
    f = open(tmp_json, 'r')
    data_json = f.read()
    data_json = json.loads(data_json)

    cfdi          = CFDIv40()
    cfdi.file_cer = tmp_cer
    cfdi.file_key = tmp_key
    cfdi.password = tmp_passwd

    # Generate CFDI from JSON
    cfdi.create_from_json(data_json)
    cfdi.save(tmp_xml)

    print(cfdi.xml)
