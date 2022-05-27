import unittest
from unittest.mock import MagicMock, patch

from libraries.widget_gui import Button, CheckBox, Combo, Font, Multiline, ProductionWidgetGui, Text, WidgetGuiEvent
from PySimpleGUI.PySimpleGUI import TIMEOUT_EVENT, WINDOW_CLOSED


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

        self.widget_gui = ProductionWidgetGui(self.TITLE, self.IS_MODAL, self.RESIZABLE, self.ELEMENT_PADDING, self.MARGINS,
                                              self.TITLEBAR_BACKGROUND_COLOR, self.TITLEBAR_TEXT_COLOR)

        self.window_mock.reset_mock()
        self.window_instance_mock.reset_mock()

    def test_constructor(self):
        ProductionWidgetGui(self.TITLE, self.IS_MODAL, self.RESIZABLE, self.ELEMENT_PADDING, self.MARGINS,
                            self.TITLEBAR_BACKGROUND_COLOR, self.TITLEBAR_TEXT_COLOR)

        self.window_mock.assert_called_once_with(self.TITLE, layout=[[]], modal=self.IS_MODAL,
                                                 resizable=self.RESIZABLE, element_padding=self.ELEMENT_PADDING,
                                                 margins=self.MARGINS,
                                                 titlebar_background_color=self.TITLEBAR_BACKGROUND_COLOR,
                                                 titlebar_text_color=self.TITLEBAR_TEXT_COLOR)

    def test_update_display(self):
        self.widget_gui.draw_layout()

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
        COMBO_VALUE = 'b'
        COMBO_FONT = Font()
        COMBO_SIZE = (10, 20)

        COMBO = Combo(COMBO_KEY, COMBO_VALUES, COMBO_FONT, COMBO_SIZE)
        COMBO.value = COMBO_VALUE

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

        self.widget_gui.draw_layout()

        BUTTON_FONT_TUPLE = (BUTTON_FONT.name, BUTTON_FONT.size, BUTTON_FONT.style)
        button_mock.assert_called_once_with(key=BUTTON_KEY, button_text=BUTTON_TEXT, font=BUTTON_FONT_TUPLE,
                                            disabled=BUTTON_DISABLED)

        TEXT_FONT_TUPLE = (TEXT_FONT.name, TEXT_FONT.size, TEXT_FONT.style)
        text_mock.assert_called_once_with(key=TEXT_KEY, text=TEXT_TEXT, font=TEXT_FONT_TUPLE)

        COMBO_FONT_TUPLE = (COMBO_FONT.name, COMBO_FONT.size, COMBO_FONT.style)
        combo_mock.assert_called_once_with(key=COMBO_KEY, values=COMBO_VALUES, default_value=COMBO_VALUE,
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

        event = self.widget_gui.read_event_and_update_gui()

        self.assertEqual(event, WidgetGuiEvent.TIMEOUT)

    def test_read_event_when_event_is_close_window(self):
        self.window_instance_mock.read.return_value = [WINDOW_CLOSED]

        event = self.widget_gui.read_event_and_update_gui()

        self.assertEqual(event, WidgetGuiEvent.CLOSE_WINDOW)

    def test_read_event(self):
        EVENT = 'hello'

        self.window_instance_mock.read.return_value = [EVENT]

        event = self.widget_gui.read_event_and_update_gui()

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

        self.assertEqual(text.value, NEW_VALUE)

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
        with ProductionWidgetGui() as widget_gui:
            pass

        self.window_instance_mock.close.assert_called_once()
