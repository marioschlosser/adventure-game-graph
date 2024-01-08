prompt_loop = "Return to step 1 in the game loop and rerun get_room_info() to get the updated information about the current room."

# Rooms visited at least once by the player
rooms_visited = []

# Actions that the player has completed
actions_completed = []

# Player's current location
location = 'RoomA'

import random
import numpy as np

# Function to initialize the game structure
def init_game():
    global actions_available
    global rooms_available

    # Function to add ancestor node in game graph
    def add_ancestor(node, ancestor):
        # add ancestor to node's list of ancestors, but only if it isn't already in the list
        if ancestor not in node_ancestors[node]:
            node_ancestors[node].append(ancestor)

        # compile list of out-links for this node: this is the list of nodes for which node is an in-link
        node_out = []
        for other_node in range(0, len(node_in)):
            if node in node_in[other_node]:
                node_out.append(other_node)

        # call add_ancestor for all out-links of this node
        for other_node in node_out:
            add_ancestor(other_node, ancestor)

    # probability distribution for in-links of a node, from new nodes
    p_in_new = [0, 0.7, 0.25, 0.05]  # @param {type:"raw"}

    # probability distribution for in-links of a node, from existing nodes
    p_in_existing = [0.7, 0.3]  # @param {type:"raw"}

    # total number of nodes for the graph
    num_nodes_max = 20  # @param {type:"integer"}

    # the number of initially accessible rooms
    num_rooms_initial = 3  # @param {type:"integer"}

    # the number of rooms in total
    num_rooms_total = 7  # @param {type:"integer"}

    # the in-links for each node: the set of nodes that directly drive this node
    node_in = [[]]
    # the ancestors of each node: the set of nodes that directly and indirectly drive this node
    node_ancestors = [[]]
    # the room that each node is in
    node_room = [0]
    # the set of nodes that are rooms
    rooms = []

    num_nodes = 0

    for node in range(0, num_nodes_max):
        # generate a random number of in-links for this new node from new nodes
        num_new_in = np.random.choice(len(p_in_new), 1, p=p_in_new)[0]
        # generate a random number of in-links for this node from existing nodes
        num_existing_in = np.random.choice(len(p_in_existing), 1, p=p_in_existing)[0]

        # create range of numbers: node to node + num_new_in to new_in
        new_in = list(range(len(node_in), len(node_in) + num_new_in))

        # increase node count by newly generated nodes
        num_nodes += num_new_in

        # create the in-links lists for num_new_in nodes
        for i in range(0, num_new_in):
            node_in.append([])
            node_ancestors.append([])
            node_room.append(None)

        # add that list to the current node's in-links
        node_in[node] = new_in

        # create empty list of ancestors for this node
        node_ancestors[node] = []

        # update ancestors for this node recursively
        add_ancestor(node, node)

        # generate list of all existing nodes where node isn't an ancestor
        existing_nodes = []
        for i in range(0, node):
            if node not in node_ancestors[i]:
                existing_nodes.append(i)

        # pick num_existing_in nodes from that list randomly
        existing_in = random.sample(existing_nodes, min(num_existing_in, len(existing_nodes)))

        # add that list to the current node's in-links
        node_in[node] += existing_in

    # create list of non-leaf nodes
    non_leaf_nodes = [i for i, sublist in enumerate(node_in) if sublist]

    # get the list of leaf nodes: all remaining rooms
    leaf_nodes = [element for element in range(0, len(node_in)) if element not in non_leaf_nodes]

    # average number of leaf nodes connected to an initial room, rounded up
    avg_leaf_nodes_per_room = int(np.ceil(len(leaf_nodes) / num_rooms_initial))

    # create the initial rooms and add them to the graph
    for i in range(0, num_rooms_initial):
        # create new node
        node_in.append([])
        node_ancestors.append([])
        node_room.append(None)
        room = len(node_in) - 1

        # this node is a room, so its room is just itself
        node_room[room] = room

        # add to the list of rooms
        rooms.append(room)

    # go through the leaf nodes and add them to the initial rooms randomly
    for leaf_node in leaf_nodes:
        # pick a random initial room
        room = random.choice(rooms)

        # add the leaf node to the room
        node_in[leaf_node].append(room)
        add_ancestor(leaf_node, room)

    # the number of rooms to unlock during the game
    num_unlocked_rooms = num_rooms_total - num_rooms_initial

    # pick this number of non-leaf nodes and make them rooms
    for i in range(0, num_unlocked_rooms):
        # pick a random non-leaf node from the list that excludes node 0
        room = random.choice(non_leaf_nodes)

        # add the room to the list of rooms
        rooms.append(room)

        # this node is a room, so its room is just itself
        node_room[room] = room

        # remove the room from the list of non-leaf nodes
        non_leaf_nodes.remove(room)

    # set all puzzle nodes to rooms
    for node in range(0, len(node_in)):
        # skip nodes that are already rooms
        if node in rooms:
            continue

        # pick a room node that is in this node's ancestors
        room = random.choice([ancestor for ancestor in node_ancestors[node] if ancestor in rooms])
        # set this as this node's room
        node_room[node] = room

    # room connections for all nodes
    node_connections = [[] for i in node_in]

    # rooms with at least one connection: initially just the first room
    rooms_with_connections = [rooms[0]]

    # connect the leaf rooms to each other
    for room in rooms:
        # only rooms that don't have connections yet
        if room not in rooms_with_connections:
            # pick one room among those rooms with at least one connection
            other_room = random.choice(rooms_with_connections)
            node_connections[room].append(other_room)
            node_connections[other_room].append(room)

            # add this room to the list of rooms with at least one connection
            rooms_with_connections.append(room)

    # iterate through all room nodes
    for room in rooms:
        # only non-leaf rooms
        if len(node_in[room]) > 0:
            # only rooms that don't have connections yet
            if room not in rooms_with_connections:
                # get the actions that unlock the room
                room_actions = node_in[room]

                # pick one of the unlocking actions at random and get the room it is in
                random_action = random.choice(room_actions)
                unlocking_room = node_room[random_action]

                # now create a connection to that room, and the other way around
                node_connections[room].append(unlocking_room)
                node_connections[unlocking_room].append(room)

    # non_rooms is the set of nodes that are not rooms
    non_rooms = [node for node in range(len(node_in)) if node not in rooms]

    # create the node names
    node_name = {node: "Room" + chr(ord('A') + rooms.index(node)) if node in rooms else "Action" + str(len(non_rooms) - non_rooms.index(node)) for node in range(len(node_in))}
    # set the name for the final node
    node_name[0] = "Game End"

    actions_available = {}
    rooms_available = {}

    # go backwards through all nodes
    for node in reversed(range(len(node_in))):
        # create list of all in-link names for this node
        node_in_names = []
        for other_node in node_in[node]:
            # only append non-rooms for conditions
            if other_node in non_rooms:
                node_in_names.append(node_name[other_node])

        if node in rooms:
            # if room:
            # get all the room's connections' names
            connection_names = []
            for other_node in node_connections[node]:
                connection_names.append(node_name[other_node])

            # add dictionary entry to rooms_available indexed with room name
            rooms_available[node_name[node]] = {"name": "TBD", "required": node_in_names, "connected": connection_names}
        else:
            # if action:
            # add dictionary entry to actions_available indexed with action name
            actions_available[node_name[node]] = {"name": "TBD", "room": node_name[node_room[node]], "required": node_in_names}

