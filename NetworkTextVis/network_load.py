import networkx as networkx
import logging
import json
from bson.json_util import loads

logger = logging.getLogger('universal_logger')

def read_network(config, scheme):

    """ Read network from file.

    Args:
        - config: Config object from main file
        - scheme: The form the input takes. Can be one of the following:
          ['edge', 'json', 'gexf', 'matrix']
    Returns:
        - G: The graph read, as a  networkx object

    """

    #scheme = config.get('network', 'scheme')
    possible_schemes = ['edge', 'json', 'gexf', 'adjlist']
    if scheme not in possible_schemes:
        logger.error('Selected scheme %s is not recognized!' % (scheme))
        print 'Use one of the following instead:'
        for sc in possible_schemes:
            print '-- %s --' % sc
        exit(1)
    configs = dict(config.items(scheme))
    #print configs
    if scheme == 'edge':
        pass
    elif scheme == 'json':
        inpath = config.get(scheme, 'path_to_json')
        with open(inpath, 'r') as infile:
            G = json_load(infile)
    elif scheme == 'gexf':
        inpath = config.get(scheme, 'path_to_gexf')
        G = networkx.read_gexf(inpath)
    elif scheme == 'adjlist':
        adjlist_path = config.get(scheme, 'path_to_adjlist')
        node_path = config.get(scheme, 'path_to_nodelist')
        with open(adjlist_path, 'r') as adjlist_fname:
            with open(node_path, 'r') as node_fname:
                G = adjlist_load(adjlist_fname, node_fname)
    if networkx.is_directed(G):
        type1 = 'directed'
    else:
        type1 = 'undirected'
    logger.info('Loaded %s graph with: %i nodes and %i edges' % (type1, len(G.nodes()), len(G.nodes())))
    return G


def gather_texts(graph, config):

    """ Gathers the posts/tweets etc of a person.

    Args:
        - graph: The graph object, in networkx format
        - config: Config object from main file
    Returns:
        - documents: List with concatenated strings for each user
        - list_docs: List of list of strings Each sublist contains
           all the the tweets/posts etc done by the user.

    """

    objects = []
    documents = []
    list_docs = []
    # If texts already gather in the input network. If yes will use text_field
    # in order to read the gathered posts
    gathered = config.getboolean('data', 'gathered')
    # Appropriate attribute name with dictionary of the posts/tweets etc.
    attribute = config.get('data', 'attribute')
    # Appropriate attribute name for the posts field
    text_field = config.get('data', 'text_field')
    label = config.get('main', 'label')
    count_failed = 0
    if not(gathered):
        for i in list(graph.nodes()):
            try:
                #print graph.node[i][attribute]
                #print loads(graph.node[i][attribute],strict=False)
                objects.append(loads(graph.node[i][attribute],strict=False))
            except Exception:
                logger.warning('Node %s could not gather texts, due to parsing errors' % (str(graph.node[i][label])))
                count_failed += 1
                graph.remove_node(i)
        for o in objects:
            posts = o[attribute]
            concat_post = ''
            tmp_doc = []
            for p in posts:
                concat_post = concat_post + ' ' + p[text_field]
                tmp_doc.append(p[text_field])
            documents.append(concat_post)
            list_docs.append(tmp_doc)
    else:
        for i in list(graph.nodes()):
            try:
                #print graph.node[i][attribute]
                #print loads(graph.node[i][attribute],strict=False)
                documents.append(graph.node[i][text_field])
            except Exception:
                logger.warning('Node %s could not gather texts, due to parsing errors' % (str(graph.node[i][label])))
                count_failed += 1
                graph.remove_node(i)
    logger.info("Number of nodes with gathered texts: %i" % len(documents))
    logger.warning("Could not load: %i users!" % count_failed)
    return documents, list_docs


def json_load(fname):
    '''
        Load from .json file.
        Args:
            - fname : file object from open()

        Returns:
            - G: Loaded directed/undirected graph

    '''
    d = json.load(fname)
    try:
        if d['directed']==True:
            G = networkx.DiGraph()
        else:
            G = networkx.Graph()
    except KeyError:
        G = networkx.Graph()
    G.add_nodes_from(d['nodes'])
    G.add_edges_from(d['edges'])
    
    return G


def adjlist_load(adjlist_fname, node_fname):
    '''
        Load from .json file.
        Args:
            - fname : file object from open()

        Returns:
            - G: Loaded directed/undirected graph

    '''

    G = networkx.read_adjlist(adjlist_fname)
    nodes = json.load(node_fname)
    G.add_nodes_from(nodes['nodes'])
    return G
