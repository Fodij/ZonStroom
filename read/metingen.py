from datetime import datetime, timedelta
import operator
import os
import string

class meting:

   def __init__(self, meetwaarden, labels, datum, delta = False, verschillend = False):
       self.meetwaarden = meetwaarden
       self.labels = labels
       self.datum = datum
       self.delta = delta
       self.verschillend = verschillend
    
   def schrijftotaal(self, tijd, bestand, vorige_tijd, vorig_bestand):
      # Lees entries van huidige bestand
      data = {}
      begin = {}
      eind = {}
      try:
         f = open(bestand,'r')
         for line in f:
            if line.startswith('tijd'):
               continue
            waarden = string.split(line,';')
            key = int(waarden[0])
            data[key] = [waarden[1],waarden[2]]
            begin[key] = [float(w) for w in waarden[3:3+len(self.meetwaarden)]]
            eind[key] = [float(w) for w in waarden[3+len(self.meetwaarden):3+2*len(self.meetwaarden)]]
         f.close()
      except IOError:
         pass
      if tijd in data:
         eind[tijd] = self.meetwaarden
         data[tijd][1] = self.datum
      else:
         # Huidige tijd moet worden toegevoegd. 
         # Controleer of de vorige periode kan worden afgesloten
         # Als er een bestand is kunnen we dit niet onafhankelijk wijzigen
         if bestand == vorig_bestand:
            if vorige_tijd in data:
               eind[vorige_tijd] = self.meetwaarden
               data[vorige_tijd][1] = str(self.datum) 
         # Als het om een ander bestand gaat verwerken we dat op dezelfde manier als het huidge
         elif vorig_bestand != '':
            self.schrijftotaal(vorige_tijd,vorig_bestand,0,'')
         begin[tijd] = self.meetwaarden
         eind[tijd] = self.meetwaarden
         data[tijd] = [str(self.datum), str(self.datum)]
     
      try:
         f = open(bestand,'w')
      except:
         sys.exit("Kon bestand %s niet openen" % bestand)
      f.write('tijd;meettijd start;meettijd eind')
      for label in self.labels[1:(len(self.labels)-1)/2+1]:
         f.write(';' + label)
      f.write('\n');
      for key in sorted(data):
         f.write(str(key))
         f.write(';' + str(data[key][0]) + ';' + str(data[key][1]))
         for stand in begin[key]:
            f.write(';' + str(stand))
         for stand in eind[key]:
            f.write(';' + str(stand))
         verbruik = map(operator.sub,eind[key],begin[key])
         for stand in verbruik:
            f.write(';' + str(stand))            
         f.write('\n')
      f.close()
      
   # Schrijf de huidige meting naar het meetbestand
   def schrijf_meting(self, bestand, vorige):

      if not os.path.isfile(bestand):
         with open(bestand, 'a') as f:
            f.write(self.labels[0])
            for label in self.labels[1:len(self.labels)]:
               f.write(";" + label)
            f.write("\n")
      with open(bestand, 'a') as f:
         f.write(str(self.datum))
         for waarde in self.meetwaarden:
            f.write(";" + str(waarde))
         if self.delta:
            tijdverschil = (self.datum - vorige.datum).total_seconds()/3600
            if (tijdverschil < 0.001):
               tijdverschil = 360000.0
            for a,b in zip(self.meetwaarden,vorige.meetwaarden):
               f.write(";" + str((a - b)/tijdverschil))
         f.write("\n")
  
  # Controleer of de directory bestaat, zo niet maak die aan
   def _check_directory(self, dirname):
      if not os.path.exists(dirname):
         os.makedirs(dirname)
      elif not os.path.isdir(dirname):
         sys.exit('Directory %s is geen directory!' % dirname)
          
   def schrijf_alles(self, vorige, root_dir, suffix):

      if (self.datum == vorige.datum):
         return
      geen_verschil = True  
      if self.verschillend:     
         for a,b in zip(self.meetwaarden,vorige.meetwaarden):
            if a != b:
               geen_verschil = False
      if (not self.verschillend) or (not geen_verschil):
         dirname = root_dir + str(self.datum.year) + '/' + "%.2d" % self.datum.month
         filename = dirname + '/'+ "%.2d" % self.datum.day + suffix
         # Update meting
         self._check_directory(dirname)
         self.schrijf_meting(filename, vorige)
         
         if self.delta:
            # Update jaartotaal
            jaarfile = root_dir + 'jaar' + suffix
            self.schrijftotaal(self.datum.year,jaarfile, self.datum.year-1, '')

            # Update maandtotaal    
            maandfile = root_dir + str(self.datum.year) + '/' + 'maand' + suffix
            vorige_maand = self.datum.month-1
            if vorige_maand == 0:
                vorige_maandfile = root_dir + str(self.datum.year-1) + '/' + 'maand' + suffix
                vorige_maand = 12
            else:
                vorige_maandfile = root_dir + str(self.datum.year) + '/' + 'maand' + suffix
            self.schrijftotaal(self.datum.month, maandfile, vorige_maand, vorige_maandfile)
            # Update dagtotaal   
            dagfile = dirname + '/' + 'dag' + suffix
            vorige_dag = (self.datum - timedelta(days=1))
            vorige_dagfile = root_dir + str(vorige_dag.year) + '/' + "%.2d" % vorige_dag.month + '/' + "dag" + suffix
            self.schrijftotaal(self.datum.day, dagfile, vorige_dag.day, vorige_dagfile)

    
