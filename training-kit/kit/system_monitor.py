"""Computer use: what the processor, memory, graphics card, disks and network are doing while the kit works, written
into the logs, so the training and Dataset Preparation can be made faster later.

Every program of the kit that works for a long time starts it once (train.py, train_pictures.py, prepare_data.py,
video_frames.py):

    import system_monitor
    system_monitor.start(say)          # say: the program's own way of writing a line (it goes into the logs)

It then writes:
  1. at the start, "Computer:" lines describing the computer once: the processor (name, cores, threads, top speed),
     the memory, the graphics card (name, driver, memory, power limit, PCIe link), the CUDA and PyTorch versions,
     Windows and its power plan, every disk (SSD, hard disk or NVMe, its drive letters, size and free space);
  2. every 5 minutes (REPORT_EVERY), one "Computer use (last 5 minutes):" line with the averages and highest values
     of the samples taken every 15 seconds (SAMPLE_EVERY): processor use (average, and the busiest core, which shows
     work that runs on one core only), its speed and temperature, memory, the graphics card's use, memory,
     temperature, power, clock speeds, fan and anything slowing it down (heat, the power limit), each disk's read
     and write speed and how busy it was, and the download and upload speed; with the phase of the work ("Step 5
     of 7: training ...");
  3. at once, a "Computer use warning:" line (at most once every 10 minutes for each kind) when the graphics card is
     very hot (83 °C or more) or slowed by heat, the processor is very hot (90 °C or more), memory is nearly full
     (95%), or a disk has less than 20 GB free;
  4. every sample as one row of a spreadsheet file (CSV), "Picture Model Training computer use <date>.csv", in the
     "Picture Model Training logs" folder on the desktop (KIT_LOG_FOLDER, which the programs pass on), or in the kit's
     work folder when it is run by hand. It can be opened in Excel to see exactly when the computer was the limit.

Lines start with "Computer" so the programs write them into the logs and "Everything said" without saying them aloud
or putting them in the Status field.

Temperatures: the graphics card's comes from NVIDIA's own tool (nvidia-smi). Windows lets ordinary programs read only
the motherboard's "thermal zone" temperature, the area around the processor (Win32_PerfFormattedData_Counters_
ThermalZoneInformation), not each core's; it is written as "processor area". When Windows does not give it either,
the log says so once. On Linux the processor's own sensors are read (psutil).

Nothing here stops or slows the work: every reading that fails is left out, and the readings take well under a
second every 15 seconds. Only the Python standard library and psutil (in requirements.txt) are needed; nothing is
sent anywhere.
"""

import csv
import datetime
import os
import re
import shutil
import subprocess
import threading
import time

SAMPLE_EVERY = 15            # seconds between samples
REPORT_EVERY = 300           # seconds between "Computer use" lines in the log
TEMP_EVERY = 60              # seconds between readings of the processor-area temperature (it starts a program)
WARN_AGAIN = 600             # seconds before the same kind of warning is written again
GPU_HOT, CPU_HOT, MEMORY_FULL, DISK_LOW_GB = 83, 90, 95, 20
NO_WINDOW = 0x08000000 if os.name == "nt" else 0       # CREATE_NO_WINDOW: no console flashes up
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_NAME = "Picture Model Training"

# What nvidia-smi is asked every sample, and the names used for them here.
GPU_FIELDS = [("utilization.gpu", "gpu_pct"), ("utilization.memory", "gpu_mem_busy_pct"),
              ("memory.used", "vram_used_mb"), ("memory.total", "vram_total_mb"), ("temperature.gpu", "gpu_temp_c"),
              ("power.draw", "gpu_power_w"), ("power.limit", "gpu_power_limit_w"), ("clocks.sm", "gpu_clock_mhz"),
              ("clocks.mem", "gpu_mem_clock_mhz"), ("fan.speed", "gpu_fan_pct"),
              ("pcie.link.gen.current", "pcie_gen"), ("pcie.link.width.current", "pcie_width"),
              ("clocks_event_reasons.active", "gpu_slowdown")]
