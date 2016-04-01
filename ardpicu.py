#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import commands #per recollir resposta d'execució de comanda
import time
import shutil #per bellugar arxius

# Versió d'aquest fitxer ardpicu: V0

u"""
Entorn Linux

ARDUINO:
El fitxer de comprovació de l'assemblat es genera automàticament.
La creació dels fitxers .elf i hexadecimals també.
La sintaxi d'execució del script per decidir si volem escriure o llegir és:

$ python nomd'aquestfitxer.py nomdelfitxerarduinosenseextensió

Per defecte llegirà ('r' de read) de la placa sense haver de posar aquest
paràmetre. Si es vol que es transfereixi l'arxiu a la placa s'afegirà un 
espai i la lletra 'w' (write).

PICOCOM:
Els paràmetres per defecte estàn detallats més avall i es mostren per
pantalla. Només prement retorn (o intro) s'escolleix la decisió per defecte
(senyalada en majúscula).
"""

u"""
Per donar-li permisos de lectura i escriptura (perquè no els demani
quan s'executa el programa) es pot escriure el següent (Ex: port ACM0):

$ sudo chmod a+rw /dev/ttyACM0

En aquest exemple el port USB es diu ACM0, però si es disposa d'altres
dispositius amb noms diferents només s'han d'afegir de la mateixa manera.
"""

############################### ARDUINO ###############################
if len(sys.argv)==1: #si només s'escriu el nom d'aquest fitxer python
	print u"\n\t----- Falten arguments. No es pot iniciar el programa. -----\n"
	sys.exit() #surt del programa
else:
	# Si aquesta part no funciona aturar el programa,
	# doncs pot ser que l'arxiu dmesg estigui corromput, provocant
	# que aparegui el mateix port repetit altres vegades o que 
	# detecti altres ports amb una sintaxi semblant.
	# Els missatges generats durant l'arranc del sistema i la
	# depuració de les aplicacions formen el buffer de missatges
	# del nucli (dmesg), del que es pot obtenir un llistat.
	# Fent un dmesg al terminal es veu el port tty que interessa.
	# Es pot obtenir un arxiu del dmesg executant: dmesg>dmesg.txt
	# El port es mostra amb les lletres tty davant.
	# Si es coneix es pot assignar directament. Per exemple, si el
	# nom del port és ACM0 haurem d'escriure això quan ho demani
	# i el port usb quedarà assignat com a:	port_usb=ttyACM0
	# Per comprovar en el kernel la última activitat del sistema
	# també es pot fer:	dmesg|tail

	# Mètode de cerca per a un cas concret consultant l'arxiu dmesg:
	# Com que sé que el que m'interessa té un espai davant i després
	# es troba declarat com a aparell USB (" ttyACM0: USB ACM device")
	# en aquest cas concret, faig la cerca directament de " tty" i 
	# sabent també que els darrers caràcters poden ser: ': [\n&'.
	dmesg_cerca=raw_input("\n\tIntrodueix el nom del port o prem RETURN per cercar-lo: ")
	if dmesg_cerca=="":
		print "\t*****   Detecció del port de comunicacions USB   *****\n"
		dmesg=commands.getoutput("dmesg|tail") #s'opta per aquesta opció més curta
		dmesg=dmesg+"&" #s'afegeix per si el nom del port és l'últim que apareix

		comprova=[]
		port_usb=""
		inici=-1
		try:
			while True:
				# Realitza cada cerca des d'un caràcter posterior a 
				# la última coincidència trobada, perquè no doni error
				# si arriba al final excedeix la llargada de la cerca.
				inici = dmesg.index(' tty', inici+1) #si troba " tty"
				j=inici+1
				caracter=""": [&\n"""

				while dmesg[j] not in caracter: #mentre no trobi els caràcters
					port_usb+=dmesg[j] #afegeix lletres
					j+=1 

				if len(port_usb)>4: #si es compleix és perquè l'ha detectat
					break
			else:
				inici+=1

		except ValueError: #quan ja no es troba cap coincidència
			print u"\t\tEl port utilitzat és:",port_usb #s'obté el resultat.
			# Lògicament ha discriminat a " TTY" en la cerca.
	else:
		port_usb="tty"+dmesg_cerca


