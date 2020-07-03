#!/usr/bin/env python
import os
import sys, getopt
import json
from datetime import datetime

####################
# DATA DEFINITIONS #
####################

# a ScarletNotes JSON object is the python representation
# of the JSON file exported from the 'Scarlet Notes FD app'

# a Dictionary-of Folders is a dictionary:
# key: string representing UUID
# value: string representing folder name

# a Note is a dictionary:
# -- 'folder': string
# -- 'title': string
# -- 'time' : string
# -- 'text' : string

# a NotesFolder is a folder representation of ScarletNotes:
# Folders are represented as directories
# Notes are represented as markdown files


#############
# CONSTANTS #
#############

HELP = '[-e --extract] <output_path> <file_path>\t\t:extract to directory \n' \
        '[-p --print] <file_path>\t\t:pretty print'

#############
# FUNCTIONS #
#############

# File path -> ScarletNotes JSON object
# Load the JSON data as a python object
def get_obj(path):
        try:
                with open(path, 'r') as f:
                        data = f.read()
                        obj = json.loads(data)
                return obj
        except FileNotFoundError:
                print("Invalid file path")
                exit()
        except json.decoder.JSONDecodeError:
                print("File's content doesn't seem to be JSON")
                exit()


# ScarletNotes JSON object -> Dictionary-of Folders
# extract the folders to uuid links
def get_folders_dict(obj):
        folders = {}
        for folder in obj['folders']:
                uuid = folder['uuid']
                title = folder['title']
                folders[uuid] = title
        return folders


# ScarletNotes JSON object -> List-of Notes
# extract all notes
def get_notes(obj):
        notes = []
        for note in obj['notes']:
                note_dict = {}

                # FOLDER
                folder_uuid = note['folder']
                folders_dict = get_folders_dict(obj)
                if folder_uuid:
                        folder_name = folders_dict[folder_uuid]
                        note_dict['folder'] = folder_name
                else:
                        note_dict['folder'] = "DELETED"
                        continue

                # TIMESTAMP
                timestamp = int(str(note['timestamp'])[:-3])
                note_dict['time'] = datetime.fromtimestamp(timestamp).strftime("%A, %B %d, %Y %I:%M:%S")
                note_dict['date'] = datetime.fromtimestamp(timestamp).strftime("%Y_%m_%d")

                # TITLE and TEXT
                note = json.loads(note['description'])['note']

                if len(note) > 1:
                        note_dict['title'] = note[0]['text']
                        note_dict['text'] = note[1]['text']
                else:
                        note_dict['title'] = "Empty"
                        note_dict['text'] = note[0]['text']

                notes.append(note_dict)
        return notes


# Note -> Markdown formatted text
# represent the note in md format
def note_to_md(note):
        str = ''
        str += 3*'-'+ '\n'
        str += ''.join('time: ' + note['time']+ '\n')
        str += ''.join('title: ' + note['title']+ '\n')
        str += 3*'-'+ '\n' + '\n'
        str += note['text']
        return str

                                                                              
# List-of Notes -> Formatted output
# return a prettifyed string representation of List-of Notes
def prettify_notes(notes):
        str = ''
        for note in notes:
                str += 30*'-' + '\n'
                str += 3*'-'+ '\n'
                str += ''.join('folder: ' + note['folder']+ '\n')
                str += ''.join('title: ' + note['title']+ '\n')
                str += ''.join('time: ' + note['time']+ '\n')
                str += 3*'-'+ '\n'
                str += note['text'] + '\n'
        return str


# JSON file path -> Formatted output
# print the notes from the JSON file
def print_notes(input_path):
        pretty = prettify_notes(get_notes(get_obj(input_path)))
        print(pretty)
        return


# JSON file, Directory Path -> Directory
# creates a directory in path with the notes in markdown format
def extract_notes(input_path, output_path):
        notes = get_notes(get_obj(input_path))
        os.mkdir(output_path)
        for note in notes:
                folder_path = os.path.join(output_path, note['folder'])
                if not os.path.isdir(folder_path):
                        os.mkdir(folder_path)
                f = open(os.path.join(folder_path, str(note['date'] + '.md')), 'w')
                f.write(note_to_md(note))
        return


########
# MAIN #
########

def main(argv):
        input_path = ''
        output_path = ''
        try:
                opts, args = getopt.getopt(argv,"pe:h",["print","extract=","help"])
        except getopt.GetoptError as e:
                print(e)
                sys.exit(2)
        try:
                input_path = args[0]
        except:
                print(HELP)
                sys.exit()
        for opt, arg in opts:
                if opt == '-h':
                        print(HELP)
                        sys.exit()
                elif opt in ("-e", "--extract"):
                        output_path = arg
                        extract_notes(input_path, output_path)
                elif opt in ("-p", "--print"):
                        print_notes(input_path)
        return


if __name__ == "__main__":
       main(sys.argv[1:])