# The reasons a graphics card runs slower than it could (NVIDIA's bit mask): bit -> plain words.
SLOWDOWN = {0x1: "", 0x2: "the application asked for lower clocks", 0x4: "the power limit",
            0x8: "a hardware slowdown", 0x10: "another program's clock settings", 0x20: "heat (software)",
            0x40: "heat (hardware)", 0x80: "the power supply (hardware brake)", 0x100: "display clock settings"}
# The spreadsheet's columns, in order.
COLUMNS = ["time", "phase", "cpu_pct", "cpu_busiest_core_pct", "cpu_ghz", "cpu_temp_c", "ram_used_gb",
           "ram_total_gb", "this_program_ram_gb", "swap_used_gb"] + [name for _f, name in GPU_FIELDS] + [
           "disk_read_mbs", "disk_write_mbs", "disk_busiest", "disk_busiest_pct", "download_mbs", "upload_mbs"]

_monitor = None
PHASE_LINE = re.compile(r"^\s*((Step|Model|Video|Collection) \d+ of \d+:?.*)")


def nvidia_smi():
    """The path of NVIDIA's tool, or None."""
    found = shutil.which("nvidia-smi")
    if found:
        return found
    for path in (os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "NVIDIA Corporation", "NVSMI",
                              "nvidia-smi.exe"),
                 os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "nvidia-smi.exe")):
        if os.path.exists(path):
            return path
    return None


def run(command, timeout=20):
    """The output of a command (no window), or "" when it fails."""
    try:
        out = subprocess.run(command, capture_output=True, text=True, timeout=timeout, creationflags=NO_WINDOW,
                             encoding="utf-8", errors="replace")
        return out.stdout if out.returncode == 0 else ""
    except Exception:  # noqa: BLE001 - a reading that fails is left out
        return ""


def powershell(script, timeout=30):
    """The output of a short PowerShell script (Windows), or ""."""
    if os.name != "nt":
        return ""
    return run(["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", script],
               timeout)


def number(text):
    """A number from nvidia-smi's text ("[N/A]" and the like: None)."""
    text = (text or "").strip()
    try:
        return int(text, 16) if text.startswith("0x") else float(text)
    except ValueError:
        return None


def gpu_sample(tool):
    """{name: value} of the first graphics card now (empty when there is no tool or it fails). Older drivers call
    the slowdown field clocks_throttle_reasons.active; it is asked that way when the new name is refused."""
    if not tool:
        return {}
    for fields in (GPU_FIELDS, [(f.replace("clocks_event_reasons", "clocks_throttle_reasons"), n)
                                for f, n in GPU_FIELDS]):
        out = run([tool, "--query-gpu=" + ",".join(f for f, _n in fields), "--format=csv,noheader,nounits"], 10)
        if out.strip():
            values = [v.strip() for v in out.strip().splitlines()[0].split(",")]
            if len(values) == len(fields):
                return {name: number(v) for (_f, name), v in zip(fields, values)}
    return {}


def slowdown_words(mask):
    """What slows the graphics card down, in plain words ("" when nothing does)."""
    if not mask:
        return ""
    return ", ".join(words for bit, words in SLOWDOWN.items() if int(mask) & bit and words)


def cpu_temperature():
    """The processor's temperature in °C (Linux: its own sensor; Windows: the processor-area thermal zone), or
    None."""
    try:
        import psutil
        readings = getattr(psutil, "sensors_temperatures", lambda: {})() or {}
        for key in ("coretemp", "k10temp", "zenpower", "cpu_thermal", "acpitz"):
            if readings.get(key):
                return max(r.current for r in readings[key])
    except Exception:  # noqa: BLE001
        pass
    out = powershell("Get-CimInstance Win32_PerfFormattedData_Counters_ThermalZoneInformation | "
                     "ForEach-Object { $_.HighPrecisionTemperature }")
    values = [number(v) for v in out.split()]
    values = [v / 10 - 273.15 for v in values if v]                  # tenths of a kelvin
    values = [v for v in values if 5 < v < 125]
    return round(max(values), 1) if values else None