print "\t\t  Connexió amb el port USB: "+port_usb+"\n"
time.sleep(1)

# Comprova que l'Arduino està connectat i preparat per rebre ordres:
usb_connect= commands.getoutput("sudo avrdude -c arduino -P /dev/"+port_usb+" -p m328p")


if "can't open" in usb_connect: #si detecta que no està connectada:
	print "\n\t-----  Ja pots connectar la placa  -----\n"
	raw_input("\tPrem Retorn (o Intro) quan estigui connectada\n\t\to CTRL+C per sortir.")
else:
	print usb_connect+"\n"

fitxer=str(sys.argv[1]) #si n'hi ha més de 1 vol dir que s'ha entrat el nom de l'arxiu com a mínim

if os.path.exists(fitxer+".S")==False:
	print u"\tEl fitxer que es demana no existeix.\n"
	sys.exit() #surt del programa
else:
	if len(sys.argv)==2: #si només hi ha el nom de l'arxiu
		lectura_escriptura="r" #per defecte, s'assigna lectura (r) a la placa
	else:
		lectura_escriptura=sys.argv[2] #si n'hi ha més de 2 s'ha entrat una lletra

print "*****  Iniciant generació i lectura o transferència de fitxers a Arduino  *****\n"

if lectura_escriptura=='r':
	print "\t***** Llegint de la placa *****\n"
	time.sleep(1)
elif lectura_escriptura=='w':
	print "\t***** Transferint a la placa *****\n" #que escriurà el programa a la placa
	time.sleep(1)
else:
	print u"\t----- No es reconeix aquest paràmetre. S'assigna r (read) -----\n"
	lectura_escriptura='r' #s'assigna lectura per no fer el codi més llarg
	time.sleep(1)

# Les següents comandes s'assignen a variables i són executades
# seguidament. Alguns dels paràmetres inclosos són:
# últim paràmetre:	indica el fitxer d'entrada
# -o:	indica el fitxer de sortida
# -mmcu:	model microcontrolador
# -E:	analitza possibles errors
# -U:	transferència de fitxers binaris:
# flash:	indica la memòria on fa la transferència
# r,w:	indica si llegeix o escriu (respectivament)

#1 Executable amb el codi assemblat:
comanda1="avr-gcc -mmcu=atmega328p -o "+fitxer+".elf "+fitxer+".S"
#2 Assemblat i anàlisi de possibles errors:
comanda2="avr-gcc -mmcu=atmega328p -o "+fitxer+".asm -E "+fitxer+".S"
#3 Converteix l'executable a format hexadecimal:
comanda3="avr-objcopy --output-target=ihex "+fitxer+".elf "+fitxer+".hex"
#4 Transferència de fitxers binaris:
comanda4="sudo avrdude -c arduino -P /dev/"+port_usb+" -p m328p -U flash:"+lectura_escriptura+":"+fitxer+".hex:i"
#5 Executable sense configuracions de funcionalitats extres:
comanda5="avr-gcc -mmcu=atmega328p -nostartfiles -o "+fitxer+"_nostartfiles.elf "+fitxer+".S"
#6 Desassemblat en codi font sense informació extra de l'original:
comanda6="avr-objdump -S "+fitxer+".elf > "+fitxer+".disam"
#7 Desassemblat en codi font sense informació extra ni interrupcions,
#apuntadors de pila, inicialització d'alguns registres,...:
comanda7="avr-objdump -S "+fitxer+"_nostartfiles.elf > "+fitxer+"_nostartfiles.disam"

os.system(comanda1)
os.system(comanda2)
os.system(comanda3)
os.system(comanda4)
os.system(comanda5)
os.system(comanda6)
os.system(comanda7)


############################### PICOCOM ###############################
opcio="SsYy"
resposta=raw_input("Vols utilitzar el terminal picocom (S/n)? ")