# Function to get all the necessary information about the current room
def get_room_info(room):
    room_info = {}
    room_info["name"] = rooms_available[room]["name"]

    # get actions that are available, not completed and currently possible in this room
    room_info["accessible_actions"] = get_actions(room, "accessible")

    # get actions that are available, not completed but lack requirements to be possible in this room
    room_info["inaccessible_actions"] = get_actions(room, "inaccessible")

    # get rooms that are connected to this room and currently accessible
    room_info["accessible_rooms"] = get_rooms(room, "accessible")

    # get rooms that are connected to this room but currently inaccessible
    room_info["inaccessible_rooms"] = get_rooms(room, "inaccessible")

    room_info["visited"] = has_visited(room)
    return room_info

# Function to get actions for the current room
def get_actions(room, all_or_some):
    room_actions = {}
    for action_id, action in actions_available.items():
        if action["room"] == room:
            # depending on all_or_accessible flag, return all actions or just those that are accessible
            if all_or_some == "all":
                room_actions[action_id] = {"name": action["name"], "required": action["required"]}
            elif all_or_some == "accessible":
                if is_action_accessible(action_id):
                    room_actions[action_id] = {"name": action["name"], "required": action["required"]}
            elif all_or_some == "inaccessible":
                if not is_action_accessible(action_id):
                    room_actions[action_id] = {"name": action["name"], "required": action["required"]}

    # remove the completed actions from the list
    for action in actions_completed:
        if action in room_actions:
            del room_actions[action]
    return room_actions

# Function to get the rooms connected to the current room
def get_rooms(room, all_or_some):
    room_rooms = {}
    # iterate through all rooms connected to this room
    connected_rooms = rooms_available[room]["connected"]

    # now get all open rooms connected to this room
    open_connected_rooms = []
    for room in connected_rooms:
        if all(action in actions_completed for action in rooms_available[room]["required"]):
            open_connected_rooms.append(room)

    if all_or_some == "all":
        for other_room in connected_rooms:
            room_rooms[other_room] = {"name": rooms_available[other_room]["name"], "required": rooms_available[other_room]["required"]}
    elif all_or_some == "accessible":
        for other_room in open_connected_rooms:
            room_rooms[other_room] = {"name": rooms_available[other_room]["name"], "required": rooms_available[other_room]["required"]}
    elif all_or_some == "inaccessible":
        for other_room in connected_rooms:
            if other_room not in open_connected_rooms:
                room_rooms[other_room] = {"name": rooms_available[other_room]["name"], "required": rooms_available[other_room]["required"]}

    return room_rooms

# Function to check if player has visited room
def has_visited(room):
    return room in rooms_visited

# Function to check if room can be accessed from the current location
def is_room_accessible(room):
    return room in get_rooms(location, "accessible")

# Function to check if all requirements for an action are fulfilled but the action hasn't been completed before
def is_action_accessible(action):
    return all(action in actions_completed for action in actions_available[action]["required"]) and action not in actions_completed

# Function to try to execute an action
def do_action(action):
    # check if action is accessible
    if not is_action_accessible(action):
        return "Can't do it. Missing one or more requirements for this action."

    # check if action is in the current location
    if actions_available[action]["room"] != location:
        return "Can't do it. This action is not available in this room."

    # check if action has already been done
    if action in actions_completed:
        return "Can't do it. This action has already been completed."

    # add action to completed actions
    actions_completed.append(action)

    return "Completed action: " + action + " = " + actions_available[action]["name"] + ". " + prompt_loop

# Function to try to move to a room
def move_to_room(room):
    global location

    # check if room is accessible
    if not is_room_accessible(room):
        return "Can't go there. Missing one or more requirements for this room, or not connected to current location."

    # check if room is the current location
    if room == location:
        return "Can't go there. Already in this room."

    # add room to visited rooms, if not already in there
    if room not in rooms_visited:
        rooms_visited.append(room)

    # set visited to True
    rooms_available[room]["visited"] = True

    # update location
    location = room

    return "Moved to room: " + room + " = " + rooms_available[room]["name"] + ". " + prompt_loop

init_game()
