from typing import Union, List, Tuple
import numpy as np

from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtWidgets import QSizePolicy

from commonroad.scenario.intersection import Intersection
from commonroad.common.util import Interval
from commonroad.scenario.scenario import Scenario
from commonroad.scenario.lanelet import Lanelet
from commonroad.visualization.mp_renderer import MPRenderer
from commonroad.geometry.shape import Circle

from crdesigner.io.scenario_designer.toolboxes.gui_sumo_simulation import SUMO_AVAILABLE
if SUMO_AVAILABLE:
    from crdesigner.sumo_map.config import SumoConfig
from crdesigner.io.scenario_designer.misc.util import Observable

import matplotlib
from matplotlib.animation import FuncAnimation, writers
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.path import Path
from matplotlib.patches import PathPatch
matplotlib.use("Qt5Agg")

__author__ = "Benjamin Orthen, Stefan Urban, Max Winklhofer, Guyue Huang, Max Fruehauf, Sebastian Maierhofer"
__copyright__ = "TUM Cyber-Physical Systems Group"
__credits__ = ["Priority Program SPP 1835 Cooperative Interacting Automobiles, BMW Car@TUM"]
__version__ = "1.2.0"
__maintainer__ = "Sebastian Maierhofer"
__email__ = "commonroad-i06@in.tum.de"
__status__ = "Released"

ZOOM_FACTOR = 1.2


