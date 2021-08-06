from vslord_classes import *
from vslord_rules import *
from vslord_strategies import *
from vslord_gui import *

def look_up_room(player):
    player.connection.send_to_server("look_up_room")
    print(player.connection.receive_from_server())

def start_new_room(player):
    room_name = input("the name of room you want to start")
    player.connection.send_to_server("start_new_room: room_owner = %s, room_name = %s" % (player.name, room_name))

def join_room(player):
    room_name = input("the name of room you want to join")
    player.connection.send_to_server("join_room: player = %s, room_name = %s" % (player.name, room_name))

########
# Main #
########


###########
# Example #
###########

local_player = Player("yangbc", "password")
connection = Connection("65.49.192.141", 28716)
local_player.login()

start_new_room(local_player)

#   room = Room("doudizhu", local_player, local_player, Vslord)
#   room.add_player("yuanye")
#   room.add_player("lvyaqiao")


