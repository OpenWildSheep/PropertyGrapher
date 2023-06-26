# PropertyGrapher
Allows to display WildSheep's EntityLib's entities dependencies in a visual or json graph.  

Get EntityLib from [here]().  
Can be used with the [PropertyEditor]().

## Install

### Get repository

### Create virtual environment

Create a virtual environment using `venv`.  
Add requirements using `pip install -r requirements.txt`.  

You need to have built `EntityLib` and have `..\EntityLib\build\release` to your `PYTHONPATH`.  
You also need to have your `PropertyGrapher` parent's folder to your `PYTHONPATH`.

To use the PropertyEditor from the PropertyGrapher, you need to have your `PropertyEditor` parent's folder in your `PYTHONPATH`.

## Configure

The grapher get dependencies from:
- instanceOf properties
- Declared sub scenes "container" properties
  - Declare their name in the `containers` key of the `config.json` file

## How to use
THe grapher can be used as a CLI tool, allowing you to generate 
both png and json files representing the property's graph.

The grapher can also be used with a PySide2 UI, 
giving you access to more advanced features like opening a sub scenes in the grapher, 
the PropertyEditor or your default text editor. 

### With UI
Display an EntityLib's file dependencies in a nice PySide2 GUI.

Launch the following command:  
```shell
python path/to/your/PropertyGrapher/__main__.py path/to/raw/data path/to/schema
```

You can automatically open an EntityLib's file using:
```shell
python path/to/your/PropertyGrapher/__main__.py path/to/raw/data path/to/schema -f path/to/your/file
```

**Note**: `raw data` and `schema` paths are EntityLib's principles.  
Have a look at its documentation to know more about their use.

#### Navigation

- Use mouse left or middle clicks to move the view
- Use the middle mouse scroll to zoom in or out

#### Nodes context menu

- Do a right click on a node to:
  - Open it in the PropertyGrapher
  - Open it in the PropertyEditor (optional, only appears if the PropertyEditor is in the environment)
  - Open it in the default text editor

#### Menu

- Click on the open icon to open a new property file in a new tab
- Click on the reload icon to reload the current tab

### CLI generator
Generates both png and json representation of the EntityLib file's dependencies.

Launch the following command:
```shell
python path/to/your/PropertyGrapher/__main__.py path/to/raw/data path/to/schema -f path/to/your/file -ng
```

**Note**: You need to specify a file path to use the no-GUI version of the tool.  

By default png and json files are generated into your `tmp` folder.    
You can use `-o` flag to specify an output directory's path.   
```shell
python path/to/your/PropertyGrapher/__main__.py path/to/raw/data path/to/schema -f path/to/your/file -ng -o /path/to/output
```

**Note**: `raw data` and `schema` paths are EntityLib's principles.
Have a look at its documentation to know more about their use.

## Graph legend

- **Nodes**
  - Blue nodes represent main entities and sub entities through "containers" properties (see [configure](#configure))
  - Green nodes represent parent entities through instanceOf

- **Arrows**
  - Red arrows represent an instanceOf connection
  - Blue arrows represent a "container" property connection
    - Dashed blue arrows represent a sub scene override