def _merge_dict(source, destination):
    """deeply merges two dicts
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            _merge_dict(value, node)
        else:
            destination[key] = value
    return destination


class DynamicCanvas(FigureCanvas):
    """ this canvas provides zoom with the mouse wheel """
    def __init__(self, parent=None, width=5, height=5, dpi=100):

        self.ax = None
        self.drawer = Figure(figsize=(width, height), dpi=dpi)
        self.rnd = MPRenderer(ax=self.ax)

        self.draw_params = {
            'scenario': {
                'dynamic_obstacle': {
                    'trajectory': {
                        'show_label': True,
                        'draw_trajectory': False
                    }
                },
                'lanelet_network': {
                    # 'traffic_light': {
                    #     'scale_factor': 0.2
                    # },
                    'traffic_sign': {
                        'draw_traffic_signs': True,
                        'show_traffic_signs': 'all',
                        # 'scale_factor': 0.2
                    },
                }
            }
        }

        self._handles = {}

        super().__init__(self.drawer)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.mpl_connect('scroll_event', self.zoom)

        self.clear_axes()

    def clear_axes(self, keep_limits=False):
        """ """
        if self.ax:
            limits = self.get_limits()
            self.ax.clear()
        else:
            limits = None
            self.ax = self.drawer.add_subplot(111)

        self.ax.set_aspect("equal", "datalim")
        self.ax.set_axis_off()
        self.draw_idle()
        if keep_limits and limits:
            self.update_plot(limits)

    def get_axes(self):
        """Gives the plots Axes

        :return: matplotlib axis
        """
        return self.ax

    def get_limits(self) -> List[float]:
        """ return the current limits of the canvas """
        x_lim = self.ax.get_xlim()
        y_lim = self.ax.get_ylim()
        return [x_lim[0], x_lim[1], y_lim[0], y_lim[1]]

    def update_plot(self, limits: List[float] = None):
        """ draw the canvas. optional with new limits"""
        if limits:
            self.ax.set(xlim=limits[0:2])
            self.ax.set(ylim=limits[2:4])
        self.draw_idle()

    def zoom(self, event):
        """ zoom in / out function in GUI by using mouse wheel """
        x_min, x_max = self.ax.get_xlim()
        y_min, y_max = self.ax.get_ylim()
        center = ((x_min + x_max) / 2, (y_min + y_max) / 2)
        x_dim = (x_max - x_min) / 2
        y_dim = (y_max - y_min) / 2

        # enlarge / shrink limits
        if event.button == 'up':
            new_x_dim = x_dim / ZOOM_FACTOR
            new_y_dim = y_dim / ZOOM_FACTOR
        elif event.button == 'down':
            new_x_dim = x_dim * ZOOM_FACTOR
            new_y_dim = y_dim * ZOOM_FACTOR
        else:
            return

        # new center sensitive to mouse position of zoom event
        mouse_pos = (event.xdata, event.ydata)
        if mouse_pos[0] and mouse_pos[1]:
            # TODO enhance zoom center
            new_center_diff_x = (center[0] - mouse_pos[0]) / 6
            new_center_diff_y = (center[1] - mouse_pos[1]) / 6
            if event.button == 'up':
                new_center_x = center[0] - new_center_diff_x
                new_center_y = center[1] - new_center_diff_y
            else:
                new_center_x = center[0] + new_center_diff_x
                new_center_y = center[1] + new_center_diff_y
            # new limits should include old limits if zooming out
            # old limits should include new limits if zooming in
            dim_diff_x = abs(new_x_dim - x_dim)
            dim_diff_y = abs(new_y_dim - y_dim)
            new_center_x = min(max(center[0] - dim_diff_x, new_center_x),
                               center[0] + dim_diff_x)
            new_center_y = min(max(center[1] - dim_diff_y, new_center_y),
                               center[1] + dim_diff_y)
        else:
            new_center_x = center[0]
            new_center_y = center[1]

        self.update_plot([
            new_center_x - new_x_dim, new_center_x + new_x_dim,
            new_center_y - new_y_dim, new_center_y + new_y_dim
        ])

    def draw_scenario(self,
                      scenario: Scenario,
                      draw_params=None,
                      plot_limits=None):
        """[summary]

        :param scenario: [description]
        :type scenario: Scenario
        :param draw_params: [description], defaults to None
        :type draw_params: [type], optional
        :param plot_limits: [description], defaults to None
        :type plot_limits: [type], optional
        """
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        self.ax.clear()

        draw_params_merged = _merge_dict(self.draw_params.copy(), draw_params)

        self.rnd.plot_limits = plot_limits
        self.rnd.ax = self.ax
        scenario.draw(renderer=self.rnd, draw_params=draw_params_merged)
        self.rnd.render()

        if not plot_limits:
            self.ax.set(xlim=xlim)
            self.ax.set(ylim=ylim)

    def update_obstacles(self,
                         scenario: Scenario,
                         draw_params=None,
                         plot_limits=None):
        """
        Redraw only the dynamic obstacles. This gives a large performance boost, when playing an animation
        :param scenario: The scneario containing the dynamic obstacles 
        :param draw_params: CommonRoad draw_object() DrawParams
        :param plot_limits: Matplotlib plot limits
        """
        # redraw dynamic obstacles
        obstacles = scenario.obstacles_by_position_intervals([
            Interval(plot_limits[0], plot_limits[1]),
            Interval(plot_limits[2], plot_limits[3])
        ]) if plot_limits else scenario.obstacles

        draw_params_merged = _merge_dict(self.draw_params.copy(), draw_params)

        self.rnd.ax = self.ax
        for obj in obstacles:
            obj.draw(renderer=self.rnd, draw_params=draw_params_merged)
            self.rnd.render(show=True)


def draw_lanelet_polygon(lanelet, ax, color, alpha, zorder,
                         label) -> Tuple[float, float, float, float]:
    # TODO efficiency
    verts = []
    codes = [Path.MOVETO]

    xlim1 = float("Inf")
    xlim2 = -float("Inf")
    ylim1 = float("Inf")
    ylim2 = -float("Inf")

    for x, y in np.vstack(
        [lanelet.left_vertices, lanelet.right_vertices[::-1]]):
        verts.append([x, y])
        codes.append(Path.LINETO)

        xlim1 = min(xlim1, x)
        xlim2 = max(xlim2, x)
        ylim1 = min(ylim1, y)
        ylim2 = max(ylim2, y)

    verts.append(verts[0])
    codes[-1] = Path.CLOSEPOLY

    path = Path(verts, codes)

    ax.add_patch(
        PathPatch(
            path,
            facecolor=color,
            edgecolor="black",
            lw=0.0,
            alpha=alpha,
            zorder=zorder,
            label=label,
        ))

    return [xlim1, xlim2, ylim1, ylim2]


class Viewer:
    """ functionality to draw a Scenario onto a Canvas """
    def __init__(self, parent, callback_function):
        self.current_scenario = None
        self.dynamic = DynamicCanvas(parent, width=5, height=10, dpi=100)
        self.callback_function = callback_function

    def open_scenario(self, scenario: Scenario):
        """ """
        self.current_scenario = scenario
        self.update_plot(focus_on_network=True)

    def update_plot(self,
                    sel_lanelet: Lanelet = None,
                    sel_intersection: Intersection = None,
                    focus_on_network: bool = False):
        """ Update the plot accordinly to the selection of scenario elements
        :param scenario: Scenario to draw
        :type scenario: Scenario
        :param sel_lanelet: selected lanelet, defaults to None
        :type sel_lanelet: Lanelet, optional
        :param sel_intersection: selected intersection, defaults to None
        :type sel_intersection: Intersection, optional
        """

        x_lim = self.dynamic.get_axes().get_xlim()
        y_lim = self.dynamic.get_axes().get_ylim()

        self.dynamic.clear_axes()
        ax = self.dynamic.get_axes()

        network_limits = [
            float("Inf"), -float("Inf"),
            float("Inf"), -float("Inf")
        ]

        draw_params = {
            'scenario': {
                'dynamic_obstacle': {
                    'trajectory': {
                        'show_label': True,
                        'draw_trajectory': False
                    }
                }
            }
        }
        self.dynamic.draw_scenario(self.current_scenario,
                                   draw_params=draw_params)

        for lanelet in self.current_scenario.lanelet_network.lanelets:

            color, alpha, zorder, label = self.get_paint_parameters(
                lanelet, sel_lanelet, sel_intersection)
            if color == "gray": continue

            lanelet_limits = draw_lanelet_polygon(lanelet, ax, color, alpha, zorder, label)
            network_limits[0] = min(network_limits[0], lanelet_limits[0])
            network_limits[1] = max(network_limits[1], lanelet_limits[1])
            network_limits[2] = min(network_limits[2], lanelet_limits[2])
            network_limits[3] = max(network_limits[3], lanelet_limits[3])

            self.draw_lanelet_vertices(lanelet, ax)

        handles, labels = ax.get_legend_handles_labels()
        legend = ax.legend(handles, labels)
        legend.set_zorder(50)

        if focus_on_network:
            # can we focus on a selection?
            if all([abs(l) < float("Inf") for l in network_limits]):
                # enlarge limits
                border_x = (network_limits[1] - network_limits[0]) * 0.1 + 1
                border_y = (network_limits[3] - network_limits[2]) * 0.1 + 1
                network_limits[0] -= border_x
                network_limits[1] += border_x
                network_limits[2] -= border_y
                network_limits[3] += border_y
                self.dynamic.update_plot(network_limits)
            # otherwise focus on the network
            else:
                self.dynamic.ax.autoscale()
        else:
            self.dynamic.update_plot([x_lim[0], x_lim[1], y_lim[0], y_lim[1]])

        self.dynamic.drawer.tight_layout()

    def get_paint_parameters(self, lanelet: Lanelet, selected_lanelet: Lanelet,
                             selected_intersection: Intersection):
        """
        Return the parameters for painting a lanelet regarding the selected lanelet.
        """

        if selected_lanelet:

            if lanelet.lanelet_id == selected_lanelet.lanelet_id:
                color = "red"
                alpha = 0.7
                zorder = 20
                label = "{} selected".format(lanelet.lanelet_id)

            elif (lanelet.lanelet_id in selected_lanelet.predecessor
                  and lanelet.lanelet_id in selected_lanelet.successor):
                color = "purple"
                alpha = 0.5
                zorder = 10
                label = "{} predecessor and successor of {}".format(
                    lanelet.lanelet_id, selected_lanelet.lanelet_id)

            elif lanelet.lanelet_id in selected_lanelet.predecessor:
                color = "blue"
                alpha = 0.5
                zorder = 10
                label = "{} predecessor of {}".format(
                    lanelet.lanelet_id, selected_lanelet.lanelet_id)
            elif lanelet.lanelet_id in selected_lanelet.successor:
                color = "green"
                alpha = 0.5
                zorder = 10
                label = "{} successor of {}".format(
                    lanelet.lanelet_id, selected_lanelet.lanelet_id)
            elif lanelet.lanelet_id == selected_lanelet.adj_left:
                color = "yellow"
                alpha = 0.5
                zorder = 10
                label = "{} adj left of {} ({})".format(
                    lanelet.lanelet_id,
                    selected_lanelet.lanelet_id,
                    "same" if selected_lanelet.adj_left_same_direction else
                    "opposite",
                )
            elif lanelet.lanelet_id == selected_lanelet.adj_right:
                color = "orange"
                alpha = 0.5
                zorder = 10
                label = "{} adj right of {} ({})".format(
                    lanelet.lanelet_id,
                    selected_lanelet.lanelet_id,
                    "same" if selected_lanelet.adj_right_same_direction else
                    "opposite",
                )
            else:
                color = "gray"
                alpha = 0.3
                zorder = 0
                label = None

        elif selected_intersection:
            incoming_ids = selected_intersection.map_incoming_lanelets.keys()
            inc_succ_ids = set()
            for inc in selected_intersection.incomings:
                inc_succ_ids |= inc.successors_right
                inc_succ_ids |= inc.successors_left
                inc_succ_ids |= inc.successors_straight


            if lanelet.lanelet_id in incoming_ids:
                color = "red"
                alpha = 0.7
                zorder = 10
                label = "{} incoming".format(lanelet.lanelet_id)
            elif lanelet.lanelet_id in selected_intersection.crossings:
                color = "blue"
                alpha = 0.5
                zorder = 10
                label = "{} crossing".format(lanelet.lanelet_id)
            elif lanelet.lanelet_id in inc_succ_ids:
                color = "green"
                alpha = 0.3
                zorder = 10
                label = "{} intersection".format(lanelet.lanelet_id)
            else:
                color = "gray"
                alpha = 0.3
                zorder = 0
                label = None
        else:
            color = "gray"
            alpha = 0.3
            zorder = 0
            label = None

        return color, alpha, zorder, label

    def draw_lanelet_vertices(self, lanelet, ax):
        ax.plot(
            [x for x, y in lanelet.left_vertices],
            [y for x, y in lanelet.left_vertices],
            color="black",
            lw=0.1,
        )
        ax.plot(
            [x for x, y in lanelet.right_vertices],
            [y for x, y in lanelet.right_vertices],
            color="black",
            lw=0.1,
        )


class AnimatedViewer(Viewer):
    def __init__(self, parent, callback_function):
        super().__init__(parent, callback_function)

        # sumo config giving dt etc
        self._config: SumoConfig = None
        self.min_time_step = 0
        self.max_time_step = 0
        # current time step
        self.time_step = Observable(0)
        # FuncAnimation object
        self.animation: FuncAnimation = None
        # if playing or not
        self.playing = False
        self.dynamic.mpl_connect('button_press_event', self.select_scenario_element)

    def open_scenario(self, scenario: Scenario, config: Observable = None):
        """[summary]

        :param scenario: [description]
        :type scenario: [type]
        :param config: [description], defaults to None
        :type config: SumoConfig, optional
        """
        self.current_scenario = scenario

        # if we have not subscribed already, subscribe now
        if config is not None:
            if not self._config:
                def set_config(conf):
                    self._config = conf
                    self._calc_max_timestep()
                config.subscribe(set_config)
            self._config = config.value

        self._calc_max_timestep()
        if self.animation:
            self.time_step.value = 0
            self.animation.event_source.stop()
            self.animation = None
        self.update_plot(focus_on_network=True)

    def _init_animation(self):
        if not self.current_scenario:
            return

        print('init animation')
        scenario = self.current_scenario
        self.dynamic.clear_axes(keep_limits=True)

        start = self.min_time_step
        end = self.max_timestep
        plot_limits: Union[list, None, str] = None
        if self._config is not None:
            dt = self._config.dt
        else:
            dt = 0
        # ps = 25
        # dpi = 120
        # ln, = self.dynamic.ax.plot([], [], animated=True)
        anim_frames = end - start

        if start == end:
            warning_dialog = QMessageBox()
            warning_dialog.warning(None, "Warning",
                                   "This Scenario only has one time step!",
                                   QMessageBox.Ok, QMessageBox.Ok)
            warning_dialog.close()

        assert start <= end, '<video/create_scenario_video> time_begin=%i needs to smaller than time_end=%i.' % (
            start, end)

        def draw_frame(draw_params):
            time_start = start + self.time_step.value
            time_end = start + min(anim_frames, self.time_step.value)
            self.time_step.value += 1
            if time_start > time_end:
                self.time_step.value = 0

            draw_params = {
                'time_begin': time_start,
                'time_end': time_end,
                'antialiased': True,
                'dynamic_obstacle': {
                    'show_label': True
                }
            }

            # plot dynamic obstracles
            # if self.timestep.value == 1:
            self.dynamic.draw_scenario(scenario, draw_params=draw_params)
            # else:
            #     self.dynamic.update_obstacles(
            #         scenario,
            #         draw_params=draw_params,
            #         plot_limits=None if plot_limits == 'auto' else plot_limits)

        # Interval determines the duration of each frame in ms
        interval = 1000 * dt
        self.dynamic.clear_axes(keep_limits=True)
        self.animation = FuncAnimation(self.dynamic.figure,
                                       draw_frame,
                                       blit=False,
                                       interval=interval,
                                       repeat=True)

    def play(self):
        """ plays the animation if existing """
        if not self.animation:
            self._init_animation()

        self.dynamic.update_plot()
        self.animation.event_source.start()

    def pause(self):
        """ pauses the animation if playing """
        if not self.animation:
            self._init_animation()
            return

        self.animation.event_source.stop()

    def set_timestep(self, timestep: int):
        """ sets the animation to the current timestep """
        print("set timestep: ", timestep)
        if not self.animation:
            self._init_animation()
        self.dynamic.update_plot()
        # self.animation.event_source.start()
        self.time_step.silent_set(timestep)

    def save_animation(self, save_file: str):
        # if self.animation is None:
        # print("no animation loaded")
        # return
        self.play()
        if save_file == "Save as mp4":
            if not self.current_scenario:
                return
            path, _ = QFileDialog.getSaveFileName(
                None,
                "QFileDialog.getSaveFileName()",
                ".mp4",
                "CommonRoad scenario video *.mp4 (*.mp4)",
                options=QFileDialog.Options(),
            )

            if not path:
                return

            try:
                with open(path, "w"):
                    messbox = QMessageBox.about(None, "Information",
                                                "Exporting as Mp4 file will take a while, please wait until process "
                                                "finished ")
                    FFMpegWriter = writers['ffmpeg']
                    writer = FFMpegWriter()
                    self.animation.save(path, dpi=120, writer=writer)


            except IOError as e:
                QMessageBox.critical(
                    None,
                    "CommonRoad file not created!",
                    "The CommonRoad file was not saved due to an error.\n\n{}".
                        format(e),
                    QMessageBox.Ok,
                )
                return

        elif save_file == "Save as gif":
            if not self.current_scenario:
                return
            path, _ = QFileDialog.getSaveFileName(
                None,
                "QFileDialog.getSaveFileName()",
                ".gif",
                "CommonRoad scenario video *.gif (*.gif)",
                options=QFileDialog.Options(),
            )

            if not path:
                return

            try:
                with open(path, "w"):
                    messbox = QMessageBox.about(None, "Information",
                                                "Exporting as Gif file will take few minutes, please wait until "
                                                "process finished")
                    self.animation.save(path, writer='imagemagick', fps=30)

            except IOError as e:
                QMessageBox.critical(
                    self,
                    "CommonRoad file not created!",
                    "The CommonRoad file was not saved due to an error.\n\n{}".
                        format(e),
                    QMessageBox.Ok,
                )
                return

    def _calc_max_timestep(self):
        """calculate maximal time step of current scenario"""
        if self.current_scenario is None:
            return 0
        timesteps = [
            obstacle.prediction.occupancy_set[-1].time_step
            for obstacle in self.current_scenario.dynamic_obstacles
        ]
        self.max_timestep = np.max(timesteps) if timesteps else 0
        return self.max_timestep

    def select_scenario_element(self, mouse_clicked_event):
        """
        Select lanelets by clicking on the canvas. Selects only one of the
        lanelets that contains the click position.
        """
        mouse_pos = np.array(
            [mouse_clicked_event.xdata, mouse_clicked_event.ydata])
        click_shape = Circle(radius=0.01, center=mouse_pos)

        l_network = self.current_scenario.lanelet_network
        selected_l_ids = l_network.find_lanelet_by_shape(click_shape)
        selected_lanelets = [l_network.find_lanelet_by_id(lid) for lid in selected_l_ids]
        selected_obstacles = [obs for obs in self.current_scenario.obstacles
                              if obs.occupancy_at_time(self.time_step.value) is not None and
                              obs.occupancy_at_time(self.time_step.value).shape.contains_point(mouse_pos)]

        if len(selected_lanelets) > 0 and len(selected_obstacles) == 0:
            self.update_plot(sel_lanelet=selected_lanelets[0])
        else:
            self.update_plot(sel_lanelet=None)

        if len(selected_obstacles) > 0:
            self.callback_function(selected_obstacles[0])
        elif len(selected_lanelets) > 0:
            self.callback_function(selected_lanelets[0])