def disk_letters():
    """{"PhysicalDrive0": "C: D:"} on Windows (which drive letters are on each disk), else {}."""
    out = powershell("Get-Partition | Where-Object DriveLetter | ForEach-Object { \"$($_.DiskNumber) "
                     "$($_.DriveLetter)\" }")
    letters = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 2:
            key = f"PhysicalDrive{parts[0]}"
            letters[key] = (letters.get(key, "") + f" {parts[1]}:").strip()
    return letters


def describe_computer(tool):
    """The "Computer:" lines written once at the start (see the module docstring)."""
    import platform
    lines = []
    try:
        import psutil
        name = platform.processor()
        if os.name == "nt":
            name = powershell("(Get-CimInstance Win32_Processor | Select-Object -First 1).Name").strip() or name
        else:
            try:
                with open("/proc/cpuinfo", encoding="utf-8") as f:
                    name = next((l.split(":", 1)[1].strip() for l in f if l.startswith("model name")), name)
            except OSError:
                pass
        freq = psutil.cpu_freq()
        lines.append(f"Computer: processor {name or 'unknown'}, {psutil.cpu_count(logical=False)} cores, "
                     f"{psutil.cpu_count()} threads" + (f", up to {freq.max / 1000:.1f} GHz" if freq and freq.max
                                                       else "") + ".")
        memory = psutil.virtual_memory()
        lines.append(f"Computer: memory {memory.total / 1024 ** 3:.0f} GB, {memory.available / 1024 ** 3:.0f} GB "
                     "free at the start.")
    except Exception as e:  # noqa: BLE001
        lines.append(f"Computer: the processor and memory could not be read ({e}).")
    if tool:
        out = run([tool, "--query-gpu=name,driver_version,memory.total,power.limit,power.max_limit,"
                   "pcie.link.gen.max,pcie.link.width.max", "--format=csv,noheader,nounits"], 10)
        for line in out.strip().splitlines():
            v = [x.strip() for x in line.split(",")]
            if len(v) == 7:
                lines.append(f"Computer: graphics card {v[0]}, driver {v[1]}, {number(v[2]) / 1024:.0f} GB of memory, "
                             f"power limit {v[3]} W (at most {v[4]} W), PCIe generation {v[5]} with {v[6]} lanes.")
    else:
        lines.append("Computer: NVIDIA's tool (nvidia-smi) was not found, so the graphics card is not measured.")
    try:
        import torch
        if getattr(torch.version, "hip", None):      # AMD's PyTorch (ROCm): new, being tested
            line = f"Computer: PyTorch {torch.__version__}, AMD ROCm (HIP {torch.version.hip})"
            if torch.cuda.is_available():
                props = torch.cuda.get_device_properties(0)
                line += (f", graphics {props.name} ({(getattr(props, 'gcnArchName', '') or '').split(':')[0]}), "
                         f"{props.total_memory / 1024 ** 3:.0f} GB reported")
            lines.append(line + ".")
        else:
            lines.append(f"Computer: PyTorch {torch.__version__}, CUDA {torch.version.cuda}"
                         + (f", cuDNN {torch.backends.cudnn.version()}" if torch.backends.cudnn.is_available() else "")
                         + ".")
    except Exception:  # noqa: BLE001 - not every tool of the kit uses PyTorch
        pass
    lines.append(f"Computer: {platform.system()} {platform.release()} ({platform.version()}), Python "
                 f"{platform.python_version()}.")
    plan = run(["powercfg", "/getactivescheme"]) if os.name == "nt" else ""
    match = re.search(r"\((.+)\)", plan)
    if match:
        lines.append(f"Computer: Windows power plan: {match.group(1)}.")
    out = powershell("Get-PhysicalDisk | ForEach-Object { \"$($_.DeviceId)|$($_.FriendlyName)|$($_.MediaType)|"
                     "$($_.BusType)|$($_.Size)\" }")
    letters = disk_letters() if out else {}
    for line in out.splitlines():
        parts = line.split("|")
        if len(parts) == 5:
            size = number(parts[4])
            lines.append(f"Computer: disk {parts[0]} {parts[1].strip()}, {parts[2] or 'unknown kind'} on "
                         f"{parts[3]}" + (f", {size / 1000 ** 3:.0f} GB" if size else "")
                         + (f", drives {letters[f'PhysicalDrive{parts[0]}']}" if f"PhysicalDrive{parts[0]}" in letters
                            else "") + ".")
    try:
        import psutil
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
            except OSError:
                continue
            if usage.total > 5 * 1024 ** 3:
                lines.append(f"Computer: drive {part.mountpoint} ({part.fstype}): {usage.free / 1024 ** 3:.0f} GB free "
                             f"of {usage.total / 1024 ** 3:.0f} GB.")
    except Exception:  # noqa: BLE001
        pass
    lines.append(f"Computer: the kit is in {KIT}.")
    return lines


