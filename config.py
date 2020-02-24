import numpy as np
import codecs, json
path = './data/faces.json'

def loadJson():
    file = open(path,'r')
    faces = json.load(file)
    data = faces['data']
    names = []
    faces = []

    for item in data:
        names.append(item['name'])
        faces.append(np.array(item['face']))

    return names, faces

def saveFace(name, face):
    data = face.tolist()
    file = open(path,'r')
    faces = json.load(file)

    faces['data'].append({'name': name, 'face': data})
    print(json.dumps(faces, indent=2))

    outfile = open(path,'w')
    json.dump(faces, outfile)
    print('successful stored')
    return
