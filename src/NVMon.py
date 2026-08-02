import csv
import os
import subprocess
import sys
from io import StringIO
from queue import Empty, Queue
from threading import Event, Thread
from tkinter import Frame, Label, PhotoImage, Tk, font
import tkinter.messagebox as MSGBox


QUERY_FIELDS = (
    "index,name,utilization.gpu,temperature.gpu,memory.used,memory.total,"
    "fan.speed,power.draw,power.limit"
)


class NVMon(Tk):
    POLL_INTERVAL_SECONDS = 0.3
    UI_INTERVAL_MS = 100

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
        self.gpu_rows = {}
        self.data_queue = Queue()
        self.stop_event = Event()
        self.after_id = None

        self.geometry('+0+0')
        self.bind('<Button-1>', self.clickwin)
        self.bind('<B1-Motion>', self.dragwin)

        self.buildWidget()
        self.startMonitor()
        self.after_id = self.after(self.UI_INTERVAL_MS, self.processUpdates)

    def quitProgram(self):
        self.stop_event.set()
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None
        self.destroy()

    def monitor(self):
        cmd = [
            'nvidia-smi',
            '--query-gpu={}'.format(QUERY_FIELDS),
            '--format=csv,noheader,nounits',
        ]

        while not self.stop_event.is_set():
            try:
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding='utf-8',
                    check=True,
                )
                self.data_queue.put(self.parseOutput(result.stdout))
            except (OSError, subprocess.SubprocessError):
                # Keep the last valid values on screen and retry on the next poll.
                pass

            self.stop_event.wait(self.POLL_INTERVAL_SECONDS)

    @staticmethod
    def parseNumber(value):
        value = value.strip()
        if value in ('', 'N/A', '[N/A]'):
            return None
        try:
            return float(value)
        except ValueError:
            return None

    @classmethod
    def parseOutput(cls, output):
        gpu_list = []
        for values in csv.reader(StringIO(output)):
            if len(values) != 9:
                continue

            index = values[0].strip()
            try:
                index = int(index)
            except ValueError:
                continue

            gpu_list.append({
                'index': index,
                'name': values[1].strip(),
                'usage': cls.parseNumber(values[2]),
                'temp': cls.parseNumber(values[3]),
                'memory_used': cls.parseNumber(values[4]),
                'memory_total': cls.parseNumber(values[5]),
                'fan': cls.parseNumber(values[6]),
                'power_draw': cls.parseNumber(values[7]),
                'power_limit': cls.parseNumber(values[8]),
            })
        return gpu_list

    def startMonitor(self):
        self.monitor_thread = Thread(target=self.monitor, daemon=True)
        self.monitor_thread.start()

    def processUpdates(self):
        latest = None
        try:
            while True:
                latest = self.data_queue.get_nowait()
        except Empty:
            pass

        if latest is not None:
            self.updateGpuRows(latest)

        if not self.stop_event.is_set():
            self.after_id = self.after(self.UI_INTERVAL_MS, self.processUpdates)

    @staticmethod
    def formatValue(value, unit='', decimals=0):
        if value is None:
            return 'N/A'
        return ('{:.%df}{}' % decimals).format(value, unit)

    def updateGpuRows(self, gpu_list):
        active_indexes = {gpu['index'] for gpu in gpu_list}

        for index in list(self.gpu_rows):
            if index not in active_indexes:
                self.gpu_rows.pop(index)['container'].destroy()

        for row_number, gpu in enumerate(sorted(gpu_list, key=lambda item: item['index'])):
            index = gpu['index']
            if index not in self.gpu_rows:
                self.createGpuRow(index)

            row = self.gpu_rows[index]
            row['container'].grid(row=row_number, column=0, sticky='w')
            name = gpu['name'].replace('NVIDIA', '').replace('GeForce', '').strip()
            row['name']['text'] = 'GPU {} {}'.format(index, name)
            row['usage']['text'] = self.formatValue(gpu['usage'], '%')
            row['temp']['text'] = self.formatValue(gpu['temp'], '°C')

            used = gpu['memory_used']
            total = gpu['memory_total']
            if used is None or total in (None, 0):
                row['memory']['text'] = 'N/A'
            else:
                percent = int(used / total * 100)
                row['memory']['text'] = '{:.1f}G / {:.1f}G({}%)'.format(
                    used / 1024, total / 1024, percent
                )

            row['fan']['text'] = self.formatValue(gpu['fan'], '%')
            row['power']['text'] = '{} / {}'.format(
                self.formatValue(gpu['power_draw'], 'W', 2),
                self.formatValue(gpu['power_limit'], 'W', 2),
            )

        self.quit_frame.grid(row=0, column=1, sticky='n')

    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

    def buildWidget(self):
        self.images = {
            'gpu': PhotoImage(file=self.resource_path('icons/gpu.png')).subsample(6),
            'usage': PhotoImage(file=self.resource_path('icons/usage.png')).subsample(6),
            'temp': PhotoImage(file=self.resource_path('icons/thermo.png')).subsample(6),
            'memory': PhotoImage(file=self.resource_path('icons/vram.png')).subsample(6),
            'fan': PhotoImage(file=self.resource_path('icons/fan.png')).subsample(6),
            'power': PhotoImage(file=self.resource_path('icons/bolt.png')).subsample(6),
            'quit': PhotoImage(file=self.resource_path('icons/quit.png')).subsample(6),
        }

        self.rows_frame = Frame(self, background=self.bg_color)
        self.rows_frame.grid(row=0, column=0)

        self.quit_frame = Frame(self, borderwidth=1, background='red')
        self.quit_btn = Label(
            self.quit_frame,
            image=self.images['quit'],
            fg='red',
            bg=self.widget_bg_color,
            font=self.font,
        )
        self.quit_btn.bind('<Button-1>', lambda event: self.quitProgram())
        self.quit_btn.grid(row=0, column=0)
        self.quit_frame.grid(row=0, column=1, sticky='n')

    def createGpuRow(self, index):
        container = Frame(self.rows_frame, background=self.bg_color)
        row = {'container': container}
        specs = (
            ('name', 'gpu', 'GPU {} No GPU'.format(index)),
            ('usage', 'usage', '0%'),
            ('temp', 'temp', '0°C'),
            ('memory', 'memory', '0G / 0G(0%)'),
            ('fan', 'fan', '0%'),
            ('power', 'power', '0W / 0W'),
        )

        for column, (key, image_key, initial_text) in enumerate(specs):
            frame = Frame(container, borderwidth=1, background=self.frame_bg_color)
            label = Label(
                frame,
                image=self.images[image_key],
                text=initial_text,
                bg=self.bg_color,
                fg=self.font_color,
                font=self.font,
                compound='left',
            )
            label.grid(row=0, column=0)
            frame.grid(row=0, column=column, padx=1)
            row[key] = label

        self.gpu_rows[index] = row

    def dragwin(self, event):
        delta_x = self.winfo_pointerx() - self._offsetx
        delta_y = self.winfo_pointery() - self._offsety
        x = self._window_x + delta_x
        y = self._window_y + delta_y
        self.geometry('+{x}+{y}'.format(x=x, y=y))
        self._offsetx = self.winfo_pointerx()
        self._offsety = self.winfo_pointery()
        self._window_x = x
        self._window_y = y

    def clickwin(self, event):
        self._offsetx = self.winfo_pointerx()
        self._offsety = self.winfo_pointery()


def main():
    # Check NVIDIA-SMI is available
    try:
        subprocess.run(
            ['nvidia-smi'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        MSGBox.showerror(
            'Error!',
            'Cannot find NVIDIA-SMI.\nPlease install the NVIDIA driver!',
        )
        sys.exit(-1)

    nvMonitor = NVMon()
    nvMonitor.mainloop()


if __name__ == '__main__':
    main()
