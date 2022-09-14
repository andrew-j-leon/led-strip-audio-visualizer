import unittest
from unittest.mock import MagicMock, patch

from libraries.PySimpleGUI import TIMEOUT_EVENT, WINDOW_CLOSED
from libraries.widget import Button, CheckBox, ColorPicker, Combo, Input, Multiline, Text
from libraries.widget_gui import ProductionWidgetGui, WidgetGuiEvent


class UnrecognizedWidget:
    def __init__(self, key):
        self.key = key


class WidgetGuiTestCase(unittest.TestCase):
    TITLE = 'title'
    IS_MODAL = True
    RESIZABLE = False
    ELEMENT_PADDING = (10, 20)
    MARGINS = (2, 5)
    TITLEBAR_BACKGROUND_COLOR = '#010101'
    TITLEBAR_TEXT_COLOR = '#100100'

    def setUp(self):
        self.__window_patch = patch('libraries.PySimpleGUI.Window')

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

    COMBO_WITH_NO_VALUES = Combo('combo_with_no_values_key')

    INPUT = Input('input_key')
    MULTILINE = Multiline('multiline_key')
    TEXT_WITH_KEY = Text('text_key')
    COLOR_PICKER = ColorPicker('color_picker_key')

    TEXT_WITH_NO_KEY = Text(text='I have no key!')

    LAYOUT = [[BUTTON],
              [],
              [CHECK_BOX, COMBO, INPUT],
              [MULTILINE, TEXT_WITH_KEY],
              [COLOR_PICKER],
              [TEXT_WITH_NO_KEY],
              [COMBO_WITH_NO_VALUES]]

    def setUp(self):
        super().setUp()

        self.__button_patch = patch('libraries.PySimpleGUI.Button', spec=Button)
        self.__checkbox_patch = patch('libraries.PySimpleGUI.Checkbox', spec=CheckBox)
        self.__combo_patch = patch('libraries.PySimpleGUI.Combo', spec=Combo)
        self.__input_patch = patch('libraries.PySimpleGUI.Input', spec=Input)
        self.__multiline_patch = patch('libraries.PySimpleGUI.Multiline', spec=Multiline)
        self.__text_patch = patch('libraries.PySimpleGUI.Text', spec=Text)

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
                            [self.multiline_instance_mock, self.text_instance_mock],
                            [self.button_instance_mock, self.input_instance_mock],
                            [self.text_instance_mock],
                            [self.combo_instance_mock]]

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


class TestContextManager(WidgetGuiTestCase):
    def test_context_manager(self):
        with ProductionWidgetGui() as widget_gui:
            pass

        self.window_instance_mock.close.assert_called_once()


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


class TestTitle(WidgetGuiTestCase):
    def test_set_title(self):
        TITLE = 'new_title'

        self.widget_gui.title = TITLE

        self.assertEqual(self.widget_gui.title, TITLE)


class TestSetLayout(WidgetGuiTestCaseWithLayout):
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
        self.widget_gui.set_layout(self.LAYOUT)
        self.widget_gui.display_layout()

        self.window_mock.assert_called_once_with(self.TITLE, layout=self.MOCK_LAYOUT, modal=self.IS_MODAL,
                                                 resizable=self.RESIZABLE, element_padding=self.ELEMENT_PADDING,
                                                 margins=self.MARGINS,
                                                 titlebar_background_color=self.TITLEBAR_BACKGROUND_COLOR,
                                                 titlebar_text_color=self.TITLEBAR_TEXT_COLOR)
        self.window_instance_mock.close.assert_called_once()
        self.window_instance_mock.read.assert_called_once_with(timeout=0)

    def test_set_and_display_layout_with_unrecognized_widget(self):
        LAYOUT = [[UnrecognizedWidget('some_key')]]

        self.widget_gui.set_layout(LAYOUT)

        with self.assertRaises(TypeError):
            self.widget_gui.display_layout()


