from flask import Flask, json, request, abort
from pubmed.PubMedSearch import PubMedHandler

from bioc import biocxml, biocjson
import json
import requests
from nltk.stem import PorterStemmer

with open("blacklist.json", 'r') as json_file:
    BLACKLIST = set([a.lower() for a in json.load(json_file)])

api = Flask(__name__)
URL3 = "http://bern2.korea.ac.kr/plain"
URL = "http://localhost:8081/tagme_string"
api_tator = "https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/biocjson?{pmtype}={docids}"
URL_PMC = "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/{mode}.cgi/BioC_xml/{id}/unicode"

pmc_api_key = "9fa42ec62c582485fb7e6c69148eaf940308"
pmh = PubMedHandler()
stemmer = PorterStemmer()

wikidata_url = "https://www.wikidata.org/wiki/{}"

ext_id_mapper = {
    "cell_line": "cellosaurus", 
    "species": "NCBITaxon",  
    "drug": "CHEBI", 
    "disease": "Mesh", 
    "gene": "NCBIGene", 
    "cell_type": "CL"
}

EXTERNAL_IDS = {}
with open("../converters/database/biowiki/external_ids.csv", 'r', encoding='utf-8') as file:
    for line in file.readlines():
        qid, title, ext_id, cats = line.split("\t")
        cats_list = [a for a in cats.split(";") if a != "NO TITLE"]
        EXTERNAL_IDS[ext_id] = {"qid": qid, 'title': title, 'cats': cats_list}

with open("../converters/database/biowiki/page_dict.json", 'r') as json_file:
    WIKIDATA_PAGE_DICT = json.load(json_file)

PROGRESS = {}
def __annotate(text):
    payload = {"name": text}
    r = requests.post(URL, payload)
    if r.status_code != 200:
        raise Exception("Error on text: {}\n{}".format(text, r.text))
    annots = []
    for a in r.json()['response']:
        tmp = a 
        tmp['annotation_mode'] = "found by biowiki"
        annots.append(tmp)
    return annots

def __annotate_split(text):
    curr_len = 0
    final_annotations = []
    for sentence in text.split("\n"):
        payload = {"name": sentence}
        r = requests.post(URL, payload)
        if r.status_code != 200:
            raise Exception("Error on text: {}\n{}".format(sentence, r.text))
        resp = r.json()['response']
        for x in resp:
            tmp = x
            tmp['start_pos'] = x['start_pos'] + curr_len
            tmp['end_pos'] = x['end_pos'] + curr_len
            tmp['annotation_mode'] = 'found by biowiki'
            final_annotations.append(tmp)
        curr_len = curr_len + len(sentence)
    return final_annotations

def fix_cancer(text):
    text = text.replace("cancers", "cancer")
    text = text.replace("Cancer", "cancer")
    text = text.replace("Cancers", "cancer")
    text = text.replace("tumors", "tumor")
    text = text.replace("Tumors", "tumor")
    text = text.replace("Tumor", "tumor")
    return text

def __annotate_pubtator(ids, mode="pmc"):
    pmtype = mode + "ids"
    annotations = []
    print(api_tator.format(pmtype=pmtype, docids=ids.strip()))
    r = requests.get(api_tator.format(pmtype=pmtype, docids=ids.strip()))
    if r.status_code != 200:
        print ("[Error]: HTTP code "+ str(r.status_code))
        return {}
    else:
        ids_str = ids.split(",")
        for i, x in enumerate(r.text.split("\n")):
            x = x.strip()
            if i >= len(ids_str):
                continue
            if not x:
                print("Not found on PubTator", ids_str[i])
                annotations.append({"failed": "not found on pubtator", "a_id": ids_str[i]})
            else:
                annotations.append(json.loads(x))
        return annotations

def __download_articles(ids):
    post = {
        "searchType": "full-text",
        'input': ids,
        "papersNumber": 1,
        "searchOn": "ids"
    }
    pmh.search(post, pmc_api_key)
    try:
        article = pmh.get_article(ids.replace("PMC", ''))
        return article
    except:
        return None

