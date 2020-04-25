from bs4 import BeautifulSoup
import os
import re

# dobimo vse točke od poti, ki ima dobre koordinate
with open('predmeja.txt','r') as fin:
    # dobimo vse tocke
    tekst = ''.join(fin.readlines())
    bsObj = BeautifulSoup(tekst, features='lxml')
    tocke = bsObj.find_all('trkpt')

#print(tocke[0].attrs['lat'])
#print(tocke[0].find('time').text)
    referenca = []
    for tocka in tocke:
        if tocka.find('time').text[11:-1] in ['16:39:07',
                                              '16:40:18',
                                              '16:42:50',
                                              '16:47:06',
                                              '16:49:42',
                                              '16:51:21',
                                              '16:53:35']:
            print(tocka.attrs['lat'],tocka.attrs['lon'])
            referenca.append((tocka.attrs['lat'],tocka.attrs['lon']))

print()

# odpremo datoteko, ki ima slabe gps koordinate
with open('predmeja_nick.txt','r') as fin:
    # dobimo vse tocke
    tekst = ''.join(fin.readlines())
    bsObj = BeautifulSoup(tekst, features='lxml')
    tocke = bsObj.find_all('trkpt')

    timestamps = ['15:03:38',
                  '15:04:32',
                  '15:06:35',
                  '15:09:45',
                  '15:11:44',
                  '15:12:55',
                  '15:14:32']

#print(tocke[0].attrs['lat'])
#print(tocke[0].find('time').text)
    kljucne = []
    stevec = 0
    stevci = []
    for tocka in tocke:
        tocka.extensions.extract();
        if tocka.find('time').text[11:-5] in timestamps:
            print(tocka.attrs['lat'],tocka.attrs['lon'])
            kljucne.append((tocka.attrs['lat'],tocka.attrs['lon']))
            stevci.append(stevec)
            stevec = 0
        else:
            stevec += 1

print()

delte = []
for i in range(len(timestamps)):
    deltax = float(kljucne[i][0])-float(referenca[i][0])
    deltay = float(kljucne[i][1])-float(referenca[i][1])
    delte.append((deltax,deltay))
    if i == 0:
        continue
    deltax = (delte[-2][0] - delte[-1][0])/stevci[i]
    deltay = (delte[-2][1] - delte[-1][1])/stevci[i]
    for j in range(stevci[i]):
        #print(tocke[sum(stevci[:i])+i-1+j]['lat'])
        lat = float(tocke[sum(stevci[:i])+i-1+j]['lat']) + j*deltax
        lon = float(tocke[sum(stevci[:i])+i-1+j]['lon']) + j*deltay
        tocke[sum(stevci[:i])+i-1+j]['lat'] = str(lat)
        tocke[sum(stevci[:i])+i-1+j]['lon'] = str(lon)
        #print('x', tocke[sum(stevci[:i])+i-1+j]['lat'])
    for j in range(sum(stevci[i+1:])+len(stevci)-i):
        #print(tocke[sum(stevci[:i+1])+i-1+j]['lat'], stevci[i]*deltax)
        lat = float(tocke[sum(stevci[:i+1])+i-1+j]['lat']) + stevci[i]*deltax
        lon = float(tocke[sum(stevci[:i+1])+i-1+j]['lon']) + stevci[i]*deltay
        tocke[sum(stevci[:i+1])+i-1+j]['lat'] = str(lat)
        tocke[sum(stevci[:i+1])+i-1+j]['lon'] = str(lon)
        #print('xx', tocke[sum(stevci[:i+1])+i-1+j]['lat'])
    print()


##with open('predmeja_nick_popravljeno.txt','w') as fout:
##    fout.write(str(tocke))
        



#print(tocke[0].attrs['lat'])
#print(tocke[0].find('time').text)
####print()
####stevec = 19
####for tocka in tocke:
####    if tocka.find('time').text[11:-5] == '15:03:38':
####        print(tocka)
####        tocka['lat']=('Bar')
####        print()
####        print(tocka)

#print(re.sub(r'lat=\"([0-9\.]+)\" lon=\"([0-9\.]+)\"', 'lat=\"{0}\" lon=\"{1}\"'.format(str(float(r'\1')+0.1), str(float(r'\2')+0.1)), str(tocke[3190])))
#>>>
# print(re.findall(r'lat=\"([0-9\.]+)\" lon=\"([0-9\.]+)\"', str(tocke[3190])))
#[('45.927419', '13.871888')]
