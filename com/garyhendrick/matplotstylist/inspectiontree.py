""" InspectionTree is being held onto in case there is any reason to use this code
"""
import Tkinter as tk
import logging
import ttk

__author__ = 'gary'


class InspectionTree(ttk.Frame):
    """ An InspectionTree is a compound widget used to depict the structure of a class
    """
    _btn_sort, _btn_showinheritance, _btn_showfields, _btn_expand, _btn_collapse = None, None, None, None, None
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
        self.grid(sticky=tk.N + tk.S + tk.E + tk.W)

    def createWidgets(self):
        """ Each widget is created here and the name is set in order to maintain appearances, see tkinter.pdf
        """
        self._btn_sort = ttk.Button(command=self.do_sort, text="sort", name="buttonSort")
        self._btn_showinheritance = ttk.Button(command=self.do_showinheritance, text="show inheritance",
                                               name="buttonShowInheritance")
        self._btn_showfields = ttk.Button(command=self.do_showfields, text="show fields", name="buttonShowFields")
        self._btn_expand = ttk.Button(command=self.do_expand, text="expand", name="buttonExpand")
        self._btn_collapse = ttk.Button(command=self.do_collapse, text="collapse", name="buttonCollapse")
        self._tre_view = ttk.Treeview(columns=('Name', 'Value'), name="treeView")

        # grid the widgets
        self._btn_sort.grid(column=0, row=0, rowspan=1)
        self._btn_showinheritance.grid(column=1, row=0, rowspan=1)
        self._btn_showfields.grid(column=1, row=0, rowspan=1)
        self._btn_expand.grid(column=3, row=0, rowspan=1)
        self._btn_collapse.grid(column=4, row=0, rowspan=1)
        self._tre_view.grid(column=0, columnspan=5, row=1, sticky=tk.N + tk.E + tk.S + tk.W)

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
        ttk.Frame.__init__(self, parent, class_='InspectionTree')  # the class_ option is recommended by ttk
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
        root = tk.Tk()
        root.wm_title("Inspector")
        root.protocol("WM_DELETE_WINDOW", root.destroy)
        root.mainloop()
        try:
            root.destroy()
        except tk.TclError as terr:
            if not terr.message == 'can\'t invoke "destroy" command:  application has been destroyed':
                logging.error(repr(terr))
            else:
                logging.debug(terr.message)