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
        self._add_fail(None, data_type=bool)

    def test_add_float(self):
        self._add(3.0)
        self._add_fail(None, data_type=float)

    def test_add_int(self):
        self._add(3)
        self._add_fail(None, data_type=int)

    def test_add_str(self):
        self._add("hello")
        self._add_fail(None, data_type=str)

    def test_add_choices(self):
        self._add("yes", choices=["yes", "no", "maybe"])
        self._add(0, choices=[0, 1, 2, 3, 4])


class TestSettingsGetter(unittest.TestCase):
    def setUp(self):
        self.s = Settings()
        self.s.add("key", "value")

    def test_get_attr(self):
        self.assertEquals(self.s.key, "value", "__getattr__ failed to retrieve correct value")

    def test_get_item(self):
        self.assertEquals(self.s["key"], "value", "__getitem__ failed to retrieve correct value")


class TestSettingsSetter(unittest.TestCase):
    def setUp(self):
        self.s = Settings()
        self.s.add("key", "value")

    def test_set_attr(self):
        self.s.key = "new_value"
        self.assertEquals(self.s.key, "new_value")

    def test_set_item(self):
        self.s["key"] = "alt_value"
        self.assertEquals(self.s.key, "alt_value")


class TestSettingsProperties(unittest.TestCase):
    def setUp(self):
        self.s = Settings()
        self.s.add("str", "string")
        self.s.add("int", 5)
        self.s.add("float", 10.0)
        self.s.add("bool", True)
        self.s.add("choices", "yes", choices=["yes", "no", "maybe"])

    def test_bool_properties(self):
        properties = self.s.get_properties("bool")
        self.assertEquals(properties, {
            "choices": None,
            "default": True,
            "hidden": False,
            "label": "bool",
            "type": bool,
            "value": True,
        })

    def test_choices_properties(self):
        properties = self.s.get_properties("choices")
        self.assertEquals(properties, {
            "choices": ["yes", "no", "maybe"],
            "default": "yes",
            "hidden": False,
            "label": "choices",
            "type": str,
            "value": "yes",
        })

    def test_float_properties(self):
        properties = self.s.get_properties("float")
        self.assertEquals(properties, {
            "choices": None,
            "default": 10.0,
            "hidden": False,
            "label": "float",
            "type": float,
            "value": 10.0,
        })

    def test_int_properties(self):
        properties = self.s.get_properties("int")
        self.assertEquals(properties, {
            "choices": None,
            "default": 5,
            "hidden": False,
            "label": "int",
            "type": int,
            "value": 5,
        })

    def test_str_properties(self):
        properties = self.s.get_properties("str")
        self.assertEquals(properties, {
            "choices": None,
            "default": "string",
            "hidden": False,
            "label": "str",
            "type": str,
            "value": "string",
        })


if __name__ == '__main__':
    unittest.main()