class TestAppendLayout(WidgetGuiTestCaseWithLayout):

    def test_key_clash_with_preexisting_layout(self):
        BUTTON = Button(self.BUTTON.key)
        LAYOUT = [[BUTTON]]

        with self.assertRaises(ValueError):
            self.widget_gui.append_layout(LAYOUT)

        self.widget_gui.display_layout()

        self.window_mock.assert_called_once_with(self.TITLE, layout=self.MOCK_LAYOUT, modal=self.IS_MODAL,
                                                 resizable=self.RESIZABLE, element_padding=self.ELEMENT_PADDING,
                                                 margins=self.MARGINS,
                                                 titlebar_background_color=self.TITLEBAR_BACKGROUND_COLOR,
                                                 titlebar_text_color=self.TITLEBAR_TEXT_COLOR)

        self.window_instance_mock.close.assert_called_once()
        self.window_instance_mock.read.assert_called_once_with(timeout=0)

    def test_multiple_widgets_have_the_same_key(self):
        KEY = 'key'

        BUTTON = Button(KEY)
        TEXT = Text(KEY)

        LAYOUT = [[BUTTON], [TEXT]]

        with self.assertRaises(ValueError):
            self.widget_gui.append_layout(LAYOUT)

        self.widget_gui.display_layout()

        self.window_mock.assert_called_once_with(self.TITLE, layout=self.MOCK_LAYOUT, modal=self.IS_MODAL,
                                                 resizable=self.RESIZABLE, element_padding=self.ELEMENT_PADDING,
                                                 margins=self.MARGINS,
                                                 titlebar_background_color=self.TITLEBAR_BACKGROUND_COLOR,
                                                 titlebar_text_color=self.TITLEBAR_TEXT_COLOR)

        self.window_instance_mock.close.assert_called_once()
        self.window_instance_mock.read.assert_called_once_with(timeout=0)

    def test_append_valid_layout(self):
        LAYOUT = [[Button(self.NON_EXISTENT_KEY)]]

        self.widget_gui.append_layout(LAYOUT)
        self.widget_gui.display_layout()

        MOCK_LAYOUT = self.MOCK_LAYOUT + [[self.button_instance_mock]]

        self.window_mock.assert_called_once_with(self.TITLE, layout=MOCK_LAYOUT, modal=self.IS_MODAL,
                                                 resizable=self.RESIZABLE, element_padding=self.ELEMENT_PADDING,
                                                 margins=self.MARGINS,
                                                 titlebar_background_color=self.TITLEBAR_BACKGROUND_COLOR,
                                                 titlebar_text_color=self.TITLEBAR_TEXT_COLOR)
        self.window_instance_mock.close.assert_called_once()
        self.window_instance_mock.read.assert_called_once_with(timeout=0)

    def test_set_and_display_layout_with_unrecognized_widget(self):
        LAYOUT = [[UnrecognizedWidget('some_key')]]

        self.widget_gui.append_layout(LAYOUT)

        with self.assertRaises(TypeError):
            self.widget_gui.display_layout()


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
        OLD_TEXT_WITH_KEY_VALUE = self.TEXT_WITH_KEY.value
        OLD_COLOR_PICKER_VALUE = self.COLOR_PICKER.value
        OLD_TEXT_WITH_NO_KEY_VALUE = self.TEXT_WITH_NO_KEY.value

        EVENT = None
        VALUES = None

        self.window_instance_mock.read.return_value = [EVENT, VALUES]

        self.widget_gui.read_event_and_update_gui()

        self.assertEqual(self.BUTTON.value, OLD_BUTTON_VALUE)
        self.assertEqual(self.CHECK_BOX.value, OLD_CHECK_BOX_VALUE)
        self.assertEqual(self.COMBO.value, OLD_COMBO_VALUE)
        self.assertEqual(self.INPUT.value, OLD_INPUT_VALUE)
        self.assertEqual(self.MULTILINE.value, OLD_MULTILINE_VALUE)
        self.assertEqual(self.TEXT_WITH_KEY.value, OLD_TEXT_WITH_KEY_VALUE)
        self.assertEqual(self.COLOR_PICKER.value, OLD_COLOR_PICKER_VALUE)
        self.assertEqual(self.TEXT_WITH_NO_KEY.value, OLD_TEXT_WITH_NO_KEY_VALUE)

    def test_color_picker_widget_set_to_none(self):
        EVENT = None
        VALUES = {self.COLOR_PICKER.key: 'None'}

        self.window_instance_mock.read.return_value = [EVENT, VALUES]

        OLD_COLOR_PICKER_VALUE = self.COLOR_PICKER.value

        self.widget_gui.read_event_and_update_gui()

        self.assertEqual(self.COLOR_PICKER.value, OLD_COLOR_PICKER_VALUE)

    def test_widget_value_was_invalid(self):
        EVENT = None
        VALUES = {self.COLOR_PICKER.key: 'not_a_valid_hex'}

        self.window_instance_mock.read.return_value = [EVENT, VALUES]

        OLD_COLOR_PICKER_VALUE = self.COLOR_PICKER.value

        with self.assertRaises(ValueError):
            self.widget_gui.read_event_and_update_gui()

        self.assertEqual(self.COLOR_PICKER.value, OLD_COLOR_PICKER_VALUE)

    def test_widget_values_updated(self):
        OLD_BUTTON_VALUE = self.BUTTON.value
        OLD_CHECK_BOX_VALUE = self.CHECK_BOX.value
        OLD_COMBO_VALUE = self.COMBO.value
        OLD_INPUT_VALUE = self.INPUT.value
        OLD_MULTILINE_VALUE = self.MULTILINE.value
        OLD_TEXT_WITH_KEY_VALUE = self.TEXT_WITH_KEY.value
        OLD_COLOR_PICKER_VALUE = self.COLOR_PICKER.value
        OLD_TEXT_WITH_NO_KEY_VALUE = self.TEXT_WITH_NO_KEY.value

        NEW_BUTTON_VALUE = f'new {OLD_BUTTON_VALUE}'
        NEW_CHECK_BOX_VALUE = not OLD_CHECK_BOX_VALUE
        NEW_COMBO_VALUE = f'new {OLD_COMBO_VALUE}'
        NEW_INPUT_VALUE = f'new {OLD_INPUT_VALUE}'
        NEW_MULTILINE_VALUE = f'new {OLD_MULTILINE_VALUE}'
        NEW_TEXT_VALUE = f'new {OLD_TEXT_WITH_KEY_VALUE}'
        NEW_COLOR_PICKER_VALUE = '#ABCDEF' if ('#ABCDEF' != OLD_COLOR_PICKER_VALUE) else '#123456'

        EVENT = None
        VALUES = {self.BUTTON.key: NEW_BUTTON_VALUE,
                  self.CHECK_BOX.key: NEW_CHECK_BOX_VALUE,
                  self.COMBO.key: NEW_COMBO_VALUE,
                  self.INPUT.key: NEW_INPUT_VALUE,
                  self.MULTILINE.key: NEW_MULTILINE_VALUE,
                  self.TEXT_WITH_KEY.key: NEW_TEXT_VALUE,
                  self.COLOR_PICKER.key: NEW_COLOR_PICKER_VALUE}

        self.window_instance_mock.read.return_value = [EVENT, VALUES]

        self.widget_gui.read_event_and_update_gui()

        self.assertEqual(self.BUTTON.value, NEW_BUTTON_VALUE)
        self.assertEqual(self.CHECK_BOX.value, NEW_CHECK_BOX_VALUE)
        self.assertEqual(self.COMBO.value, NEW_COMBO_VALUE)
        self.assertEqual(self.INPUT.value, NEW_INPUT_VALUE)
        self.assertEqual(self.MULTILINE.value, NEW_MULTILINE_VALUE)
        self.assertEqual(self.TEXT_WITH_KEY.value, NEW_TEXT_VALUE)
        self.assertEqual(self.COLOR_PICKER.value, NEW_COLOR_PICKER_VALUE)
        self.assertEqual(self.TEXT_WITH_NO_KEY.value, OLD_TEXT_WITH_NO_KEY_VALUE)


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
        TEXT_WITH_KEY = self.widget_gui.get_widget(self.TEXT_WITH_KEY.key)
        COLOR_PICKER = self.widget_gui.get_widget(self.COLOR_PICKER.key)

        self.assertIs(BUTTON, self.BUTTON)
        self.assertIs(CHECK_BOX, self.CHECK_BOX)
        self.assertIs(COMBO, self.COMBO)
        self.assertIs(INPUT, self.INPUT)
        self.assertIs(MULTILINE, self.MULTILINE)
        self.assertIs(TEXT_WITH_KEY, self.TEXT_WITH_KEY)
        self.assertIs(COLOR_PICKER, self.COLOR_PICKER)


