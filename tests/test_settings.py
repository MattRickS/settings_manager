import unittest
from settings_manager import Settings, SettingsError


class TestSettingsAdd(unittest.TestCase):
    def _add(self, val, **kwargs):
        s = Settings()
        try:
            s.add("val", val, **kwargs)
        except Exception as e:
            self.fail("Raised exception while adding {}: {}".format(type(val), e))

    def _add_fail(self, val, **kwargs):
        s = Settings()
        self.assertRaises(SettingsError, s.add, "val", val, **kwargs)

    def test_add_bool(self):
        self._add(True)

    def test_add_float(self):
        self._add(3.0)

    def test_add_int(self):
        self._add(3)

    def test_add_str(self):
        self._add("hello")

    def test_add_choices(self):
        self._add("yes", choices=["yes", "no", "maybe"])
        self._add(0, choices=[0, 1, 2, 3, 4])

    def test_add_fail(self):
        s = Settings()
        s.add("a", "b")
        # Setting default is not in choices
        self.assertRaises(SettingsError, s.add, "thing", 0, choices=["a", "b"])
        # Setting choices are not the right type
        self.assertRaises(SettingsError, s.add, "thing", 0, choices=[0, "b"])
        # Setting exists
        self.assertRaises(SettingsError, s.add, "a", "val")
        # Setting isn't a string
        self.assertRaises(SettingsError, s.add, 0, "val")


class TestSettingsSetter(unittest.TestCase):
    def test_set(self):
        s = Settings()
        s.add("key", "value")
        self.assertEqual(s.get("key"), "value")
        s.set("key", "new_value")
        self.assertEqual(s.get("key"), "new_value")

    def test_set_item(self):
        s = Settings()
        s.add("key", "value")
        self.assertEqual(s["key"], "value")
        s["key"] = "alt_value"
        self.assertEqual(s["key"], "alt_value")

    def test_set_none(self):
        s = Settings()
        s.add("key", None, data_type=str)
        s["key"] = "alt_value"
        self.assertEqual(s["key"], "alt_value")
        s.set("key", None)
        self.assertEqual(s["key"], None)

        s.add("nullable", 1, nullable=True)
        s.set("nullable", None)

        s.add("choices", 1, choices=[1, 2, 3], nullable=True)
        s.set("choices", None)

    def test_set_range(self):
        s = Settings()
        s.add("value", 1, minmax=(0, 100))
        self.assertRaises(SettingsError, s.add, "key", 1, minmax=1)
        s.set("value", 99)
        self.assertRaises(SettingsError, s.set, "value", -1)


class TestSettingsProperties(unittest.TestCase):
    def _get_properties(self, setting, *args, **kwargs):
        s = Settings()
        s.add(setting, *args, **kwargs)
        return s.properties(setting)

    def test_bool_properties(self):
        properties = self._get_properties("bool", True)
        self.assertEqual(properties, {
            "choices": list(),
            "default": True,
            "hidden": False,
            "label": "bool",
            "minmax": None,
            "nullable": False,
            "parent": None,
            "data_type": bool,
            "value": True,
            "widget": None,
        })
        properties = self._get_properties("bool", None, data_type=bool)
        self.assertEqual(properties, {
            "choices": list(),
            "default": None,
            "hidden": False,
            "label": "bool",
            "minmax": None,
            "nullable": True,
            "parent": None,
            "data_type": bool,
            "value": None,
            "widget": None,
        })
        properties = self._get_properties("bool", True, data_type=bool, choices=[True, False])
        self.assertEqual(properties, {
            "choices": [True, False],
            "default": True,
            "hidden": False,
            "label": "bool",
            "minmax": None,
            "nullable": False,
            "parent": None,
            "data_type": bool,
            "value": True,
            "widget": None,
        })

    def test_choices_properties(self):
        properties = self._get_properties("choices", "yes", choices=["yes", "no", "maybe"])
        self.assertEqual(properties, {
            "choices": ["yes", "no", "maybe"],
            "default": "yes",
            "hidden": False,
            "label": "choices",
            "minmax": None,
            "nullable": False,
            "parent": None,
            "data_type": str,
            "value": "yes",
            "widget": None,
        })
        properties = self._get_properties("choices", "yes", choices=["yes", "no", "maybe"],
                                          nullable=True)
        self.assertEqual(properties, {
            "choices": ["yes", "no", "maybe"],
            "default": "yes",
            "hidden": False,
            "label": "choices",
            "minmax": None,
            "nullable": True,
            "parent": None,
            "data_type": str,
            "value": "yes",
            "widget": None,
        })

    def test_float_properties(self):
        properties = self._get_properties("float", 10.0)
        self.assertEqual(properties, {
            "choices": list(),
            "default": 10.0,
            "hidden": False,
            "label": "float",
            "minmax": None,
            "nullable": False,
            "parent": None,
            "data_type": float,
            "value": 10.0,
            "widget": None,
        })

    def test_int_properties(self):
        properties = self._get_properties("int", 5)
        self.assertEqual(properties, {
            "choices": list(),
            "default": 5,
            "hidden": False,
            "label": "int",
            "minmax": None,
            "nullable": False,
            "parent": None,
            "data_type": int,
            "value": 5,
            "widget": None,
        })

    def test_str_properties(self):
        properties = self._get_properties("str", "string")
        self.assertEqual(properties, {
            "choices": list(),
            "default": "string",
            "hidden": False,
            "label": "str",
            "minmax": None,
            "nullable": False,
            "parent": None,
            "data_type": str,
            "value": "string",
            "widget": None,
        })


class TestSettingsExtra(unittest.TestCase):
    def test_iter(self):
        s = Settings()
        s.add("key", "val")
        s.add("a", "b")
        self.assertSetEqual(set(s), {"key", "a"})
        self.assertEqual(len(s), 2)

    def test_bool(self):
        s = Settings()
        self.assertFalse(bool(s))
        s.add("a", "b")
        self.assertTrue(bool(s))


class TestParent(unittest.TestCase):
    def test_set_child(self):
        s = Settings()
        s.add("key", "val")
        s.add("a", "b", parent="key")
        s.set("a", "c")
        s.set("key", "")
        self.assertRaises(SettingsError, s.set, "a", "d")

    def test_set_grandchild(self):
        s = Settings()
        s.add("parent", False, nullable=True)
        s.add("child", "b", parent="parent")
        s.add("grandchild", 1, parent="child")

        self.assertRaises(SettingsError, s.set, "child", "c")
        self.assertRaises(SettingsError, s.set, "grandchild", 2)
        s.set("parent", True)
        s.set("grandchild", 2)
        s.set("child", "")
        self.assertRaises(SettingsError, s.set, "grandchild", 3)


if __name__ == '__main__':
    unittest.main()
