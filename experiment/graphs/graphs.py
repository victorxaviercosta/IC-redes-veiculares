from domain.types import LaneData

import xml.etree.ElementTree as ET
import networkx as nx

def parse_network_to_graph(network_filepath: str, lane_data: dict[str, LaneData]) -> nx.DiGraph:
    xml_tree: ET.ElementTree[ET.Element[str]] = ET.parse(network_filepath)
    xml_root: ET.Element[str] = xml_tree.getroot()

    network_graph:nx.DiGraph = nx.DiGraph()

    """
    Structure for a SUMO edge on .net.xml file:
        <edge id="edge_id" from="from_id" to="to_id" priority="1" type="highway.service" shape="692.35,633.54 702.77,628.64">
            <lane id="lane_id" index="0" allow="pedestrian delivery bicycle" speed="5.56" length="3.14" shape="694.54,630.74 697.38,629.40">
                <param key="origId" value="1075226350"/>
            </lane>
            <param key="origFrom" value="9861352748"/>
        </edge>
    """

    for edge in xml_root.findall("edge"):
        node_origin:  str = edge.get("from")
        node_destiny: str = edge.get("to")
        node_id:      str = edge.get("id")
        weight: float = 0

        if node_origin and node_destiny:
            weight = 0
            for lane in edge.findall("lane"):
                lane_id: str = lane.get("id")
                if lane_id in lane_data.keys():
                    weight += lane_data[lane_id].visits_count
            
            # Getting the inverse of the weight so that most visited lanes get the least weight.
            if weight == 0:
                weight = float("inf") # Non-visited lanes will be considered with infinity weight.
            else:
                weight = 1 / weight

            # Adding the new edge to the graph
            network_graph.add_edge(node_origin, node_destiny, id=node_id, weight=weight)

    return network_graph



import matplotlib.pyplot as plt

def show_graph(graph: nx.DiGraph):
    pos: dict[str, tuple] = nx.circular_layout(graph)  # other layouts: shell_layout, circular_layout, etc.
    print(f"pos = {pos}")

    nx.draw(graph, pos=pos, with_labels=True, node_size=100, font_size=10)

    edge_labels = nx.get_edge_attributes(graph, "weight")
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

    plt.show()