class TestUpdateWidget(WidgetGuiTestCaseWithLayout):
    def test_unrecognized_widget(self):
        with self.assertRaises(TypeError):
            widget = UnrecognizedWidget(self.BUTTON.key)
            self.widget_gui.update_widget(widget)

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
        NEW_TEXT = Text(self.TEXT_WITH_KEY.key)
        NEW_COLOR_PICKER = ColorPicker(self.COLOR_PICKER.key)
        NEW_COMBO_WITH_NO_VALUES = Combo(self.COMBO_WITH_NO_VALUES.key)

        self.widget_gui.update_widget(NEW_BUTTON)
        self.widget_gui.update_widget(NEW_CHECK_BOX)
        self.widget_gui.update_widget(NEW_COMBO)
        self.widget_gui.update_widget(NEW_INPUT)
        self.widget_gui.update_widget(NEW_MULTILINE)
        self.widget_gui.update_widget(NEW_TEXT)
        self.widget_gui.update_widget(NEW_COLOR_PICKER)
        self.widget_gui.update_widget(NEW_COMBO_WITH_NO_VALUES)

        self.assertIs(NEW_BUTTON, self.widget_gui.get_widget(NEW_BUTTON.key))
        self.assertIs(NEW_CHECK_BOX, self.widget_gui.get_widget(NEW_CHECK_BOX.key))
        self.assertIs(NEW_COMBO, self.widget_gui.get_widget(NEW_COMBO.key))
        self.assertIs(NEW_INPUT, self.widget_gui.get_widget(NEW_INPUT.key))
        self.assertIs(NEW_MULTILINE, self.widget_gui.get_widget(NEW_MULTILINE.key))
        self.assertIs(NEW_TEXT, self.widget_gui.get_widget(NEW_TEXT.key))
        self.assertIs(NEW_COLOR_PICKER, self.widget_gui.get_widget(NEW_COLOR_PICKER.key))
        self.assertIs(NEW_COMBO_WITH_NO_VALUES, self.widget_gui.get_widget(NEW_COMBO_WITH_NO_VALUES.key))


