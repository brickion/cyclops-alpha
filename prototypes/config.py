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

def loadFaceAndMeta():
    file = open(path,'r')
    faces = json.load(file)
    data = faces['data']
    names = []
    faces = []
    metas = []

    for item in data:
        names.append(item['name'])
        faces.append(np.array(item['face']))
        metas.append(item['meta'])
    return names, faces, metas

def saveFace(name, face):
    data = face.tolist()
    file = open(path,'r')
    faces = json.load(file)
    meta = {"first_seen": 0, "first_seen_this_interaction": 0, "last_seen": 0, "seen_count": 1, "seen_frames": 1, "name": name}

    faces['data'].append({'name': name, 'face': data, 'meta': meta})
    print(json.dumps(faces, indent=2))

    outfile = open(path,'w')
    json.dump(faces, outfile)
    print('successful stored')
    return

def saveFaceAndMeta(name, face, Meta):
    data = face.tolist()
    file = open(path,'r')
    faces = json.load(file)

    faces['data'].append({'name': name, 'face': data, 'meta': meta})
    print(json.dumps(faces, indent=2))

    outfile = open(path,'w')
    json.dump(faces, outfile)
    print('successful stored')
    return
