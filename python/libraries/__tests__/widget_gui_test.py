import unittest
from unittest.mock import MagicMock, call, patch

from libraries.widget_gui import Button, CheckBox, Combo, Font, Input, Multiline, ProductionWidgetGui, Text, WidgetGuiEvent
from PySimpleGUI.PySimpleGUI import TIMEOUT_EVENT, WINDOW_CLOSED


class WidgetGuiTestCase(unittest.TestCase):
    TITLE = 'title'
    IS_MODAL = True
    RESIZABLE = False
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


class WidgetGuiTestCaseWithLayout(WidgetGuiTestCase):
    NON_EXISTENT_KEY = 'non_existent_key'

    BUTTON = Button('button_key')
    CHECK_BOX = CheckBox('check_box_key')

    COMBO_VALUES = ['a', 'b', 'c']
    COMBO = Combo('combo_key', COMBO_VALUES)

    INPUT = Input('input_key')
    MULTILINE = Multiline('multiline_key')
    TEXT = Text('text_key')

    LAYOUT = [[BUTTON],
              [],
              [CHECK_BOX, COMBO, INPUT],
              [MULTILINE, TEXT]]

    def setUp(self):
        super().setUp()

        self.__button_patch = patch('PySimpleGUI.Button', spec=Button)
        self.__checkbox_patch = patch('PySimpleGUI.Checkbox', spec=CheckBox)
        self.__combo_patch = patch('PySimpleGUI.Combo', spec=Combo)
        self.__input_patch = patch('PySimpleGUI.Input', spec=Input)
        self.__multiline_patch = patch('PySimpleGUI.Multiline', spec=Multiline)
        self.__text_patch = patch('PySimpleGUI.Text', spec=Text)

        self.addCleanup(self.__button_patch.stop)
        self.addCleanup(self.__checkbox_patch.stop)
        self.addCleanup(self.__combo_patch.stop)
        self.addCleanup(self.__input_patch.stop)
        self.addCleanup(self.__multiline_patch.stop)
        self.addCleanup(self.__text_patch.stop)

        self.button_mock = self.__button_patch.start()
        self.checkbox_mock = self.__checkbox_patch.start()
        self.combo_mock = self.__combo_patch.start()
        self.input_mock = self.__input_patch.start()
        self.multiline_mock = self.__multiline_patch.start()
        self.text_mock = self.__text_patch.start()

        self.button_instance_mock: MagicMock = self.button_mock()
        self.checkbox_instance_mock: MagicMock = self.checkbox_mock()
        self.combo_instance_mock: MagicMock = self.combo_mock()
        self.input_instance_mock: MagicMock = self.input_mock()
        self.multiline_instance_mock: MagicMock = self.multiline_mock()
        self.text_instance_mock: MagicMock = self.text_mock()

        self.MOCK_LAYOUT = [[self.button_instance_mock],
                            [],
                            [self.checkbox_instance_mock, self.combo_instance_mock, self.input_instance_mock],
                            [self.multiline_instance_mock, self.text_instance_mock]]

        self.widget_gui.set_layout(self.LAYOUT)
        self.widget_gui.display_layout()

        self.window_mock.reset_mock()
        self.window_instance_mock.reset_mock()

        self.button_mock.reset_mock()
        self.checkbox_mock.reset_mock()
        self.combo_mock.reset_mock()
        self.input_mock.reset_mock()
        self.multiline_mock.reset_mock()
        self.text_mock.reset_mock()


class TestConstructor(WidgetGuiTestCase):
    def test_constructor(self):
        ProductionWidgetGui(self.TITLE, self.IS_MODAL, self.RESIZABLE, self.ELEMENT_PADDING, self.MARGINS,
                            self.TITLEBAR_BACKGROUND_COLOR, self.TITLEBAR_TEXT_COLOR)

        self.window_mock.assert_called_once_with(self.TITLE, layout=[[]], modal=self.IS_MODAL,
                                                 resizable=self.RESIZABLE, element_padding=self.ELEMENT_PADDING,
                                                 margins=self.MARGINS,
                                                 titlebar_background_color=self.TITLEBAR_BACKGROUND_COLOR,
                                                 titlebar_text_color=self.TITLEBAR_TEXT_COLOR)


