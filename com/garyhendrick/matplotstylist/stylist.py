__author__ = 'gary'
import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:\t%(message)s")

import matplotlib

matplotlib.use("TkAgg")

from numpy import arange, sin, pi
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.figure import Figure
from matplotlib.artist import getp
import sys, os

if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk
import tkColorChooser
import ttk

themes = ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')

# app is being maintained in the global scope in order to maintain a reference
app = None


class StylistTkinter(ttk.Frame):
    _WINDOW_TITLE = "Generic Title"
    opts = {}
    mplparams = {}

    """
    Present tool sytlization choices for a matplotlib plot.
    1. Create the plot required to build this up
    2. Create all of the appropriate widgets
    """

    def styleChange(self, name1, name2, op):
        """
        :param name1: http://www.tcl.tk/man/tcl8.4/TclCmd/trace.htm#M14
        :param name2: http://www.tcl.tk/man/tcl8.4/TclCmd/trace.htm#M14
        :param op: http://www.tcl.tk/man/tcl8.4/TclCmd/trace.htm#M14
        """
        logging.debug("styleChange detected with arguments (%s, %s, %s)" % (name1, name2, op))
        logging.debug("styleChange executing a change from to %s", self.mpl_global_style.get())
        plt.style.use(
            self.mpl_global_style.get())  # TODO can you set this up to use name1 ? Yes, tk.StringVar() contains _name

        # clean up the existing stuff, deleting all of the components within the canvas
        self.canvas.get_tk_widget().delete("all")
        for child in self.mplframe.winfo_children():
            child.destroy()
        self.figure.clear()
        self.axes.clear()
        del self.line, self.axes, self.figure

        # recretae the plot, the frame it resides in is already created and useful
        self.createPlot()
        logging.debug("styleChange completed with new style changed to %s" % self.mpl_global_style.get())

    def loadOptions(self):
        logging.debug("loadOptions invocation")
        self.opts['mpl_style_idx'] = 0
        self.mplparams["styles"] = plt.style.available
        logging.debug("loadOptions set self.mplparams[\"styles\"] = %s"
                      % repr(self.mplparams["styles"]))
        optpath = os.path.join(os.getcwd(), "res", "stylist.opt")
        logging.debug('loading options: loading option file from %s' % (optpath))
        self.master.option_readfile(optpath)
        # fixme having some trouble with the namespaces of the options database

    def applyOptions(self):
        logging.debug("applyOptions invocation")
        plt.style.use(self.mplparams["styles"][self.opts['mpl_style_idx']])
        for s in self.mplparams["styles"]:
            if self.opts["mpl_style_idx"] == s:
                self.mplparams["style_default"] = self.mplparams["styles"].index[s]

    def createPlot(self):
        logging.debug("createPlot invocation")
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.line, = self.axes.plot(self.x, self.y)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.mplframe)
        self.canvas.show()
        # add the mpl toolbar to the toolbar
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.mplframe)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def scaleFigAlpha(self, value):
        logging.debug("scaleFigAlpha called with alpha = %s" % value)
        self.figure.set_alpha(value)

    def createWidgets(self):
        logging.debug("createWidgets invocation")
        # todo add a menu region
        # a tk.DrawingArea containing the appropriate toolbars
        logging.debug("createWidgets building Matplotlib components for Tkinter integration")
        self.mplframe = ttk.Frame(class_="matplotstylist", name="mplframe")
        self.createPlot()
        self.mplframe.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # The following contains the right hand style configuration area
        self.styleframe = ttk.Frame(class_="matplotstylist", name="styleframe")
        self.styleframe.pack(side=tk.RIGHT, anchor=tk.NE, fill=tk.X, expand=1, ipadx=2, ipady=2, padx=2, pady=2)
        # todo evaluation if you should Add a listbox describing the potentially available styles, permits compositing
        # self.lbx_styles = tk.Listbox(self, activestyle='dotbox',
        #                              listvariable=tk.StringVar(value=" ".join(self.mplparams["styles"])
        #                                                        , name="mplparams.styles"),
        #                              selectmode=tk.SINGLE)
        # self.lbx_styles.activate(self.opts['mpl_style_idx'])
        # self.lbx_styles.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # Add an OptionsMenu describing the potentially available styles
        self.mpl_global_style = tk.StringVar()
        self.mpl_global_style.set(self.mplparams["styles"][self.opts['mpl_style_idx']])
        self.omu_styles = tk.OptionMenu(self.styleframe, self.mpl_global_style, *self.mplparams["styles"])
        self.omu_styles.pack(side=tk.TOP, fill=tk.X, expand=1)

        logging.debug("createWidgets creating and populating styleframe artist's notebook")
        self.artist_notebook = ArtistStyleBook(self.styleframe)

        # add one tab for each type of artist in the plot
        """ populate the artists notebook with the controls to set/get each and every setable property
        of the artists used by the figure and its children.  Each artist may be inspected interactively
        using matplotlib.artist.getp(object), which lists each property and their values.
        These same properties may be identified using "artists"
        """
        self.styletab_figure = FigureParametrics(self.artist_notebook, self.figure)
        self.styletab_axes = AxesParametrics(self.artist_notebook, self.axes)
        self.styletab_primitives = PrimitiveParametrics(self.artist_notebook, self.figure)
        self.artist_notebook.add(self.styletab_figure, sticky=tk.N + tk.E + tk.S + tk.W, text="Figure")
        self.artist_notebook.add(self.styletab_axes, sticky=tk.N + tk.E + tk.S + tk.W, text="Axes")
        self.artist_notebook.add(self.styletab_primitives, sticky=tk.N + tk.E + tk.S + tk.W, text="Primitives")

        # Lay it out
        self.artist_notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        logging.debug("createWidgets creating options for master window")
        self.master.wm_title(self._WINDOW_TITLE)
        self.master.wm_minsize(width=1024, height=640)
        self.master.wm_iconbitmap()
        self.pack()

    def bindWidgetVariables(self):
        self.mpl_global_style.trace("w", self.styleChange)

    def bindWidgetEvents(self):
        pass

    def __init__(self, master=None):
        ttk.Frame.__init__(self, master, class_='matplotstylist')
        plt.ion()
        self.loadOptions()
        self.applyOptions()
        StylistTheme.configure()

        self.x = arange(0.0, pi, 0.01)
        self.y = sin(2 * pi * self.x)

        self.createWidgets()
        self.bindWidgetVariables()
        self.bindWidgetEvents()
        # TODO: can we change any master level features such as title and author for this frame

    @staticmethod
    def launch(style=None):
        logging.debug("%s launch invoked with style %s" % (repr(StylistTkinter), repr(style)))
        global app
        ttk.Style().theme_use(style)
        app = StylistTkinter()
        app.mainloop()
        try:
            app.destroy()
        except tk.TclError as terr:
            if not terr.message == 'can\'t invoke "destroy" command:  application has been destroyed':
                logging.error(repr(terr))
            else:
                logging.debug(terr.message)


