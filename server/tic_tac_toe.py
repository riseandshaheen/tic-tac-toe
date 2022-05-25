# Copyright 2022 Cartesi Pte. Ltd.
#
# SPDX-License-Identifier: Apache-2.0
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from os import environ
import traceback
import logging
import requests
from generate_board import *
import json
from math import sqrt,floor
from enum import Enum
from random import randint

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")

'''
Initializes game board, players' addresses and game id
'''
saved_board = {}
players = {'X':'', 'O':''}
game_id = 0
turn = 'X'

PLAYER_X = 'X'
PLAYER_O = 'O'
EMPTY = '-'

class RequestType(Enum):
    NEW_GAME = 'new'
    JOIN_GAME = 'join'
    BOARD_UPDATE = 'update'

def hex2str(hex):
    """
    Decodes a hex string into a regular string
    """
    return bytes.fromhex(hex[2:]).decode("utf-8")

def str2hex(str):
    """
    Encodes a string as a hex string
    """
    return "0x" + str.encode("utf-8").hex()

def init_board(n):
    board = {}
    for x in range(n):
        for y in range(n):
            board[(x, y)] = EMPTY
    return board

def board_list2dict(board_state):
    """
    Translates the input board list type to a dictionary type
    """
    board = {}
    for x in range(3):
        for y in range(3):
            board[(x, y)] = board_state[x][y]
    return board

def has_won(board, size, player):
    logger.info(f"Inside HAS_WON\n{generate_board_pretty_str(board)}--{size}--{player}")
    for n in range(size):
        rows = [board[(x, y)] for x, y in sorted(board.keys()) if n is x]
        cols = [board[(x, y)] for x, y in sorted(board.keys()) if n is y]
        diagonals = [board[(x, y)] for x, y in sorted(board.keys()) if x is y]
        if rows.count(player) is size or cols.count(player) is size or diagonals.count(player) is size:
            return True
    return False

def board_full(board):
    logger.info(f"Inside BOARD_FULL\n{generate_board_pretty_str(board)}")
    return list(board.values()).count(EMPTY) == 0

def game_ended(board, size):
    return board_full(board) or has_won(board, size, PLAYER_X) or has_won(board, size, PLAYER_O)

def game_winner(board, size):
    logger.info(f"Initiating game_winner!")
    if has_won(board, size, PLAYER_X):
        logger.info(f"Inside PLAYER X WON")
        notice = '{"notice": "game_ended", "winner": "X"}'
        requests.post(rollup_server + "/notice", json={"payload": str2hex(notice)})
        logger.info(f"Game ended, notice:{notice}")
        return PLAYER_X
    elif has_won(board, size, PLAYER_O):
        logger.info(f"Inside PLAYER O WON")
        notice = '{"notice": "game_ended", "winner": "O"}'
        requests.post(rollup_server + "/notice", json={"payload": str2hex(notice)})
        logger.info(f"Game ended, notice:{notice}")
        return PLAYER_O
    elif board_full(board):
        logger.info(f"Inside BOARD FULL")
        notice = '{"notice": "game_ended", "result": "Draw"}'
        requests.post(rollup_server + "/notice", json={"payload": str2hex(notice)})
        return None

def new_game(board):
    logger.info(f"Initiating new_game!")

def join_game(address):
    logger.info(f"Initiating join_game!")

def valid_join_request(gameid_p2, player):
    logger.info(f"Initiating valid_join_request!")
    global game_id
    logger.info(f"Global game_id: {game_id}")
    logger.info(f"Input game_id: {gameid_p2}")
    if player == players['X'] or gameid_p2 != game_id:
        logger.info(f"Invalid request! Change request address and try again!")
        return False
    else:
        return True

def compare_dict(prev_state, next_state):
    """
    Compares two given dictionaries and returns true if the (saved_board) == (saved_board+input) 
    """
    mismatch_count = 0
    if prev_state == next_state:
        logger.info(f"Equal dictionaries!")
        return False
    else:
        logger.info(f"Unequal dictionaries!")
        for x in range(3):
            for y in range(3):
                if prev_state[(x, y)] != next_state[(x,y)]:
                    mismatch_count = mismatch_count + 1
        if mismatch_count == 1:
            return True
        else:
            return False

