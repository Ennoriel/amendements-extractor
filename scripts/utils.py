from os import walk, path, environ
from pymongo import MongoClient
import json
from scripts.acteur import Acteur

mongo_url = environ['MONGO_URL']
mongo_db = environ['MONGO_DB']
mongo_collection_acteurs = 'acteurs-16'


def walk_level(some_dir, level=1):
    some_dir = some_dir.rstrip(path.sep)
    assert path.isdir(some_dir)
    num_sep = some_dir.count(path.sep)
    for root, dirs, files in walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]


def import_records(dir_name, db_name, obj_instance):
    client = MongoClient(mongo_url, retryWrites=False)[mongo_db][db_name]
    records = []
    for root, dirs, files in walk(dir_name):
        for file in files:
            with open(path.join(root, file)) as json_file:
                data = json.load(json_file)
                record = obj_instance(data)
                records.append(record)

    client.insert_many([record.__dict__ for record in records])
    

def import_acteurs():
    client = MongoClient(mongo_url, retryWrites=False)[mongo_db][mongo_collection_acteurs]
    client.delete_many({})

    # Load file https://data.assemblee-nationale.fr/acteurs/deputes-en-exercice (Fichier json (composite))
    import_records(
        'C://Users//Maxime//Downloads//AMO10_deputes_actifs_mandats_actifs_organes.json//json//acteur',
        mongo_collection_acteurs,
        Acteur
    )

    # Load file https://www2.assemblee-nationale.fr/instances/liste/groupes_politiques/effectif/(hemi)/true
    # request https://www2.assemblee-nationale.fr/ezjscore/call/
    # reformated with js: a = { "error_text": "", "content": { "s1": { ...
    # b = Object.entries(a.content).map(([k, v]) => ({place: k, ...v}))
    # c = b.map(p => ({...p, departement: p.circo.split('(')[0], circo: `(${p.circo.split('(')[1]}`}))
    # also found here: https://www2.assemblee-nationale.fr/deputes/hemicycle in the html
    db_deputees = list(client.find().sort("nom", 1).sort("prenom", 1).limit(5000))
    count = 0

    with open('deputees16.json', encoding='utf-8') as json_file:
        deputees = json.load(json_file)
        for deputee in deputees:
            for db_deputee in db_deputees:
                # print(db_deputee['prenom'] + ' ' + db_deputee['nom'])
                if deputee['nom'] == db_deputee['prenom'] + ' ' + db_deputee['nom']:
                    count = count + 1
                    db_deputees.remove(db_deputee)
                    try:
                        pass
                        client.update_one({"_id": db_deputee['_id']}, {
                            "$set": {
                                "place": deputee['place'],
                                "departement": deputee['departement'],
                                "circo": deputee['circo'],
                                "groupe": deputee['groupe'],
                                "photo_id": deputee['id']
                            }
                        })
                    except:
                        print(deputee)
                    break
    print(count)
    print(db_deputees)


if __name__ == '__main__':
    import_acteurs()