class FigureParametrics(ttk.Frame):
    """ Figure Parametrics contains the controls required to stylize the Figure and links
     to the PrimitiveParametrics of its patch

    the __doc__ of Figure shows us the following active params
    figsize=None,  # defaults to rc figure.figsize
    dpi=None,  # defaults to rc figure.dpi
    facecolor=None,  # defaults to rc figure.facecolor
    edgecolor=None,  # defaults to rc figure.edgecolor
    linewidth=0.0,  # the default linewidth of the frame
    frameon=None,  # whether or not to draw the figure frame
    subplotpars=None,  # default to rc
    tight_layout=None,  # default to rc figure.autolayout
    """

    def createWidgets(self):
        """ create an internal set of widgets with labels to represent the artists involved in the
        figure itself.  The figure's axes may be linked, as well as its patch
        """
        # column 1
        self.lbl_figsize = ttk.Label(self, text="figsize")
        self.lbl_dpi = ttk.Label(self, text="dpi")
        self.lbl_facecolor = ttk.Label(self, text="facecolor")
        self.lbl_edgecolor = ttk.Label(self, text="edgecolor")
        self.lbl_linewidth = ttk.Label(self, text="linewidth")
        self.lbl_frameon = ttk.Label(self, text="frameon")
        self.lbl_subplotpars = ttk.Label(self, text="subplotpars")
        self.lbl_tight_layout = ttk.Label(self, text="tight_layout")
        self.sep_parentchild = ttk.Separator(self, orient=tk.HORIZONTAL)

        # column 2
        self.ent_figsize = ttk.Entry(self)
        self.ent_dpi = ttk.Entry(self)
        self.ent_facecolor = ttk.Entry(self)
        self.ent_edgecolor = ttk.Entry(self)
        self.ent_linewidth = ttk.Entry(self)
        self.ent_frameon = ttk.Entry(self)
        self.ent_subplotpars = ttk.Entry(self)
        self.ent_tight_layout = ttk.Entry(self)

        # layout
        self.lbl_figsize.grid(column=0, row=0)
        self.lbl_dpi.grid(column=0, row=1)
        self.lbl_facecolor.grid(column=0, row=2)
        self.lbl_edgecolor.grid(column=0, row=3)
        self.lbl_linewidth.grid(column=0, row=4)
        self.lbl_frameon.grid(column=0, row=5)
        self.lbl_subplotpars.grid(column=0, row=6)
        self.lbl_tight_layout.grid(column=0, row=7)
        self.sep_parentchild.grid(column=0, row=8, columnspan=2, sticky=tk.E + tk.W)

        self.ent_figsize.grid(column=1, row=0)
        self.ent_dpi.grid(column=1, row=1)
        self.ent_facecolor.grid(column=1, row=2)
        self.ent_edgecolor.grid(column=1, row=3)
        self.ent_linewidth.grid(column=1, row=4)
        self.ent_frameon.grid(column=1, row=5)
        self.ent_subplotpars.grid(column=1, row=6)
        self.ent_tight_layout.grid(column=1, row=7)

        self.btn_patch = ttk.Button(self, text="View Figure Patch")
        self.btn_patch.grid(column=0, columnspan=2, row=9)

    def bindWidgetEvents(self):
        """
        TODO: bind the widgets to their event handlers
        TODO: set up a "return to default" state so that the user can freely fuck this up without breaking himself
        """
        pass

    def __init__(self, parent, figure):
        ttk.Frame.__init__(self, parent)
        self.figure = figure
        self.createWidgets()
        self.bindWidgetEvents()