def __download_pmc_new_url(id_, mode="pmc"):
    query_type = "pmcoa" if mode == "pmc" else "pubmed"
    r = requests.get(URL_PMC.format(mode=query_type, id=id_))
    if r.status_code != 200:
        print("Could not download article ID: {}\n{}".format(id_, r.text))
        return []
    bioc_ = biocxml.loads(r.text)
    json_ = json.loads(biocjson.dumps(bioc_))
    document = json_['documents'][0]['passages']
    article = []
    for passage in document:
        if mode != "pmc" or passage['infons']['section_type'] not in ['TABLE', 'REF', 'COMP_INT', 'AUTH_CONT', 'SUPPL']:
            article.append(passage)
    return article

def __annotate_new_pmc_format(article):
    final_annotations = []
    final_article = {}
    for i, passage in enumerate(article):
        txt = passage['text']
        sec_type = "abstract" if "section_type" not in passage['infons'] else passage['infons']['section_type'] 
        offset = passage['offset']
        curr_sect = "{}_{}".format(str(i), sec_type)
        final_article[curr_sect] = (txt, offset)
        bio = [x for x in __annotate(txt)]
        for x in bio:
            x['section'] = curr_sect
        for annot in bio:
            annot['start_pos'] = annot['start_pos'] + offset
            annot['end_pos'] = annot['end_pos'] + offset
            final_annotations.append(annot)

    return final_annotations, final_article

def __cleanup_annots(annotations):
    final_annotations = []

    first_filter = []
    for a in annotations:
        if a['spot'].lower() in BLACKLIST:
            continue
        if a['spot'].lower() == 'mice' and 'gene' in a['categories']:
            continue
        if a['Word'] == "ThiS protein BBPR_1770":
            continue

        if a['annotation_mode'] != "found by biowiki":
            first_filter.append(a)
        else:
            if len(a['spot']) > 3 and a['Word'] != 'water' and a['spot'].lower() != "subunit":
                x = a
                x['categories'] = [j for j in a['categories'] if j != "NO TITLE"]
                if 'section' not in x:
                    x['section'] = "UNKNOWN"
                    wiki_id = WIKIDATA_PAGE_DICT[a['Word']] if a['Word'] in WIKIDATA_PAGE_DICT else None
                    x['wiki_url'] = wikidata_url.format(wiki_id) if wiki_id else None
                    first_filter.append(x) 

    good_stems_, bad_stems_ = {}, {}
    for a in first_filter: 
        if a['annotation_mode'] != 'found by pubtator':
            good_stems_[stemmer.stem(a['Word'].lower())] = a
        else: 
            stem = a['Word']
            if stem not in bad_stems_:
                bad_stems_[stem] = a
            else: 
                if len(a['categories']) > len(bad_stems_[stem]['categories']):
                    bad_stems_[stem] = a

    for a in first_filter:
        tmp = a
        if any([x == a['Word'].lower() for x in ["cancer", "cancers", "-cancer", "-cancers", "-"]]):
            tmp['categories'] = ["disease", "disease of cellular proliferation"]
            tmp['Word'] = 'cancer'
            tmp['wiki_url'] = "https://www.wikidata.org/wiki/Q12078"
            final_annotations.append(tmp)
            continue
        if 'Mutation' in tmp['categories']:
            tmp['categories'].append("gene variant")
        if 'Chemical' in tmp['categories']:
            tmp['categories'].append("chemical entity")
        if tmp['Word'].lower().strip() == "homo sapiens":
            tmp['Word'] = "Human"

        if a['annotation_mode'] not in ["found by pubtator", "missed by biowiki, found by external id in pubtator"]:
            final_annotations.append(a)
        else:
            if a['Word'] in good_stems_:
                xxxx = good_stems_[a['Word']]
                tmp["wid"] = xxxx['wid']
                tmp["Word"] = xxxx['Word']
                tmp["categories"] = xxxx['categories']
                tmp["wiki_url"] = xxxx["wiki_url"]
                final_annotations.append(tmp)
            else:
                if a['Word'] in bad_stems_:
                    xxxx = bad_stems_[a['Word']]
                    tmp["wid"] = xxxx['wid']
                    tmp["Word"] = xxxx['Word']
                    tmp["categories"] = xxxx['categories']
                    tmp["wiki_url"] = xxxx["wiki_url"]
                    final_annotations.append(tmp)
                else:
                    final_annotations.append(a)    

    new_final_annots = []
    lowercased_words = {a['Word'].lower(): {"cats": a['categories'], "url": a['wiki_url'], "wid": a['wid'], "real": a['Word']} for a in final_annotations if a['annotation_mode'] not in ["found by pubtator", "missed by biowiki, found by external id in pubtator"]}
    for a in final_annotations:     
        if a['annotation_mode'] in ["found by pubtator", "missed by biowiki, found by external id in pubtator"]:
            if a['Word'].lower() in lowercased_words.keys():
                tmp = a
                tmp["wid"] = lowercased_words[a['Word'].lower()]['wid']
                tmp["Word"] = lowercased_words[a['Word'].lower()]['real']
                tmp["categories"] = lowercased_words[a['Word'].lower()]['cats']
                tmp["wiki_url"] = lowercased_words[a['Word'].lower()]["url"]
                new_final_annots.append(tmp)
            else:
                new_final_annots.append(a)
                lowercased_words[a['Word'].lower()] = {"cats": a['categories'], "url": a['wiki_url'], "wid": a['wid'], "real": a['Word']}
        else:
            new_final_annots.append(a)

    return new_final_annots