class TestClose(WidgetGuiTestCase):
    def test_close_when_not_displayed(self):
        self.widget_gui.close()

        self.window_instance_mock.close.assert_called_once()

    def test_close_when_displayed(self):
        self.widget_gui.display_layout()

        self.window_instance_mock.reset_mock()

        self.widget_gui.close()

        self.window_instance_mock.close.assert_called_once()


class TestSetAndDisplayLayout(WidgetGuiTestCaseWithLayout):
    def test_set_layout_where_multiple_widgets_have_the_same_key(self):
        KEY = 'key'

        BUTTON = Button(KEY)
        TEXT = Text(KEY)

        LAYOUT = [[BUTTON], [TEXT]]

        with self.assertRaises(ValueError):
            self.widget_gui.set_layout(LAYOUT)

        self.widget_gui.display_layout()

        self.window_mock.assert_called_once_with(self.TITLE, layout=self.MOCK_LAYOUT, modal=self.IS_MODAL,
                                                 resizable=self.RESIZABLE, element_padding=self.ELEMENT_PADDING,
                                                 margins=self.MARGINS,
                                                 titlebar_background_color=self.TITLEBAR_BACKGROUND_COLOR,
                                                 titlebar_text_color=self.TITLEBAR_TEXT_COLOR)

        self.window_instance_mock.close.assert_called_once()
        self.window_instance_mock.read.assert_called_once_with(timeout=0)

    def test_set_and_display_valid_layout(self):
        def create_font(font: Font):
            return (font.name, font.size, font.style)

        BUTTON_KEY = 'button_key'
        CHECK_BOX_KEY = 'check_box_key'
        COMBO_KEY = 'combo_key'
        INPUT_KEY = 'input_key'
        MULTILINE_KEY = 'multiline_key'
        TEXT_KEY = 'text_key'

        BUTTON = Button(BUTTON_KEY)
        CHECK_BOX = CheckBox(CHECK_BOX_KEY)

        COMBO_VALUES = ['a', 'b', 'c']
        COMBO = Combo(COMBO_KEY, COMBO_VALUES)

        INPUT = Input(INPUT_KEY)
        MULTILINE = Multiline(MULTILINE_KEY)
        TEXT = Text(TEXT_KEY)

        LAYOUT = [[BUTTON],
                  [],
                  [CHECK_BOX, COMBO, INPUT],
                  [MULTILINE, TEXT]]

        self.widget_gui.set_layout(LAYOUT)
        self.widget_gui.display_layout()

        BUTTON_FONT = create_font(BUTTON.font)
        EXPECTED_BUTTON_MOCK_CALL = call(key=BUTTON.key, button_text=BUTTON.value,
                                         font=BUTTON_FONT, disabled=not BUTTON.enabled)
        self.assertEqual(self.button_mock.call_args, EXPECTED_BUTTON_MOCK_CALL)

        CHECK_BOX_FONT = create_font(CHECK_BOX.font)
        EXPECTED_CHECK_BOX_CALL = call(key=CHECK_BOX.key, text=CHECK_BOX.text, font=CHECK_BOX_FONT,
                                       default=CHECK_BOX.value, disabled=not CHECK_BOX.enabled)
        self.assertEqual(self.checkbox_mock.call_args, EXPECTED_CHECK_BOX_CALL)

        COMBO_FONT = create_font(COMBO.font)
        EXPECTED_COMBO_CALL = call(key=COMBO.key, values=COMBO.values, default_value=COMBO.value,
                                   font=COMBO_FONT, size=COMBO.size, disabled=not COMBO.enabled)
        self.assertEqual(self.combo_mock.call_args, EXPECTED_COMBO_CALL)

        EXPECTED_INPUT_CALL = call(key=INPUT.key, default_text=INPUT.value, disabled=not INPUT.enabled)
        self.assertEqual(self.input_mock.call_args, EXPECTED_INPUT_CALL)

        EXPECTED_MULTILINE_CALL = call(key=MULTILINE.key, default_text=MULTILINE.value,
                                       size=MULTILINE.size, autoscroll=MULTILINE.auto_scroll,
                                       disabled=not MULTILINE.enabled)
        self.assertEqual(self.multiline_mock.call_args, EXPECTED_MULTILINE_CALL)

        TEXT_FONT = create_font(TEXT.font)
        EXPECTED_TEXT_FONT = call(key=TEXT.key, text=TEXT.value, font=TEXT_FONT)
        self.assertEqual(self.text_mock.call_args, EXPECTED_TEXT_FONT)

        MOCK_LAYOUT = [[self.button_instance_mock],
                       [],
                       [self.checkbox_instance_mock, self.combo_instance_mock, self.input_instance_mock],
                       [self.multiline_instance_mock, self.text_instance_mock]]

        self.window_mock.assert_called_once_with(self.TITLE, layout=MOCK_LAYOUT, modal=self.IS_MODAL,
                                                 resizable=self.RESIZABLE, element_padding=self.ELEMENT_PADDING,
                                                 margins=self.MARGINS,
                                                 titlebar_background_color=self.TITLEBAR_BACKGROUND_COLOR,
                                                 titlebar_text_color=self.TITLEBAR_TEXT_COLOR)

        self.window_instance_mock.close.assert_called_once()
        self.window_instance_mock.read.assert_called_once_with(timeout=0)


