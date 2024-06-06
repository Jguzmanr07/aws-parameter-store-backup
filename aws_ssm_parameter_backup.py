#!/usr/bin/env python3
#! Jesús Guzmán

"""Export or import AWS Systems Manager Parameter Store parameters."""

import argparse
import logging
import re
import sys
import json
import boto3

def main():

    args = parse_args()

    boto_session = boto3.Session(profile_name=args.profile, region_name=args.region)
    ssm_client = boto_session.client('ssm')

    regex_filter = None
    if args.filter:
        regex_filter = re.compile(args.filter)

    if args.mode == 'export':
        parameters = {'Parameters': []}
        for param in sort_parameters(get_parameters(ssm_client), args.sort):
            if regex_filter and not regex_filter.search(param['Name']):
                continue

            logging.info('Getting value for %s', param['Name'])
            param_detail = ssm_client.get_parameter(Name=param['Name'], WithDecryption=True)['Parameter']
            parameters['Parameters'].append({'Name': param['Name'], 
                                             'Type': param['Type'],
                                             'Value': param_detail['Value']})
        logging.info('Writing Parameters to outfile %s', args.outfile.name)
        print(json.dumps(parameters, indent=2, sort_keys=True), file=args.outfile)

    elif args.mode == 'import':
        logging.info('Loading Parameters from infile %s', args.infile.name)
        parameters = json.load(args.infile)
        for param in parameters['Parameters']:
            if regex_filter and not regex_filter.search(param['Name']):
                continue

            try:
                logging.info('Updating Parameter %s with Value %s', param['Name'], param['Value'])
                ssm_client.put_parameter(Name=param['Name'], Value=param['Value'], Type=param['Type'], Overwrite=True)
            except ssm_client.exceptions.ParameterNotFound:
                logging.warning('Parameter %s does not exist, creating it', param['Name'])
                logging.info('Creating Parameter %s with Value %s', param['Name'], param['Value'])
                ssm_client.put_parameter(Name=param['Name'], Value=param['Value'], Type=param['Type'])

def sort_parameters(parameters, sort_mode):
    sort_key = lambda param: param['Name']
    if sort_mode == 'ascending':
        return sorted(parameters, key=sort_key)
    elif sort_mode == 'descending':
        return sorted(parameters, reverse=True, key=sort_key)
        
    return parameters

def get_parameters(ssm_client):
    """Iterator for parameters.

    Yield parameters
    """
    paginator = ssm_client.get_paginator('describe_parameters')
    pages = paginator.paginate()
    for page in pages:
        for param in page['Parameters']:
            yield param

def parse_args():
    """Create arguments and populate variables from args.

    Return args namespace
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-m', '--mode', type=str, default='export', choices=['export', 'import'],
                        help='Export parameters (default) or import')
    parser.add_argument('-l', '--loglevel', type=str,
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Logging/output verbosity')
    parser.add_argument('-f', '--filter', type=str, default=None, metavar='REGEX',
                        help='Filter parameters to import/export using a supplied regular expression')
    parser.add_argument('-s', '--sort', type=str, default=None, choices=['ascending', 'descending'],
                        help='Sort parameters to export in ascending or descending order')

    file_group = parser.add_mutually_exclusive_group(required=False)
    file_group.add_argument('-i', '--infile', type=argparse.FileType('r'), default=sys.stdin,
                            help='Filename for import (default: stdin)')
    file_group.add_argument('-o', '--outfile', type=argparse.FileType('w'), default=sys.stdout,
                            help='Filename for export (default: stdout)')

    aws_group = parser.add_argument_group(title='AWS configuration options')
    aws_group.add_argument('-p', '--profile', type=str, default=None,
                           help='Override AWS credentials/configuration profile')
    aws_group.add_argument('-r', '--region', type=str, default=None,
                           help='Override AWS region')

    args = parser.parse_args()

    if args.loglevel:
        logging.basicConfig(level=args.loglevel)

    if args.mode == 'import' and args.outfile is not parser.get_default('outfile'):
        parser.error('--outfile cannot be used with --mode import')
    elif args.mode == 'export' and args.infile is not parser.get_default('infile'):
        parser.error('--infile cannot be used with --mode export')

    return args

if __name__ == '__main__':
    main()
