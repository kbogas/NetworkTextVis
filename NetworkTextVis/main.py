from operator import attrgetter
from argparse import ArgumentParser
import networkx as nx
from network_load import read_network, gather_texts
from text import update_graph_topics
from ranking import graph_influence
#from topic_extraction import gather_texts,topic_extract,graph_cleansing
import urllib2
import json
import ConfigParser
import logging
import subprocess
import webbrowser


def configure_logging():
    logger = logging.getLogger("universal_logger")
    logger.setLevel(logging.DEBUG)
    # Format for our loglines
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # Setup console logging
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    # Setup file logging as well
    fh = logging.FileHandler('log.txt')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# fh = logging.FileHandler('log.txt')
# fh.setLevel(logging.DEBUG)
# fh.setFormatter(formatter)
# logger.addHandler(fh)

# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# ch.setFormatter(formatter)
# logger.addHandler(ch)



if __name__ == '__main__':
    logger = configure_logging()
    parser = ArgumentParser(description='Create a dashboard with '
                            'visualizations stemming form network+text info.')
    parser.add_argument('-c', '--config', required=True, default='simple.cfg', help='config file path')
    parser.add_argument('-i', '--input', required=True, default='edbge', choices=('edge', 'json', 'gexf', 'adjlist'), help='choices of network input')
    opts = parser.parse_args()
    getter = attrgetter('config', 'input')
    conf_path, scheme = getter(opts)
    config = ConfigParser.SafeConfigParser()
    config.read(conf_path)
    logger.info('Starting Topic Module!')
    G = read_network(config, scheme)
    model = 'LDA'
    docs, _ = gather_texts(G, config)
    G, out_G = update_graph_topics(G, docs, config)
    logger.info('Finished Topic Modeling!')
    out_path = config.get('out_gexf', 'path_to_gexf')
    jar_path = config.get('out_gexf', 'path_to_jar')
    final_out_path = config.get('out_gexf', 'path_to_final_gexf')
    logger.info('Will write temporary gexf to: %s' % out_path)
    nx.write_gexf(out_G, out_path)
    logger.info('Will run jar layout mechanism from: %s \n Reads from: %s \n Writes to: %s' % (jar_path, out_path, final_out_path))
    subprocess.call(['java', '-jar', jar_path, out_path, final_out_path])
    logger.info('Created Final Gexf!')
    logger.info('Will open browser to network!')
    #subprocess.Popen(['python', '-m', 'SimpleHTTPServer', '8000'], cwd='/media/kostas/DATA/GIT/NetworkTextVis/Visualization_Network/')
    #webbrowser.open_new_tab('http://0.0.0.0:8000/?assesment_id=reddit_try/')