class TestReadEventAndUpdateDisplay(WidgetGuiTestCaseWithLayout):
    def test_read_event_when_event_is_timeout(self):
        self.window_instance_mock.read.return_value = [TIMEOUT_EVENT, None]

        event = self.widget_gui.read_event_and_update_gui()

        self.assertEqual(event, WidgetGuiEvent.TIMEOUT)

    def test_read_event_when_event_is_close_window(self):
        self.window_instance_mock.read.return_value = [WINDOW_CLOSED, None]

        event = self.widget_gui.read_event_and_update_gui()

        self.assertEqual(event, WidgetGuiEvent.CLOSE_WINDOW)

    def test_read_event(self):
        EVENT = 'hello'

        self.window_instance_mock.read.return_value = [EVENT, None]

        event = self.widget_gui.read_event_and_update_gui()

        self.assertEqual(event, EVENT)

    def test_widget_values_not_updated(self):
        OLD_BUTTON_VALUE = self.BUTTON.value
        OLD_CHECK_BOX_VALUE = self.CHECK_BOX.value
        OLD_COMBO_VALUE = self.COMBO.value
        OLD_INPUT_VALUE = self.INPUT.value
        OLD_MULTILINE_VALUE = self.MULTILINE.value
        OLD_TEXT_VALUE = self.TEXT.value

        EVENT = None
        VALUES = None

        self.window_instance_mock.read.return_value = [EVENT, VALUES]

        self.widget_gui.read_event_and_update_gui()

        self.assertEqual(self.BUTTON.value, OLD_BUTTON_VALUE)
        self.assertEqual(self.CHECK_BOX.value, OLD_CHECK_BOX_VALUE)
        self.assertEqual(self.COMBO.value, OLD_COMBO_VALUE)
        self.assertEqual(self.INPUT.value, OLD_INPUT_VALUE)
        self.assertEqual(self.MULTILINE.value, OLD_MULTILINE_VALUE)
        self.assertEqual(self.TEXT.value, OLD_TEXT_VALUE)

    def test_widget_values_updated(self):
        OLD_BUTTON_VALUE = self.BUTTON.value
        OLD_CHECK_BOX_VALUE = self.CHECK_BOX.value
        OLD_COMBO_VALUE = self.COMBO.value
        OLD_INPUT_VALUE = self.INPUT.value
        OLD_MULTILINE_VALUE = self.MULTILINE.value
        OLD_TEXT_VALUE = self.TEXT.value

        NEW_BUTTON_VALUE = f'new {OLD_BUTTON_VALUE}'
        NEW_CHECK_BOX_VALUE = not OLD_CHECK_BOX_VALUE
        NEW_COMBO_VALUE = f'new {OLD_COMBO_VALUE}'
        NEW_INPUT_VALUE = f'new {OLD_INPUT_VALUE}'
        NEW_MULTILINE_VALUE = f'new {OLD_MULTILINE_VALUE}'
        NEW_TEXT_VALUE = f'new {OLD_TEXT_VALUE}'

        EVENT = None
        VALUES = {self.BUTTON.key: NEW_BUTTON_VALUE,
                  self.CHECK_BOX.key: NEW_CHECK_BOX_VALUE,
                  self.COMBO.key: NEW_COMBO_VALUE,
                  self.INPUT.key: NEW_INPUT_VALUE,
                  self.MULTILINE.key: NEW_MULTILINE_VALUE,
                  self.TEXT.key: NEW_TEXT_VALUE}

        self.window_instance_mock.read.return_value = [EVENT, VALUES]

        self.widget_gui.read_event_and_update_gui()

        self.assertEqual(self.BUTTON.value, NEW_BUTTON_VALUE)
        self.assertEqual(self.CHECK_BOX.value, NEW_CHECK_BOX_VALUE)
        self.assertEqual(self.COMBO.value, NEW_COMBO_VALUE)
        self.assertEqual(self.INPUT.value, NEW_INPUT_VALUE)
        self.assertEqual(self.MULTILINE.value, NEW_MULTILINE_VALUE)
        self.assertEqual(self.TEXT.value, NEW_TEXT_VALUE)


