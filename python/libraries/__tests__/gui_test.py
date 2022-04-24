import unittest
from unittest.mock import MagicMock, patch

from libraries.gui import Font, ProductionGui, Rectangle


class TestFont(unittest.TestCase):
    def test_constructor_defaults(self):
        font = Font()

        self.assertEqual(font.name, 'Arial')
        self.assertEqual(font.size, 12)
        self.assertEqual(font.style, 'normal')
        self.assertEqual(font.color, '#000000')

    def test_constructor_override_defaults(self):
        NAME = 'Times New Roman'
        SIZE = 20
        STYLE = 'bold'
        COLOR = '#121212'

        font = Font(name=NAME, size=SIZE, style=STYLE, color=COLOR)

        self.assertEqual(font.name, NAME)
        self.assertEqual(font.size, SIZE)
        self.assertEqual(font.style, STYLE)
        self.assertEqual(font.color, COLOR)

    def test_repr(self):
        NAME = 'Times New Roman'
        SIZE = 20
        STYLE = 'bold'
        COLOR = '#121212'

        font = Font(name=NAME, size=SIZE, style=STYLE, color=COLOR)

        self.assertEqual(repr(font), f'Font(name={NAME}, size={SIZE}, style={STYLE}, color={COLOR})')


class TestRectangle(unittest.TestCase):
    def test_valid_constructor(self):
        ARGS = [(0, 0), (0, 1), (1, 0), (1, 1), (1920, 1080)]

        for width, height in ARGS:
            with self.subTest(width=width, height=height):

                rectangle = Rectangle(width, height)

                self.assertEqual(rectangle.width, width)
                self.assertEqual(rectangle.height, height)

    def test_invalid_constructor(self):
        WIDTHS = [-100, -1]

        for width in WIDTHS:
            with self.subTest(width=width):

                with self.assertRaises(ValueError) as error:
                    height = 100

                    Rectangle(width, height)

                actual_error_message = str(error.exception)
                expected_error_message = f'width must be >= 0, but was {width}.'

                self.assertEqual(actual_error_message, expected_error_message)

        HEIGHTS = [-100, -1]

        for height in HEIGHTS:
            with self.subTest(height=height):

                with self.assertRaises(ValueError) as error:
                    width = 100

                    Rectangle(width, height)

                actual_error_message = str(error.exception)
                expected_error_message = f'height must be >= 0, but was {height}.'

                self.assertEqual(actual_error_message, expected_error_message)

    def test_repr(self):
        WIDTH = 100
        HEIGHT = 200

        rectangle = Rectangle(WIDTH, HEIGHT)

        self.assertEqual(repr(rectangle), f'Rectangle({WIDTH}, {HEIGHT})')


@patch('libraries.gui.Canvas')
@patch('libraries.gui.Window')
class TestConstructor(unittest.TestCase):
    def test_valid(self, window_mock: MagicMock, canvas_mock: MagicMock):
        WIDTH = 1350
        HEIGHT = 600

        ProductionGui(WIDTH, HEIGHT)

        window_mock.assert_called_once()
        canvas_mock.assert_called_once()

    def test_invalid_width(self, window_mock: MagicMock, canvas_mock: MagicMock):
        WIDTHS = [-100, -1]

        for width in WIDTHS:
            with self.subTest(width=width):

                with self.assertRaises(ValueError):
                    height = 600

                    ProductionGui(width, height)

    def test_invalid_height(self, window_mock: MagicMock, canvas_mock: MagicMock):
        HEIGHTS = [-100, -1]

        for height in HEIGHTS:
            with self.subTest(height=height):

                with self.assertRaises(ValueError):
                    width = 600

                    ProductionGui(width, height)


class TestMethod(unittest.TestCase):
    def setUp(self):
        self.__canvas_patch = patch('libraries.gui.Canvas')
        self.__window_patch = patch('libraries.gui.Window')

        self.addCleanup(self.__canvas_patch.stop)
        self.addCleanup(self.__window_patch.stop)

        self.__window_mock = self.__window_patch.start()

        self.window_instance_mock = self.__window_mock.return_value = MagicMock()
        self.element_instance_mock = self.window_instance_mock.find_element.return_value = MagicMock()

        WIDTH = 1350
        HEIGHT = 600
        self.gui = ProductionGui(WIDTH, HEIGHT)


class TestDimensions(TestMethod):
    def test_dimensions(self):
        WIDTH = 1350
        HEIGHT = 600

        gui = ProductionGui(WIDTH, HEIGHT)

        dimensions = gui.dimensions

        self.assertEqual(dimensions.width, WIDTH)
        self.assertEqual(dimensions.height, HEIGHT)


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

        element_id = self.gui.create_text(CENTER_X, CENTER_Y, TEXT, FONT)

        tk_canvas_mock.create_text.assert_called_once_with(CENTER_X, CENTER_Y, text=TEXT, fill=FONT.color,
                                                           font=(FONT.name, FONT.size, FONT.style))

        self.assertEqual(element_id, ELEMENT_ID)

    def test_update_not_called(self):
        self.element_instance_mock.TKCanvas = None

        with self.assertRaises(ValueError) as error:
            CENTER_X = 10
            CENTER_Y = 20
            TEXT = 'hello'
            FONT = Font()

            self.gui.create_text(CENTER_X, CENTER_Y, TEXT, FONT)

        actual_error_message = str(error.exception)
        expected_error_message = 'You must call self.update() before creating elements on a ProductionGui.'

        self.assertEqual(actual_error_message, expected_error_message)


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

        with self.assertRaises(ValueError) as error:
            TOP_LEFT_X = 10
            TOP_LEFT_Y = 20

            BOTTOM_RIGHT_X = 20
            BOTTOM_RIGHT_Y = 30

            FILL_COLOR = '#122436'

            self.gui.create_oval(TOP_LEFT_X, TOP_LEFT_Y, BOTTOM_RIGHT_X, BOTTOM_RIGHT_Y, FILL_COLOR)

        actual_error_message = str(error.exception)
        expected_error_message = 'You must call self.update() before creating elements on a ProductionGui.'

        self.assertEqual(actual_error_message, expected_error_message)


class TestSetElementFillColor(TestMethod):
    def test_valid(self):
        tk_canvas_mock = self.element_instance_mock.TKCanvas = MagicMock()

        ELEMENT_ID = 10
        FILL_COLOR = '#112233'
        self.gui.set_element_fill_color(ELEMENT_ID, FILL_COLOR)

        tk_canvas_mock.itemconfig.assert_called_once_with(ELEMENT_ID, fill=FILL_COLOR)

    def test_update_not_called(self):
        with self.assertRaises(ValueError) as error:
            self.element_instance_mock.TKCanvas = None

            FILL_COLOR = '#112233'
            self.gui.set_element_fill_color(20, FILL_COLOR)

        actual_error_message = str(error.exception)
        expected_error_message = 'You must call self.update() before editting elements.'

        self.assertEqual(actual_error_message, expected_error_message)
