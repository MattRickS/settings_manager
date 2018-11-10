# Settings Manager

_A simple interface for fixed type settings that provides automated UI and CLI._

Settings Manager is ideal for configuration based settings without having to update the code base. It can be used to launch a UI (Qt) or present a command line (argparse) tool using only the objects provided in the repository.

Each setting is a single object with a name, type, value and additional properties. If the setting is a list type, it also has a subtype for the values it should contain. Multiple settings are grouped in a SettingsGroup.

## Example Usage
The simple usage example below will present a UI with three settings.
```python
from settings_manager import SettingsGroup
from settings_manager.ui import SettingsViewer


settings = SettingsGroup({
    'max_count': {
        'default': 3,
        'minmax': (1, 5),
        'label': 'Max Number of Items'
    },
    'directory': '',
    'filetypes': {
        'default': ['png'],
        'choices': ['png', 'jpg', 'exr']
    }
})
widget = SettingsViewer.launch(settings)
```

## Settings Group
SettingsGroup acts like an OrderedDict, using the setting name as the key. Settings are ordered to provide consistent UI/CLI behaviour. Each setting value can be accessed directly with `get()` and `set()`, and the Setting object can be retrieved with `setting()`.
Settings can be added one at a time, or in batch. Batching settings accepts a list or dict of valid data, or another SettingsGroup (valid data means a key value pair, or a dictionary of properties).
Convenience methods exist for writing to/from json and creating an ArgumentParser. The SettingsGroup is used when generating an automatic UI.

## Properties
A Setting has a set of fixed properties as listed below. Custom properties can be added at creation or using `set_property`. Note: some properties may be automatically set based on incomplete user data.

| property | type            | description |
|----------|-----------------|-------------|
| choices  | list[object]    | A list of valid values for the setting. Must match the settings type and contain the default value (if default is not None).
| default  | object          | The base value that determines whether a setting is modified and what it reverts to when using `reset()`. By default this is value the setting is initialised with.
| hidden   | bool            | Prevents the setting from showing up in UI or CLI. CLI hidden can be overridden at creation time. Defaults to False.
| label    | str             | The UI display name. If not provided, it uses the setting name with underscores replaced with spaces.
| minmax   | tuple[int, int] | A fixed range for the setting. For numeric settings, the value must fit inside the range. For list and string settings, it restricts the length of the value.
| nullable | bool            | Whether or not the setting can be set to None. Defaults to False.
| tooltip  | str             | Help message for CLI and Tooltip for UI.
| widget   | type            | Class to use for the widget. If not set, the default UI widget is used.


## Settings UI
SettingsViewer automatically builds a GridLayout for a SettingsGroup, where each row in the grid is comprised of a QLabel, the setting widget, and a checkbox if the setting is nullable. A setting with a None value has it's widget disabled. A setting's row can be retrieved with `get_row()` using the Setting object or it's name.

Launching the UI can be done with or without an existing QApplication using the `SettingsViewer.launch()` class method.

#### settingChanged Signal
Whenever a setting is modified the settingChanged signal is emitted with the Setting object (note, the value must be changed for the signal to emit, not just be set). This is true for the individual widgets and the SettingsViewer.

#### Modifying rows
A number of convenience methods are provided for quick modification of the entire row:
* `set_setting_hidden`  -- hides/shows the entire row
* `set_setting_modified` -- updates the look of the row to indicate the value is modified. Default behaviour sets the label to bold, but custom looks can be defined by subclassing the method.
* `set_setting_none` -- sets the setting to None, updating the UI accordingly

#### Checkable Combo Box
The UI provides a CheckableComboBox widget which acts like a regular QComboBox with check state for each item. This is used by default for "Multi choice" settings, ie, a list setting with the choices property.

#### Custom Setting Widget
To use a specific UI class for a particular Setting object, set the 'widget' property to the class to use. The class must accept the Setting object as the first argument to `__init__`.


## Making a Custom SettingUI
To create a custom UI for a setting, inherit from SettingUI and implement the following methods:
* `setValue()` -- update the widget (should trigger the signal that triggers onValueChanged)
* `value()` -- return the widget value
* `onValueChanged` -- to convert any UI values to python values before calling the base method, eg, QtCore.Qt.Checked -> True
* [Optional] `setSetting()` -- after calling the superclass method, implement any additional setup that might be required
* Connect the widget's normal 'valueChanged' signal to self.onValueChanged
