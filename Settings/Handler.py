import discord
from discord.ext import commands

def check_access_command():
    pass

# Check Global Author
def check_author(author):
    def inner_check(message):
        if message.author == author:
            return True
        else:
            return False
    return inner_check

# UNO Section
def check_author_join_uno(channel_id):
    def inner_check(message):
        if (message.content.lower() == "join" or message.content.lower() == "skip") and message.channel.id == channel_id:
            return True
        else:
            return False
    return inner_check

def check_uno_pick_card(author, his_cards: list or tuple):
    def inner_check(message):
        try:
            if message.author == author and int(message.content) > 0 and int(message.content) <= len(his_cards):
                return True
            else:
                return False
        except Exception as exc:
            return False
    return inner_check

def check_uno_match(crn, nxt): # id, color, type, name, image_url, bin, number
    if crn[1] == nxt[1] or nxt[1] == 'black': # Check Color
        return True
    elif crn[6] is not None and nxt[6] is not None and crn[6] == nxt[6]: # Check Number
        return True
    elif crn[2] != "normal" and nxt[2] != "normal" and crn[2] == nxt[2]: # Check Card Type
        return True
    else:
        return False
    
def check_uno_can_draw(crn, deck: list or tuple):
    for card in deck: 
        if crn[1] == card[1] or card[1] == 'black': # Check Color
            return True 
        if crn[6] is not None and card[6] is not None and crn[6] == card[6]: # Check Number
            return True
        if crn[2] != "normal" and card[2] != "normal" and crn[2] == card[2]: # Check Card Type
            return True
    else:
        return False
    
def check_uno_stack(deck: list or tuple):
    for card in deck:
        if card[2] == "plus":
            return True
    else:
        return False
    
def check_uno_person_turn(turn, cond: dict, many_ppl: int): # {"skip", "reversed", "stack":[,]}
    next_turn = turn
    if cond['reversed'] is True:
        if cond['skip'] is True:
            cond['skip'] = False
            next_turn -= 2
        else:
            next_turn -= 1
    else:
        if cond['skip'] is True:
            cond['skip'] = False
            next_turn += 2
        else:
            next_turn += 1
    if next_turn < 0:
        next_turn += (many_ppl + 1)
    if next_turn > many_ppl:
        next_turn -= (many_ppl + 1)
    return next_turn, cond

def check_uno_card_effect(crn_cond, card): # {"skip", "reversed", "stack":[,]}
    if card[2] == "normal":
        crn_cond['skip'] = False
        crn_cond['stack'][0], crn_cond['stack'][1] = False, 0
        return crn_cond
    if card[2] == "plus":
        crn_cond['skip'] = False
        crn_cond['stack'][0] = True
        if '4' in card[3]:
            crn_cond['stack'][1] += 4
            return crn_cond
        if '2' in card[3]:
            crn_cond['stack'][1] += 2
            return crn_cond
    if card[2] == "reverse":
        crn_cond['skip'] = False
        if crn_cond["reversed"] is True:
            crn_cond["reversed"] = False
        else:
            crn_cond["reversed"] = True
        return crn_cond
    if card[2] == "special":
        crn_cond['skip'] = False
        return crn_cond
    if card[2] == 'skip':
        crn_cond['skip'] = True
        return crn_cond
    
def uno_game_pick_color(author):
    def inner_check(message):
        if message.author == author and (message.content.lower() == "green" or message.content.lower() == "blue" or message.content.lower() == "red" or message.content.lower() == "yellow"):
            return True
        else:
            return False
    return inner_check

# Utility
def convert_to_binary_type(filename):
    f = open(filename, 'rb')
    blobData = f.read()
    f.close()
    return blobData