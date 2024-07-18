from facturacion_electronica.cfdv40.cfdv40 import (
  Comprobante,
  EmisorType as Emisor,
  ReceptorType as Receptor,
  ConceptosType as Conceptos,
  ConceptoType as Concepto,
  ImpuestosType as Impuestos,
  ImpuestosType10 as ImpuestosGlobal,
  TrasladosType as Traslados,
  TrasladoType as Traslado,
  RetencionesType as Retenciones,
  RetencionType as Retencion
)
from M2Crypto import RSA
from lxml import etree as ET
from io import StringIO
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import os, codecs, hashlib, base64

class CFDIv40:

  """
  Autor. Jesús Alejandro Ambriz Bedolla
  Email. aambrizb@gmail.com

  Clase CFDIv40 que permite crear un XML sellando a través de un formato JSON.
  Preparandolo para poder realizar integración directa con el PAC de elección.
  """

  file_cer             = None
  file_certificate_pem = None
  file_key             = None
  file_pem             = None
  password             = None

  file_xml = None
  document = None
  xml      = None

  def __init__(self):
    pass

  def validate_pem(self):

    # Try to create pem file
    if self.file_key and self.password:

      self.file_pem = f'{self.file_key}.pem'

      if not os.path.exists(self.file_pem):
        tmp_command = f"openssl pkcs8 -inform DER -in {self.file_key} -out {self.file_pem} -passin pass:'{self.password}'"
        os.system(tmp_command)
    else:
      raise Exception("[ERR] - Requiere configurar file_key y password.")

  def validate_cer(self):

    if self.file_cer:
      self.file_certificate_pem = f"{self.file_cer}.pem"

    if not os.path.exists(self.file_certificate_pem):
      tmp_command = f"openssl x509 -inform DER -in {self.file_cer} -out {self.file_certificate_pem}"
      os.system(tmp_command)
    with open(self.file_certificate_pem, "rb") as f:
      cert = x509.load_pem_x509_certificate(f.read(), default_backend())
      self.document.set_NoCertificado(hex(cert.serial_number)[2:][1::2])


  def create_from_json(self,data_json):

    tmp_node_comprobante = data_json.get('Comprobante', None)

    if tmp_node_comprobante:
      self.document = Comprobante(
        Version           = tmp_node_comprobante.get('Version',None),
        Serie             = tmp_node_comprobante.get('Serie',None),
        Folio             = tmp_node_comprobante.get('Folio',None),
        Fecha             = tmp_node_comprobante.get('Fecha',None),
        FormaPago         = tmp_node_comprobante.get('FormaPago',None),
        NoCertificado     = tmp_node_comprobante.get('NoCertificado',None),
        SubTotal          = tmp_node_comprobante.get('SubTotal',None),
        Descuento         = tmp_node_comprobante.get('Descuento',None),
        Moneda            = tmp_node_comprobante.get('Moneda',None),
        TipoCambio        = tmp_node_comprobante.get('TipoCambio',None),
        Total             = tmp_node_comprobante.get('Total',None),
        TipoDeComprobante = tmp_node_comprobante.get('TipoDeComprobante',None),
        Exportacion       = tmp_node_comprobante.get('Exportacion',None),
        MetodoPago        = tmp_node_comprobante.get('MetodoPago',None),
        LugarExpedicion   = tmp_node_comprobante.get('LugarExpedicion',None),
        MotivoTraslado    = tmp_node_comprobante.get('MotivoTraslado',None),
        Confirmacion      = tmp_node_comprobante.get('Confirmacion',None)
      )

      tmp_node_emisor = tmp_node_comprobante.get('Emisor', None)

      if tmp_node_emisor:
        self.document.set_Emisor(
          Emisor(
            Rfc           = tmp_node_emisor.get('Rfc',None),
            Nombre        = tmp_node_emisor.get('Nombre',None),
            RegimenFiscal = tmp_node_emisor.get('RegimenFiscal',None)
          )
        )

      tmp_node_receptor = tmp_node_comprobante.get('Receptor', None)

      if tmp_node_receptor:
        self.document.set_Receptor(
          Receptor(
            Rfc                     = tmp_node_receptor.get('Rfc',None),
            Nombre                  = tmp_node_receptor.get('Nombre',None),
            RegimenFiscalReceptor   = tmp_node_receptor.get('RegimenFiscalReceptor',None),
            DomicilioFiscalReceptor = tmp_node_receptor.get('DomicilioFiscalReceptor', None),
            UsoCFDI                 = tmp_node_receptor.get('UsoCFDI', None)
          )
        )

      tmp_node_conceptos     = tmp_node_comprobante.get('Conceptos', None)
      tmp_trasladados_amount = 0
      tmp_retenciones_amount = 0

      if tmp_node_conceptos:

        tmp_conceptos = Conceptos()

        for item in tmp_node_conceptos:

          tmp_concepto = Concepto(
            Cantidad      = item.get('Cantidad',None),
            ClaveProdServ = item.get('ClaveProdServ',None),
            ClaveUnidad   = item.get('ClaveUnidad', None),
            Unidad        = item.get('Unidad', None),
            Descripcion   = item.get('Descripcion', None),
            ValorUnitario = item.get('ValorUnitario', None),
            Importe       = item.get('Importe', None),
            ObjetoImp     = item.get('ObjetoImp', None)
          )

          tmp_traslados   = item.get('traslados', [])
          tmp_retenciones = item.get('retenciones', [])

          if tmp_traslados or tmp_retenciones:
            tmp_impuestos = Impuestos()

            if tmp_traslados:

              tmp_node_traslados = Traslados()

              for x in tmp_traslados:
                tmp_importe = x.get('Importe', None)
                tmp_node_traslados.add_Traslado(
                  Traslado(
                    Base       = x.get('Base',None),
                    Importe    = tmp_importe,
                    Impuesto   = x.get('Impuesto', None),
                    TasaOCuota = x.get('TasaOCuota', None),
                    TipoFactor = x.get('TipoFactor', None)
                  )
                )

                tmp_trasladados_amount += tmp_importe

              tmp_impuestos.set_Traslados(tmp_node_traslados)

            if tmp_retenciones:

              tmp_node_retenciones = Retenciones()

              for x in tmp_retenciones:
                tmp_importe = x.get('Importe', None)
                tmp_node_retenciones.add_Retencion(
                  Retencion(
                    Base       = x.get('Base', None),
                    Importe    = tmp_importe,
                    Impuesto   = x.get('Impuesto', None),
                    TasaOCuota = x.get('TasaOCuota', None),
                    TipoFactor = x.get('TipoFactor', None)
                  )
                )

                tmp_retenciones_amount += tmp_importe

              tmp_impuestos.set_Retenciones(tmp_node_retenciones)

            tmp_concepto.set_Impuestos(tmp_impuestos)

          tmp_conceptos.add_Concepto(tmp_concepto)

        self.document.set_Conceptos(tmp_conceptos)

        if tmp_retenciones_amount <= 0:
          tmp_retenciones_amount = None

        self.document.set_Impuestos(ImpuestosGlobal(
          TotalImpuestosTrasladados = tmp_trasladados_amount,
          TotalImpuestosRetenidos   = tmp_retenciones_amount,
          Traslados                 = tmp_node_traslados,
          Retenciones               = None
        ))

    self.generate()


  def generate(self):

    self.validate_pem()
    self.validate_cer()
    self.sign()

  def create_xml(self):
    xmlStr = StringIO()
    xmlStr.seek(0)
    self.document.export(xmlStr, 0)
    self.xml = xmlStr.getvalue()

  def sign(self):

    self.create_xml()

    keys                         = RSA.load_key(self.file_pem)
    cert_file                    = open(self.file_cer, 'rb')

    file_content = codecs.encode(cert_file.read(), 'base64')
    file_content = file_content.decode("utf-8")
    file_content = file_content.replace("\n","")

    self.document.Certificado = file_content
    self.XSLT_PATH = f'{os.path.dirname(__file__)}/cfdv40/xslt/cadenaoriginal_4_0.xslt'

    xdoc            = ET.fromstring(self.xml)

    xsl_root        = ET.parse(self.XSLT_PATH)
    xsl             = ET.XSLT(xsl_root)

    self.cadena_original   = xsl(xdoc)

    self.cadena_original = str(self.cadena_original)
    digest               = hashlib.new('sha256', self.cadena_original.encode('utf8')).digest()
    self.document.Sello  = base64.b64encode(keys.sign(digest, "sha256"))
    self.document.Sello  = self.document.Sello.decode("utf-8")

    self.create_xml()

  def save(self,destination):
    f = open(destination,'w')
    f.write(self.xml)
    f.close()