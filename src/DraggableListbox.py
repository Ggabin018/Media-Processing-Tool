import tkinter as tk

class DraggableListbox(tk.Listbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind('<B1-Motion>', self.__on_drag)
        self.bind('<ButtonRelease-1>', self.__on_drop)
        self.dragging_index = None

    def __on_drag(self, event):
        index = self.nearest(event.y)
        if self.dragging_index is None:
            self.dragging_index = index

        if index != self.dragging_index:
            # get moving elt 
            item = self.get(self.dragging_index)
            # del et reinsert elt to new pos
            self.delete(self.dragging_index)
            self.insert(index, item)
            self.selection_set(index)
            self.dragging_index = index

    def __on_drop(self, event):
        self.dragging_index = None

class WindowDragListBox:
    def __init__(self, l):
        self.root = tk.Tk()
        self.root.title("Liste Réorganisable avec Tkinter")

        self.listbox = DraggableListbox(self.root, height=6, selectmode=tk.SINGLE)
        self.listbox.pack(padx=20, pady=20)

        for item in l:
            self.listbox.insert(tk.END, item)

        btn = tk.Button(self.root, text="OK", command=self.__stop)
        btn.pack(pady=10)

    def change_list(self):
        self.root.mainloop()
        return self.listbox.get(0, tk.END)

    def __stop(self):
        self.root.quit()

if __name__ == "__main__":
    l = ["Ligne 1", "Ligne 2", "Ligne 3", "Ligne 4", "Ligne 5"]
    wdlb = WindowDragListBox(l)
    print(wdlb.change_list())