def __check_overlap(spot1, spot2):
    start_1, end_1 = spot1[1], spot1[2]
    start_2, end_2 = spot2[1], spot2[2]
    return max(start_1, start_2) < min(end_1, end_2) + 1

def __merge_annotations(pubtator):
    pre_change_annotations = []
    article = {}
    for i, passage in enumerate(pubtator['passages']):
        txt = passage['text']
        sec_type = "abstract" if "section_type" not in passage['infons'] else passage['infons']['section_type']         
        offset = passage['offset']
        article["{}_{}".format(str(i), sec_type)] = (txt, offset)
        if sec_type in ['TABLE', 'REF', 'COMP_INT', 'AUTH_CONT', 'SUPPL']:
            continue
        pubtator_annots = passage['annotations']
        bio = [x for x in __annotate(txt)]
        bio_spots = [(a['spot'], a['start_pos'], a['end_pos']) for a in bio] 
        pubtator_spots = [(a['text'], a['locations'][0]['offset'] - offset, a['locations'][0]['offset'] + a['locations'][0]['length'] - offset) for a in pubtator_annots]
        curr_bio = bio_spots[0] if len(bio_spots) > 0 else ('', 999997, 999997)
        curr_pubtator = pubtator_spots[0] if len(pubtator_spots) > 0 else ('', 999999, 999999)
        finished_bio, finished_pubtator = len(bio_spots) == 0, len(pubtator_spots) == 0
        i, j = 0, 0
        while not (finished_bio and finished_pubtator):
            if __check_overlap(curr_bio, curr_pubtator):
                tmp = bio[i]
                tmp['start_pos'] = tmp['start_pos'] + offset
                tmp['end_pos'] = tmp['end_pos'] + offset
                tmp['categories'] = [a for a in tmp['categories'] if a != "NO TITLE"]
                tmp['annotation_mode'] = 'found by both pubtator and biowiki'
                wiki_id = WIKIDATA_PAGE_DICT[tmp['Word']] if tmp['Word'] in WIKIDATA_PAGE_DICT else None
                tmp['wiki_url'] = wikidata_url.format(wiki_id) if wiki_id else None
                pre_change_annotations.append(tmp)
                i = i + 1
                j = j + 1
            else:
                if (not finished_bio and curr_bio[1] < curr_pubtator[1]) or finished_pubtator:
                    if len(curr_bio[0]) >= 4 or curr_bio[0] == 'H2O':
                        tmp = bio[i]
                        tmp['start_pos'] = tmp['start_pos'] + offset
                        tmp['end_pos'] = tmp['end_pos'] + offset
                        tmp['categories'] = [a for a in tmp['categories'] if a != "NO TITLE"]
                        tmp['annotation_mode'] = 'found by biowiki'
                        wiki_id = WIKIDATA_PAGE_DICT[tmp['Word']] if tmp['Word'] in WIKIDATA_PAGE_DICT else None
                        tmp['wiki_url'] = wikidata_url.format(wiki_id) if wiki_id else None
                        pre_change_annotations.append(tmp)
                    i = i + 1 
                if (not finished_pubtator and curr_pubtator[1] < curr_bio[1]) or finished_bio:
                    ext_id = pubtator_annots[j]['infons']['identifier']
                    ext_type = pubtator_annots[j]['infons']['type']
                    if ext_id and ext_type.lower() in ext_id_mapper:
                        if ":" not in ext_id:
                            ext_id = ext_id_mapper[ext_type.lower()] + ":" + ext_id
                    if ext_id in EXTERNAL_IDS:
                        cats = set([a.replace('\n', '') for a in EXTERNAL_IDS[ext_id]['cats']])
                        cats.add(ext_type)
                        cats_l = [a for a in cats if a != "NO TITLE"]
                        page_title = EXTERNAL_IDS[ext_id]['title']
                        wiki_id = WIKIDATA_PAGE_DICT[page_title] if page_title in WIKIDATA_PAGE_DICT else None
                        tmp = {
                            "wid": EXTERNAL_IDS[ext_id]['qid'],
                            "spot": curr_pubtator[0],
                            "rho": "0.5",
                            "Word": page_title,
                            "originWord": curr_pubtator[0],
                            "categories": cats_l,
                            "start_pos": curr_pubtator[1] + offset,
                            "end_pos": curr_pubtator[2] + offset,
                            "section": sec_type,
                            "wiki_url": wikidata_url.format(wiki_id) if wiki_id else None,
                            "annotation_mode": "missed by biowiki, found by external id in pubtator"
                        }
                        pre_change_annotations.append(tmp)
                    else:
                        if curr_pubtator[0] != 'patients':
                            spot_lower = curr_pubtator[0].lower()
                            if spot_lower.startswith("-"):
                                spot_lower = spot_lower[:1]
                            tmp = {
                                "wid": ext_id if ext_id else "NO_ID",
                                "spot": curr_pubtator[0],
                                "rho": "0.5",
                                "Word": fix_cancer(spot_lower),
                                "originWord": curr_pubtator[0],
                                "categories": [
                                    pubtator_annots[j]['infons']['type']
                                ],
                                "start_pos": curr_pubtator[1] + offset,
                                "end_pos": curr_pubtator[2] + offset,
                                "section": sec_type,
                                "annotation_mode": "found by pubtator",
                                "wiki_url": None
                            }
                            pre_change_annotations.append(tmp)
                    j = j + 1

            if i >= len(bio):
                finished_bio = True
                i = max(0, len(bio) - 1)
            if len(bio_spots) != 0:
                curr_bio = bio_spots[i]

            if j >= len(pubtator_annots):
                finished_pubtator = True
                j = len(pubtator_annots) - 1 
            if len(pubtator_spots) != 0:
                curr_pubtator = pubtator_spots[j]

    return pre_change_annotations, article