class AxesParametrics(ttk.Frame):
    """ from _AxesBase.__init__
    ================   =========================================
    Keyword            Description
    ================   =========================================
    *adjustable*       [ 'box' | 'datalim' | 'box-forced']
    *alpha*            float: the alpha transparency (can be None)
    *anchor*           [ 'C', 'SW', 'S', 'SE', 'E', 'NE', 'N',
                       'NW', 'W' ]
    *aspect*           [ 'auto' | 'equal' | aspect_ratio ]
    *autoscale_on*     [ *True* | *False* ] whether or not to
                     autoscale the *viewlim*
    *axis_bgcolor*     any matplotlib color, see
                     :func:`~matplotlib.pyplot.colors`
    *axisbelow*        draw the grids and ticks below the other
                     artists
    *cursor_props*     a (*float*, *color*) tuple
    *figure*           a :class:`~matplotlib.figure.Figure`
                     instance
    *frame_on*         a boolean - draw the axes frame
    *label*            the axes label
    *navigate*         [ *True* | *False* ]
    *navigate_mode*    [ 'PAN' | 'ZOOM' | None ] the navigation
                     toolbar button status
    *position*         [left, bottom, width, height] in
                     class:`~matplotlib.figure.Figure` coords
    *sharex*           an class:`~matplotlib.axes.Axes` instance
                     to share the x-axis with
    *sharey*           an class:`~matplotlib.axes.Axes` instance
                     to share the y-axis with
    *title*            the title string
    *visible*          [ *True* | *False* ] whether the axes is
                     visible
    *xlabel*           the xlabel
    *xlim*             (*xmin*, *xmax*) view limits
    *xscale*           [%(scale)s]
    *xticklabels*      sequence of strings
    *xticks*           sequence of floats
    *ylabel*           the ylabel strings
    *ylim*             (*ymin*, *ymax*) view limits
    *yscale*           [%(scale)s]
    *yticklabels*      sequence of strings
    *yticks*           sequence of floats
    ================   =========================================
    """
    props = {}
    mAxes = None

    def ask_color_axis_bgcolor(self, *args, **kwargs):
        logging.debug("clicked axis_bgcolor button")
        result = tkColorChooser.askcolor(parent=self.master, initialcolor=None, title="axis_bgclor")
        ttk.Style().configure('axis_bgcolor.TButton', background=result[1])
        logging.debug("setting axis_bgcolor to chose color %s" % (repr(result)))
        plt.colors()
        self.mAxes.set_axis_bgcolor(result[1])

    def createWidgets(self):
        s = ttk.Style()

        self.lbl_adjustable = ttk.Label(self, text="adjustable")
        values = ('box', 'datalim', 'box-forced')
        self.props['adjustable'] = tk.StringVar()
        self.omu_adjustable = ttk.OptionMenu(self, self.props['adjustable'], values[0], *(values))
        del values
        self.lbl_adjustable.grid(column=0, row=0)
        self.omu_adjustable.grid(column=1, row=0)

        self.lbl_alpha = ttk.Label(self, text="alpha")
        self.props['alpha'] = tk.DoubleVar()
        self.scl_alpha = ttk.Scale(self, variable=self.props['alpha'], from_=0.0, to=1.0, orient=tk.HORIZONTAL)
        self.lbl_alpha.grid(column=0, row=1)
        self.scl_alpha.grid(column=1, row=1)

        self.lbl_anchor = ttk.Label(self, text="anchor")
        values = ('C', 'SW', 'S', 'SE', 'E', 'NE', 'N', 'NW', 'W')
        self.props['anchor'] = tk.StringVar()
        self.omu_anchor = ttk.OptionMenu(self, self.props['anchor'], values[0], *(values))
        del values
        self.lbl_anchor.grid(column=0, row=2)
        self.omu_anchor.grid(column=1, row=2)

        self.lbl_aspect = ttk.Label(self, text="aspect")
        values = ('auto', 'equal', 'aspect_ratio')
        self.props['aspect'] = tk.StringVar()
        self.omu_aspect = ttk.OptionMenu(self, self.props['aspect'], values[0], *(values))
        del values
        self.lbl_aspect.grid(column=0, row=3)
        self.omu_aspect.grid(column=1, row=3)

        self.lbl_autoscale_on = ttk.Label(self, text="autoscale_on")
        self.props['autoscale_on'] = tk.IntVar()
        self.chk_autoscale_on = ttk.Checkbutton(self, variable=self.props['autoscale_on'], text="Autoscale viewlim")
        self.lbl_autoscale_on.grid(column=0, row=4)
        self.chk_autoscale_on.grid(column=1, row=4)

        self.lbl_axis_bgcolor = ttk.Label(self, text="axis_bgcolor")
        self.props['axis_bgcolor'] = tk.StringVar()
        s.configure('axis_bgcolor.TButton', background="black")
        self.clr_axis_bgcolor = ttk.Button(self, style='axis_bgcolor.TButton', width=42,
                                           command=self.ask_color_axis_bgcolor)
        self.lbl_axis_bgcolor.grid(column=0, row=5)
        self.clr_axis_bgcolor.grid(column=1, row=5)

        self.lbl_axisbelow = ttk.Label(self, text="axisbelow")
        self.props['axisbelow'] = tk.IntVar()
        self.chk_axisbelow = ttk.Checkbutton(self, variable=self.props['axisbelow'],
                                             text="Draw grids and ticks below others")
        self.lbl_axisbelow.grid(column=0, row=6)
        self.chk_axisbelow.grid(column=1, row=6)
        #
        # cursor_props

        self.lbl_frame_on = ttk.Label(self, text="frame_on")
        self.props['frame_on'] = tk.IntVar()
        self.chk_frame_on = ttk.Checkbutton(self, variable=self.props['frame_on'], text="Draw axes frame")
        self.lbl_frame_on.grid(column=0, row=7)
        self.chk_frame_on.grid(column=1, row=7)

        self.lbl_label = ttk.Label(self, text="label")
        self.props['label'] = tk.StringVar()
        self.ent_label = ttk.Entry(self, textvariable=self.props['label'])
        self.lbl_label.grid(column=0, row=8)
        self.ent_label.grid(column=1, row=8)

        self.lbl_navigate = ttk.Label(self, text="navigate")
        self.props['navigate'] = tk.IntVar()
        self.chk_navigate = ttk.Checkbutton(self, variable=self.props['navigate'], text="Navigation commands enabled")
        self.lbl_navigate.grid(column=0, row=9)
        self.chk_navigate.grid(column=1, row=9)

        self.lbl_navigate_mode = ttk.Label(self, text="navigate_mode")
        values = ('PAN', 'Zoom', None)
        self.props['navigate_mode'] = tk.StringVar()
        self.omu_navigate_mode = ttk.OptionMenu(self, self.props['navigate_mode'], values[0], *(values))
        del values
        self.lbl_navigate_mode.grid(column=0, row=10)
        self.omu_navigate_mode.grid(column=1, row=10)

        # position
        # todo add controls for left, bottom, width, height

        # sharex
        # todo add a selection list for the axes with which this may share
        #
        # sharey
        # todo add a selection list for the axes with which this may share

        self.lbl_title = ttk.Label(self, text="title")
        self.props['title'] = tk.StringVar()
        self.ent_title = ttk.Entry(self, textvariable=self.props['title'])
        self.lbl_title.grid(column=0, row=14)
        self.ent_title.grid(column=1, row=14)

        self.lbl_visible = ttk.Label(self, text="visible")
        self.props['visible'] = tk.IntVar()
        self.chk_visible = ttk.Checkbutton(self, variable=self.props['visible'], text="show axes")
        self.lbl_visible.grid(column=0, row=15)
        self.chk_visible.grid(column=1, row=15)

        self.lbl_xlabel = ttk.Label(self, text="xlabel")
        self.props['xlabel'] = tk.StringVar()
        self.ent_xlabel = ttk.Entry(self, textvariable=self.props['xlabel'])
        self.lbl_xlabel.grid(column=0, row=16)
        self.ent_xlabel.grid(column=1, row=16)

        # xlim
        # todo xlimits, to be set using (xmin, xmax) view limits, requires controls for this tuple

        self.lbl_xscale = ttk.Label(self, text="xscale")
        self.props['xscale'] = tk.DoubleVar()
        self.scl_xscale = ttk.Scale(self, variable=self.props['xscale'], from_=0, to=100, orient=tk.HORIZONTAL)
        self.lbl_xscale.grid(column=0, row=18)
        self.scl_xscale.grid(column=1, row=18)

        # xticklabels
        # todo: add a widget to handle a sequence of string

        # xticks
        # todo: add a widget to handle a sequence of floats

        self.lbl_ylabel = ttk.Label(self, text="ylabel")
        self.props['ylabel'] = tk.StringVar()
        self.ent_ylabel = ttk.Entry(self, textvariable=self.props['ylabel'])
        self.lbl_ylabel.grid(column=0, row=19)
        self.ent_ylabel.grid(column=1, row=19)

        # ylim
        # todo ylimits, to be set using (ymin, ymax) view limits, requires controls for this tuple

        self.lbl_yscale = ttk.Label(self, text="yscale")
        self.props['yscale'] = tk.DoubleVar()
        self.scl_yscale = ttk.Scale(self, variable=self.props['yscale'], from_=0, to=100, orient=tk.HORIZONTAL)
        self.lbl_yscale.grid(column=0, row=20)
        self.scl_yscale.grid(column=1, row=20)
        #
        # yticklabels
        # todo: add a widget to handle a sequence of strings

        # yticks
        # todo: add a widget to handle a sequence of floats

    def setAxes(self, pAxes):
        logging.debug("%s.setAxes invoked" % self.__class__)
        self.mAxes = pAxes
        for prop in self.props.keys():
            logging.debug("\tsetting prop %s to value %s" % (prop, repr(getp(self.mAxes, prop))))
            self.props[prop].set(getp(self.mAxes, prop))

    def __init__(self, parent, axes=None):
        ttk.Frame.__init__(self, parent)
        self.createWidgets()
        if not axes is None:
            self.setAxes(axes)


