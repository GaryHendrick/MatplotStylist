__author__ = 'gary'
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:\t%(message)s")

import matplotlib
matplotlib.use("TkAgg")

import ttk

import numpy as np
from numpy import arange, sin, pi

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import sys, os
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk

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
        plt.style.use(self.mpl_global_style.get()) # TODO can you set this up to use name1 ? Yes, tk.StringVar() contains _name

        #clean up the existing stuff, deleting all of the components within the canvas
        self.canvas.get_tk_widget().delete("all")
        for child in self.mplframe.winfo_children():
            child.destroy()
        self.figure.clear()
        self.axes.clear()
        del self.line,self.axes, self.figure

        # recretae the plot, the frame it resides in is already created and useful
        self.createPlot()

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
        self.styletab_axes = AxesParametrics(self.artist_notebook, self.figure)
        self.styletab_primitives = PrimitiveParametrics(self.artist_notebook,self.figure)
        self.artist_notebook.add(self.styletab_figure, sticky=tk.N + tk.E + tk.S + tk.W, text="Figure")
        self.artist_notebook.add(self.styletab_axes, sticky=tk.N + tk.E + tk.S + tk.W, text="Axes")
        self.artist_notebook.add(self.styletab_primitives, sticky=tk.N + tk.E + tk.S + tk.W, text="Lines")

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

        self.x =arange(0.0, pi, 0.01)
        self.y = sin(2*pi*self.x)

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
        try :
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
        #column 1
        self.lbl_figsize = ttk.Label(self, text="figsize")
        self.lbl_dpi = ttk.Label(self, text="dpi")
        self.lbl_facecolor = ttk.Label(self, text="facecolor")
        self.lbl_edgecolor = ttk.Label(self, text="edgecolor")
        self.lbl_linewidth = ttk.Label(self, text="linewidth")
        self.lbl_frameon = ttk.Label(self, text="frameon")
        self.lbl_subplotpars = ttk.Label(self, text="subplotpars")
        self.lbl_tight_layout = ttk.Label(self, text="tight_layout")
        self.sep_parentchild    = ttk.Separator(self, orient=tk.HORIZONTAL)

        #column 2
        self.ent_figsize = ttk.Entry(self)
        self.ent_dpi = ttk.Entry(self)
        self.ent_facecolor = ttk.Entry(self)
        self.ent_edgecolor = ttk.Entry(self)
        self.ent_linewidth = ttk.Entry(self)
        self.ent_frameon = ttk.Entry(self)
        self.ent_subplotpars = ttk.Entry(self)
        self.ent_tight_layout = ttk.Entry(self)

        #layout
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
    def __init__(self, parent, axes):
        ttk.Frame.__init__(self, parent)

class PrimitiveParametrics(ttk.Frame):
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
        s.configure(".", font=('Helvetica', 8)) # root
        s.configure("mps.TButton", background="blue")
        s.configure("mps.TCheckbutton",background="blue")
        s.configure("mps.TCombobox",background="blue")
        s.configure("mps.TEntry",background="blue")
        s.configure("mps.TFrame",background="blue")
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


class InspectionTree(ttk.Frame):
    """ An InspectionTree is a compound widget used to depict the structure of a class
    """
    _btn_sort, _btn_showinheritance, _btn_showfields,_btn_expand, _btn_collapse = None, None, None, None, None
    _tre_view = None
    subject = None

    def do_sort(self):
        logging.debug("calling do_sort")

    def do_showinheritance(self):
        logging.debug("calling do_showinheritance")

    def do_showfields(self):
        logging.debug("calling do_showfields")

    def do_expand(self):
        logging.debug("calling do_expand")

    def do_collapse(self):
        logging.debug("calling do_collapse")

    def createLayout(self):
        self.columnconfigure(0, minsize=32, pad=2)
        self.columnconfigure(1, minsize=32, pad=2)
        self.columnconfigure(2, minsize=32, pad=2)
        self.columnconfigure(3, minsize=32, pad=2)
        self.columnconfigure(4, minsize=32, pad=2)
        self.rowconfigure(0, minsize=32, pad=2)
        self.rowconfigure(1, minsize=32, pad=2)

        # permitting resizing will require the following sticky
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)

    def createWidgets(self):
        """ Each widget is created here and the name is set in order to maintain appearances, see tkinter.pdf
        """
        self._btn_sort = ttk.Button(command=self.do_sort, text="sort", name="buttonSort")
        self._btn_showinheritance = ttk.Button(command=self.do_showinheritance, text="show inheritance", name="buttonShowInheritance")
        self._btn_showfields = ttk.Button(command=self.do_showfields, text="show fields", name="buttonShowFields")
        self._btn_expand= ttk.Button(command=self.do_expand, text="expand", name="buttonExpand")
        self._btn_collapse = ttk.Button(command=self.do_collapse, text="collapse", name="buttonCollapse")
        self._tre_view = ttk.Treeview(columns=('Name', 'Value'), name="treeView")

        # grid the widgets
        self._btn_sort.grid(column=0,row=0, rowspan=1)
        self._btn_showinheritance.grid(column=1, row=0, rowspan=1)
        self._btn_showfields.grid(column=1, row=0, rowspan=1)
        self._btn_expand.grid(column=3, row=0, rowspan=1)
        self._btn_collapse.grid(column=4, row=0, rowspan=1)
        self._tre_view.grid(column=0, columnspan=5, row=1, sticky=tk.N+tk.E+tk.S+tk.W)

    def bindWidgetVariables(self):
        pass

    def bindWidgetEvents(self):
        pass

    def buildTree(self):
        """ build a tree using the subject
        :param subject: an object which will be inspected to build its tree
        """

        for s in self.subject:
            self._tre_view.insert('', 'end', s, text=s, values=("foo", s))

    def __init__(self, parent=None, subject=None):
        ttk.Frame.__init__(self, parent, class_='InspectionTree') # the class_ option is recommended by ttk
        self.subject = subject
        self.createLayout()
        self.createWidgets()
        self.buildTree()
        self.bindWidgetVariables()
        self.bindWidgetEvents()

    @staticmethod
    def launch(style=None):
        logging.debug("%s launch invoked with style %s" % (repr(InspectionTree), repr(style)))
        global app
        ttk.Style().theme_use(style)
        root = tk.Tk()
        root.wm_title("Inspector")
        root.withdraw()
        root.protocol("WM_DELETE_WINDOW", root.destroy)
        subject = np.arange(0.0, 11.0, 0.01)
        app = InspectionTree(parent=root,subject=subject)
        app.mainloop()
        try :
            app.destroy()
            root.destroy()
        except tk.TclError as terr:
            if not terr.message == 'can\'t invoke "destroy" command:  application has been destroyed':
                logging.error(repr(terr))
            else:
                logging.debug(terr.message)

def main():
    logging.info("Running main invocation for %s" % __file__)
    StylistTkinter.launch(style='clam') # ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
    logging.info("Finished main invocation")
    exit()

if __name__== "__main__":
    main()