@api.route('/annotate_by_id', methods=['POST'])
def get_annotations_by_id():
    a_id = request.json['a_id']
    mode = request.json['mode'] if 'mode' in request.json else 'pmc'
    pubtator = __annotate_pubtator(a_id, mode)
    if pubtator and "failed" not in pubtator[0]:
        annotations, article = __merge_annotations(pubtator[0])
        results = {'annotations': __cleanup_annots(annotations), 'mode': 'pubtator+ontotagme', 'a_id': a_id, 'content': article}
    else:
        article = __download_articles(a_id)
        if article:
            bio = [x for x in __annotate_split(article)]
            results = {'annotations': __cleanup_annots(bio), 'mode': 'ontotagme', 'a_id': a_id, 'content': article}
        else:
            print("ERROR: Unable to download the article from {}".format(mode))
            abort(404)
    
    return json.dumps(results)

@api.route('/annotate_netme', methods=['POST'])
def get_netme_annotation():
    a_id = request.json['a_id']
    text = request.json['text']
    mode = request.json['mode'] if 'mode' in request.json else 'pmc'
    pubtator = __annotate_pubtator(a_id, mode)
    if pubtator and "failed" not in pubtator[0]:        
        annotations, article = __merge_annotations(pubtator[0])
        results = {'annotations': __cleanup_annots, 'mode': 'pubtator+ontotagme', 'a_id': a_id, 'content': article}
    else:
        article_tmp = __download_pmc_new_url(a_id, mode)
        if article_tmp:
            annotations, article = __annotate_new_pmc_format(article_tmp)
        else:
            bio = [x for x in __annotate_split(text)]
            annotations =  bio
            article = text
        results = {'annotations': __cleanup_annots(annotations), 'mode': 'ontotagme', 'a_id': a_id, 'content': article}
    return json.dumps(results)

