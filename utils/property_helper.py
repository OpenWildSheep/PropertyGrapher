from __future__ import annotations

import itertools
import json
import os
from pathlib import Path
from typing import List, Tuple, Optional, Any

from EntityLibPy import EntityLib, DataKind
from EntityLibPy import Property as LibProperty


def load_config() -> dict:
    with open(
        os.path.join(os.path.realpath(os.path.dirname(__file__)), "..", "config.json")
    ) as config_file:
        return json.load(config_file)


CONFIG = load_config()


class GraphProperty:
    def __init__(
        self,
        prop: LibProperty,
        file_path: Path,
        property_name: Optional[str] = None,
        parent: GraphProperty = None,
        source_is_set: Optional[bool] = None,
    ) -> None:

        self.entity_lib = prop.entitylib
        self.property = prop
        self.parent = parent

        self.file_path = file_path.as_posix()
        self.file_name = file_path.name
        self.property_name = property_name
        self._property_path = None

        self.prefab = self.get_prefab()
        self.sub_scenes = self.get_sub_scenes()
        self.check_for_overrides()

        # Used to override is_set value from source property
        self.source_is_set = source_is_set

        # Used to store the name of the overriden property
        self.override = None
        self.overriden = False

    @property
    def name(self):

        if self.property_path:
            return self.property_path
        elif self.property_name:
            return self.property_name
        else:
            return self.file_name

    @property
    def property_path(self) -> Optional[str]:
        if self._property_path:
            if self.parent and self.parent.property_path:
                return f"{self.parent.property_path}/{self._property_path}"
            else:
                return self._property_path
        else:
            return None

    @property_path.setter
    def property_path(self, value: str) -> None:
        self._property_path = value

    @property
    def is_instance_of(self) -> bool:
        return not self.is_sub_scene

    @property
    def is_sub_scene(self) -> bool:
        if self.parent:
            return self in self.parent.sub_scenes
        else:
            return False

    @property
    def instance_of(self) -> Optional[str]:
        return self.property.first_instance_of

    @property
    def is_set(self) -> bool:
        if self.source_is_set is not None:
            return self.source_is_set
        else:
            return self.property.is_set

    @staticmethod
    def load_from_file(
        entity_lib: EntityLib,
        file_to_open: Path,
        property_name: str = None,
        parent: GraphProperty = None,
    ) -> GraphProperty:
        prop = entity_lib.load_property(file_to_open.as_posix())
        return GraphProperty(
            prop,
            file_to_open,
            property_name=property_name,
            parent=parent,
        )

    def is_introduced_in(self, prop: GraphProperty) -> bool:
        if not self.property.is_set:
            return False

        if not prop.prefab:
            return True

        return bool(
            prop.get_child_by_name(self.name)
        ) and not prop.prefab.get_child_by_name(self.name)

    def get_child_by_name(self, name: str) -> Optional[GraphProperty]:
        for child in self.sub_scenes:
            if child.name == name:
                return child
        return None

    def get_sub_scenes_containers(self) -> List[LibProperty]:
        sub_scenes = []
        for child_node_ref in CONFIG["containers"]:
            child_prop_name = child_node_ref.split("/")[-1]

            # Begin by searching children with matching names
            # name is taken from the last part of the declared container's path
            for child in self.property.search_child(child_prop_name):

                # Only keep direct children
                # a direct child has only one matching node reference path
                # in it own node reference path
                if child.absolute_noderef.count(child_node_ref) == 1:
                    sub_scenes.append(child)

        return sub_scenes

    def get_prefab(self) -> Optional[GraphProperty]:
        prefab = self.property.first_instance_of
        if prefab:
            return self.load_from_file(self.entity_lib, Path(prefab), parent=self)
        return None

    def get_sub_scenes(self) -> List[GraphProperty]:
        sub_scenes = []
        for container in self.get_sub_scenes_containers():
            for i in range(container.size):
                child_prop, child_name, _ = get_property_child_by_index(container, i)
                if not child_prop:
                    continue

                if child_prop.first_instance_of:
                    source_is_set = child_prop.is_set
                    new_sub_scene = self.load_from_file(
                        self.entity_lib,
                        Path(child_prop.first_instance_of),
                        property_name=child_name,
                        parent=self,
                    )

                    # Set source is set from child property instead
                    # of the one loaded from the instance of file
                    # This way we get the right is_set value for this sub property
                    new_sub_scene.source_is_set = source_is_set
                    new_sub_scene.property_path = child_prop.absolute_noderef

                else:
                    new_sub_scene = GraphProperty(child_prop, Path(child_name), parent=self)
                sub_scenes.append(new_sub_scene)
        return sub_scenes

    def check_for_overrides(self) -> None:

        if not self.prefab or not self.prefab.sub_scenes or not self.sub_scenes:
            return

        for sub_scene in self.sub_scenes:
            for prefab_sub_scene in self.prefab.sub_scenes:
                if (
                    sub_scene.property_path == prefab_sub_scene.property_path
                    and sub_scene.file_name != prefab_sub_scene.file_name
                ):
                    sub_scene.override = prefab_sub_scene
                    prefab_sub_scene.overriden = True

    def __repr__(self) -> str:
        return (
            f"{'-' * 30}\n"
            f"Name: {self.name}\n"
            f"Is sub scene: {self.is_sub_scene}\n"
            f"Is instance of: {self.is_instance_of}\n"
            f"Sub scenes: {len(self.sub_scenes)}\n"
            f"{'-' * 30}\n"
        )


def get_property_child_by_index(
    root_prop: LibProperty, index: int, inline: bool = False
) -> Tuple[LibProperty, str, Any]:
    kind = root_prop.schema.data_kind
    property_name = new_property = property_value = None

    if kind == DataKind.array:
        property_name = str(index)
        if index >= root_prop.size:
            property_name = index
        else:
            new_property = root_prop.get_array_item(index)

    elif kind == DataKind.map:
        for i, key in enumerate(root_prop.map_keys):
            if i == index:
                property_name = key
                new_property = root_prop.get_map_item(key)
                break

    elif kind == DataKind.object:
        if not inline:
            property_name = next(
                itertools.islice(root_prop.schema.properties.keys(), index, None)
            )
            new_property = root_prop.get_object_field(property_name)

    elif kind == DataKind.objectSet:
        for i, key in enumerate(root_prop.objectset_keys):
            if i == index:
                property_name = key
                new_property = root_prop.get_objectset_item(key)
                break

    elif kind == DataKind.unionSet:
        for i, key in enumerate(root_prop.unionset_keys):
            if i == index:
                property_name = key
                new_property = root_prop.get_unionset_item(key)
                break

    elif kind in [DataKind.boolean, DataKind.integer, DataKind.number, DataKind.string]:
        if index == 0:
            property_name = index
            new_property = root_prop
            property_value = root_prop.value
        else:
            property_name = index
            new_property = root_prop

    elif kind == DataKind.primitiveSet:
        property_name = str(index)
        if index >= root_prop.size:
            property_name = index
        else:
            property_value = root_prop.primset_keys[index]

    elif kind == DataKind.union:
        if index == 0:
            property_name = "Union"
            new_property = root_prop.get_union_data()
            property_value = root_prop.union_type
        elif index == 1:
            property_name = "Data"
            new_property = root_prop.get_union_data()

    return new_property, property_name, property_value
