import argparse
from dataclasses import dataclass
from pathlib import Path
import json
import tempfile
from typing import Optional

from EntityLibPy import EntityLib
from graphviz import Digraph

from PropertyGrapher.grapher.styles import (
    BaseNodeStyle,
    PrefabNodeStyle,
    SubSceneNodeStyle,
    SubSceneArrowStyle,
    PrefabArrowStyle,
    EditedPrefabSubSceneArrow,
)
from PropertyGrapher.utils.property_helper import GraphProperty


@dataclass
class GraphOrient:

    TopToBottom: str = "TB"
    BottomToTop: str = "BT"


class PropertyGrapher:
    """Represent Property's dependencies using Graphviz.Digraph()."""

    _file_suffix = None
    _graph_orient = GraphOrient.BottomToTop

    def __init__(
        self, root_prop: GraphProperty, graphs_output_path: Path, view: bool = True
    ):
        self.root_prop = root_prop
        self.output_path = graphs_output_path
        self.graph = Digraph(
            comment=f"Dependencies of {root_prop.name}",
            graph_attr={"rankdir": self._graph_orient, "dpi": "200"},
            strict=True,
        )
        self.view = view

        self.errors = []

    @property
    def graph_name(self) -> str:
        return self.root_prop.name

    @property
    def graph_output_path(self) -> str:
        return Path(
            self.output_path,
            self.graph_name,
        ).as_posix()

    @staticmethod
    def get_prop_label(prop: GraphProperty) -> str:
        if not prop.property_name:
            return prop.file_name
        elif not prop.file_name:
            return prop.property_name
        else:
            return f"<{prop.property_name}<br/>---------<br/>{prop.file_name}>"

    def add_node(
        self,
        prop: GraphProperty,
        graph: Digraph,
        node_style: BaseNodeStyle,
        name: str = None,
    ):
        graph.node(
            name if name else prop.name,
            label=self.get_prop_label(prop),
            shape=node_style.shape,
            fillcolor=node_style.color,
            style=node_style.style,
            tooltip=prop.file_path,
        )

    def get_arrow_style(
        self,
        source_prop: GraphProperty,
        destination_prop: GraphProperty,
        node_style: BaseNodeStyle,
    ) -> Optional[BaseNodeStyle]:
        if node_style == PrefabNodeStyle:
            arrow_style = PrefabArrowStyle
        elif destination_prop.is_introduced_in(source_prop):
            arrow_style = SubSceneArrowStyle
        elif destination_prop.is_set:
            arrow_style = EditedPrefabSubSceneArrow
        else:
            arrow_style = None
        return arrow_style

    def connect_nodes(
        self,
        source_prop: GraphProperty,
        destination_prop: GraphProperty,
        graph: Digraph,
        node_style: BaseNodeStyle,
    ) -> None:

        arrow_style = self.get_arrow_style(source_prop, destination_prop, node_style)
        if arrow_style:
            graph.edge(
                source_prop.name,
                destination_prop.name,
                color=arrow_style.color,
                style=arrow_style.style,
            )

    def add_and_connect(
        self,
        source_prop: GraphProperty,
        destination_prop: GraphProperty,
        graph: Digraph,
        node_style: BaseNodeStyle,
    ) -> None:

        self.add_node(
            destination_prop,
            graph,
            node_style=node_style,
        )

        self.connect_nodes(
            source_prop, destination_prop, graph, node_style=node_style
        )

    def log_errors(self) -> None:
        if not self.errors:
            return

        print("SOME ERRORS HAPPENED:")
        for error in list(set(self.errors)):
            print(f"\t- {error}")

    def generate_graph(self) -> Optional[dict]:
        print(f"Generate graph for {self.root_prop.name}")
        if self.create_graph(self.root_prop, self.graph):
            self.graph.attr(ranksep="2")
            self.log_errors()

            json_string = self.graph.pipe("json").decode()

            return json.loads(json_string)
        return None

    def generate_graph_files(self, graph_data: dict) -> None:
        with open(f"{self.graph_output_path}.json", "w") as json_file:
            json.dump(graph_data, json_file, indent=2, sort_keys=True)

        self.graph.render(
            self.graph_output_path,
            view=self.view,
            format="png",
        )
        print(f"{self.graph_output_path}.png and {self.graph_output_path}.json created")

    def create_graph(self, prop: GraphProperty, graph: Digraph) -> bool:

        # We don't want to display
        # overriden property's hierarchy
        if prop.overriden:
            return False

        if prop == self.root_prop:
            self.add_node(prop, graph, node_style=SubSceneNodeStyle)

        elif not prop.prefab and not prop.sub_scenes:
            return False

        if prop.prefab:
            sub_graph = graph
            self.add_and_connect(
                prop,
                prop.prefab,
                sub_graph,
                node_style=PrefabNodeStyle,
            )
            self.create_graph(prop.prefab, sub_graph)

        for sub_scene in prop.sub_scenes:
            self.add_and_connect(
                prop,
                sub_scene,
                graph,
                node_style=SubSceneNodeStyle,
            )
            self.create_graph(sub_scene, graph)

        return True


def create_graph(
    entity_lib: EntityLib,
    file_to_open: Path,
    output_path: Path,
    view=True,
    generate_files=True,
):

    prop_graph = PropertyGrapher(
        GraphProperty.load_from_file(entity_lib, file_to_open),
        output_path,
        view=view,
    )
    graph_data = prop_graph.generate_graph()

    if generate_files:
        prop_graph.generate_graph_files(graph_data)

    return graph_data

