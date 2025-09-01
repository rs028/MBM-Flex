from typing import List, Any, Dict, Set
from dataclasses import dataclass
from .window import Window, Side


class TransportPath:
    """
        @brief A route between 2 terminus (probably outside sides of the house)
        Defined by the ordered list of windows traversed
    """

    def __init__(self, terminus: Set[Any], route: List[Window]):
        self.terminus: Set[Any] = terminus
        self.route: List[Window] = route


def paths_through_building(rooms: List[Any], windows: List[Window]) -> List[TransportPath]:
    """
        @brief Given a list of rooms and a list of windows joining them (either to each other or the outside)
        Produces a list of the unique transport paths from one outside side of the house to another
        Each path goes through each room only once, preventing cycles
    """

    # build a graph where nodes are either rooms or outsides, and edges are windows
    @dataclass
    class Node:
        item: Any
        edges: List

    @dataclass
    class Edge:
        source: Node
        destination: Node
        window: Window

    graph: Dict[Any, Node] = {}
    for s in [Side.Back, Side.Front, Side.Left, Side.Right]:
        graph[s] = Node(item=s, edges=[])
    for r in rooms:
        graph[r] = Node(item=r, edges=[])

    for w in windows:
        node_1: Node = graph[w.room1]
        node_2: Node = graph[w.room2 or w.side_of_room_1]
        node_1.edges.append(Edge(source=node_1, destination=node_2, window=w))
        node_2.edges.append(Edge(source=node_2, destination=node_1, window=w))

    # method to find all the paths from one start node to an end node

    def all_paths_between(start_node, end_node) -> List[TransportPath]:
        result: List[TransportPath] = []

        # recursive utility function
        def find_all_paths(current_node: Node, final_destination: Node, visited: List[Node], path):
            if (current_node == final_destination):
                result.append(TransportPath(terminus={start_node.item, end_node.item}, route=path))
                return
            new_visited = visited.copy()
            new_visited.append(current_node)
            for edge in current_node.edges:
                if (edge.destination not in visited):
                    new_path = path.copy()
                    new_path.append(edge.window)
                    find_all_paths(edge.destination, final_destination, new_visited, new_path)

        find_all_paths(start_node, end_node, [], [])
        return result

    # Use this method 6 times to accumulate all routes between the 4 outside nodes
    result: List[TransportPath] = []
    result.extend(all_paths_between(graph[Side.Front], graph[Side.Left]))
    result.extend(all_paths_between(graph[Side.Front], graph[Side.Back]))
    result.extend(all_paths_between(graph[Side.Front], graph[Side.Right]))

    result.extend(all_paths_between(graph[Side.Left], graph[Side.Back]))
    result.extend(all_paths_between(graph[Side.Left], graph[Side.Right]))

    result.extend(all_paths_between(graph[Side.Back], graph[Side.Right]))

    return result
