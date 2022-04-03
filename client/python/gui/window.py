import PySimpleGUI as sg


class Window(sg.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def read(self, *args, **kwargs)->str:
        """
        THE biggest deal method in the Window class! This is how you get all of your data from your Window.
            Pass in a timeout (in milliseconds) to wait for a maximum of timeout milliseconds. Will return timeout_key
            if no other GUI events happen first.

        :param timeout:     Milliseconds to wait until the Read will return IF no other GUI events happen first
        :type timeout:      (int)
        :param timeout_key: The value that will be returned from the call if the timer expired
        :type timeout_key:  (Any)
        :param close:       if True the window will be closed prior to returning
        :type close:        (bool)
        :return:            event
        :rtype:             Tuple[(Any), Dict[Any, Any], List[Any], None]
        """
        EVENT = 0
        return super().read(*args, **kwargs)[EVENT]