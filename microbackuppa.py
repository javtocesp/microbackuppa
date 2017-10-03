import os
import sys
import subprocess
#from boto.s3.key import Key
import urllib2
import ssl
from bs4 import BeautifulSoup
import socket
import boto3
import logging
import time


#LOG_FILE='/var/backup.log'
#logging.basicConfig(filename=LOG_FILE,level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')


PA_TOKEN=os.environ["PA_TOKEN"]
MY_KEY1=os.environ["MY_KEY1"]
MY_SECRET1=os.environ["MY_SECRET1"]
BUCKET_NAME1=os.environ["BUCKET_NAME1"]
MY_KEY=os.environ["MY_KEY"]
MY_SECRET=os.environ["MY_SECRET"]
BUCKET_NAME=os.environ["BUCKET_NAME"]

def getconfig(fw):
      if not testconnection1(fw):
            print ("error en la conexin a {}".format(fw))
            logging.info('Error de conexion al firewall '+fw)
            return
       
      print (PA_TOKEN)
      print ('Bajando config {}'.format(fw))
      COMMAND_GET_CONFIG='curl --silent -k -H "Accept: application/xml" -H "Content-Type: application/xml" -X GET "https://{}/api/?type=export&category=configuration&key={}"'.format(fw,PA_TOKEN)
      result=subprocess.check_output(COMMAND_GET_CONFIG,shell=True)
      print ("Config bajada!")
      result1=result.split(' ')
      if "<config" in result1[0]:
            COMMAND_GET_CONFIG='curl --silent -o `date +%Y%m%d`-{}.xml  -k -H "Accept: application/xml" -H "Content-Type: application/xml" -X GET "https://{}/api/?type=export&category=configuration&key={}"'.format(fw,fw,PA_TOKEN)
            result=subprocess.check_output(COMMAND_GET_CONFIG,shell=True)
      else:
            soup=BeautifulSoup(result,"html.parser")
            for strong_tag in soup.find_all('msg'):
                  logging.info(str(strong_tag) +' in '+fw)


def upandcleanconfig():
      FINDFILE="ls -t | head -n1"
      result=subprocess.check_output(FINDFILE,shell=True)
      print ("result compression: {}".format(result))
      result=result.split('/')
      up=[line.replace('\n.','') for line in result if ".xml" in line]
      print ('name: {}'.format(up[-1]))
      logging.info('Archivo a subir: {}'.format(up[-1]))
      uploadconfig(up[-1])

def uploadconfig (filezip):
      ERASEBZ2="rm *.bz2"
      filezip=filezip.replace(" ","")
      filezip=filezip.replace("\n","")
      boto3_connect=boto3.client('s3', aws_access_key_id=MY_KEY,aws_secret_access_key=MY_SECRET)
      boto3_connect.upload_file(filezip,BUCKET_NAME,filezip)
      time.sleep(10)


def testconnection1(fwip):
      s=socket.socket()
      s.settimeout(3)
      try:
            s.connect((fwip,443))
      except Exception as e:
            return False
      else:
            return True
      finally:
            s.close()

def main():
    getconfig(sys.argv[1])
    upandcleanconfig()

main()
