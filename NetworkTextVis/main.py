from operator import attrgetter
from argparse import ArgumentParser
from network_load import read_network, gather_texts, execute_task
#from topic_extraction import gather_texts,topic_extract,graph_cleansing
import ConfigParser
import logging
import time


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
    t0 = time.time()
    logger = configure_logging()
    parser = ArgumentParser(description='Create a dashboard with '
                            'visualizations stemming form network+text info.')
    parser.add_argument('-c', '--config', required=True, default='simple.cfg', help='config file path')
    parser.add_argument('-i', '--input', required=True, default='edbge', choices=('edge', 'json', 'gexf', 'adjlist', 'twitter'), help='choices of network input')
    opts = parser.parse_args()
    getter = attrgetter('config', 'input')
    conf_path, scheme = getter(opts)
    config = ConfigParser.SafeConfigParser()
    config.read(conf_path)
    logger.info('Parsing Network!')
    G = read_network(config, scheme)
    docs, list_docs = gather_texts(G, config, scheme)
    vis_tasks = config.get('main', 'vis').split(',')
    for task in vis_tasks:
        logger.info('Executing task: %s' % task)
        execute_task(G, docs, list_docs, config, scheme, task)
    logger.info('Finished in: %0.3f seconds!' % (time.time() - t0))
    #subprocess.Popen(['python', '-m', 'SimpleHTTPServer', '8000'], cwd='/media/kostas/DATA/GIT/NetworkTextVis/Visualization_Network/')
    #webbrowser.open_new_tab('http://0.0.0.0:8000/?assesment_id=reddit_try/')



    
    