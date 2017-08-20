from pySerialMonitor import *

def main():
    #Create the main application
    root = Tk.Tk()
    root.title("Serial Port Monitor")
    #root.tk.call('wm', 'iconphoto', root._w, Tk.PhotoImage(file='if_port.png'))
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
    #If a serial port is selected in the Combobox, create serial object
    app_frame.rx_event_observer.filter(lambda ev: int(ev.type)==35)\
                               .map(lambda ev: app_frame.connect_serial(BAUD=int(app_frame.serial_baud_value.get())))\
                               .subscribe(lambda sobj: print("Connected to {} at {} baud".format(sobj.port, sobj.baudrate)) if(sobj) else print("Error connecting to port."))
    #If serial port is not None, then read anything coming in and print to text widget
    app_frame.serial_observer.filter(lambda ser: ser is not None)\
                             .map(lambda ser: ser.read(512).decode())\
                             .filter(lambda txt: len(txt)>0)\
                             .subscribe(app_frame.update_monitoring_window)
     #Send data to the Serial port when enter is pressed in the entry
    app_frame.rx_event_observer.observe_on(app_frame.pool_scheduler)\
              .filter(lambda ev: int(ev.type) == 2)\
              .filter(lambda ev: type(ev.widget) == ttk.Entry)\
              .filter(lambda ev: app_frame.SERIAL_DEVICE != None)\
              .map(lambda ev: app_frame.serial_send_text.get())\
              .filter(lambda txt: len(txt) > 0)\
              .subscribe(app_frame.send_serial)

    root.mainloop()
    try:
        app_frame.SERIAL_DEVICE.close()
    except:
        pass

if __name__ == '__main__':
    main()