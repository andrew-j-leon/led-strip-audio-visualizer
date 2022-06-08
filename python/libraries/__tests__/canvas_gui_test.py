import unittest
from unittest.mock import MagicMock, patch

from libraries.canvas_gui import ProductionCanvasGui
from util import Font


class TestFont(unittest.TestCase):
    def test_constructor_defaults(self):
        font = Font()

        self.assertEqual(font.name, 'Arial')
        self.assertEqual(font.size, 12)
        self.assertEqual(font.style, 'normal')

    def test_constructor_override_defaults(self):
        NAME = 'Times New Roman'
        SIZE = 20
        STYLE = 'bold'

        font = Font(name=NAME, size=SIZE, style=STYLE)

        self.assertEqual(font.name, NAME)
        self.assertEqual(font.size, SIZE)
        self.assertEqual(font.style, STYLE)

    def test_repr(self):
        NAME = 'Times New Roman'
        SIZE = 20
        STYLE = 'bold'

        font = Font(name=NAME, size=SIZE, style=STYLE)

        self.assertEqual(repr(font), f'Font(name={NAME}, size={SIZE}, style={STYLE})')

    def test_eq(self):
        NAME_1 = 'Times New Roman'
        SIZE_1 = 20
        STYLE_1 = 'bold'

        NAME_2 = 'Arial'
        SIZE_2 = 12
        STYLE_2 = 'normal'

        font_1a = Font(NAME_1, SIZE_1, STYLE_1)
        font_1b = Font(NAME_1, SIZE_1, STYLE_1)

        font_2 = Font(NAME_2, SIZE_2, STYLE_2)

        self.assertEqual(font_1a, font_1b)

        self.assertNotEqual(font_1a, font_2)

        self.assertNotEqual(font_1a, 'not a font')

    def test_hash(self):
        NAME_1 = 'Times New Roman'
        SIZE_1 = 20
        STYLE_1 = 'bold'

        NAME_2 = 'Arial'
        SIZE_2 = 12
        STYLE_2 = 'normal'

        hash_1a = hash(Font(NAME_1, SIZE_1, STYLE_1))
        hash_1b = hash(Font(NAME_1, SIZE_1, STYLE_1))

        hash_2 = hash(Font(NAME_2, SIZE_2, STYLE_2))

        self.assertTrue(isinstance(hash_1a, int))

        self.assertEqual(hash_1a, hash_1b)
        self.assertNotEqual(hash_1a, hash_2)


class TestConstructor(unittest.TestCase):
    def setUp(self):
        self.__canvas_patch = patch('PySimpleGUI.Canvas')
        self.__window_patch = patch('PySimpleGUI.Window')

        self.canvas_mock = self.__canvas_patch.start()
        self.window_mock = self.__window_patch.start()

        self.addCleanup(self.__canvas_patch.stop)
        self.addCleanup(self.__window_patch.stop)

    def test_valid(self):
        WIDTH = 1350
        HEIGHT = 600

        ProductionCanvasGui(WIDTH, HEIGHT)

        self.window_mock.assert_called_once()
        self.canvas_mock.assert_called_once()

    def test_invalid_width(self,):
        WIDTHS = [-100, -1]

        for width in WIDTHS:
            with self.subTest(width=width):

                with self.assertRaises(ValueError):
                    height = 600

                    ProductionCanvasGui(width, height)

    def test_invalid_height(self):
        HEIGHTS = [-100, -1]

        for height in HEIGHTS:
            with self.subTest(height=height):

                with self.assertRaises(ValueError):
                    width = 600

                    ProductionCanvasGui(width, height)


class TestMethod(unittest.TestCase):
    def setUp(self):
        self.__canvas_patch = patch('PySimpleGUI.Canvas')
        self.__window_patch = patch('PySimpleGUI.Window')

        self.addCleanup(self.__canvas_patch.stop)
        self.addCleanup(self.__window_patch.stop)

        self.__window_mock = self.__window_patch.start()

        self.window_instance_mock = self.__window_mock.return_value = MagicMock()
        self.element_instance_mock = self.window_instance_mock.find_element.return_value = MagicMock()

        WIDTH = 1350
        HEIGHT = 600
        self.gui = ProductionCanvasGui(WIDTH, HEIGHT)


