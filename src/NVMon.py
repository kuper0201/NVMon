from tkinter import Tk, Frame, Label, font, PhotoImage
from threading import Thread
import tkinter.messagebox as MSGBox
import subprocess
import sys

class NVMon(Tk):
    def __init__(self, master=None):
        Tk.__init__(self, master)
        self.overrideredirect(True)
        
        # Color Palette
        self.bg_color = '#252526'
        self.widget_bg_color = '#3e3e42'
        self.frame_bg_color = '#33FF00'
        self.font_color = '#FFFFFF'
        
        self.font = font.Font(size=10)
        self.config(bg=self.bg_color)
        self.wm_attributes("-topmost", 1)
        self._offsetx = 0
        self._offsety = 0
        self._window_x = 0
        self._window_y = 0
        self._window_w = 700
        self._window_h = 25
        self.geometry('{w}x{h}+{x}+{y}'.format(w=self._window_w,h=self._window_h,x=self._window_x,y=self._window_y))
        self.geometry('')
        self.bind('<Button-1>', self.clickwin)
        self.bind('<B1-Motion>', self.dragwin)

        self.buildWidget()
        self.startMonitor()

    def quitProgram(self):
        self.destroy()
        self.quit()
        sys.exit()
    
    def monitor(self):
        cmd = "nvidia-smi --query-gpu=name,utilization.gpu,temperature.gpu,memory.used,memory.total,fan.speed,power.draw,power.limit --format=csv,noheader,nounits -lms 300"
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, encoding='utf-8')
            
        while True:
            output = result.stdout.readline()
            if output == '' and result.poll() is not None:
                break
            if output:
                self.updateData(*output.strip().split(','))
            
    def startMonitor(self):
        Thread(target=self.monitor, daemon=True).start()

    def updateData(self, name, usage, temp, memoryUsed, memoryTotal, fan, powerDraw, powerLimit):
        self.name_label['text'] = name
        self.usage_data['text'] = '{}%'.format(usage)
        self.temp_data['text'] = '{}°C'.format(temp)
        self.mem_data['text'] = '{:.1f}G / {:.1f}G({}%)'.format((int(memoryUsed) / 1024), int(memoryTotal) / 1024, int((int(memoryUsed) / int(memoryTotal)) * 100))
        self.fan_data['text'] = '{}%'.format(fan)
        self.power_data['text'] = '{}W / {}W'.format(powerDraw, powerLimit)
        self.update()

    def buildWidget(self):
        # Load Image
        global usageImg, thermoImg, vramImg, fanImg, powerImg
        usageImg = PhotoImage(file='icons/usage.png').subsample(7)
        thermoImg = PhotoImage(file='icons/thermo.png').subsample(7)
        fanImg = PhotoImage(file='icons/fan.png').subsample(7)
        vramImg = PhotoImage(file='icons/vram.png').subsample(7)
        powerImg = PhotoImage(file='icons/bolt.png').subsample(7)

        # Name Monitor
        name_frame = Frame(self, borderwidth=1, background=self.frame_bg_color)
        self.name_label = Label(name_frame, text='No GPU', bg=self.bg_color, fg=self.font_color, font=self.font)
        self.name_label.grid(row=0, column=0)
        name_frame.grid(row=0, column=0, padx=1)

        # Usage Monitor
        usage_frame = Frame(self, borderwidth=1, background=self.frame_bg_color)
        usage_label = Label(usage_frame, image=usageImg, text='Usg.', bg=self.bg_color, fg=self.font_color, font=self.font)
        usage_label.grid(row=0, column=0)
        
        self.usage_data = Label(usage_frame, text='0%', bg=self.bg_color, fg=self.font_color, font=self.font)
        self.usage_data.grid(row=0, column=1)
        usage_frame.grid(row=0, column=1, padx=1)

        # Temp Monitor
        temp_frame = Frame(self, borderwidth=1, background=self.frame_bg_color)
        temp_label = Label(temp_frame, image=thermoImg, text='Tmp.', bg=self.bg_color, fg=self.font_color, font=self.font)
        temp_label.grid(row=0, column=0)

        self.temp_data = Label(temp_frame, text='0°C', bg=self.bg_color, fg=self.font_color, font=self.font)
        self.temp_data.grid(row=0, column=1)
        temp_frame.grid(row=0, column=2, padx=1)

        # Memory Monitor
        mem_frame = Frame(self, borderwidth=1, background=self.frame_bg_color)
        mem_label = Label(mem_frame, image=vramImg, text='VRAM.', bg=self.bg_color, fg=self.font_color, font=self.font)
        mem_label.grid(row=0, column=0)

        self.mem_data = Label(mem_frame, text='0%', bg=self.bg_color, fg=self.font_color, font=self.font)
        self.mem_data.grid(row=0, column=1)
        mem_frame.grid(row=0, column=3, padx=1)

        # Fan Monitor
        fan_frame = Frame(self, borderwidth=1, background=self.frame_bg_color)
        fan_label = Label(fan_frame, image=fanImg, text='FAN.', bg=self.bg_color, fg=self.font_color, font=self.font)
        fan_label.grid(row=0, column=0)

        self.fan_data = Label(fan_frame, text='0%', bg=self.bg_color, fg=self.font_color, font=self.font)
        self.fan_data.grid(row=0, column=1)
        fan_frame.grid(row=0, column=4, padx=1)

        # Power Monitor
        power_frame = Frame(self, borderwidth=1, background=self.frame_bg_color)
        power_label = Label(power_frame, image=powerImg, text='PWR.', bg=self.bg_color, fg=self.font_color, font=self.font)
        power_label.grid(row=0, column=0)

        self.power_data = Label(power_frame, text='0W / 0W', bg=self.bg_color, fg=self.font_color, font=self.font)
        self.power_data.grid(row=0, column=1)
        power_frame.grid(row=0, column=5, padx=1)

        # Quit Button
        quit_frame = Frame(self, borderwidth=1, background='red')
        self.quit_btn = Label(quit_frame, text="X", fg='red', width=2, bg=self.widget_bg_color, font=self.font)
        self.quit_btn.bind("<Button-1>", lambda e:self.quitProgram())
        self.quit_btn.grid(row=0, column=0)
        quit_frame.grid(row=0, column=6)

    def dragwin(self, event):
        delta_x = self.winfo_pointerx() - self._offsetx
        delta_y = self.winfo_pointery() - self._offsety
        x = self._window_x + delta_x
        y = self._window_y + delta_y
        self.geometry("+{x}+{y}".format(x=x, y=y))
        self._offsetx = self.winfo_pointerx()
        self._offsety = self.winfo_pointery()
        self._window_x = x
        self._window_y = y

    def clickwin(self, event):
        self._offsetx = self.winfo_pointerx()
        self._offsety = self.winfo_pointery()

def main():
    # Check NVIDIA-SMI is available
    # try:
    #     subprocess.run('nvidia-smi', stdout=subprocess.DEVNULL, check=True)
    # except:
    #     MSGBox.showerror("Error!", "Cannot found NVIDIA-SMI.\nPlease install NVIDIA driver!")
    #     sys.exit(-1)

    nvMonitor = NVMon()
    nvMonitor.mainloop()
    
if __name__ == "__main__":
    main()
