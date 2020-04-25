with open('blip.txt', 'r+') as f:
    line = f.readline()
    while line:
        if 'jejhata' in line:
            print(f.tell())
        line = f.readline()
    f.seek(36,0)
    print(f.tell())
    print(f.read())

#torej: ce nastavis f.seek na konec neke vrstice
# bos pravzaprav zacel