def log_folder():
    """Where the spreadsheet goes: the desktop logs folder the program passed on (KIT_LOG_FOLDER), else the kit's work
    folder."""
    folder = os.environ.get("KIT_LOG_FOLDER") or os.path.join(KIT, "work")
    try:
        os.makedirs(folder, exist_ok=True)
        return folder
    except OSError:
        return os.path.join(KIT, "work")


class Monitor:
    """Takes a sample every SAMPLE_EVERY seconds in a background thread and writes the lines and the spreadsheet
    (see the module docstring)."""

    def __init__(self, write, sample_every=SAMPLE_EVERY, report_every=REPORT_EVERY):
        """write(line): how a line reaches the logs (the program's say)."""
        self.write, self.sample_every, self.report_every = write, sample_every, report_every
        self.tool = nvidia_smi()
        self.phase = ""
        self.samples = []                       # since the last report
        self.warned = {}                        # kind -> when it was last written
        self.temperature, self.temperature_at, self.no_temperature_said = None, 0.0, False
        self.letters = {}
        self.stop_event = threading.Event()
        self.last_disks = self.last_net = None
        self.last_time = time.time()
        self.thread = None

    # -- one sample
    def sample(self):
        """One sample of everything (a dict with the COLUMNS); each reading that fails is left empty."""
        import psutil
        now = time.time()
        span = max(0.5, now - self.last_time)
        self.last_time = now
        row = {"time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "phase": self.phase}
        cores = psutil.cpu_percent(percpu=True)
        if cores:
            row["cpu_pct"] = round(sum(cores) / len(cores), 1)
            row["cpu_busiest_core_pct"] = round(max(cores), 1)
        freq = psutil.cpu_freq()
        if freq:
            row["cpu_ghz"] = round(freq.current / 1000, 2)
        if now - self.temperature_at >= TEMP_EVERY:
            self.temperature, self.temperature_at = cpu_temperature(), now
            if self.temperature is None and not self.no_temperature_said:
                self.no_temperature_said = True
                self.write("Computer: this computer does not give the processor's temperature to ordinary programs, so "
                           "it is not measured." + (" The graphics card's temperature is." if self.tool else ""))
        row["cpu_temp_c"] = self.temperature
        memory, swap = psutil.virtual_memory(), psutil.swap_memory()
        row.update(ram_used_gb=round((memory.total - memory.available) / 1024 ** 3, 1),
                   ram_total_gb=round(memory.total / 1024 ** 3, 1), swap_used_gb=round(swap.used / 1024 ** 3, 1))
        try:
            me = psutil.Process()
            row["this_program_ram_gb"] = round(sum(p.memory_info().rss for p in [me] + me.children(recursive=True))
                                               / 1024 ** 3, 1)
        except Exception:  # noqa: BLE001
            pass
        row.update(gpu_sample(self.tool))
        disks = psutil.disk_io_counters(perdisk=True) or {}
        if self.last_disks is not None:
            read = write = 0.0
            busiest, busiest_pct = "", 0.0
            for name, now_io in disks.items():
                before = self.last_disks.get(name)
                if before is None:
                    continue
                read += (now_io.read_bytes - before.read_bytes) / span
                write += (now_io.write_bytes - before.write_bytes) / span
                busy_ms = getattr(now_io, "busy_time", None)
                if busy_ms is not None and getattr(before, "busy_time", None) is not None:
                    busy = (now_io.busy_time - before.busy_time) / (span * 10)
                else:                                   # Windows: the time spent reading and writing
                    busy = ((now_io.read_time - before.read_time) + (now_io.write_time - before.write_time)) / (span * 10)
                if busy > busiest_pct:
                    busiest, busiest_pct = name, min(100.0, busy)
            row.update(disk_read_mbs=round(read / 1e6, 1), disk_write_mbs=round(write / 1e6, 1),
                       disk_busiest=self.disk_name(busiest), disk_busiest_pct=round(busiest_pct, 1))
        self.last_disks = disks
        net = psutil.net_io_counters()
        if self.last_net is not None and net is not None:
            row.update(download_mbs=round((net.bytes_recv - self.last_net.bytes_recv) / span / 1e6, 2),
                       upload_mbs=round((net.bytes_sent - self.last_net.bytes_sent) / span / 1e6, 2))
        self.last_net = net
        return row

    def disk_name(self, name):
        """A disk's name with its drive letters ("PhysicalDrive0 (C:)")."""
        return f"{name} ({self.letters[name]})" if name in self.letters else name

    # -- warnings, the report and the spreadsheet
    def warn(self, kind, text):
        """Write a warning, at most once every WARN_AGAIN seconds for each kind."""
        if time.time() - self.warned.get(kind, 0) >= WARN_AGAIN:
            self.warned[kind] = time.time()
            self.write(f"Computer use warning: {text}")

    def check(self, row):
        """Write a warning when something is too hot or too full (see the module docstring)."""
        temp, slow = row.get("gpu_temp_c"), slowdown_words(row.get("gpu_slowdown"))
        if temp and temp >= GPU_HOT:
            self.warn("gpu hot", f"the graphics card is at {temp:.0f} °C. Check that its fans are not blocked and the "
                      "room is not too warm.")
        if "heat" in slow:
            self.warn("gpu heat", f"the graphics card is slowing itself down because of {slow}.")
        if row.get("cpu_temp_c") and row["cpu_temp_c"] >= CPU_HOT:
            self.warn("cpu hot", f"the processor area is at {row['cpu_temp_c']:.0f} °C.")
        if row.get("ram_total_gb") and row.get("ram_used_gb") and \
                row["ram_used_gb"] / row["ram_total_gb"] * 100 >= MEMORY_FULL:
            self.warn("memory", f"memory is nearly full ({row['ram_used_gb']:.0f} of {row['ram_total_gb']:.0f} GB); "
                      "Windows then uses the disk instead, which is much slower. Close other programs.")
        try:
            free = shutil.disk_usage(KIT).free / 1024 ** 3
            if free < DISK_LOW_GB:
                self.warn("disk", f"only {free:.0f} GB is free on the kit's drive.")
        except OSError:
            pass

    def save(self, row):
        """Add the sample to today's spreadsheet."""
        try:
            path = os.path.join(log_folder(), f"{APP_NAME} computer use {datetime.date.today():%Y-%m-%d}.csv")
            new = not os.path.exists(path)
            with open(path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
                if new:
                    writer.writeheader()
                writer.writerow({k: ("" if row.get(k) is None else row.get(k)) for k in COLUMNS})
        except OSError:
            pass

    def report(self):
        """The "Computer use (last N minutes):" line from the samples since the last report."""
        samples, self.samples = self.samples, []
        if not samples:
            return
        minutes = max(1, round(len(samples) * self.sample_every / 60))

        def stat(key, digits=0):
            """(average, highest) of a reading over the samples, or None."""
            values = [s[key] for s in samples if isinstance(s.get(key), (int, float))]
            if not values:
                return None
            return round(sum(values) / len(values), digits), round(max(values), digits)
        parts = []
        cpu, core, ghz, ctemp = stat("cpu_pct"), stat("cpu_busiest_core_pct"), stat("cpu_ghz", 1), stat("cpu_temp_c")
        if cpu:
            parts.append(f"processor {cpu[0]:.0f}% busy on average (highest {cpu[1]:.0f}%)"
                         + (f", busiest core {core[0]:.0f}% on average" if core else "")
                         + (f", {ghz[0]:.1f} GHz" if ghz else "")
                         + (f", processor area {ctemp[0]:.0f} °C (highest {ctemp[1]:.0f} °C)" if ctemp else ""))
        ram, mine = stat("ram_used_gb", 1), stat("this_program_ram_gb", 1)
        if ram:
            parts.append(f"memory {ram[1]:.1f} of {samples[-1].get('ram_total_gb', 0):.0f} GB used at most"
                         + (f" ({mine[1]:.1f} GB by the kit)" if mine else "")
                         + (f", {samples[-1]['swap_used_gb']:.1f} GB on the disk instead"
                            if samples[-1].get("swap_used_gb") else ""))
        gpu = stat("gpu_pct")
        if gpu:
            vram, temp, power, clock = (stat("vram_used_mb"), stat("gpu_temp_c"), stat("gpu_power_w"),
                                        stat("gpu_clock_mhz"))
            mem_busy, fan = stat("gpu_mem_busy_pct"), stat("gpu_fan_pct")
            text = f"graphics card {gpu[0]:.0f}% busy on average (lowest moments show waiting)"
            if mem_busy:
                text += f", its memory {mem_busy[0]:.0f}% busy"
            if vram:
                text += f", {vram[1] / 1024:.1f} of {(samples[-1].get('vram_total_mb') or 0) / 1024:.0f} GB of its memory used"
            if temp:
                text += f", {temp[0]:.0f} °C (highest {temp[1]:.0f} °C)"
            if power:
                limit = samples[-1].get("gpu_power_limit_w")
                text += f", {power[0]:.0f} W on average" + (f" of {limit:.0f} W allowed" if limit else "")
            if clock:
                text += f", {clock[0]:.0f} MHz"
            if fan:
                text += f", fan {fan[0]:.0f}%"
            if samples[-1].get("pcie_gen"):
                text += f", PCIe {samples[-1]['pcie_gen']:.0f} x{samples[-1].get('pcie_width') or 0:.0f}"
            slow = sorted({w for s in samples for w in slowdown_words(s.get("gpu_slowdown")).split(", ") if w})
            if slow:
                text += "; slowed at times by " + " and ".join(slow)
            parts.append(text)
        read, write = stat("disk_read_mbs", 1), stat("disk_write_mbs", 1)
        if read:
            busy = [s for s in samples if s.get("disk_busiest")]
            busiest = max(busy, key=lambda s: s.get("disk_busiest_pct") or 0) if busy else None
            parts.append(f"disks reading {read[0]:.1f} MB/s on average (highest {read[1]:.1f}), writing "
                         f"{write[0]:.1f} MB/s (highest {write[1]:.1f})"
                         + (f", busiest {busiest['disk_busiest']} at {busiest['disk_busiest_pct']:.0f}% busy"
                            if busiest and (busiest.get("disk_busiest_pct") or 0) >= 1 else ""))
        down, up = stat("download_mbs", 2), stat("upload_mbs", 2)
        if down and (down[1] >= 0.05 or (up and up[1] >= 0.05)):
            parts.append(f"downloading {down[0]:.1f} MB/s on average (highest {down[1]:.1f})"
                         + (f", uploading {up[0]:.1f} MB/s" if up and up[0] >= 0.05 else ""))
        phase = samples[-1].get("phase")
        span = "minute" if minutes == 1 else f"{minutes} minutes"
        self.write(f"Computer use (last {span}{', ' + phase.rstrip('.') if phase else ''}): " + "; ".join(parts) + ".")

    # -- the thread
    def loop(self):
        """Sample, warn, save, and report every report_every seconds, until stopped."""
        last_report = time.time()
        while not self.stop_event.wait(self.sample_every):
            try:
                row = self.sample()
                self.samples.append(row)
                self.check(row)
                self.save(row)
                if time.time() - last_report >= self.report_every:
                    last_report = time.time()
                    self.report()
            except Exception as e:  # noqa: BLE001 - the monitor never stops the work
                self.warn("monitor", f"a reading failed ({e}); the work carries on.")

    def begin(self):
        """Describe the computer, take the first readings (the speeds need two) and start the thread."""
        for line in describe_computer(self.tool):
            self.write(line)
        self.letters = disk_letters()
        try:
            import psutil
            psutil.cpu_percent(percpu=True)             # the first call only starts the count
            self.last_disks, self.last_net = psutil.disk_io_counters(perdisk=True) or {}, psutil.net_io_counters()
        except Exception:  # noqa: BLE001
            self.write("Computer: psutil is missing, so the processor, memory and disks are not measured.")
            return
        self.last_time = time.time()
        self.thread = threading.Thread(target=self.loop, name="computer use", daemon=True)
        self.thread.start()

    def end(self):
        """Stop the thread and write what was measured since the last report."""
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=30)
        try:
            self.report()
        except Exception:  # noqa: BLE001
            pass


def start(write, sample_every=SAMPLE_EVERY, report_every=REPORT_EVERY):
    """Start measuring for this program (once; later calls return the same monitor). Never raises."""
    global _monitor
    if _monitor is None:
        try:
            _monitor = Monitor(write, sample_every, report_every)
            _monitor.begin()
            import atexit
            atexit.register(_monitor.end)
        except Exception as e:  # noqa: BLE001
            write(f"Computer: the computer cannot be measured ({e}); the work carries on.")
    return _monitor


def note(line):
    """Remember the phase of the work from a line the program said ("Step 5 of 7: training ...")."""
    match = PHASE_LINE.match(line or "")
    if match and _monitor is not None:
        _monitor.phase = match.group(1).strip()[:120]


class Timer:
    """Where the time goes in a loop (the training): add(kind, seconds) for each part; line(count, what) says the
    shares since the last line, e.g. "preparing pictures (processor) 9%, graphics card work 88%, saving 3%"."""

    def __init__(self):
        """Nothing counted yet."""
        self.parts, self.started = {}, time.time()

    def add(self, kind, seconds):
        """Count seconds spent on kind."""
        self.parts[kind] = self.parts.get(kind, 0.0) + seconds

    def line(self, count, what="pictures"):
        """The shares of the time since the last line (and start again), with the time for each of count items."""
        total = time.time() - self.started
        parts, self.parts, self.started = self.parts, {}, time.time()
        if total <= 0:
            return ""
        shares = [f"{kind} {seconds * 100 / total:.0f}%" for kind, seconds in parts.items()]
        other = total - sum(parts.values())
        if other > total * 0.02:
            shares.append(f"other {other * 100 / total:.0f}%")
        return (f"Computer use (the last {count} {what}): {total / max(1, count):.2f} seconds each; "
                + ", ".join(shares) + ".")
