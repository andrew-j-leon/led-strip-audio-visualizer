import unittest
from unittest.mock import MagicMock, patch

from libraries.gui import Button, CheckBox, Combo, Font, Input, Multiline, Text, WidgetGui, WidgetGuiEvent
from PySimpleGUI.PySimpleGUI import TIMEOUT_EVENT, WINDOW_CLOSED


class TestButton(unittest.TestCase):
    KEY = 'button_key'
    TEXT = 'click me'
    FONT = Font('Times New Roman', 18, 'bold')
    DISABLED = False

    def setUp(self):
        self.button = Button(self.KEY, self.TEXT, self.FONT, self.DISABLED)

    def test_attributes(self):
        self.assertEqual(self.button.key, self.KEY)
        self.assertEqual(self.button.text, self.TEXT)
        self.assertEqual(self.button.font, self.FONT)
        self.assertEqual(self.button.disabled, self.DISABLED)

    def test_repr(self):
        expected = f'Button(key={self.KEY}, text={self.TEXT}, font={self.FONT}, disabled={self.DISABLED})'
        actual = repr(self.button)

        self.assertEqual(actual, expected)

    def test_equal(self):
        BUTTON_EQUAL = Button(self.KEY, self.TEXT, self.FONT, self.DISABLED)

        NEW_KEY = f'new {self.KEY}'
        NEW_TEXT = f'new {self.TEXT}'
        NEW_FONT = Font()
        NEW_DISABLED = not self.DISABLED

        BUTTON_NOT_EQUAL = Button(NEW_KEY, NEW_TEXT, NEW_FONT, NEW_DISABLED)

        self.assertEqual(self.button, BUTTON_EQUAL)
        self.assertNotEqual(self.button, BUTTON_NOT_EQUAL)
        self.assertNotEqual(self.button, 'not a button')


class TestText(unittest.TestCase):
    KEY = 'text_key'
    TEXT = 'hello'
    FONT = Font('Wing Dings', 20, 'italic')

    def setUp(self):
        self.text = Text(self.KEY, self.TEXT, self.FONT)

    def test_attributes(self):
        self.assertEqual(self.text.key, self.KEY)
        self.assertEqual(self.text.text, self.TEXT)
        self.assertEqual(self.text.font, self.FONT)

    def test_repr(self):
        expected = f'Text(key={self.KEY}, text={self.TEXT}, font={self.FONT})'
        actual = repr(self.text)

        self.assertEqual(actual, expected)

    def test_equal(self):
        TEXT_EQUAL = Text(self.KEY, self.TEXT, self.FONT)

        NEW_KEY = f'new {self.KEY}'
        NEW_TEXT = f'new {self.TEXT}'
        NEW_FONT = Font()

        TEXT_NOT_EQUAL = Button(NEW_KEY, NEW_TEXT, NEW_FONT)

        self.assertEqual(self.text, TEXT_EQUAL)
        self.assertNotEqual(self.text, TEXT_NOT_EQUAL)
        self.assertNotEqual(self.text, 'text')


class TestCombo(unittest.TestCase):
    KEY = 'combo_key'
    VALUES = ['a', 'b', 'c']
    DEFAULT_VALUE = 'b'
    FONT = Font()
    SIZE = (10, 20)

    def setUp(self):
        self.combo = Combo(self.KEY, self.VALUES, self.DEFAULT_VALUE, self.FONT, self.SIZE)

    def test_attributes(self):
        self.assertEqual(self.combo.key, self.KEY)
        self.assertEqual(self.combo.values, self.VALUES)
        self.assertEqual(self.combo.default_value, self.DEFAULT_VALUE)
        self.assertEqual(self.combo.font, self.FONT)
        self.assertEqual(self.combo.size, self.SIZE)

    def test_repr(self):
        expected = f'Combo(key={self.KEY}, values={self.VALUES}, default_value={self.DEFAULT_VALUE}, font={self.FONT}, size={self.SIZE})'
        actual = repr(self.combo)

        self.assertEqual(actual, expected)

    def test_equal(self):
        COMBO_EQUAL = Combo(self.KEY, self.VALUES, self.DEFAULT_VALUE, self.FONT, self.SIZE)

        NEW_KEY = f'new {self.KEY}'
        NEW_VALUES = self.VALUES + ['d']
        NEW_DEFAULT_VALUE = 'd'
        NEW_FONT = Font()
        NEW_SIZE = (self.SIZE[0] + 10,
                    self.SIZE[1] + 20)

        COMBO_NOT_EQUAL = Combo(NEW_KEY, NEW_VALUES, NEW_DEFAULT_VALUE, NEW_FONT, NEW_SIZE)

        self.assertEqual(self.combo, COMBO_EQUAL)
        self.assertNotEqual(self.combo, COMBO_NOT_EQUAL)
        self.assertNotEqual(self.combo, 'not a combo')