velocitat_banda="9600"
if resposta in opcio:
	print u"""\n\tVelocitat de banda per defecte:  {} kbps""".format(velocitat_banda)

	resposta=raw_input("\nVols mantenir la velocitat de banda (S/n)? ")
	if resposta not in opcio:
		velocitat_banda=raw_input("Introdueix la velocitat de banda en kbps: ")

	print u"""\n\tRecorda que per sortir del terminal picocom
	has de prémer		CTRL+A+X\n"""
	time.sleep(1)
	comanda_p="sudo picocom -b "+velocitat_banda+" /dev/"+port_usb
	os.system(comanda_p)



############################### CUTECOM ###############################
opcio="SsYy"
resposta=raw_input("\n\nVols utilitzar el terminal cutecom (S/n)? ")
if resposta in opcio:
	print u"""\n\tRecorda que has de posar el nom del port en la
	part superior:			/dev/"""+port_usb
	print u"\n\tLa configuració de comunicació per defecte és:"
	print u"\n\t\tBaud rate:	{} kbps".format(velocitat_banda)
	time.sleep(0.5)
	print u"\n\t\tData bits:	8 bits".format(velocitat_banda)
	time.sleep(0.5)
	print u"\n\t\tStop bits:	1 bit(s)".format(velocitat_banda)
	time.sleep(0.5)
	print u"\n\t\tParity:		None".format(velocitat_banda)
	time.sleep(0.5)
	comanda_c="cutecom"
	os.system(comanda_c)


# NETEJA DELS ARXIUS GENERATS CAP A ALTRES CARPETES
# Les comandes per Linux estan comentades perquè demana permisos.
#os.system("mkdir arxius")
ruta=os.getcwd()
if os.path.exists("arxius")==False:
	os.mkdir("arxius")
	#moure="sudo mv "+fitxer+".elf /arxius"
	#os.system(moure)
if os.path.exists("arxius/"+fitxer)==False:
	os.mkdir("arxius/"+fitxer)
ruta_completa=ruta+"/arxius/"+fitxer #ruta completa (amb carpeta per fitxer)

#1
if os.path.exists(fitxer+".elf")==False:
	print "\n\tNo s'ha generat el fitxer:\t{}.elf\n\tperquè existeixen errors en:\t{}.S".format(fitxer,fitxer)
else:
	try:
		shutil.move(fitxer+".elf", ruta_completa)
	except:
		os.remove(ruta_completa+"/"+fitxer+".elf", )
		shutil.move(fitxer+".elf", ruta_completa)

#2
try:
	shutil.move(fitxer+".asm", ruta_completa)
except:
	os.remove(ruta_completa+"/"+fitxer+".asm", )
	shutil.move(fitxer+".asm", ruta_completa)

#3
if os.path.exists(fitxer+".hex")==False:
	print "\n\tNo s'ha generat el fitxer:\t{}.hex\n\tperquè existeixen errors en:\t{}.S".format(fitxer,fitxer)
else:
	try:
		shutil.move(fitxer+".hex", ruta_completa)
	except:
		os.remove(ruta_completa+"/"+fitxer+".hex", )
		shutil.move(fitxer+".hex", ruta_completa)

#5
if os.path.exists(fitxer+"_nostartfiles.elf")==False:
	print "\n\tNo s'ha generat el fitxer:\t{}_nostartfiles.elf\n\tperquè existeixen errors en:\t{}.S".format(fitxer,fitxer)
else:
	try:
		shutil.move(fitxer+"_nostartfiles.elf", ruta_completa)
	except:
		os.remove(ruta_completa+"/"+fitxer+"_nostartfiles.elf", )
		shutil.move(fitxer+"_nostartfiles.elf", ruta_completa)

#6
try:
	shutil.move(fitxer+".disam", ruta_completa)
except:
	os.remove(ruta_completa+"/"+fitxer+".disam", )
	shutil.move(fitxer+".disam", ruta_completa)

#7
try:
	shutil.move(fitxer+"_nostartfiles.disam", ruta_completa)
except:
	os.remove(ruta_completa+"/"+fitxer+"_nostartfiles.disam", )
	shutil.move(fitxer+"_nostartfiles.disam", ruta_completa)


print """\n\tEls arxius generats per a la compilació i execució s'han
	traslladat a una carpeta amb el nom del mateix fitxer i 
	dins de la carpeta arxius, creada en la carpeta actual.\n"""
time.sleep(1)
print "\n\t\tFins la pròxima!!!\n"

