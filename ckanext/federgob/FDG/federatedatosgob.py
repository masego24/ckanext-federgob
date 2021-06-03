#!/usr/bin/python
# -*- coding: utf-8 -*-

#Script by: Jesús Redondo García
#Date: 28-10-2014

#Modified by Filip Radulovic and Idafen Santana Pérez
#Date: 31-03-2016

#Script to generate the whole metadata of the Catalog.

import urllib2
import json
from datetime import datetime
import re
import sys
import os
import ssl


base_path = os.path.dirname( os.path.realpath( __file__ ) )
url_catalog = 'URL-CATALOG' #Get info from fields.conf
url_dataset_path = 'URL-DATASET' #Get info from fields.conf
base_filename = os.path.join(base_path,'base_catalog.rdf')
output_filename = os.path.join(base_path,'../public/federator.rdf')
logfile = os.path.join(base_path,'Logs/log_federator')
fields_conf = os.path.join(base_path,'fields.conf')
excluded_filename = os.path.join(base_path,'Logs/log_excluded')


def fixTags(line,stream) :
    print >>stream, line.replace('<dct:title>','<dct:title xml:lang="es">').replace('<dct:description>','<dct:description xml:lang="es">'),

def load_metadata() :
    global url_catalog, url_dataset_path
    fields_conf_file = open(fields_conf,'r')
    fields_lines = fields_conf_file.readlines()

    for l in fields_lines :
        if '{-URL-CATALOG-} : ' in l : url_catalog = l.replace('{-URL-CATALOG-} : ','').replace('\n','')
        elif '{-URL-DATASET-} : ' in l : url_dataset_path = l.replace('{-URL-DATASET-} : ','').replace('\n','')
    if (url_catalog == 'URL-CATALOG') or (url_dataset_path == 'URL-DATASET') :
        print 'Error, federatedatosgob is not configured. Please run \"python config.py\".'
        sys.exit(0)


load_metadata()
print url_catalog

final_file = open(output_filename, 'w+')
excluded_file = open(excluded_filename, 'w+')
base_file = open(base_filename,'r')
base_strings = base_file.readlines()
publisher_base_config = ''

for linea in base_strings:
    print >>final_file, linea.replace("@@SCRIPT-Date-update@@",str(datetime.now()).replace(" ","T")[0:19]),
    if linea.strip().startswith('<dct:publisher'):
        publisher_base_config = linea
print >>final_file,"\n"


#Check all distributions of all datasets
#################################################################

# Deactivate SSL certificate verification
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

# Get datasets in the catalog.
try:
    response = urllib2.urlopen(url_catalog+'/api/3/action/package_list')
except Exception, e:
    print 'The catalog URL is not correct. Can not load CKAN API from:', url_catalog
    print url_catalog+'/api/3/action/package_list','is not accessible.'
    sys.exit(0)

assert response.code == 200

#Parse response
response_dict = json.loads(response.read())
assert response_dict['success'] is True
result = response_dict['result']