class TestCheckBox(unittest.TestCase):
    KEY = 'check_box_key'
    TEXT = 'hello i am a checkbox'
    FONT = Font('some font', 20)
    DEFAULT = True

    def setUp(self):
        self.check_box = CheckBox(self.KEY, self.TEXT, self.FONT, self.DEFAULT)

    def test_attributes(self):
        self.assertEqual(self.check_box.key, self.KEY)
        self.assertEqual(self.check_box.text, self.TEXT)
        self.assertEqual(self.check_box.font, self.FONT)
        self.assertEqual(self.check_box.default, self.DEFAULT)

    def test_repr(self):
        expected = f'CheckBox(key={self.KEY}, text={self.TEXT}, font={self.FONT}, default={self.DEFAULT})'
        actual = repr(self.check_box)

        self.assertEqual(expected, actual)

    def test_equal(self):
        CHECK_BOX_EQUAL = CheckBox(self.KEY, self.TEXT, self.FONT, self.DEFAULT)

        NEW_KEY = f'new {self.KEY}'
        NEW_TEXT = f'new {self.TEXT}'
        NEW_FONT = Font()
        NEW_DEFAULT = not self.DEFAULT

        CHECK_BOX_NOT_EQUAL = CheckBox(NEW_KEY, NEW_TEXT, NEW_FONT, NEW_DEFAULT)

        self.assertEqual(self.check_box, CHECK_BOX_EQUAL)
        self.assertNotEqual(self.check_box, CHECK_BOX_NOT_EQUAL)
        self.assertNotEqual(self.check_box, 'not a checkbox')


class TestMultiline(unittest.TestCase):
    KEY = 'multiline_key'
    TEXT = 'some multiline text'
    SIZE = (20, 30)
    AUTO_SCROLL = False

    def setUp(self):
        self.multiline = Multiline(self.KEY, self.TEXT, self.SIZE, self.AUTO_SCROLL)

    def test_attributes(self):
        self.assertEqual(self.multiline.key, self.KEY)
        self.assertEqual(self.multiline.text, self.TEXT)
        self.assertEqual(self.multiline.size, self.SIZE)
        self.assertEqual(self.multiline.auto_scroll, self.AUTO_SCROLL)

    def test_repr(self):
        expected = f'Multiline(key={self.KEY}, text={self.TEXT}, size={self.SIZE}, auto_scroll={self.AUTO_SCROLL})'
        actual = repr(self.multiline)

        self.assertEqual(expected, actual)

    def test_equal(self):
        MULTILINE_EQUAL = Multiline(self.KEY, self.TEXT, self.SIZE, self.AUTO_SCROLL)

        NEW_KEY = f'new {self.KEY}'
        NEW_TEXT = f'new {self.TEXT}'
        NEW_SIZE = (self.SIZE[0] + 10,
                    self.SIZE[1] + 20)
        NEW_AUTO_SCROLL = not self.AUTO_SCROLL

        MULTILINE_NOT_EQUAL = Multiline(NEW_KEY, NEW_TEXT, NEW_SIZE, NEW_AUTO_SCROLL)

        self.assertEqual(self.multiline, MULTILINE_EQUAL)
        self.assertNotEqual(self.multiline, MULTILINE_NOT_EQUAL)
        self.assertNotEqual(self.multiline, 'not a multiline')


