import logging
import json
import numpy
import csv

logger = logging.getLogger('universal_logger')

def chord_diagram_create(list_docs, config):
    
    """
        Create the names.csv and matrix.json file needed for visualizing 
        the chord diagram of the most freqeunt named entities found
        in the text collection.
        
        Args:
            - list_docs : list of lists, containing the posts of each user
            - config: config file
        Returns:
            Nothing. Creates the wanted csv, json files for the chord diagram

    """

    from spacy import English

    nlp = English()
    wanted_ents = config.get('chord', 'entities').split(',')
    color_dic = config.get('chord', 'colors').split(',')
    print color_dic
    print wanted_ents
    N_freq = config.getint('chord', 'num_top_freq')
    normalize_freq = config.getboolean('chord', 'normalize_freq')
    path_to_csv = config.get('chord', 'path_to_csv')
    path_to_json = config.get('chord', 'path_to_json')
    c = 0
    named_entities = []
    found_entities = []
    found_types = []
    counter = []
    for posts in list_docs:
        if type(posts) == list:
            for doc in posts:
                ents = list(nlp(unicode(doc)).ents)
                # if there are named entities
                tmp_ents = []
                if ents:
                    for ent in ents:
                        if ent.label_ in wanted_ents:
                            tmp_ents.append(ent.orth_.encode('utf-8'))
                            if not(ent.orth_.encode('utf-8') in found_entities):
                                found_entities.append(ent.orth_.encode('utf-8'))
                                found_types.append(ent.label_)
                                counter.append(1)
                            else:
                                counter[found_entities.index(ent.orth_.encode('utf-8'))] += 1 
                c += 1
                if c % 5000 == 0:
                    logger.info('Proccesed %i documents!' % c)
        else:
            # case of gathered texts
            ents = list(nlp(unicode(posts)).ents)
            # if there are named entities
            tmp_ents = []
            if ents:
                for ent in ents:
                    if ent.label_ in wanted_ents:
                        tmp_ents.append(ent.orth_.encode('utf-8'))
                        if not(ent.orth_.encode('utf-8') in found_entities):
                            found_entities.append(ent.orth_.encode('utf-8'))
                            found_types.append(ent.label_)
                            counter.append(1)
                        else:
                            counter[found_entities.index(ent.orth_.encode('utf-8'))] += 1
            c += 1
            if c % 1000 == 0:
                logger.info('Proccesed %i documents!' % c)
        named_entities.append(tmp_ents)

    freq_names = numpy.array(found_entities)[numpy.argsort(counter)[::-1][:N_freq]]
    freq_types = numpy.array(found_types)[numpy.argsort(counter)[::-1][:N_freq]]
    count_freq = numpy.zeros([N_freq, N_freq])
    for i, ent in enumerate(freq_names):
        #print i
        for j in xrange(i+1, len(freq_names)):
            for doc in named_entities:
                if ent in doc and freq_names[j] in doc:
                    count_freq[i, j] += 1
    frequencies = numpy.copy(count_freq)
    numpy.fill_diagonal(count_freq, 0)
    count_freq += count_freq.T
    if normalize_freq:
        count_freq /= count_freq.max()
    else:
        from sklearn.preprocessing import normalize
        count_freq = normalize(count_freq, norm='l1', axis=1)

    names_list = [['name', 'color']]
    for i, ent in enumerate(freq_names):
        names_list.append([ent, color_dic[wanted_ents.index(freq_types[i])]])
    with open(path_to_csv, 'w+') as out_csv:
        writer = csv.writer(out_csv)
        writer.writerows(names_list)
    with open(path_to_json, 'w+') as out_json:
        json.dump(count_freq.tolist(), out_json)
    logger.info('Created csv and json files for chord diagram!')

    if config.getboolean('bubbles', 'create_bubbles'):
        path_to_bubble_csv = config.get('bubbles', 'path_to_csv')
        max_bubbles = config.getint('bubbles', 'max_bubbles')
        if max_bubbles > len(found_entities):
            max_bubbles = len(found_entities)
        bubble_names = numpy.array(found_entities)[numpy.argsort(counter)[::-1][:max_bubbles]]
        bubble_types = numpy.array(found_types)[numpy.argsort(counter)[::-1][:max_bubbles]]
        counter2 = numpy.array(counter)[numpy.argsort(counter)[::-1][:max_bubbles]]
        bubbles_list = [['id', 'total_amount', 'grant_title', 'group', 'start_year']]
        print bubble_names.shape
        for i in xrange(max_bubbles):
            bubbles_list.append([i, counter2[i], bubble_names[i], bubble_types[i], bubble_types[i]])
        with open(path_to_bubble_csv, 'w+') as out_b:
            writer = csv.writer(out_b)
            writer.writerows(bubbles_list)
        logger.info('Created csv for bubbles diagram!')
