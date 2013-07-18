#!/usr/bin/python

versie = 1.0

from datetime import datetime, timedelta
import re
import serial
import sys
from metingen import meting

# --- Meter lees informatie ---
# Maximum aantal regels dat gelezen mag worden
# dient om programma te stoppen wanneer er geen 'eofline' voorbij komt
maxlines = 30
# Einde van bericht regel
eofline = '!'
# Aantal verwachte regels (verschilt per slimme meter type)
expectedlines = 17
# Header van het datagram voor deze meter
# let op de r aan het begin om te voorkomen dat \ als escape
# character wordt gebruikt
meteridentification = r"/ISk5\2ME382-1003"

# --- Bestands informatie ---
# Bestand met vorige meting
root_dir = '/usr/local/P1tools/database'
if root_dir[-1] != '/':
   root_dir = root_dir + '/'
vorige_meting_bestand = 'vorige_meting'

# Informatie die de meter oplevert
meterinfo = [
   'meter_id',
   'gebruikt1',
   'gebruikt2',
   'geleverd1',
   'geleverd2',
   'huidigtarief',
   'vermogen_in',
   'vermogen_uit',
   'max_vermogen',
   'stroom_hoofdschakelaar',
   'tekst_code',
   'tekst',
   'device_type',
   'gas_meter_id',
   'gas_meetdatum',
   'gas_hoofdschakelaar',
   'gas_gebruik',
   'datum_tijd'
]   

# Herkenningsstrings voor meter informatie
meteruitvoerformaat_list = [
   '0-0:96.1.1',
   '1-0:1.8.1',
   '1-0:1.8.2',
   '1-0:2.8.1',
   '1-0:2.8.2',
   '0-0:96.14.0',
   '1-0:1.7.0',
   '1-0:2.7.0',
   '0-0:17.0.0',
   '0-0:96.3.10',
   '0-0:96.13.1',
   '0-0:96.13.0',
   '0-1:24.1.0',
   '0-1:96.1.0',
   '0-1:24.3.0',
   '0-1:24.4.0',
   '(',
   'Not applicable'
]
meteruitvoerformaat = dict(zip(meterinfo,meteruitvoerformaat_list))

meteruitvoer_waarden = [
   'gebruikt1','gebruikt2','geleverd1',
   'geleverd2','vermogen_in','vermogen_uit',
   'max_vermogen','gas_gebruik'
 ]
   

##############################################################################
# Lees meterinformatie
##############################################################################
def lees_meter():
   #Stel de seriele poort in
   ser = serial.Serial()
   ser.baudrate = 9600
   ser.bytesize=serial.SEVENBITS
   ser.parity=serial.PARITY_EVEN
   ser.stopbits=serial.STOPBITS_ONE
   # Hopelijk helpt dit om complete boodschappen te krijgen
   # was bij 0 een probleem. cu heeft dit echter standaard aan staan
   # en daar trad dit probleem niet op
   ser.xonxoff=1
   ser.rtscts=0
   # timeout voor het wachten op invoer
   # er moet elke 10 seconden een bericht komen
   ser.timeout=12
   # Seriele poort waar p1 naar USB interface op zit
   ser.port="/dev/ttyUSB0"
   
   #Open seriele poort
   try:
       ser.open()
   except:
       sys.exit ("Fout bij het openen van seriele poort %s"  % ser.name)      

   p1_output = [] 
   nlines = 0
   nparsedlines = 0
   header = False
   while (nlines < maxlines):
      try:
         line = str(ser.readline()).strip()
         nlines = nlines + 1
         # Eerst moet er een header komen.
         # Voorkomt dat we incomplete datagrammen parsen
         if not header: 
            if line == meteridentification:
               header = True
         else:
            if line == eofline:
               break
            elif line != '':
               p1_output.append(line)
               nparsedlines = nparsedlines + 1
      except:
         sys.exit ("Kon seriele poort niet openen")

   #Close port and show status
   try:
       ser.close()
   except:
       sys.exit ("Programma afgebroken. Kon de seriele poort %s niet sluiten." % ser.name )

   # Initialiseer dictionary met datum van de meting
   meteruitvoer={'datum_tijd':datetime.now()}
   # Parse de meter uitvoer
   for line in p1_output: 
#DEBUG      print line
      for key in meteruitvoerformaat:
         if line.startswith(meteruitvoerformaat[key]):
            meteruitvoer[key] = line[line.find('(')+1:line.find(')')]
  
   for key in meteruitvoer_waarden:
      try:
         meteruitvoer[key] = float(re.sub('[^0-9\.]', '', meteruitvoer[key]))
      except KeyError:
         sys.exit("Missende invoer vanuit meter, waarschijnlijk probleem met seriele poort")

