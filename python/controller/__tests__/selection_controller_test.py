
from unittest import TestCase

from controller.__tests__.fake_widget_gui import FakeWidgetGui
from controller.selection_controller import SelectionController
from libraries.widget_gui import WidgetGuiEvent
from selection.selection import Selection
from selection.selection_gui import Element, Event, SelectionGui


class FakeSelectionGui(SelectionGui):
    def __init__(self, create_gui):
        super().__init__(create_gui)

        self.selection = None
        self.displayed_selection = None
        self.updated_selection = None
        self.read_selection = None

        self.event = None
        self.open = False

        self.current_save_name = ''

    def close(self):
        self.open = False

    def get_current_save_name(self):
        return self.current_save_name

    def get_selection(self):
        return self.selection

    def update_widgets(self, selection):
        self.updated_selection = selection

    def display(self, selection):
        self.open = True
        self.selection = selection

    def read_event_and_update_gui(self, selection):
        self.read_selection = selection
        return self.event

    def _get_title(self):
        return 'Fake Title'

    def _get_selection(self, selected_key, gui):
        return self.selection

    def _create_layout(self, selection):
        return [[]]

    def _create_updatable_widgets(self, selection):
        return []


class SaveSelection:
    def __init__(self):
        self.number_of_calls = 0
        self.previously_saved_selection = None

    def __call__(self, selection: Selection):
        self.number_of_calls += 1
        self.previously_saved_selection = selection


class SelectionControllerTestCase(TestCase):
    SELECTED_KEY = 'selected_key'
    NON_SELECTED_KEY = 'non_selected_key'
    NON_EXISTENT_KEY = 'non_existent_key'

    def setUp(self):
        self.selected_value = object()
        self.non_selected_value = object()

        self.selection = Selection({self.SELECTED_KEY: self.selected_value,
                                    self.NON_SELECTED_KEY: self.non_selected_value})

        self.widget_gui = FakeWidgetGui()

        self.selection_gui = FakeSelectionGui(lambda: self.widget_gui)

        self.save_selection = SaveSelection()

        self.selection_controller = SelectionController(self.selection_gui, self.save_selection, self.selection)


class TestClose(SelectionControllerTestCase):
    def test_close(self):
        self.selection_gui.open = True
        self.selection_gui.close()

        self.assertFalse(self.selection_gui.open)


class TestDisplay(SelectionControllerTestCase):
    def test_display(self):
        self.assertIsNot(self.selection_gui.displayed_selection, self.selection)
        self.selection_controller.display()
        self.assertIs(self.selection_gui.selection, self.selection)


class TestReadEventAndUpdateGui(SelectionControllerTestCase):
    def test_read_event_and_update_gui(self):
        self.assertIsNot(self.selection_gui.read_selection, self.selection)

        self.selection_gui.event = 'hello'
        EVENT = self.selection_controller.read_event_and_update_gui()

        self.assertIs(self.selection_gui.read_selection, self.selection)
        self.assertEqual(EVENT, self.selection_gui.event)


class TestHandleEvent(SelectionControllerTestCase):

    def test_save(self):
        KEY = 'some_key'
        VALUE = object()
        self.selection_gui.selection = Selection({KEY: VALUE})

        EXPECTED_SELECTION = Selection(dict(self.selection.items()))
        EXPECTED_SELECTION[KEY] = VALUE
        EXPECTED_SELECTION.selected_key = KEY

        self.selection_controller.handle_event(Element.SAVE_BUTTON)

        self.assertEqual(self.selection, EXPECTED_SELECTION)
        self.assertIs(self.selection_gui.updated_selection, self.selection)
        self.assertIs(self.save_selection.previously_saved_selection, self.selection)
        self.assertEqual(self.save_selection.number_of_calls, 1)

    def test_save_empty_selection(self):
        self.selection_gui.selection = Selection()

        EXPECTED_SELECTION = Selection(dict(self.selection.items()))

        self.selection_controller.handle_event(Element.SAVE_BUTTON)

        self.assertEqual(self.selection, EXPECTED_SELECTION)
        self.assertIs(self.selection_gui.updated_selection, None)
        self.assertIs(self.save_selection.previously_saved_selection, None)
        self.assertEqual(self.save_selection.number_of_calls, 0)

    def test_delete(self):
        self.selection_gui.current_save_name = self.SELECTED_KEY
        EXPECTED_SELECTION = Selection(dict(self.selection.items()))
        del EXPECTED_SELECTION[self.SELECTED_KEY]

        self.selection_controller.handle_event(Element.DELETE_BUTTON)

        self.assertEqual(self.selection, EXPECTED_SELECTION)
        self.assertIs(self.selection_gui.updated_selection, self.selection)
        self.assertIs(self.save_selection.previously_saved_selection, self.selection)
        self.assertEqual(self.save_selection.number_of_calls, 1)

    def test_delete_what_does_not_exist(self):
        self.selection_gui.current_save_name = self.NON_EXISTENT_KEY
        EXPECTED_SELECTION = Selection(dict(self.selection.items()))

        with self.assertRaises(ValueError):
            self.selection_controller.handle_event(Element.DELETE_BUTTON)

        self.assertEqual(self.selection, EXPECTED_SELECTION)
        self.assertIs(self.selection_gui.updated_selection, None)
        self.assertIs(self.save_selection.previously_saved_selection, None)
        self.assertEqual(self.save_selection.number_of_calls, 0)

    def test_select_non_current_save(self):
        self.selection_gui.current_save_name = self.NON_SELECTED_KEY
        EXPECTED_SELECTION = Selection(dict(self.selection.items()))
        EXPECTED_SELECTION.selected_key = self.NON_SELECTED_KEY

        self.selection_controller.handle_event(Event.SELECT_NON_CURRENT_SAVE)

        self.assertEqual(self.selection, EXPECTED_SELECTION)
        self.assertIs(self.selection_gui.updated_selection, self.selection)
        self.assertIs(self.save_selection.previously_saved_selection, None)
        self.assertEqual(self.save_selection.number_of_calls, 0)

    def test_select_non_existent_save(self):
        self.selection_gui.current_save_name = self.NON_EXISTENT_KEY
        EXPECTED_SELECTION = Selection(dict(self.selection.items()))

        with self.assertRaises(ValueError):
            self.selection_controller.handle_event(Event.SELECT_NON_CURRENT_SAVE)

        self.assertEqual(self.selection, EXPECTED_SELECTION)
        self.assertIs(self.selection_gui.updated_selection, None)
        self.assertIs(self.save_selection.previously_saved_selection, None)
        self.assertEqual(self.save_selection.number_of_calls, 0)

    def test_close_window(self):
        self.selection_gui.open = True
        self.selection_controller.handle_event(WidgetGuiEvent.CLOSE_WINDOW)
        self.assertFalse(self.selection_gui.open)