class PrimitiveParametrics(ttk.Frame):
    """
    """

    def __init__(self, parent, figure):
        ttk.Frame.__init__(self, parent)


class ArtistStyleBook(ttk.Notebook):
    """ represents the hierarchy of artists and offers options to edit styles for each
    """

    def __init__(self, master):
        ttk.Notebook.__init__(self, master)


class StylistTheme(object):
    """ Tkinter theming needs a lot of work
    """

    @staticmethod
    def configure():
        logging.debug("StylistTheme.configure() static method invocation")
        s = ttk.Style()
        logging.info(s)
        s.configure(".", font=('Helvetica', 8))  # root
        s.configure("mps.TButton", background="blue")
        s.configure("mps.TCheckbutton", background="blue")
        s.configure("mps.TCombobox", background="blue")
        s.configure("mps.TEntry", background="blue")
        s.configure("mps.TFrame", background="blue")
        s.configure("mps.TLabel", background="blue")
        s.configure("mps.TLabelFrame", background="blue")
        s.configure("mps.TMenubutton", background="blue")
        s.configure("mps.TNotebook", background="blue")
        s.configure("mps.TPanedwindow ", background="blue")
        s.configure("mps.Horizontal.TProgressbar", background="blue")
        s.configure("mps.Vertical.TProgressbar", background="blue")
        s.configure("mps.TRadiobutton", background="blue")
        s.configure("mps.Horizontal.TScale", background="blue")
        s.configure("mps.Vertical.TScale", background="blue")
        s.configure("mps.Horizontal.TScrollbar", background="blue")
        s.configure("mps.Vertical.TScrollbar", background="blue")
        s.configure("mps.TSeparator", background="blue")
        s.configure("mps.TSizegrip", background="blue")
        s.configure("Treeview", background="blue")


