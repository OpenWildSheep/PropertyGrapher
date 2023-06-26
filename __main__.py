import argparse
import tempfile
from pathlib import Path

from EntityLibPy import EntityLib

from PropertyGrapher.grapher import graph
from PropertyGrapher.ui import main_window


def create_no_gui_grapher(entity_lib: EntityLib, file_path: Path, output_path: Path):
    if not file_path:
        raise FileNotFoundError("Can only use no GUI mode with a provided file.")
    graph.create_graph(
        entity_lib,
        file_path,
        output_path,
    )


def create_gui_grapher(
    entity_lib: EntityLib, output_path: Path, file_path: Path = None
) -> main_window.GraphViewer:
    return main_window.create_window(
        entity_lib,
        output_path,
        file_path=file_path,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dependencies grapher")
    parser.add_argument("rawdata_path", help="Entity library rawdata_path")
    parser.add_argument("schema_path", help="Entity library schema path")
    parser.add_argument("-f", "--file", help="File to open", type=str)
    parser.add_argument(
        "-ng",
        "--no_gui",
        help="If set, launch the tool without GUI",
        action="store_true",
    )
    parser.add_argument(
        "-o",
        "--output_path",
        help="Set created graph output path, otherwise temp folder will be used",
    )
    args = parser.parse_args()

    _output_path = Path(args.output_path or tempfile.gettempdir())
    _file_path = Path(args.file) if args.file else None

    entity_lib = EntityLib(args.rawdata_path, args.schema_path)

    if args.no_gui:
        create_no_gui_grapher(entity_lib, _file_path, _output_path)
    else:
        create_gui_grapher(entity_lib, _output_path, file_path=_file_path)
