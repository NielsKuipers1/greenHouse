import matplotlib.pyplot as plt

plt.ion()
class Gantry():
    
    def __init__(self, vs, ee=[0, 0]) -> None:
        self._vs = vs
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.plot([vs[0][0], vs[1][0], vs[2][0], vs[3][0], vs[0][0]], [vs[0][1], vs[1][1], vs[2][1], vs[3][1], vs[0][1]])
        self._dot, = self.ax.plot(ee[0], ee[1], 'ro')
        plt.show()
        self.fig.canvas.flush_events()

    def update(self, new_ee):
        self._dot.set_data([new_ee[0]], [new_ee[1]])
        self.fig.canvas.flush_events()