def valid_move(board, player):
    logger.info(f"Initiating valid_move!")
    """
    Check required: Neither player gets more than one move in a row!
    """
    empty_count = list(board.values()).count(EMPTY)
    logger.info(f"Input board state:\n{generate_board_pretty_str(board)}")
    logger.info(f"Empty count of input board: {empty_count}")
    empty_count_prev = list(saved_board.values()).count(EMPTY)
    logger.info(f"Saved board state:\n{generate_board_pretty_str(saved_board)}")
    logger.info(f"Empty count of saved board: {empty_count_prev}")
    #todo -> no need of empty count. compare_dict() should do!
    if empty_count == empty_count_prev - 1 and compare_dict(saved_board, board):
        seta = set(saved_board.items())
        setb = set(board.items())
        setdiff = seta ^ setb
        logger.info(f"New input entered is: {setdiff}")
        global players
        logger.info(f"{players} AND request by {player}")
        if (str(setdiff).find('X')>=0 and player==players['X']) and (turn=='X'):
            logger.info(f"Valid move from Player X")
            return True
        elif (str(setdiff).find('O')>=0 and player==players['O']) and (turn=='O'):
            logger.info(f"Valid move from Player O")
            return True
        else:
            logger.info(f"Inputs rejected! Possible errors:\n1. Input differs from 'X' or 'O'\n2. Input player assigned is different\n3. Not your turn!")
            return False
        return True
    else:
        return False



def handle_advance(data):
    try:
        logger.info(f"Received advance request data {data}")
        request_metadata = data['metadata']
        payload = json.loads(hex2str(data['payload']))
        request_type: str = payload.get('request', 'unknown').lower()
        status = "accept"
        global players
        global turn
        if request_type == RequestType.NEW_GAME.value:
            player = request_metadata['msg_sender']
            logger.info(f"New Game request received from {player}")
            players['X'] = player  #assign 'X' to game creater
            global saved_board
            saved_board = init_board(3)
            logger.info(f"New board initialised:\n{generate_board_pretty_str(saved_board)}")
            global game_id
            game_id = randint(100, 999)
            notice = '{"id":1, "notice": "new_game_created", "gameid": "'+str(game_id)+'"}'
            requests.post(rollup_server + "/notice", json={"payload": str2hex(notice)})
            logger.info(f"New game started -> 'X' assigned to player: {players['X']}")
            logger.info(f"Opponent can join with Game ID: {game_id}")
        elif request_type == RequestType.JOIN_GAME.value:
            player = request_metadata['msg_sender']
            gameid_p2 = payload.get('id')
            logger.info(f"Join Game request received from {player} with id {gameid_p2}")
            if valid_join_request(gameid_p2, player):
                players['O'] = player
                notice = '{"id":2, "notice": "opponent_joined", "gameid": "'+str(gameid_p2)+'"}'
                requests.post(rollup_server + "/notice", json={"payload": str2hex(notice)}) 
                logger.info(f"Opponent joined! Let's begin. {players}")
            else:
                logger.info(f"Invalid join request!")
        elif request_type == RequestType.BOARD_UPDATE.value:
            logger.info(f"New board update request received {request_type}")
            board_state = payload.get('move')
            board_dict = board_list2dict(board_state)
            player = request_metadata['msg_sender']
            if valid_move(board_dict, player):
                if turn == 'O':
                    turn = 'X'
                    logger.info(f"Next turn: X")
                elif turn == 'X':
                    turn = 'O'
                    logger.info(f"Next turn: O")
                saved_board = board_dict
                logger.info(f"Board updated:\n{generate_board_pretty_str(saved_board)}")
                board_size: int = payload.get('size')
                #board_list = board_dict2list(saved_board)
                board_str = str(saved_board)
                #board_json = json.dumps(saved_board)
                #logger.info(f"board list :{board_list}")
                notice = '{"id":3, "notice": "board_updated", "state":"'+board_str+'", "next":"'+turn+'"}'
                #notice_json = json.dumps(notice)
                logger.info(f"notice : {notice}")
                requests.post(rollup_server + "/notice", json={"payload": str2hex(notice)})
                logger.info(f"Current board size: {board_size}")
                #Check if anybody won!
                game_winner(board_dict, board_size)
            else:
                logger.info(f"Invalid update request")

        else:
            logger.error(f"Error in field 'request'. Expecting 'new' 'join' or 'update'")
            status = "reject"
    except Exception as e:
        logger.error(f"Error processing data: {data}\n\nException: {e}")
        status = "reject"
    return status

def handle_inspect(data):
    logger.info(f"Received inspect request data {data}")
    logger.info("Adding report")
    response = requests.post(rollup_server + "/report", json={"payload": data["payload"]})
    logger.info(f"Received report status {response.status_code}")
    return "accept"

handlers = {
    "advance_state": handle_advance,
    "inspect_state": handle_inspect,
}

finish = {"status": "accept"}
while True:
    logger.info("Sending finish")
    response = requests.post(rollup_server + "/finish", json=finish)
    logger.info(f"Received finish status {response.status_code}")
    if response.status_code == 202:
        logger.info("No pending rollup request, trying again")
    else:
        rollup_request = response.json()
        handler = handlers[rollup_request["request_type"]]
        finish["status"] = handler(rollup_request["data"])
