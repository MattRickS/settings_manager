import os
import tempfile
from settings_manager import Settings
from settings_manager.ui import show_settings


if __name__ == '__main__':
    # Initialise settings
    s = Settings()
    s.add('integer', 1)
    s.add('string1', None, data_type=str)
    s.add('float', 5.0)
    s.add('choice', 'A', choices=['A', 'B', 'C', 'D'])
    s.add('list', ['/path/to/one.txt', '/path/to/two.txt', '/path/three.txt'])
    s.add('bool', False)
    s.add('string2', 'Only if parent is enabled', data_type=str, parent='string1')
    s.add('string3', 'Only if parent is enabled', data_type=str, parent='string2')

    # Get a temporary file path, close the handle
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.close()
    json_path = temp.name
    print("Saving to:", json_path)

    # Show settings UI and write to file
    show_settings(s)
    s.to_json(json_path, values_only=False)

    # Read from file to a new settings object and show the new UI -- identical
    s2 = Settings.from_json(json_path)
    show_settings(s2)

    # Manually clean up temp path
    os.remove(json_path)