class TestGetWidget(WidgetGuiTestCaseWithLayout):
    def test_get_widget_that_does_not_exist(self):
        with self.assertRaises(KeyError):
            self.widget_gui.get_widget(self.NON_EXISTENT_KEY)

    def test_get_widget_that_exists(self):
        BUTTON = self.widget_gui.get_widget(self.BUTTON.key)
        CHECK_BOX = self.widget_gui.get_widget(self.CHECK_BOX.key)
        COMBO = self.widget_gui.get_widget(self.COMBO.key)
        INPUT = self.widget_gui.get_widget(self.INPUT.key)
        MULTILINE = self.widget_gui.get_widget(self.MULTILINE.key)
        TEXT = self.widget_gui.get_widget(self.TEXT.key)

        self.assertIs(BUTTON, self.BUTTON)
        self.assertIs(CHECK_BOX, self.CHECK_BOX)
        self.assertIs(COMBO, self.COMBO)
        self.assertIs(INPUT, self.INPUT)
        self.assertIs(MULTILINE, self.MULTILINE)
        self.assertIs(TEXT, self.TEXT)


class TestUpdateWidget(WidgetGuiTestCaseWithLayout):
    def test_widget_does_not_have_a_key(self):
        text = Text()

        with self.assertRaises(AttributeError):
            self.widget_gui.update_widget(text)

    def test_widget_key_is_not_in_the_gui(self):
        text = Text(self.NON_EXISTENT_KEY)

        with self.assertRaises(KeyError):
            self.widget_gui.update_widget(text)

    def test_widget_key_is_in_the_gui(self):
        NEW_BUTTON = Button(self.BUTTON.key)
        NEW_CHECK_BOX = CheckBox(self.CHECK_BOX.key)

        VALUES = ['a', 'b', 'c']
        NEW_COMBO = Combo(self.COMBO.key, VALUES)

        NEW_INPUT = Input(self.INPUT.key)
        NEW_MULTILINE = Multiline(self.MULTILINE.key)
        NEW_TEXT = Text(self.TEXT.key)

        self.widget_gui.update_widget(NEW_BUTTON)
        self.widget_gui.update_widget(NEW_CHECK_BOX)
        self.widget_gui.update_widget(NEW_COMBO)
        self.widget_gui.update_widget(NEW_INPUT)
        self.widget_gui.update_widget(NEW_MULTILINE)
        self.widget_gui.update_widget(NEW_TEXT)

        self.assertIs(NEW_BUTTON, self.widget_gui.get_widget(NEW_BUTTON.key))
        self.assertIs(NEW_CHECK_BOX, self.widget_gui.get_widget(NEW_CHECK_BOX.key))
        self.assertIs(NEW_COMBO, self.widget_gui.get_widget(NEW_COMBO.key))
        self.assertIs(NEW_INPUT, self.widget_gui.get_widget(NEW_INPUT.key))
        self.assertIs(NEW_MULTILINE, self.widget_gui.get_widget(NEW_MULTILINE.key))
        self.assertIs(NEW_TEXT, self.widget_gui.get_widget(NEW_TEXT.key))


class TestWidgetGui(WidgetGuiTestCase):

    def test_context_manager(self):
        with ProductionWidgetGui() as widget_gui:
            pass

        self.window_instance_mock.close.assert_called_once()
