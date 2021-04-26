#!/usr/bin/env python3
# TODO: Add PC check
# TODO: Add stdoutput

from unidiff import PatchSet # unidiff
from profanity_check import predict, predict_prob # alt-profanity-check
from pprint import pprint
from argparse import ArgumentParser, SUPPRESS, FileType, Action, ArgumentTypeError
from sys import stdin
from os import path, access, R_OK, getcwd
from io import TextIOWrapper
import json

class readable_dir(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir=values
        if not path.isdir(prospective_dir):
            raise ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
        if access(prospective_dir, R_OK):
            setattr(namespace,self.dest,prospective_dir)
        else:
            raise ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))

parser = ArgumentParser(description='''Parse git commit to provide information about potential
                                       not politically correct language''')
parser.add_argument('--profanity-threshold', '-pt',
                    required=False,
                    default=0.9,
                    type=int,
                    help='Threshold for profanity model')
parser.add_argument('--pretty-print', '-pp',
                    required=False,
                    default=False,
                    action='store_const',
                    const=True,
                    help='Threshold for profanity model')
group = parser.add_mutually_exclusive_group()
group.add_argument('--file', '-f',
                    metavar='FILE',
                    dest='source',
                    action='store',
                    help='Path to file in \'diff\' format')
group.add_argument('--directory', '-d',
                    metavar='DIRECTORY',
                    dest='source',
                    action=readable_dir,
                    help='path to directory with GIT repository')
group.add_argument('--stdin', '-s',
                    nargs='?',
                    default=None,
                    const=stdin,
                    # FIXME: default doesnt work, because dir is not a file
                    type=FileType('r'),
                    dest='source',
                    action='store',
                    help='Stream of file in \'diff\' format')
parser.set_defaults(source=getcwd())
args = parser.parse_args()

if (isinstance(args.source, TextIOWrapper)):
    patch_set = PatchSet(args.source)
elif (path.isdir(args.source)):
    raise Exception("Directory is unsupported")
elif (path.isfile(args.source)):
    patch_set = PatchSet(open(args.source, "rb"), encoding='utf-8')
else:
    raise Exception("Unknown input")

change_list = []

for patched_file in patch_set:
    for hunk in patched_file:
        for line in hunk:
            # TODO: Implement SARIF spec as output
            #  https://github.com/oasis-tcs/sarif-spec
            if(line.is_added == False):
                break
            modified_line = {}
            modified_line['file'] = patched_file.path
            modified_line['line_no'] = line.target_line_no
            modified_line['value'] = line.value.strip()
            prediction = predict_prob([line.value.strip()])[0]
            modified_line['prediction_profanity'] = prediction
            modified_line['is_profanity'] = bool(prediction >= args.profanity_threshold)
            change_list.append(modified_line)

if (args.pretty_print == True):
    result=json.dumps(change_list, indent=4)
else:
    result=json.dumps(change_list)
print(result)