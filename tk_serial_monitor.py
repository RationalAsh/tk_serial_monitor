from rx.subjects import Subject
from rx.concurrency import TkinterScheduler
from rx import Observable
import tkinter as Tk
from tkinter import ttk, N, E, W, S, filedialog
import serial
from serial.tools import list_ports
import time

class main_app(Tk.Frame):
    """
    The main application class of the serial monitor. Inherits from the 
    Tk.Frame object. 
    """
    def __init__(self, parent, *args, **kwargs):
        #Call the frame's init function
        Tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        #Setup the scheduler
        self.scheduler = TkinterScheduler(parent)
        #Setup some observables
        self.rx_event_observer = Subject()
        self.time_observer = Observable.interval(1000).observe_on(self.scheduler)

        #Build the GUI here
        #Scrollbar for the text widget
        self.serial_stream_display_sb = ttk.Scrollbar(self)
        self.serial_stream_display_sb.grid(row=0, column=7)
        #Text widget to display the serial stream
        self.serial_stream_display = Tk.Text(self,
                                        yscrollcommand=self.serial_stream_display_sb.set)
        self.serial_stream_display_sb.config(command=self.serial_stream_display.yview)
        self.serial_stream_display.grid(row=0, column=0, columnspan=7, 
                                    sticky=(N, E, W, S), padx=5, pady=5)
        
        #Checkboxes for adding newlines (\n) , carriage returns (\r) and for
        #Autoscrolling the text widget as new data comes in
        self.NL_stat = Tk.StringVar()
        self.CR_stat = Tk.StringVar()
        self.AS_stat = Tk.StringVar()
        self.NL_chkbox = ttk.Checkbutton(self, text="NL", onvalue="\n", 
                                    offvalue="", variable=self.NL_stat)
        self.CR_chkbox = ttk.Checkbutton(self, text="CR", onvalue="\r",
                                    offvalue="", variable=self.CR_stat)
        self.AS_chkbox = ttk.Checkbutton(self, text="Autoscroll", onvalue="Y",
                                    offvalue="N", variable=self.AS_stat)
        self.NL_chkbox.grid(row=3, column=5, padx=5, pady=5, sticky=(N, E, W, S))
        self.CR_chkbox.grid(row=3, column=6, padx=5, pady=5, sticky=(N, E, W, S))
        self.AS_chkbox.grid(row=1, column=0, padx=5, pady=5, sticky=(N, E, W, S))

        #Buttons for clearing screen and saving data
        self.save_button = ttk.Button(self, text="Save")
        self.save_button.bind("<ButtonRelease-1>", lambda ev: self.rx_event_observer.on_next(ev))
        self.clear_button = ttk.Button(self, text="Clear")
        self.clear_button.bind("<ButtonRelease-1>", lambda ev: self.rx_event_observer.on_next(ev))
        self.save_button.grid(row=1, column=5, padx=5, pady=5, sticky=(N, E, W, S))
        self.clear_button.grid(row=1, column=6, padx=5, pady=5, sticky=(N, E, W, S))

        #Combobox for selecting serial port settings
        self.serial_port_name = Tk.StringVar()
        self.serial_baud_value = Tk.StringVar()
        self.serial_port_label = ttk.Label(self, text="Select Serial Port:")
        self.serial_baud_label = ttk.Label(self, text="Baud Rate:")
        self.serial_port_combobox = ttk.Combobox(self, textvariable=self.serial_port_name, width=20)
        self.serial_port_combobox.bind("<<ComboboxSelected>>", lambda ev: self.rx_event_observer.on_next(ev))
        self.serial_baud_combobox = ttk.Combobox(self, textvariable=self.serial_baud_value, width=20)
        self.serial_port_label.grid(row=1, column=1, padx=5, pady=5, sticky=(E,N,S))
        self.serial_port_combobox.grid(row=1, column=2, padx=5, pady=5, sticky=(N, E, W, S))
        self.serial_baud_label.grid(row=1, column=3, padx=5, pady=5, sticky=(N, S, E))
        self.serial_baud_combobox.grid(row=1, column=4, padx=5, pady=5, sticky=(N, E, W, S))

        #Entry for sending data over serial port
        self.serial_send_text = Tk.StringVar()
        self.serial_send_entry = ttk.Entry(self, textvariable=self.serial_send_text)
        self.serial_send_entry.grid(row=3, column=0, columnspan=5, padx=5, pady=5, sticky=(N, E, W, S))
        self.serial_send_entry.bind("<Return>", lambda ev: self.rx_event_observer.on_next(ev))

    def update_comports(self, val):
        """
        Updates the list of detected COM Ports in the combobox
        """
        available_ports = [p.device for p in list_ports.comports()]
        self.serial_port_combobox['values'] = available_ports
        #print("Available ports: {}".format(available_ports))

    def save_stream_as_file(self):
        """
        Saves whatever's in the stream as a file
        """
        filetypelist = [("Text file", '.txt'), ("Comma Separated Values", '.csv')]
        default_filename = time.strftime('LOG_%Y_%m_%d_%H_%M_%S')
        f = filedialog.asksaveasfile(title="Save data as file", mode='w', defaultextension=".txt",
                                     parent=self, filetypes=filetypelist, initialfile=default_filename)
        if f is None:
            return
        text2save = str(serial_stream_display.get(1.0, Tk.END))
        f.write(text2save)
        f.close()


if __name__=="__main__":
    #Create the main application
    root = Tk.Tk()
    root.title("Serial Port Monitor")
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    app_frame = main_app(root, width=500, height=500)
    app_frame.grid(row=0, column=0, sticky=(N, E, W, S))
    app_frame.rowconfigure(0, weight=1)
    app_frame.columnconfigure(0, weight=1)

    #Setup the application logic using RxPy
    app_frame.rx_event_observer.subscribe_on(scheduler=app_frame.scheduler)\
             .subscribe(lambda ev: print("{} {}".format(ev.type, ev.widget)))
    #Update the combobox with new serial ports
    app_frame.time_observer.subscribe(app_frame.update_comports)
    #Clear screen if clear is pressed
    app_frame.rx_event_observer.filter(lambda ev: int(ev.type)==5)\
                               .filter(lambda ev: ev.widget['text'].lower() == 'clear')\
                               .subscribe(lambda ev: app_frame.serial_stream_display.delete('1.0', Tk.END))
    #Open dialog to save file if the save button is pressed
    app_frame.rx_event_observer.filter(lambda ev: int(ev.type)==5)\
                               .filter(lambda ev: ev.widget['text'].lower() == 'save')\
                               .subscribe(lambda ev: app_frame.save_stream_as_file())

    root.mainloop()