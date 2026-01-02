import requests
import os
import time
import argparse
from tqdm import tqdm


def escape(text):
    return text.replace('\\', '\\\\').replace(']', '\\]')

def writeInitialStones(file, string):
    for i in range(0, len(string), 2):
        file.write('[')
        file.write(string[i:i+2])
        file.write(']')
        
def otherPlayer(player):
    return 'B' if player == 'W' else 'W'
        
def writeCoordinates(file, node):
    file.write(chr(97 + node['x']))
    file.write(chr(97 + node['y']))
    
def writeCoordinatesInBrackets(file, node):
    file.write('[')
    writeCoordinates(file, node)
    file.write(']')
            
def writeMarks(file, marks):
    for mark in marks:
        if 'letter' in mark['marks']:
            file.write('LB[')
            writeCoordinates(file, mark)
            file.write(':')
            file.write(escape(mark['marks']['letter']))
            file.write(']')
        elif 'triangle' in mark['marks']:
            file.write('TR')
            writeCoordinatesInBrackets(file, mark)
        elif 'square' in mark['marks']:
            file.write('SQ')
            writeCoordinatesInBrackets(file, mark)
        elif 'cross' in mark['marks']:
            file.write('MA')
            writeCoordinatesInBrackets(file, mark)
        elif 'circle' in mark['marks']:
            file.write('CR')
            writeCoordinatesInBrackets(file, mark)

def prependText(node, text): 
    if 'text' in node:
        node['text'] = text + '\n\n' + node['text']
    else:
        node['text'] = text
            
def writeNode(file, node, player):
    if 'marks' in node:
        writeMarks(file, node['marks'])
    if 'correct_answer' in node:
        prependText(node, "CORRECT")
    elif 'wrong_answer' in node:
        prependText(node, "WRONG")
    if 'text' in node:
        file.write('C[')
        file.write(escape(node['text']))
        file.write(']')
    if 'branches' in node:
        branches = node['branches']
        for branch in branches:
            if len(branches) > 1:
                file.write('(')
            writeBranch(file, branch, player)
            if len(branches) > 1:
                file.write(')')
        
def writeBranch(file, branch, player):
    file.write(';')
    file.write(player)
    writeCoordinatesInBrackets(file, branch)
    writeNode(file, branch, otherPlayer(player))
        
def writePuzzle(file, puzzle):
    file.write('(;FF[4]CA[UTF-8]AP[puzzle2sgf:0.1]GM[1]GN[')
    file.write(escape(puzzle['name']))
    file.write(']SZ[')
    file.write(str(puzzle['width']))
    if puzzle['width'] != puzzle['height']:
        file.write(':')
        file.write(str(puzzle['height']))
    file.write(']')
    initial_black = puzzle['initial_state']['black']
    if initial_black:
        file.write('AB')
        writeInitialStones(file, initial_black)
    initial_white = puzzle['initial_state']['white']
    if initial_white:
        file.write('AW')
        writeInitialStones(file, initial_white)
    if 'puzzle_description' in puzzle:
        prependText(puzzle['move_tree'], puzzle['puzzle_description'])
    player = puzzle['initial_player'][0].upper()
    file.write('PL[')
    file.write(player)
    file.write(']')
    writeNode(file, puzzle['move_tree'], player)
    file.write(')')

def authenticate():
    url = 'https://online-go.com/api/v0/login'
    username =  input('Username: ')
    password =  input('Password: ')
    response = requests.post(url, data={'username' : username, 'password' : password})
    return response.cookies

def sanitize_filename(name):
    return name.replace('/', ' - ')

def create_sgf_file(puzzle, output_dir):
    filename = sanitize_filename(puzzle['name']) + '.sgf'
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding="utf-8") as file:
        writePuzzle(file, puzzle)

def download_puzzle(puzzle_id, cookies):
    puzzleUrl = f'https://online-go.com/api/v1/puzzles/{puzzle_id}'
    response = requests.get(puzzleUrl, cookies=cookies)
    response.raise_for_status()
    return response.json()

def download_collection(puzzle_id, cookies):
    collectionUrl = f'https://online-go.com/api/v1/puzzles/{puzzle_id}/collection_summary'
    response = requests.get(collectionUrl, cookies=cookies)
    response.raise_for_status()
    return response.json()

def main():
    parser = argparse.ArgumentParser(description='Download OGS puzzles and convert them to SGF files.')
    parser.add_argument('puzzle_id', type=int, help='The ID of the puzzle to download.')
    parser.add_argument('--collection', action='store_true', help='Download the whole collection. A subdirectory named after the collection will be created inside the output directory.')
    parser.add_argument('--no-auth', action='store_true', help='Skip authentication.')
    parser.add_argument('--output', default='.', help='The output directory.')
    args = parser.parse_args()

    cookies = [] if args.no_auth else authenticate()
    
    os.makedirs(args.output, exist_ok=True)

    if args.collection:
        responseJSON = download_puzzle(args.puzzle_id, cookies)
        collectionName = responseJSON['collection']['name']
        collectionFolder = os.path.join(args.output, collectionName)
        os.makedirs(collectionFolder, exist_ok=True)
        create_sgf_file(responseJSON['puzzle'], collectionFolder)

        collection = download_collection(args.puzzle_id, cookies)
        for puzzle in tqdm(collection, desc="Downloading puzzles"):
            if puzzle['id'] != args.puzzle_id:
                time.sleep(5.0)
                puzzleJSON = download_puzzle(puzzle['id'], cookies)['puzzle']
                create_sgf_file(puzzleJSON, collectionFolder)
    else:
        responseJSON = download_puzzle(args.puzzle_id, cookies)
        create_sgf_file(responseJSON['puzzle'], args.output)

if __name__ == '__main__':
    main()