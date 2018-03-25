import unittest
from settings_manager import Signal
from settings_manager import Settings


class TestSignal(unittest.TestCase):
    def test_signal(self):
        class A(object):
            s = Signal()

        global_list = list()

        def do():
            global_list.append(1)

        def dont():
            global_list.append(2)

        a = A()
        a.s.connect(do)
        a.s.connect(dont)
        a.s.emit()
        self.assertEqual([1, 2], global_list)

        b = A()
        b.s.connect(do)
        b.s.emit()
        self.assertEqual([1, 2, 1], global_list)

    def test_deletion(self):
        class A(object):
            s = Signal()

        def fake_func():
            pass

        a = A()
        a.s.connect(fake_func)
        b = A()
        b.s.connect(fake_func)

        self.assertEqual(len(list(A.s._Signal__signals.keys())), 2)
        del a
        self.assertEqual(len(list(A.s._Signal__signals.keys())), 1)


class TestSettingsChanged(unittest.TestCase):
    def test_settings_changed(self):
        s = Settings()
        s.add("key", "value")

        def func(name, val):
            self.assertEqual(name, "key")
            self.assertEqual(val, "alt")

        s.settingChanged.connect(func)
        s.set("key", "alt")


if __name__ == '__main__':
    unittest.main()