for name in result:
    print url_dataset_path+"/"+name+".rdf\n",

    try:
        pageRDF = urllib2.urlopen(url_dataset_path+"/"+name+".rdf")
    except Exception, e:
        print 'The dataset URL is not correct:', url_dataset_path
        print 'Can not download rdf file:', url_dataset_path+"/"+name+".rdf"
        sys.exit(0)

    strings_page_RDF = pageRDF.readlines()

    """
        Transforms for each dataset

        1.- replace values:
            *_old and *_new and others varibles are used to replace values

        2.- excluded is used to don't include datasets which doesn't have distribution tag 
            publisher_base_config is used to replace the old publisher tag as base_catalog publisher tag
            
    """
    pca_old = "<rdf:value>pc-axis</rdf:value>"
    pca_new = "<rdf:value>text/pc-axis</rdf:value>"

    pcam_old = "<rdfs:label>pc-axis</rdfs:label>"
    pcam_new = "<rdfs:label>PC-Axis</rdfs:label>"
    
    rdf_old = "<rdf:value>RDF</rdf:value>"
    rdf_new = "<rdf:value>application/rdf+xml</rdf:value>"
    
    sdmx_old = "<rdf:value>sdmx</rdf:value>"
    sdmx_new = "<rdf:value>application/zip</rdf:value>"
    
    html_old = "<rdf:value>HTML</rdf:value>"
    html_new = "<rdf:value>text/HTML</rdf:value>"
    
    xls_old = "<rdf:value>XLS</rdf:value>"
    xls_new = "<rdf:value>application/vnd.ms-excel</rdf:value>"
    
    json_old = "<rdf:value>JSON</rdf:value>"
    json_new = "<rdf:value>application/json</rdf:value>"
    
    media_type_pca_old = "<dcat:mediaType>application/vnd.pc-axis</dcat:mediaType>"
    media_type_pca_new = "<dcat:mediaType>text/pc-axis</dcat:mediaType>"
    
    dct = "dct:mediaType"
    dcat = "dcat:mediaType"
    
    uri = "<dct:identifier>https://www.icane.es/data/"
    
    freq_wrong = "https://purl.org/cld/freq/https://purl.org/cld/freq/"
    freq_right = "https://purl.org/cld/freq/"

    strings_page_RDF = [line.replace(pca_old, pca_new) for line in strings_page_RDF]
    strings_page_RDF = [line.replace(pcam_old, pcam_new) for line in strings_page_RDF]
    strings_page_RDF = [line.replace(pcam_old, pcam_new) for line in strings_page_RDF]
    strings_page_RDF = [line.replace(rdf_old, rdf_new) for line in strings_page_RDF]
    strings_page_RDF = [line.replace(sdmx_old, sdmx_new) for line in strings_page_RDF]
    strings_page_RDF = [line.replace(html_old, html_new) for line in strings_page_RDF]
    strings_page_RDF = [line.replace(json_old, json_new) for line in strings_page_RDF]
    strings_page_RDF = [line.replace(xls_old, xls_new) for line in strings_page_RDF]
    strings_page_RDF = [line.replace(dct, dcat) for line in strings_page_RDF]
    strings_page_RDF = [line.replace(media_type_pca_old, media_type_pca_new) for line in strings_page_RDF]
    strings_page_RDF = [re.sub("<dct:identifier>", uri, line)for line in strings_page_RDF]
    strings_page_RDF = [re.sub("http:", "https:", line)for line in strings_page_RDF]
    strings_page_RDF = [re.sub(freq_wrong, freq_right, line)for line in strings_page_RDF]
    
    excluded = False

    print >>final_file,"<dcat:dataset>"

    # if after language tag don't exists a distribution tag, we exclude it
    for index, line in enumerate(strings_page_RDF):           
        if "dct:language" in line:
            if "dcat:distribution" in strings_page_RDF[index+1]:
                pass
            else:
                excluded = True

    if excluded == False:
        counter_line = 0

        while not strings_page_RDF[counter_line].strip().startswith("<dcat:Dataset"):
            counter_line += 1

        while not strings_page_RDF[counter_line].strip().startswith("</rdf:RDF>"):
            # change <dct:publisher for publisher_base_config
            if strings_page_RDF[counter_line].strip().startswith("<dct:publisher") and \
            strings_page_RDF[counter_line + 6].strip().startswith("</dct:publisher"):
            
                # delete old publisher tag
                for i in range(1,7):
                    strings_page_RDF.pop(counter_line)
                # add publisher_base_config
                strings_page_RDF[counter_line] = publisher_base_config
            
            fixTags(strings_page_RDF[counter_line],final_file)
            counter_line += 1
        
        print >>final_file,"</dcat:dataset>\n"

    else:
        # save reference in excluded file log
        references = [s for s in strings_page_RDF if "<dct:references" in s]
        print >>excluded_file, references
            
        # delete initial <dcat:dataset> unused
        final_file.seek(-15, 1)


#################################################################

#Añadimos las lineas para cerrar los metadatos
print >>final_file, "\t</dcat:Catalog>\n</rdf:RDF>"

#Añadimos la hora en la que se realiza la actualización en el fichero de log
fLog = open(logfile,'a')
print >>fLog, "["+str(datetime.now())+"]Metadata updated"
