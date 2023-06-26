from dataclasses import dataclass


@dataclass
class BaseNodeStyle:
    color: str = NotImplementedError()
    shape: str = "box"
    style: str = "filled"


@dataclass
class SubSceneNodeStyle(BaseNodeStyle):
    """Node style for sub scene representation."""
    color: str = "cadetblue1"


@dataclass
class OverridenSubSceneNodeStyle(BaseNodeStyle):
    """Node style for overriden sub scene representation."""
    color: str = "darkorange"


@dataclass
class PrefabNodeStyle(BaseNodeStyle):
    """Node style for prefab representation."""
    color: str = "aquamarine"


@dataclass
class BaseArrowStyle:
    color: str = NotImplementedError()
    style: str = "solid"


@dataclass
class PrefabArrowStyle(BaseArrowStyle):
    """Arrow style for prefab connection."""
    color: str = "red"


@dataclass
class SubSceneArrowStyle(BaseArrowStyle):
    """Arrow style for sub scene connection."""
    color: str = "blue"


@dataclass
class EditedPrefabSubSceneArrow:
    """Arrow style for edited prefab sub scene connection."""
    color: str = "blue"
    style: str = "dashed"


@dataclass
class OverridePrefabSubSceneArrow:
    """Arrow style for edited prefab sub scene connection."""
    color: str = "firebrick2"
    style: str = "dotted"