class ColorSelectButton(ttk.Button):
    """Ttk Button widget displaying the color represented by the StringVar instance associated with this widget
    and handling the click/choose behavior of the button and its relationship to the tkColorChooser

    The command indicated by the constructor will be executed only after the associated tkColorChooser is used to
    select the indicated color.
    """
    """ :type   :   tk.StringVar """
    _color_var = None
    """:type    :   str """
    _chooser_title = None
    _invocation = None
    _DEFAULT_COLOR = "#FFFFFF"
    _STYLE_NAME_TEMPLATE = '%s.ColorSelectButton.TButton'
    _style_name = None
    def __init__(self, master=None, *args, **kwargs):
        """ Construct a ColorSelectButton with parent master

        Standard Options

            class, compound, cursor, image, style, takefocus, text, textvariable, underline, width

        Widget-Specific Option
            anchor, background, font, foreground, justify, padding, relief, text, wraplength
            chooser_title  = The name of the color property, to be inserted as the title in the tkColorchooser dialog
            textvariable    = The StringVar() instance to be populated with the chosen color
        """
        self._color_var = kwargs.get('textvariable', tk.StringVar(value=self._DEFAULT_COLOR))
        if kwargs.get('textvariable') and not kwargs.get('showtext'):
            del kwargs['textvariable']

        if kwargs.get('showtext'):
            del kwargs['showtext']

        if kwargs.get('color'):
            self._color_var.set(kwargs.get('color'))
            del kwargs['color']

        self._chooser_title = kwargs.get('chooser_title', "")
        if 'chooser_title' in kwargs.keys():
            del kwargs['chooser_title']

        cmd = kwargs.get('command') # a temp reference to the command argument, used below to register the function
        kwargs['command'] = self._choose_color

        ttk.Button.__init__(self, master, *args, **kwargs)
        self._style_name = ColorSelectButton._STYLE_NAME_TEMPLATE % (self._name)
        self.configure(style=self._style_name)
        # register the passed in command, or generate the necessaries
        if cmd and not isinstance(cmd, basestring):
            # callback not registered yet, do it now
            #fixme use self.register, and also, use the subst function of register rather than this anti-idion
            self._invocation = self.register(cmd)
        self._color_var.trace("w", self._trace_color_var)
        self._stylize()

    def _choose_color(self):
        result = tkColorChooser.askcolor(parent=self.master, initialcolor=self._color_var.get(),
                                         title=self._chooser_title)
        """Invokes the command associated with the button."""
        if not result[1] is  None:
            self._color_var.set(result[1])
        return self.tk.call(self._invocation, "invoke", self)

    def _trace_color_var(self, *args, **kwargs):
        self._stylize()

    def _stylize(self):
        s = ttk.Style()
        s.configure(self._style_name, background=self._color_var.get())
        s.map(self._style_name,
              background=[
                  ('active', self._color_var.get()),
                  ('background', self._color_var.get()),
                  ('disabled', self._color_var.get()),
                  ('focus', self._color_var.get()),
                  ('invalid', self._color_var.get()),
                  ('pressed', self._color_var.get()),
                  ('readonly', self._color_var.get()),
                  ('selected', self._color_var.get())
              ],
              relief=[('pressed', 'groove'),
                        ('!pressed', 'flat')])

    @staticmethod
    def launch(style=None):
        logging.debug("%s launch invoked with style %s" % (repr(ColorSelectButton), repr(style)))
        global app
        ttk.Style().theme_use(style)
        global var_color
        var_color = tk.StringVar(value="#EDE45C")
        var_color.trace("w", test_write)
        global colorizer
        colorizer = ColorSelectButton(command=test_cmd, textvariable=var_color)
        colorizer.master.wm_title("ColorSelectButton")
        colorizer.master.wm_minsize(400, colorizer.master.winfo_width())
        colorizer.pack(side=tk.LEFT, fill=tk.Y, expand=1)

        slave = ColorSelectButton(master=colorizer.master, color='blue')
        slave.pack(side=tk.TOP, fill=tk.Y, expand=1)
        colorizer.mainloop()
        try:
            colorizer.destroy()
        except tk.TclError as terr:
            if not terr.message == 'can\'t invoke "destroy" command:  application has been destroyed':
                logging.error(repr(terr))
            else:
                logging.debug(terr.message)

var_color = None
colorizer = None

def test_write(*args, **kwargs):
    logging.debug(("calling external variable trace for the written variable "))

def test_cmd(*args, **kwargs):
    logging.debug("calling external function for button invocation")


def main():
    logging.info("Running main invocation for %s" % __file__)
    ColorSelectButton.launch(style='clam')  # ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
    # StylistTkinter.launch(style='clam')
    logging.info("Finished main invocation")
    exit()


if __name__ == "__main__":
    main()
