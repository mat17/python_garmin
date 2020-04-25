from bs4 import BeautifulSoup
import os
import re
import subprocess
import turtle as tt
import math
import matplotlib.pyplot as plt
import mplleaflet
from matplotlib.widgets import Cursor
import matplotlib.widgets as widgets

########## razne funkcije in algoritmi #########################################

def razdalja_2t(lon0, lat0, lon, lat):
    #earth mean radius = 6371.0088km (wiki_earth radius)
    #earth circumference around poles = 40,007.863km (wiki_earth circumference), podobno tudi po ramanujanovi formuli
    #ramanujan = pi + (3*(a+b) - (10*a*b+3*(a**2 + b**2))**0.5)
    #40,007.863km/2pi = 6367.449158993345km
    #zato vzamimo priblizek 6370km
    return (6378137**2 * math.cos(math.radians((lat0+lat)*0.5))**2 * math.radians(lon0-lon)**2 + 6370000**2 * math.radians(lat0-lat)**2)**0.5

##def kot_f(lon0, lat0, lon, lat):
##    return (((math.radians(lon-lon0))**2)*((math.sin(math.radians(lat)))**2)+(math.radians(lat-lat0))**2)**0.5

def rdp_algoritem(bsObj):
    tocke = bsObj.find_all('trkpt')
    vse_lat = [float(tocka.attrs['lat']) for tocka in tocke]
    vse_lon = [float(tocka.attrs['lon']) for tocka in tocke]
    vse_ele = [float(tocka.text) for tocka in bsObj.find_all('ele')]
    vsi_casi = [tocka.text for tocka in bsObj.find_all('time')]
    ele = sum(vse_ele)/len(vse_ele) #povprečje nadmorske visine
    toleranca = 0.5 #(v metrih)
    korak = len(vse_ele)//2
    
    def razdalja(lon1, lat1, lon2, lat2, lon3, lat3):
        dx = lon2 - lon1
        dy = lat2 - lat1
        if dy == 0:
            x = lon3
            y = lat1
        elif dx == 0:
            x = lon1
            y = lat3
        else:
            k1 = dy/dx
            k2 = -dx/dy
            n1 = lat1 - k1*lon1
            n2 = lat3 - k2*lon3
            x = (n2-n1) / (k1-k2)
            y = k2*x + n2
            # (x,y) je tocka na veznici med t1 in t2, ki je najblizje t3
        return razdalja_2t(lon3, lat3, x, y)
    
    # tukaj se dejansko zacne algoritem
    zacetna = 0
    koncna = min(korak, len(vse_lat)-1)
    ohrani = [0]
    while zacetna != len(vse_lat)-1:
        maxi = (0,0)
        for i in range(zacetna + 1, koncna):
            razdaljax = razdalja(vse_lat[zacetna], vse_lon[zacetna],
                                vse_lat[koncna], vse_lon[koncna],
                                vse_lat[i], vse_lon[i])
            if razdaljax > maxi[0]:
                maxi = (razdaljax, i)
        if maxi[0] <= toleranca:
            ohrani.append(koncna)
            zacetna = koncna
            koncna = min(zacetna + korak, len(vse_lat)-1)
        else:
            koncna = maxi[1]
    print(len(vse_lat), len(ohrani))
    # vrnemo seznam indeksov vseh tock, ki jih ohranimo
    return [vse_lon[i] for i in ohrani], [vse_lat[i] for i in ohrani], ohrani


def rdp_razdalja(lon1, lat1, lon2, lat2, lon3, lat3):
    dx = lon2 - lon1
    dy = lat2 - lat1
    if dy == 0:
        x = lon3
        y = lat1
    elif dx == 0:
        x = lon1
        y = lat3
    else:
        k1 = dy/dx
        k2 = -dx/dy
        n1 = lat1 - k1*lon1
        n2 = lat3 - k2*lon3
        x = (n2-n1) / (k1-k2)
        y = k2*x + n2
        # (x,y) je tocka na veznici med t1 in t2, ki je najblizje t3
    return x,y

def zgladi(seznam, roll=12):
    izhod = []
    i = 0
    while i < len(seznam)//2:
        relevantno = seznam[max(0,i-roll):max(0,i-roll)+2*roll]
        izhod.append(sum(relevantno)/len(relevantno))
        i += 1
    while i < len(seznam):
        relevantno = seznam[min(i+roll,len(seznam))-2*roll:min(i+roll,len(seznam))]
        izhod.append(sum(relevantno)/len(relevantno))
        i += 1
    return izhod

