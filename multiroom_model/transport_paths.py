from typing import List,  Dict, Union, TypeVar
from dataclasses import dataclass
from .aperture import Aperture, Side

Room = TypeVar('Room')

@dataclass
class TransportPathParticipation:
    """
        @brief The involvement of an aperture in a transport path
        If reversed then the 2nd room of the aperture comes first in the transport path
    """
    aperture: Aperture
    reversed: bool = False


@dataclass
class TransportPath:
    """
        @brief A route from a start to an end (probably outside sides of the house)
        Defined by the ordered list of Apertures traversed
    """
    start: Union[Room | Side]
    end: Union[Room | Side]
    route: List[TransportPathParticipation]


def paths_through_building(rooms: List[Room], apertures: List[Aperture]) -> List[TransportPath]:
    """
        @brief Given a list of rooms and a list of apertures joining them (either to each other or the outside)
        Produces a list of the unique transport paths from one outside side of the house to another
        Each path goes through each room only once, preventing cycles
    """

    # build a graph where nodes are either rooms or outsides, and edges are apertures
    @dataclass
    class Node:
        item: Union[Room | Side]
        edges: List

    @dataclass
    class Edge:
        source: Node
        destination: Node
        aperture: TransportPathParticipation

    graph: Dict[Union[Room | Side], Node] = {}
    for s in [Side.Back, Side.Front, Side.Left, Side.Right]:
        graph[s] = Node(item=s, edges=[])
    for r in rooms:
        graph[r] = Node(item=r, edges=[])

    for a in apertures:
        node_1: Node = graph[a.room1]
        node_2: Node = graph[a.room2]
        node_1.edges.append(Edge(source=node_1, destination=node_2, aperture=TransportPathParticipation(a, False)))
        node_2.edges.append(Edge(source=node_2, destination=node_1, aperture=TransportPathParticipation(a, True)))

    # method to find all the paths from one start node to an end node

    def all_paths_between(start_node, end_node) -> List[TransportPath]:
        result: List[TransportPath] = []

        # we don't want to be able to leave the building and reenter it
        # exclude those outsides which are not the start or end
        excluded_nodes = [r for r in [graph[Side.Front], graph[Side.Left], graph[Side.Back],
                                      graph[Side.Right]] if r is not start_node and r is not end_node]

        # recursive utility function
        def find_all_paths(current_node: Node, final_destination: Node, visited: List[Node], path: List[TransportPathParticipation]):
            if (current_node == final_destination):
                result.append(TransportPath(start=start_node.item, end=end_node.item, route=path))
                return
            new_visited = visited.copy()
            new_visited.append(current_node)
            for edge in current_node.edges:
                if (edge.destination not in visited):
                    new_path = path.copy()
                    new_path.append(edge.aperture)
                    find_all_paths(edge.destination, final_destination, new_visited, new_path)

        # invoke the recursive function
        find_all_paths(start_node, end_node, excluded_nodes, [])
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
