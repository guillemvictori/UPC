#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys


#Nom de l'arxiu vhdl que es passa per paràmetres, i que ens servirà per generar el TB
name = sys.argv[1]
vhdl = open(name, 'r')
text = vhdl.read()

nom = name.partition(".vhd")

#Generem un nou arxiu .vhd que serà el testbench
tb = open(nom[0] + "_tb" + nom[1], 'w')

###################################
### 1- Escriure en 'tb' tot el contingut fins al primer entity

pos1 = text.find("entity")

tb.write(text[:pos1])

### 2- identificar el nom de l'entity  **pos1+7 és la posició de la primera lletra del "n_entity"
n_entity = text[ pos1+7 : text.find(" ", pos1+7)]
print n_entity

### 3- anunciar l'entity

tb.write("entity " + n_entity + "_tb is" + "\nend entity " + n_entity + "_tb;\n\n")



### 4- escriure els ports en el component
tb.write("architecture behav of " + n_entity + "_tb is\n\t" + "component my_" + n_entity)
pos_aux = text.find("port")
pos_aux2 = text.find("end", pos1)


### 4.1- guardar els ports
port = text[pos_aux+4 : pos_aux2 - 3]
port = port[port.find('(') + 1: pos_aux2 - 3]
port2 = port
port2 = port2.replace("\n", "")
port2 = port2.replace("\t", "")
port_list = port2.split(';')
#print port_list

T = []
aux = []
for p in port_list:
    L = p.split(':')
    L[0] = L[0].strip()
    L[1] = L[1].strip()
    if L[0].find(',') != -1:
        aux = L[0].split(',')
        for a in aux:
            a.strip()
            tup = (a, L[1])
            T.append(tup)
        aux = []
    else:
        tup = (L[0],L[1])
        T.append(tup)



tb.write("\n\tport(")
for t in T:
    tb.write("\n\t\t" + t[0] + " : " + t[1] + ";")
tb.write("\n\t\t );" + "\n\tend component;")

### 5- for dut...
tb.write("\n\tfor dut : my_" + n_entity + " use" + "\n\t\tentity work." + n_entity + ";")

### 6- signals
###classificar entre serie, bus
bus = []
serie = []
for t in T:
    if t[1].find("std_logic_vector") != -1:
        bus.append(t[0])
    else:
        serie.append(t[0])
tb.write("\nsignal ")
for t in serie:
    if t == serie[len(serie) - 1]:
        tb.write(",\n\t\tt_" + t + " : std_logic;\n")
    else:
        if t == serie[0]:
            tb.write(" t_" + t)
        else:
            tb.write(",\n\t\tt_" + t)
for t in bus:
    if t == bus[len(bus) - 1]:
        tb.write(",\n\t\tt_" + t + " : std_logic_vector; \n")
    else:
        if t == bus[0]:
            tb.write("t_" + t)
        else:
            tb.write(",\n\t\tt_" + t)

### 7- port map
tb.write("begin" + "\ndut : " + "my_" + n_entity + " port map(")

for t in T:
    tb.write("\n\t " + t[0] + " <= " + "t_" + t[0])
    if t == T[len(T) - 1]:
        tb.write("\n\t);")
### 8- clock?

r = raw_input("Vols afegir un CLOCK al testbench? (S/N) \n")

if r == 'S' or r == 's':

    r2 = raw_input("Digues el període(ns): \n")
    r2 = float(r2)   * 0.5
    tb.write("\nclk_process: process" + "\n\tbegin")
    tb.write("\n\t\tclk <= '0';" + "\n\t\twait for " + str(r2) + " ns;")
    tb.write("\n\tfor i in 1 to 20 loop \n\t\tclk <= not clk; \n\t\twait for " + str(r2) + " ns;")
    tb.write("\n\tend loop; \n\twait;")
    tb.write("\nend process;")
    print "\n\n\n\n\n\n\tTestBench: " + n_entity + "_tb, ja està apunt!"
    print "\n\n\t\t\tGràcies\n\n\n"
else:
    print "\n\n\n\n\n\n\tTestBench: " + n_entity + "_tb, ja està apunt!"
    print "\n\n\t\t\tGràcies\n\n\n"


tb.write("\nend behav")


