from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtCore import QTimer
# from Cope import debug
from threading import Thread


class LoadingBar(QProgressBar):
    # How fast the bar moves, 0 is not at all, 1 is max speed
    rate = 0.2
    startInverted = True
    increments = 1

    def __init__(self, *args, **kwargs):
        super(LoadingBar, self).__init__(*args, **kwargs)
        self.playing = False

        self.min = 0
        self.max = 100
        self._fps = (1 - self.rate) * (self.max / 10)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._increment)

        self._currentlyInverted = self.startInverted
        self.setInvertedAppearance(self._currentlyInverted)
        self.setMaximum(self.max)
        self.setMinimum(self.min)
        self.setValue(self.min)

    def _increment(self):
        # debug(self.value(), 'value')
        if self.value() <= self.min or self.value() >= self.max:
            self._currentlyInverted = not self._currentlyInverted
            self.setInvertedAppearance(self._currentlyInverted)
            # debug('inverting', color=4)

        self.setValue(self.value() + (-self.increments if self._currentlyInverted else self.increments))

    def start(self):
        # debug('loading!', color=4)
        if not self.playing:
            self.setEnabled(True)
            self._timer.start(self._fps)

    def stop(self):
        # debug('stopped loading', color=4)
        self.setValue(0)
        self.setEnabled(False)
        self._timer.stop()




# A helper class to use with 'with'
class showWithLoading:
    """ A class that does whatever is in the with statement while showing the loading bar
    """
    def __init__(self, bar: LoadingBar):
        self.bar = bar

    def __enter__(self):
        self.bar.start()

    def __exit__(self, *args):
        self.bar.stop()


# A function decorator to use with '@'
def showLoading(func, bar):
    def wrap(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        bar.start()
        thread.start()
        thread.join()
        bar.stop()
        # with showWithLoading(bar):
            # return func(*args, **kwargs)
        # return rtn
    return wrap
