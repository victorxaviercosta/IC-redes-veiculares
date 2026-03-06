"""
graphs/graphs.py
------------------------------

...
"""

from ..domain.types import LaneData, Point, Grid
from ..params import DEFAULT_GRID_SIZE

import xml.etree.ElementTree as ET
import networkx as nx


class NetworkGraph() :
    """  """

    def __init__(self, network_filepath : str, lane_data : dict[str, LaneData], grid_size : int = DEFAULT_GRID_SIZE):
        self.network_graph : nx.DiGraph = nx.DiGraph() # The network is a directed graph
        self.lane_centers : dict[str, Point] = {}
        self.grid : Grid = Grid(0, Point(0,0), Point(0,0), 0.0, 0.0)
        self.network_grid : dict[tuple[int, int], list[str]] = {}

        self.parse_network_to_graph(network_filepath, lane_data, grid_size)

    def parse_network_to_graph(self, network_filepath : str, lane_data : dict[str, LaneData], grid_size : int) -> None:
        """
        Example Structure for a SUMO edge on .net.xml file:
            <edge id="edge_id" from="from_id" to="to_id" priority="1" type="highway.service" shape="692.35,633.54 702.77,628.64">
                <lane id="lane_id" index="0" allow="pedestrian delivery bicycle" speed="5.56" length="3.14" shape="694.54,630.74 697.38,629.40">
                    <param key="origId" value="1075226350"/>
                </lane>
                <param key="origFrom" value="9861352748"/>
            </edge>
        """

        """
        Lane lenght and vehicle time count relation (influence in the wieght):
            W = LL / VT
        """

        xml_tree: ET.ElementTree[ET.Element[str]] = ET.parse(network_filepath)
        xml_root: ET.Element[str] = xml_tree.getroot()

        for edge in xml_root.findall("edge"):
            if edge.get("type") != "highway.footway":
                node_origin : str = edge.get("from")
                node_destiny: str = edge.get("to")
                node_id     : str = edge.get("id")
                weight : float = 0

                if node_origin and node_destiny:
                    weight = 0
                    for lane in edge.findall("lane"):
                        lane_id : str = lane.get("id")
                        lane_shape = lane.get("shape")

                        self.lane_centers[lane_id] = NetworkGraph.__get_lane_center(lane_shape) # for later building the network grid.

                        if lane_id in lane_data.keys():
                            weight += lane_data[lane_id].vehicle_time
                            lane_lenght = lane_data[lane_id].lane_length
                    
                    # Getting the inverse of the weight so that most visited lanes get the least weight.
                    if weight == 0:
                        weight = float("inf") # Non-visited lanes will be considered with infinity weight.
                    else:
                        weight = round((lane_lenght / weight), 2)

                    # Getting positions of each lane in the edge's shape
                    pos : list[Point] = [
                        tuple(map(float, p.split(",")))
                        for p in lane_shape.strip().split()
                    ]
                    # Adding the new edge to the graph
                    self.network_graph.add_edge(node_origin, node_destiny, id=node_id, weight=weight, pos=pos)

        self.build_grid(grid_size)


    @staticmethod
    def __get_lane_center(lane_shape : str) -> Point:
        """ Gets the lane's center point from it's shape """

        shape_points = [
            tuple(map(float, p.split(",")))
            for p in lane_shape.strip().split()
        ]

        xs, ys = zip(*shape_points)
        center_x, center_y = sum(xs) / len(xs), sum(ys) / len(ys)

        return Point(center_x, center_y)


    def __get_boundings(self) -> None:
        xs : list[float] = [p.x for p in self.lane_centers.values()]
        ys : list[float] = [p.y for p in self.lane_centers.values()]

        self.grid.bottom_left = Point(min(xs), min(ys))
        self.grid.top_right   = Point(max(xs), max(ys))


    def __get_grid_dimentions(self, grid_size : int) -> None :
        self.grid.size = grid_size
        self.grid.cell_width  = (self.grid.top_right.x - self.grid.bottom_left.x) / grid_size
        self.grid.cell_height = (self.grid.top_right.y - self.grid.bottom_left.y) / grid_size
            
    def __get_grid_cell(self, point : Point) -> tuple[int, int] :
        lin = int((point.x - self.grid.bottom_left.x) / self.grid.cell_width)
        col = int((point.y - self.grid.bottom_left.y) / self.grid.cell_height)

        lin = min(lin, self.grid.size - 1)
        col = min(col, self.grid.size - 1)

        return lin, col

    def build_grid(self, grid_size : int) -> None:
        self.__get_boundings()
        self.__get_grid_dimentions(grid_size)
        
        for lane_id, lane_center in self.lane_centers.items():
            grid_cell : tuple[int, int] = self.__get_grid_cell(lane_center)
            if grid_cell not in self.network_grid.keys() :
                self.network_grid[grid_cell] = []
            self.network_grid[grid_cell].append(lane_id)


    def show(self, with_labels : bool = False, arrows: bool = False):
        import matplotlib.pyplot as plt
        from random import choice

        pos : dict[str, tuple] = {}
        for u, v, data in self.network_graph.edges(data=True):
            points = data["pos"]
            pos[u] = points[0]
            pos[v] = points[-1]

        if False:
            if nx.check_planarity(self.network_graph, counterexample=False)[0]:
                pos : dict[str, tuple] = nx.planar_layout(self.network_graph)

            else:
                start = list(self.network_graph.nodes())[0]
                pos : dict[str, tuple] = nx.bfs_layout(self.network_graph, start)  # other layouts: shell_layout, circular_layout, etc.

        nx.draw(self.network_graph, pos=pos, with_labels= with_labels, node_size=1, font_size=10, arrows=arrows)

        if with_labels:
            edge_labels = nx.get_edge_attributes(self.network_graph, "weight")
            nx.draw_networkx_edge_labels(self.network_graph, pos, edge_labels=edge_labels)

        for i in range(self.grid.size + 1):
            plt.plot([self.grid.bottom_left.x, self.grid.top_right.x], [self.grid.bottom_left.y + i * self.grid.cell_height, self.grid.bottom_left.y + i * self.grid.cell_height], color="red")
            plt.plot([self.grid.bottom_left.x + i * self.grid.cell_width, self.grid.bottom_left.x + i * self.grid.cell_width], [self.grid.bottom_left.y, self.grid.top_right.y], color="red")

        plt.show()


if __name__ == "__main__" : 
    net_graph : NetworkGraph = NetworkGraph("scenarios/ev_test_grid/ev_test.net.xml", lane_data={})
    
    print(f"GRID:")
    for region in net_graph.network_grid.keys():
        print(f"{region}: [ ", end="")
        for lane in net_graph.network_grid[region]:
            print(f"\"{lane}\", ", end="")
        print(" ]\n")

    net_graph.show()
    