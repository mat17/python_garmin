with open('predmeja_nick_popravljeno_gpx.txt', 'r') as f:
    datoteka = f.read()

datoteka = datoteka.replace(', ', '\n      ')
datoteka = datoteka.replace('\n<trkpt', '\n      <trkpt')
datoteka = datoteka.replace('\n</trkpt', '\n      </trkpt')
datoteka = datoteka.replace('\n<ele', '\n        <ele')
datoteka = datoteka.replace('\n<time', '\n        <time')
datoteka = datoteka.replace('\n\n', '\n')
print(datoteka[:1000])

with open('predmeja_nick_popravljeno_gpx.txt', 'w') as f:
    f.write(datoteka)
    print('koncano!')
