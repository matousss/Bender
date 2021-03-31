# MonitorScreen.py
from datetime import time
from threading import Thread

import kivy
import psutil
from kivy.base import runTouchApp
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.properties import Property
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.graphics import Color, Ellipse, Rectangle

kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.widget import Canvas

BACKGROUND_COLOR = (.9, .9, .9, 1)


class Graph(Widget):
    def __init__(self, base: int, value: int):
        super(Graph, self).__init__()
        self.thickness = 40
        if base < 0:
            raise Exception("Illegal argument: base can't be smaller than zero")
        self.size = (100, 100)
        self.base = base
        self.texture_size = None

        self.label = Label(text="0%", font_size=self.thickness / 2, color="black")

        self.set_value(value)
        self.add_widget(self.label)

    def redraw(self):
        with self.canvas:
            self.canvas.clear()
            Color(.5, 0, 0)
            Ellipse(pos=self.pos, size=self.size)
            Color(1, 0, 0)
            Ellipse(pos=self.pos, size=self.size,
                    angle_end=(0.001 if self.value == 0 else self.value / self.base * 360))
            Color(BACKGROUND_COLOR)
            Ellipse(pos=(self.pos[0] + self.thickness / 2, self.pos[1] + self.thickness / 2),
                    size=(self.size[0] - self.thickness, self.size[1] - self.thickness))
            Color(1, 1, 1)

        self.label.color = "black"
        self.label.text = str(self.value) + '%'

    def set_value(self, value: int):
        if value > self.base:
            raise Exception("Illegal arguments: base must be greater than value")
        if value < 0:
            raise Exception("Illegal argument: value can't be smaller than zero")

        self.value = value
        print(self.value)
        self.redraw()

    pass


class MonitorScreen(Screen):
    def __init__(self, name: str):
        super(MonitorScreen, self).__init__(name=name)

        layout = GridLayout(cols=3)
        self.cpu_graph = Graph(100, 10)
        layout.add_widget(self.cpu_graph)
        layout.add_widget(Label(text="lmao", color="black"))
        self.add_widget(layout)

        pass

    pass


MONITOR_SCREEN = MonitorScreen(name="monitor");


class Bender(App):

    def build(self):
        Window.clearcolor = BACKGROUND_COLOR

        sb = ScreenManager()
        sb.add_widget(MONITOR_SCREEN)

        LoadCounter(graph=MONITOR_SCREEN.cpu_graph).run()

        return sb;

    pass

    def update_monitors(self, td, value):
        MONITOR_SCREEN.cpu_graph.set_value(value)
        pass


class LoadCounter(Thread):
    def __init__(self, graph: Graph):
        self.graph = graph

    def run(self):
        Clock.schedule_interval(self.update_graph, .5)
    @mainthread
    def update_graph(self, td):

        MONITOR_SCREEN.cpu_graph.set_value(int(psutil.cpu_percent(4)))


if __name__ == '__main__':
    Bender().run()