def percentil97(seznam, plusminus = '+'):
    delta = 0.03
    if plusminus == '+':
        osnova = 1
    elif plusminus == '-':
        osnova = 0
    predmet = sorted(seznam)
    return predmet[int((len(predmet)*abs(osnova-delta))//1)]


###################################################################################



######## ustvarjanje berljive .txt datoteke iz .gpx datoteke ######################        

# ustvari .txt kopijo z enakim imenom (do koncnice)
datoteke = []
for datoteka in os.listdir():
    if datoteka[-4:] == '.gpx':
        novo_ime = ''.join([datoteka[:-4],'.txt'])
        os.rename(datoteka, 'kopija.txt')
        with open(novo_ime, 'w') as txt:
            with open('kopija.txt', 'r') as file:
                for vrstica in file:
                    txt.write(vrstica)
        os.rename('kopija.txt', datoteka)
        datoteke.append(novo_ime)

###################################################################################



######### odpiranje datoteke in manipulacija s podatki ############################
######### risanje na zemljevid ####################################################


# bsObj in iskanje po oznakah
with open(datoteke[0], 'r') as f:
    
    # dobimo vse tocke
    tekst = ''.join(f.readlines())
    bsObj = BeautifulSoup(tekst, features='lxml')
    tocke = bsObj.find_all('trkpt')

    #rdp algoritem
    vse_lon, vse_lat, ohrani = rdp_algoritem(bsObj)
    # narisi tocke iz rdp algoritma
    zemljevid = plt.figure(1)
    #plt.plot(vse_lon, vse_lat, 'or')
    plt.plot(vse_lon, vse_lat, 'r')
    #plt.show()

    mplleaflet.show(fig=zemljevid)

    
    
    # ustvari zreducirano txt (gpx oblikovanje) datoteko
    # ta datoteka se bo uporabljala za risanje
    with open(''.join([datoteke[0][:-4], '_reducirano.txt']), 'w') as w:
        f.seek(0)
        for vrstica in f:
            if '<trkpt lat' in vrstica:
                break
            else:
                w.write(vrstica)
        for i in range(len(ohrani)):
            w.write('            <trkpt lat=\"'+str(vse_lon[i])+'\" lon=\"'+str(vse_lon[i])+'\">\n')
            w.write('            </trkpt>\n')
        w.write('        </trkseg>\n    </trk>\n</gpx>')
        f.seek(0)

    # ustvari txt datoteko, ki bo enako velika kot originalna,
    # ampak bodo vse točke premaknjene na RDP veznice
    with open(''.join([datoteke[0][:-4], '_rdp_hitrost_in_dolzina.txt']), 'w') as w:
        for vrstica in f:
            if '<trkpt lat' in vrstica:
                break
            else:
                w.write(vrstica)
        k = 0
        for v in re.split(', |\n', str(tocke).strip('[]')):
            if v[:6] == '<trkpt':
                if re.findall(r'lat=\"([0-9.]+)\"',v)[0] == str(vse_lat[k]) and re.findall(r'lon=\"([0-9.]+)\"',v)[0] == str(vse_lon[k]):
                    # imamo tocko iz RDP. jo preprosto vpisemo
                    k+=1
                    w.write('            '+v+'\n')
                else:
                    # imamo tocko ki ni iz RDP, premaknemo jo na veznico med RDP tocki k-1 in k.
                    x,y = rdp_razdalja(vse_lon[k-1], vse_lat[k-1], vse_lon[k], vse_lat[k], float(re.findall(r'lon=\"([0-9.]+)\"',v)[0]), float(re.findall(r'lat=\"([0-9.]+)\"',v)[0]))
                    w.write('            '+'<trkpt lat=\"'+str(round(y,7))+'\" lon=\"'+str(round(x,7))+'\">\n')
            elif v[:7] == '</trkpt':
                w.write('            '+v+'\n')
            elif v[:4] == '<ele' or v[:5] == '<time':
                w.write('                '+v+'\n')
            else:
                print(v)
        w.write('        </trkseg>\n    </trk>\n</gpx>')
        f.seek(0)
                                                                                        
                    
# bsObj in iskanje po oznakah
# hitrost racunamo s tockami, ki so bodisi RDP ali na veznici
with open(''.join([datoteke[0][:-4], '_rdp_hitrost_in_dolzina.txt']), 'r') as f:
    
    # dobimo vse tocke
    tekst = ''.join(f.readlines())
    bsObj = BeautifulSoup(tekst, features='lxml')
    tocke = bsObj.find_all('trkpt')
    
    # preverimo, da sta zacetni in koncni cas v istem dnevu.
    cas0 = (re.match(r'([^<>T]+)T([^<>Z]+)Z',tocke[0].time.text)[1],
            re.match(r'([^<>T]+)T([^<>Z]+)Z',tocke[0].time.text)[2])
    casK = (re.match(r'([^<>T]+)T([^<>Z]+)Z',tocke[-1].time.text)[1],
            re.match(r'([^<>T]+)T([^<>Z]+)Z',tocke[-1].time.text)[2])
    zacetni = cas0[1][:cas0[1].index('.')].split(':')
    zacetni = sum([int(i)*j for i,j in zip(zacetni,[3600,60,1])])
    koncni = casK[1][:casK[1].index('.')].split(':')
    koncni = sum([int(i)*j for i,j in zip(koncni,[3600,60,1])])
    if cas0[0] != casK[0]:
        koncni = koncni + zacetni
        #v tem primeru je koncni > 24h (v sekundah)

    # podatki za vsako tocko
    lat0 = 0
    lon0 = 0
    ele0 = 0
    time = 0
    sum_razdalja = 0
    for tocka in tocke:
        lat = float(tocka.attrs['lat'])
        lon = float(tocka.attrs['lon'])
        #plt.plot(lon, lat, '.g')
        ele = float(tocka.ele.text)
        datum = re.match(r'([^<>T]+)T([^<>Z]+)Z',tocka.time.text)[1]
        # 'time' naj bo st. sekund od zacetka do casa, v katere mse zgodi ta tocka
        time = re.match(r'([^<>T]+)T([^<>Z]+)Z',tocka.time.text)[2]
        time = time[:time.index('.')].split(':')
        time = sum([int(i)*j for i,j in zip(time,[3600,60,1])])
        if datum == cas0[0]:
            time = time - zacetni
        else:
            time += 24*3600 - zacetni
        # imamo 4 stevila: lat, lon, ele in time
        if time != 0:
            razdalja = razdalja_2t(lon0, lat0, lon, lat) # razdalja v metrih
            razdalja = (razdalja**2 + (ele-ele0)**2)**0.5 #upostevamo tudi z koordinato
            cas = time - time0 # najverjetneje 1s (casovni interval meritve)
            hitrost = 60 / ((razdalja/cas) * 3.6) # min/km
            hitrosti.append(hitrost)
            sum_razdalja += razdalja
            razdalje.append(sum_razdalja/1000)
            min_ele = min(min_ele, ele)
            max_ele = max(max_ele, ele)
            #print(hitrost, razdalja, sum_razdalja/1000)
        else:
            hitrosti = []
            razdalje = [0]
            min_ele = ele
            max_ele = ele
            # to se izvede samo pri zacetni tocki!!!
            pass #zacetna tocka
        lat0 = lat
        lon0 = lon
        ele0 = ele
        time0 = time
    print(sum_razdalja/1000)
    grafi = plt.figure(2)
    graf_v = plt.subplot()
    graf_v.set_xlabel('razdalja[km]')
    graf_v.set_ylabel('hitorst[min/km]', color = 'r')
    zglajene = zgladi(hitrosti)
    graf_v.plot(razdalje[1:], zglajene, 'r')
    graf_v.set_ylim([min((percentil97(zglajene, '+')+1)//1 + 1, 12), percentil97(zglajene, '-')//1 - 1])
    #graf_v.gca().invert_yaxis()
    graf_v.axhline(y=(100/6)/(sum_razdalja/time))
    graf_v.grid(True)

    graf_h = graf_v.twinx()
    graf_h.set_ylabel('višina[m]', color = 'g')
    graf_h.fill_between(razdalje, zgladi([float(tocka.text) for tocka in bsObj.find_all('ele')], roll=6), min_ele//1, facecolor = 'g', alpha=0.2)
    graf_h.set_ylim([min_ele//10 * 10, max(max_ele, min_ele + sum_razdalja//46)])

    cursor = Cursor(graf_h, useblit=True, linewidth=2, horizOn=False)
#    grafi.canvas.mpl_connect('motion_notify_event', cursor.mouse_move)
    plt.savefig("graf_hitrosti_in_elevacije.png")
    plt.show()

    
##    
##    plt.subplot(211)
##    plt.plot(razdalje[1:], hitrosti, 'r')
##    plt.axhline(y=(100/6)/(sum_razdalja/time))
##    plt.ylim([2,10])
##    plt.gca().invert_yaxis()
##    plt.grid(True)
##    plt.subplot(212)
##    plt.fill_between(razdalje, [float(tocka.text) for tocka in bsObj.find_all('ele')], min_ele//1, facecolor = 'g', alpha=0.2)
##    plt.grid(True)
##    plt.show()

    
      

