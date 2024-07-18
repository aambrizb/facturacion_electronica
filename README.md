# SAT CFDI 4.0

|         |                                                     |
|---------|-----------------------------------------------------|
| Autor   | Jesús Alejandro Ambríz Bedolla                      |
| Email   | aambrizb@gmail.com |

## Introducción

Utilidad que permite generar una estructura básica de XML sellado sin timbrar, para que se pueda integrar directamente
con el PAC de tú preferencia.

## Requerimientos

| Requerimiento | Descripción                                                                                                                                                  |
|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| python3       | python 3.10 >                                                                                                                                                |
| openssl       | brew install openssl                                                                                                                                         |
| swig          | brew install swig                                                                                                                                            |
| M2Crypto      | LDFLAGS="-L$(brew --prefix openssl)/lib" CFLAGS="-I$(brew --prefix openssl)/include" SWIG_FEATURES="-I$(brew --prefix openssl)/include" pip install M2Crypto |

## Instalación

`
pip install -r requiriments.txt
`

Dicha utilidad puede ser llamada de 2 formas distintas:

a) Comando en Terminal

b) Importando Metodo


### Comando en Terminal
`
python timbrar_cfdi.py data/test.json data/CSD_Sucursal_1_EKU9003173C9_20230517_223850.cer data/CSD_Sucursal_1_EKU9003173C9_20230517_223850.key 12345678a output/FACT_1.xml
`

| Argumento     | Descripción                               |
|---------------|-------------------------------------------|
| json_file     | Archivo JSON (Ver data/test_json)         |
| cer_file      | Archivo *.cer de Sellos Digitales         |
| key_file      | Archivo *.key de Sellos Digitales         |
| password      | Contraseña de los Certificados            |
| output_xml    | Destino XML |

### Importación Metodo

```
cfdi          = CFDIv40()
cfdi.file_cer = 'data/CSD_Sucursal_1_EKU9003173C9_20230517_223850.cer'
cfdi.file_key = 'data/CSD_Sucursal_1_EKU9003173C9_20230517_223850.key'
cfdi.password = '12345678a'

# Generate CFDI from JSON
cfdi.create_from_json(data_json)
cfdi.save('output/FACT_1.xml')

# TODO
#
# Here your implementation with specific PAC.
```

Actualmente he integrado con los siguientes PAC's, si requieres apoyo o asesoria para integrar con estos pac's o algún otro no dudes en contactarme.

| PAC's |
|--------------------|
| Formas Digitales   |
| SIFEI              | 
| Advans             |
