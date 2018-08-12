# !/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import os
import sys
import logging

from pathlib import Path

from superfocus_app.superfocus import which


LOGGER_FORMAT = '[%(asctime)s - %(levelname)s] %(message)s'
logging.basicConfig(format=LOGGER_FORMAT, level=logging.INFO)
LOGGER = logging.getLogger(__name__)

WORK_DIRECTORY = str(Path(__file__).parents[0])


def check_aligners():
    """Check if aligners are installed on the system path.

    Returns:
        list: Paths for aligners if exists

    """
    return [
        info
        for info in [which(x) for x in ['prerapsearch', 'diamond']]
        if info != None
    ]


def download_format(aligners):
    """Download and format database base.

    Args:
        aligners (list): Aligners to have the database formatted

    """
    LOGGER.info('  Downloading DB')
    os.system('wget edwards.sdsu.edu/superfocus/downloads/db_small.zip')
    #os.system('wget edwards.sdsu.edu/superfocus/downloads/db.zip')

    LOGGER.info('  Uncompressing DB')
    #os.system('unzip db.zip')  # uncompress db
    os.system('unzip db_small.zip')  # uncompress db

    os.system('mv clusters/ {}/db/'.format(WORK_DIRECTORY))  # mv db
    #os.system('rm db.zip')  # delete original downloaded file
    os.system('rm db_small.zip')  # delete original downloaded file

    LOGGER.info('  Joining files')
    [
        os.system(
            'cat {}/db/clusters/{}/*.faa > {}/db/clusters/{}.fasta'.format(WORK_DIRECTORY,
                                                                                    cluster, WORK_DIRECTORY, cluster)
        )
        for cluster in os.listdir('{}/db/clusters/'.format(WORK_DIRECTORY)) if 'cluster' in cluster
    ]

    # Format database
    LOGGER.info('  Formatting Database')
    cluster_identities = ['100', '98', '95', '90']
    for dbname in cluster_identities:
        for aligner in aligners:
            if aligner == 'prerapsearch':
                LOGGER.info('  RAPSearch2: DB_{}'.format(dbname))
                os.system(
                    'prerapsearch -d {}/db/clusters/{}_clusters.fasta '
                ' -n {}/db/static/rapsearch2/{}.db'.format(WORK_DIRECTORY, dbname, WORK_DIRECTORY, dbname)
                )
            else:
                LOGGER.info('  DIAMOND: DB_{}'.format(dbname))
                os.system(
                    'diamond makedb --in  {}/db/clusters/{}_clusters.fasta '
                    '--db {}/db/static/diamond/{}.db'.
                        format(WORK_DIRECTORY, dbname, WORK_DIRECTORY, dbname)
                )
    os.system('rm {}/db/clusters/*.fasta'.format(WORK_DIRECTORY))


def parse_args():
    """Parse args entered by the user.

    Returns:
        argparse.Namespace: Parsed arguments

    """
    parser = argparse.ArgumentParser(description="SUPER-FOCUS: A tool for agile functional analysis of shotgun "
                                                 "metagenomic data",
                                     epilog="python superfocus_downloadDB -a diamond,rapsearch")
    # basic parameters
    parser.add_argument("-a", "--aligner", help="Aligner name separed by ',' if more than one", required=True)

    return parser.parse_args()


def main():
    args = parse_args()

    valid_aligners = {'rapsearch', 'diamond', 'prerapsearch'}
    aligner_db_creators = {os.path.basename(x) for x in check_aligners() if x != 'None'}
    if not aligner_db_creators:
        LOGGER.critical('  None of the required aligners are installed {}'.format(list(valid_aligners)))
        sys.exit(1)

    # Parse which aligner(s) the user wants to format the database to
    requested_aligners = {aligner.lower() for aligner in args.aligner.split(",")}
    for aligner in requested_aligners:
        if aligner not in valid_aligners:
            LOGGER.critical('  None of the required aligners are installed {}'.format(list(valid_aligners)))
            sys.exit(1)

    aligners = []
    if 'rapsearch' in requested_aligners and 'prerapsearch' in aligner_db_creators:
        aligners.append("prerapsearch")
    if 'diamond' in requested_aligners and 'diamond' in aligner_db_creators:
        aligners.append("diamond")

    os.system('rm {}/db/clusters/ -r 2> /dev/null'.format(WORK_DIRECTORY))  # delete folder if exists
    download_format(aligners)
    LOGGER.info('  Done! Now you can run superfocus')


if __name__ == "__main__":
    main()