class TestInput(unittest.TestCase):
    KEY = 'multiline_key'
    TEXT = 'some multiline text'

    def setUp(self):
        self.input = Input(self.KEY, self.TEXT)

    def test_attributes(self):
        self.assertEqual(self.input.key, self.KEY)
        self.assertEqual(self.input.text, self.TEXT)

    def test_repr(self):
        expected = f'Input(key={self.KEY}, text={self.TEXT})'
        actual = repr(self.input)

        self.assertEqual(expected, actual)

    def test_equal(self):
        INPUT_EQUAL = Input(self.KEY, self.TEXT)

        NEW_KEY = f'new {self.KEY}'
        NEW_TEXT = f'new {self.TEXT}'

        INPUT_NOT_EQUAL = Input(NEW_KEY, NEW_TEXT)

        self.assertEqual(self.input, INPUT_EQUAL)
        self.assertNotEqual(self.input, INPUT_NOT_EQUAL)
        self.assertNotEqual(self.input, 'not an Input')


class TestWidgetGui(unittest.TestCase):
    TITLE = 'title'
    IS_MODAL = True
    RESIZABLE = True
    ELEMENT_PADDING = (10, 20)
    MARGINS = (2, 5)
    TITLEBAR_BACKGROUND_COLOR = '#010101'
    TITLEBAR_TEXT_COLOR = '#100100'

    def setUp(self):
        self.__window_patch = patch('PySimpleGUI.Window')

        self.addCleanup(self.__window_patch.stop)

        self.window_mock = self.__window_patch.start()
        self.window_instance_mock: MagicMock = self.window_mock()

        self.widget_gui = WidgetGui(self.TITLE, self.IS_MODAL, self.RESIZABLE, self.ELEMENT_PADDING, self.MARGINS,
                                    self.TITLEBAR_BACKGROUND_COLOR, self.TITLEBAR_TEXT_COLOR)

        self.window_mock.reset_mock()
        self.window_instance_mock.reset_mock()

    def test_constructor(self):
        WidgetGui(self.TITLE, self.IS_MODAL, self.RESIZABLE, self.ELEMENT_PADDING, self.MARGINS,
                  self.TITLEBAR_BACKGROUND_COLOR, self.TITLEBAR_TEXT_COLOR)

        self.window_mock.assert_called_once_with(self.TITLE, layout=[[]], modal=self.IS_MODAL,
                                                 resizable=self.RESIZABLE, element_padding=self.ELEMENT_PADDING,
                                                 margins=self.MARGINS,
                                                 titlebar_background_color=self.TITLEBAR_BACKGROUND_COLOR,
                                                 titlebar_text_color=self.TITLEBAR_TEXT_COLOR)

    def test_update_display(self):
        self.widget_gui.update_display()

        self.window_mock.assert_called_once_with(self.TITLE, layout=[[]], modal=self.IS_MODAL,
                                                 resizable=self.RESIZABLE, element_padding=self.ELEMENT_PADDING,
                                                 margins=self.MARGINS,
                                                 titlebar_background_color=self.TITLEBAR_BACKGROUND_COLOR,
                                                 titlebar_text_color=self.TITLEBAR_TEXT_COLOR)

        self.window_instance_mock.close.assert_called_once()
        self.window_instance_mock.read.assert_called_once_with(timeout=0)

    @patch('PySimpleGUI.Multiline')
    @patch('PySimpleGUI.Checkbox')
    @patch('PySimpleGUI.Combo')
    @patch('PySimpleGUI.Text')
    @patch('PySimpleGUI.Button')
    def test_set_layout(self, button_mock: MagicMock, text_mock: MagicMock, combo_mock: MagicMock,
                        checkbox_mock: MagicMock, multiline_mock: MagicMock):
        BUTTON_KEY = 'button_key'
        BUTTON_TEXT = 'click me'
        BUTTON_FONT = Font('Times New Roman', 18, 'bold')
        BUTTON_DISABLED = False

        BUTTON = Button(BUTTON_KEY, BUTTON_TEXT, BUTTON_FONT, BUTTON_DISABLED)

        TEXT_KEY = 'text_key'
        TEXT_TEXT = 'hello'
        TEXT_FONT = Font('Wing Dings', 20, 'italic')

        TEXT = Text(TEXT_KEY, TEXT_TEXT, TEXT_FONT)

        COMBO_KEY = 'combo_key'
        COMBO_VALUES = ['a', 'b', 'c']
        COMBO_DEFAULT_VALUE = 'b'
        COMBO_FONT = Font()
        COMBO_SIZE = (10, 20)

        COMBO = Combo(COMBO_KEY, COMBO_VALUES, COMBO_DEFAULT_VALUE, COMBO_FONT, COMBO_SIZE)

        CHECK_BOX_KEY = 'check_box_key'
        CHECK_BOX_TEXT = 'hello i am a checkbox'
        CHECK_BOX_FONT = Font('some font', 20)
        CHECK_BOX_DEFAULT = True

        CHECK_BOX = CheckBox(CHECK_BOX_KEY, CHECK_BOX_TEXT, CHECK_BOX_FONT, CHECK_BOX_DEFAULT)

        MULTILINE_KEY = 'multiline_key'
        MULTILINE_TEXT = 'some multiline text'
        MULTILINE_SIZE = (20, 30)
        MULTILINE_AUTO_SCROLL = False

        MULTILINE = Multiline(MULTILINE_KEY, MULTILINE_TEXT, MULTILINE_SIZE, MULTILINE_AUTO_SCROLL)

        LAYOUT = [[BUTTON],
                  [],
                  [TEXT, COMBO, CHECK_BOX],
                  [MULTILINE]]

        self.widget_gui.set_layout(LAYOUT)

        self.widget_gui.update_display()

        BUTTON_FONT_TUPLE = (BUTTON_FONT.name, BUTTON_FONT.size, BUTTON_FONT.style)
        button_mock.assert_called_once_with(key=BUTTON_KEY, button_text=BUTTON_TEXT, font=BUTTON_FONT_TUPLE,
                                            disabled=BUTTON_DISABLED)

        TEXT_FONT_TUPLE = (TEXT_FONT.name, TEXT_FONT.size, TEXT_FONT.style)
        text_mock.assert_called_once_with(key=TEXT_KEY, text=TEXT_TEXT, font=TEXT_FONT_TUPLE)

        COMBO_FONT_TUPLE = (COMBO_FONT.name, COMBO_FONT.size, COMBO_FONT.style)
        combo_mock.assert_called_once_with(key=COMBO_KEY, values=COMBO_VALUES, default_value=COMBO_DEFAULT_VALUE,
                                           font=COMBO_FONT_TUPLE, size=COMBO_SIZE)

        CHECK_BOX_FONT_TUPLE = (CHECK_BOX_FONT.name, CHECK_BOX_FONT.size, CHECK_BOX_FONT.style)
        checkbox_mock.assert_called_once_with(key=CHECK_BOX_KEY, text=CHECK_BOX_TEXT, font=CHECK_BOX_FONT_TUPLE, default=CHECK_BOX_DEFAULT)

        multiline_mock.assert_called_once_with(key=MULTILINE_KEY, default_text=MULTILINE_TEXT,
                                               size=MULTILINE_SIZE, autoscroll=MULTILINE_AUTO_SCROLL)

        BUTTON_INSTANCE_MOCK = button_mock()
        TEXT_INSTANCE_MOCK = text_mock()
        COMBO_INSTANCE_MOCK = combo_mock()
        CHECKBOX_INSTANCE_MOCK = checkbox_mock()
        MULTILINE_INSTANCE_MOCK = multiline_mock()

        EXPECTED_LAYOUT = [[BUTTON_INSTANCE_MOCK],
                           [],
                           [TEXT_INSTANCE_MOCK, COMBO_INSTANCE_MOCK, CHECKBOX_INSTANCE_MOCK],
                           [MULTILINE_INSTANCE_MOCK]]

        self.window_mock.assert_called_once_with(self.TITLE, layout=EXPECTED_LAYOUT, modal=self.IS_MODAL,
                                                 resizable=self.RESIZABLE, element_padding=self.ELEMENT_PADDING,
                                                 margins=self.MARGINS,
                                                 titlebar_background_color=self.TITLEBAR_BACKGROUND_COLOR,
                                                 titlebar_text_color=self.TITLEBAR_TEXT_COLOR)

        self.window_instance_mock.close.assert_called_once()
        self.window_instance_mock.read.assert_called_once_with(timeout=0)

    def test_set_layout_multiple_widgets_with_same_key(self):
        KEY = 'key'

        BUTTON_TEXT = 'click me'
        BUTTON_FONT = Font('Times New Roman', 18, 'bold')
        BUTTON_DISABLED = False

        BUTTON = Button(KEY, BUTTON_TEXT, BUTTON_FONT, BUTTON_DISABLED)

        TEXT_TEXT = 'hello'
        TEXT_FONT = Font('Wing Dings', 20, 'italic')

        TEXT = Text(KEY, TEXT_TEXT, TEXT_FONT)

        LAYOUT = [[BUTTON], [TEXT]]

        with self.assertRaises(ValueError):
            self.widget_gui.set_layout(LAYOUT)

    def test_read_event_when_event_is_timeout(self):
        self.window_instance_mock.read.return_value = [TIMEOUT_EVENT]

        event = self.widget_gui.read_event()

        self.assertEqual(event, WidgetGuiEvent.TIMEOUT)

    def test_read_event_when_event_is_close_window(self):
        self.window_instance_mock.read.return_value = [WINDOW_CLOSED]

        event = self.widget_gui.read_event()

        self.assertEqual(event, WidgetGuiEvent.CLOSE_WINDOW)

    def test_read_event(self):
        EVENT = 'hello'

        self.window_instance_mock.read.return_value = [EVENT]

        event = self.widget_gui.read_event()

        self.assertEqual(event, EVENT)

    def test_disable_widget_when_widget_does_not_exist(self):
        WIDGET_KEY = 'key'

        with self.assertRaises(KeyError):
            self.widget_gui.disable_widget(WIDGET_KEY)

    def test_disable_widget(self):
        WIDGET_KEY = 'key'

        button = Button(WIDGET_KEY, disabled=False)

        LAYOUT = [[button]]

        self.widget_gui.set_layout(LAYOUT)

        self.assertFalse(button.disabled)

        self.widget_gui.disable_widget(WIDGET_KEY)

        self.assertTrue(button.disabled)
        self.window_instance_mock.find_element(WIDGET_KEY).update.assert_called_once_with(disabled=True)

    def test_enable_widget_when_widget_does_not_exist(self):
        WIDGET_KEY = 'key'

        with self.assertRaises(KeyError):
            self.widget_gui.enable_widget(WIDGET_KEY)

    def test_enable_widget(self):
        WIDGET_KEY = 'key'

        button = Button(WIDGET_KEY, disabled=True)

        LAYOUT = [[button]]

        self.widget_gui.set_layout(LAYOUT)

        self.assertTrue(button.disabled)

        self.widget_gui.enable_widget(WIDGET_KEY)

        self.assertFalse(button.disabled)
        self.window_instance_mock.find_element(WIDGET_KEY).update.assert_called_once_with(disabled=False)

    def test_set_widget_value(self):
        WIDGET_KEY = 'key'

        text = Text(WIDGET_KEY)

        LAYOUT = [[text]]

        self.widget_gui.set_layout(LAYOUT)

        NEW_VALUE = 'hello'

        self.widget_gui.set_widget_value(WIDGET_KEY, NEW_VALUE)

        self.assertEqual(text.text, NEW_VALUE)

        self.window_instance_mock.find_element(WIDGET_KEY).update.assert_called_once_with(value=NEW_VALUE)

    def test_set_widget_value_when_widget_does_not_exist(self):
        WIDGET_KEY = 'key'

        with self.assertRaises(KeyError):
            self.widget_gui.set_widget_value(WIDGET_KEY, 'value')

    def test_get_widget_value(self):
        WIDGET_KEY = 'key'
        WIDGET_VALUE = 'hello'

        self.window_instance_mock.find_element(WIDGET_KEY).get.return_value = WIDGET_VALUE

        value = self.widget_gui.get_widget_value(WIDGET_KEY)

        self.assertEqual(value, WIDGET_VALUE)

    def test_context_manager(self):
        with WidgetGui() as widget_gui:
            pass

        self.window_instance_mock.close.assert_called_once()