# DEBUG      
#   for key in meteruitvoer:
#      print key + ': ' + str(meteruitvoer[key])

   if nparsedlines != expectedlines:
     sys.exit("ERROR: aantal regels (%i) is anders dan verwacht (%i)!" % (nparsedlines,expectedlines))


   return meteruitvoer
   
def lees_vorige_meting(huidige_meting):
   # Lees de vorige meting
   vorige_meting = {}
   try:
      with open(root_dir + vorige_meting_bestand,'r') as f:
         for line in f: 
            for key in meteruitvoerformaat:
               if line.startswith(key + ':'):
                  vorige_meting[key] = line[line.find(':')+1:-1]
   except IOError:
      pass
   if vorige_meting == {}:
      vorige_meting = huidige_meting
   else:
      for key in meteruitvoer_waarden:
         vorige_meting[key] = float(vorige_meting[key])
      vorige_meting['datum_tijd'] = datetime.strptime(vorige_meting['datum_tijd'], "%Y-%m-%d %H:%M:%S.%f")

   return vorige_meting

def schrijf_vorige_meting(meteruitvoer):
   # Schrijf de vorige meting
   try:
      with open(root_dir + vorige_meting_bestand,'w') as f:
         for key in meteruitvoer:
            f.write(key + ':' + str(meteruitvoer[key]) + '\n')
   except IOError:
      sys.exit('Probleem met wegschrijven huidige meting als vorige meting')

def maak_stroommeting(meteruitvoer):
   stroommeting = meting([meteruitvoer['gebruikt1'], meteruitvoer['gebruikt2'], meteruitvoer['geleverd1'], meteruitvoer['geleverd2']],
                         ["meettijd"    ,"gebruikt1"   ,"gebruikt2"    ,"geleverd1"    ,"geleverd2",
                          "vermogen1_in","vermogen2_in","vermogen1_uit","vermogen2_uit"             ],
                         meteruitvoer['datum_tijd'], delta = True)
   return stroommeting

def maak_gasmeting(meteruitvoer):
   gasmeting = meting([meteruitvoer['gas_gebruik']], 
                      ["meettijd", "gebruik", "m3/u"], 
                      datetime.strptime(meteruitvoer["gas_meetdatum"], "%y%m%d%H%M%S"),delta = True)
   return gasmeting
   
def maak_vermogenmeting(meteruitvoer):
   vermogenmeting = meting([meteruitvoer['vermogen_in'],
                    meteruitvoer['vermogen_uit']],
                    ['meettijd','vermogen_in','vermogen_uit'],meteruitvoer['datum_tijd'])
   return vermogenmeting
   
def maak_overigemeting(meteruitvoer):
   overigemeting = meting([meteruitvoer['meter_id'],meteruitvoer['huidigtarief'],meteruitvoer['max_vermogen'],
                           meteruitvoer['stroom_hoofdschakelaar'],meteruitvoer['tekst_code'],meteruitvoer['tekst'],
                           meteruitvoer['device_type'],meteruitvoer['gas_meter_id'],meteruitvoer['gas_hoofdschakelaar']],
                           ['meettijd','meterid','huidigtarief','max_vermogen','stroom_hoofdschakelaar','tekst_code','tekst',
                            'device_type','gas_meter_id','gas_hoofdschakelaar'],
                            meteruitvoer['datum_tijd'], verschillend = True)
   return overigemeting
   
   
def main():
   # Lees meter uitvoer en zet om naar dictionary
   huidige_meting = lees_meter()
   # Lees de vorige meting in
   vorige_meting = lees_vorige_meting(huidige_meting) 

   # Definieer de elektriciteits meting
   stroommeting = maak_stroommeting(huidige_meting)
   vorige_stroommeting = maak_stroommeting(vorige_meting)
   
   # Definieer de gas meting
   gasmeting = maak_gasmeting(huidige_meting)
   vorige_gasmeting = maak_gasmeting(vorige_meting)
   
   # Definieer de vermogen meting
   vermogenmeting = maak_vermogenmeting(huidige_meting)
   vorige_vermogenmeting = maak_vermogenmeting(vorige_meting)
   
   # Definieer de overige info
   overigemeting = maak_overigemeting(huidige_meting)
   vorige_overigemeting = maak_overigemeting(vorige_meting)

   # Schrijf de stroommeting
   stroommeting.schrijf_alles(vorige_stroommeting, root_dir, '.stroom')
      
   # Schrijf de gasmeting
   gasmeting.schrijf_alles(vorige_gasmeting, root_dir, '.gas')
   
   # Schrijf de vermogen meting
   vermogenmeting.schrijf_alles(vorige_vermogenmeting, root_dir, '.vermogen')
   
   # Schrijf de overige meetwaarden
   overigemeting.schrijf_alles(vorige_overigemeting, root_dir, '.overig')
   
   # Schrijf een nieuwe vorige meting
   schrijf_vorige_meting(huidige_meting)
   
if __name__ == "__main__":
    main()