class TestUpdateWidgets(WidgetGuiTestCaseWithLayout):
    def test_unrecognized_widget(self):
        with self.assertRaises(TypeError):
            widget = UnrecognizedWidget(self.BUTTON.key)
            self.widget_gui.update_widgets(widget)

    def test_widget_does_not_have_a_key(self):
        text = Text()

        with self.assertRaises(AttributeError):
            self.widget_gui.update_widgets(text)

    def test_widget_key_is_not_in_the_gui(self):
        text = Text(self.NON_EXISTENT_KEY)

        with self.assertRaises(KeyError):
            self.widget_gui.update_widgets(text)

    def test_widget_key_is_in_the_gui(self):
        NEW_BUTTON = Button(self.BUTTON.key)
        NEW_CHECK_BOX = CheckBox(self.CHECK_BOX.key)

        VALUES = ['a', 'b', 'c']
        NEW_COMBO = Combo(self.COMBO.key, VALUES)

        NEW_INPUT = Input(self.INPUT.key)
        NEW_MULTILINE = Multiline(self.MULTILINE.key)
        NEW_TEXT = Text(self.TEXT_WITH_KEY.key)
        NEW_COLOR_PICKER = ColorPicker(self.COLOR_PICKER.key)
        NEW_COMBO_WITH_NO_VALUES = Combo(self.COMBO_WITH_NO_VALUES.key)

        self.widget_gui.update_widgets(NEW_BUTTON, NEW_CHECK_BOX, NEW_COMBO, NEW_INPUT,
                                       NEW_MULTILINE, NEW_TEXT, NEW_COLOR_PICKER, NEW_COMBO_WITH_NO_VALUES)

        self.assertIs(NEW_BUTTON, self.widget_gui.get_widget(NEW_BUTTON.key))
        self.assertIs(NEW_CHECK_BOX, self.widget_gui.get_widget(NEW_CHECK_BOX.key))
        self.assertIs(NEW_COMBO, self.widget_gui.get_widget(NEW_COMBO.key))
        self.assertIs(NEW_INPUT, self.widget_gui.get_widget(NEW_INPUT.key))
        self.assertIs(NEW_MULTILINE, self.widget_gui.get_widget(NEW_MULTILINE.key))
        self.assertIs(NEW_TEXT, self.widget_gui.get_widget(NEW_TEXT.key))
        self.assertIs(NEW_COLOR_PICKER, self.widget_gui.get_widget(NEW_COLOR_PICKER.key))
        self.assertIs(NEW_COMBO_WITH_NO_VALUES, self.widget_gui.get_widget(NEW_COMBO_WITH_NO_VALUES.key))
