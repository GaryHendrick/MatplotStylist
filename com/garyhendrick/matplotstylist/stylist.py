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

import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk

themes = ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')

# app is being maintained in the global scope in order to maintain a reference
app = None

class ClassGlass(tk.Frame):
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
    #     fixme redraw the plot using the new theme
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

    def applyOptions(self):
        logging.debug("applyOptions invocation")
        plt.style.use(self.mplparams["styles"][self.opts['mpl_style_idx']])

    def createPlot(self):
        logging.debug("createPlot invocation")
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.line = self.axes.plot(self.x, self.y)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.mplframe)
        self.canvas.show()
        # add the mpl toolbar to the toolbar
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.mplframe)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def createWidgets(self):
        logging.debug("createWidgets invocation")

        # a tk.DrawingArea containing the appropriate toolbars
        logging.debug("createWidgets building Matplotlib components for Tkinter integration")
        self.mplframe = ttk.Frame()
        self.createPlot()
        self.mplframe.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)


        # Add a listbox describing the potentially available styles
        # self.lbx_styles = tk.Listbox(self, activestyle='dotbox',
        #                              listvariable=tk.StringVar(value=" ".join(self.mplparams["styles"])
        #                                                        , name="mplparams.styles"),
        #                              selectmode=tk.SINGLE)
        # self.lbx_styles.activate(self.opts['mpl_style_idx'])
        # self.lbx_styles.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # Add an OptionsMenu describing the potentially available styles
        self.mpl_global_style = tk.StringVar()
        self.mpl_global_style.set(self.mplparams["styles"][self.opts['mpl_style_idx']])
        self.omu_styles = tk.OptionMenu(self, self.mpl_global_style, *self.mplparams["styles"])
        self.omu_styles.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.mpl_global_style.trace("w", self.styleChange)

        # TODO set up a selector for all available styles using plt.style.available, mpl 3.2
        logging.debug("createWidgets creating options for master window")
        self.master.wm_title(self._WINDOW_TITLE)
        self.pack()


    def bindWidgetVariables(self):
        pass


    def bindWidgetEvents(self):
        pass


    def __init__(self, master=None):
        tk.Frame.__init__(self, master, class_="ClassGlass")
        plt.ion()
        self.loadOptions()
        self.applyOptions()

        self.x =arange(0.0, pi, 0.01)
        self.y = sin(2*pi*self.x)

        for s in self.mplparams["styles"]:
            if self.opts["mpl_style_idx"] == s:
                self.mplparams["style_default"] = self.mplparams["styles"].index[s]
        self.createWidgets()
        self.bindWidgetVariables()
        self.bindWidgetEvents()
    #     TODO: can we change any master level features such as title and author for this frame


    @staticmethod
    def launch(style=None):
        logging.debug("%s launch invoked with style %s" % (repr(ClassGlass), repr(style)))
        global app
        ttk.Style().theme_use(style)
        app = ClassGlass()
        app.mainloop()
        try :
            app.destroy()
        except tk.TclError as terr:
            if not terr.message == 'can\'t invoke "destroy" command:  application has been destroyed':
                logging.error(repr(terr))
            else:
                logging.debug(terr.message)

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
        self._btn_showfields.grid(column=2, row=0, rowspan=1)
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
    ClassGlass.launch(style='clam') # ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
    logging.info("Finished main invocation")
    exit()

if __name__== "__main__":
    main()