class TestWidth(TestMethod):
    def test_width(self):
        WIDTH = 1350
        HEIGHT = 600

        gui = ProductionCanvasGui(WIDTH, HEIGHT)

        self.assertEqual(gui.width, WIDTH)


class TestUpdate(TestMethod):
    def test_update(self):
        self.gui.update()

        self.window_instance_mock.read.assert_called_once_with(timeout=0)


class TestClose(TestMethod):
    def test_close(self):
        self.gui.close()

        self.window_instance_mock.close.assert_called_once()


class TestCreateText(TestMethod):
    def test_valid(self):
        tk_canvas_mock = self.element_instance_mock.TKCanvas = MagicMock()

        ELEMENT_ID = 10
        tk_canvas_mock.create_text.return_value = ELEMENT_ID

        CENTER_X = 10
        CENTER_Y = 20
        TEXT = 'hello'
        FONT = Font()
        FILL_COLOR = '#000000'

        element_id = self.gui.create_text(CENTER_X, CENTER_Y, TEXT, FONT, FILL_COLOR)

        tk_canvas_mock.create_text.assert_called_once_with(CENTER_X, CENTER_Y, text=TEXT, fill=FILL_COLOR,
                                                           font=(FONT.name, FONT.size, FONT.style))

        self.assertEqual(element_id, ELEMENT_ID)

    def test_update_not_called(self):
        self.element_instance_mock.TKCanvas = None

        with self.assertRaises(ValueError):
            CENTER_X = 10
            CENTER_Y = 20
            TEXT = 'hello'
            FONT = Font()

            self.gui.create_text(CENTER_X, CENTER_Y, TEXT, FONT)


class TestOval(TestMethod):
    def test_valid(self):
        tk_canvas_mock = self.element_instance_mock.TKCanvas = MagicMock()

        ELEMENT_ID = 10
        tk_canvas_mock.create_oval.return_value = ELEMENT_ID

        TOP_LEFT_X = 10
        TOP_LEFT_Y = 20

        BOTTOM_RIGHT_X = 20
        BOTTOM_RIGHT_Y = 30

        FILL_COLOR = '#122436'

        element_id = self.gui.create_oval(TOP_LEFT_X, TOP_LEFT_Y, BOTTOM_RIGHT_X, BOTTOM_RIGHT_Y, FILL_COLOR)

        tk_canvas_mock.create_oval.assert_called_once_with((TOP_LEFT_X, TOP_LEFT_Y),
                                                           (BOTTOM_RIGHT_X, BOTTOM_RIGHT_Y),
                                                           fill=FILL_COLOR)

        self.assertEqual(element_id, ELEMENT_ID)

    def test_update_not_called(self):
        self.element_instance_mock.TKCanvas = None

        with self.assertRaises(ValueError):
            TOP_LEFT_X = 10
            TOP_LEFT_Y = 20

            BOTTOM_RIGHT_X = 20
            BOTTOM_RIGHT_Y = 30

            FILL_COLOR = '#122436'

            self.gui.create_oval(TOP_LEFT_X, TOP_LEFT_Y, BOTTOM_RIGHT_X, BOTTOM_RIGHT_Y, FILL_COLOR)


class TestSetElementFillColor(TestMethod):
    def test_valid(self):
        tk_canvas_mock = self.element_instance_mock.TKCanvas = MagicMock()

        ELEMENT_ID = 10
        FILL_COLOR = '#112233'
        self.gui.set_element_fill_color(ELEMENT_ID, FILL_COLOR)

        tk_canvas_mock.itemconfig.assert_called_once_with(ELEMENT_ID, fill=FILL_COLOR)

    def test_update_not_called(self):
        with self.assertRaises(ValueError):
            self.element_instance_mock.TKCanvas = None

            FILL_COLOR = '#112233'
            self.gui.set_element_fill_color(20, FILL_COLOR)