@api.route('/annotate_netme_idlist', methods=['POST'])
def get_netme_annotation_list():
    idlist = request.json['idlist']
    mode = request.json['mode'] if 'mode' in request.json else 'pmc'
    token = request.json['token'] if 'token' in request.json else None
    idlist_str = idlist.split(",")
    if token:
        PROGRESS[token] = ((1, len(idlist_str)))
    pubtator = __annotate_pubtator(idlist, mode)
    final_result = []
    not_failed = []
    for i, res in enumerate(pubtator):
        a_id = idlist_str[i]
        if res and "failed" not in res:
            annotations, article = __merge_annotations(res)
            final_result.append({'annotations': __cleanup_annots(annotations), 'mode': 'pubtator+ontotagme', 'a_id': a_id, 'content': article})
            not_failed.append(a_id)
        else:
            article_tmp = __download_pmc_new_url(a_id, mode)
            if article_tmp:
                annotations, article = __annotate_new_pmc_format(article_tmp)
                final_result.append({'annotations': __cleanup_annots(annotations), 'mode': 'ontotagme', 'a_id': a_id, 'content': article})
                not_failed.append(a_id)
        if token:
            PROGRESS[token] = ((i+1, len(idlist_str)))
            
    for a_id in [x for x in idlist_str if x not in not_failed]:
        final_result.append({"failed": "not found", "a_id": a_id})
    
    if token:
        del(PROGRESS[token])

    return json.dumps(final_result)

@api.route('/get_progress_log', methods=['GET'])
def log_progress():
    token = request.args.get('token')
    if token in PROGRESS:
        curr, len_ = PROGRESS[token]
        prog_str = "OntoTagME is processing article {} out of {}".format(curr, len_)
    else:
        prog_str = "Unable to compute OntoTagME progress"
    return json.dumps({'token': token, 'progress': prog_str})

@api.route('/annotate_by_text', methods=['POST'])
def get_annotations_by_text(): 
    # ONLY QUERY ONTOTAGME
    text = request.json['text']
    bio = [x for x in __annotate(text)]
    return json.dumps({'mode': 'text', 'annotations': __cleanup_annots(bio), 'query': text})

@api.route('/annotate_sections', methods=['POST'])
def get_annotations_section_dict(): 
    # ONLY QUERY ONTOTAGME
    print(request.json)
    a = request.json['article']
    annotations = {k: [] for k in a.keys()}
    for k, v in a.items():
        bio = __annotate(v)
        annotations[k] =  __cleanup_annots(bio)
    return json.dumps({'mode': 'article_dict', 'annotations': annotations, 'query': a})


def main():
    api.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    main()