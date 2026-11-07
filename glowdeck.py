#!/usr/bin/env python3
"""
Glowdeck - tray app for Tuya lights (LED strips and bulbs).

Sign in once with the Tuya Smart / Smart Life app (QR code), pick the lights you want, and control each one
from the tray window: colour, brightness, 6 favourites, and screen sync (whole screen, top edge or bottom
edge). Every light has its own mode, so one strip can follow the top of the screen, another the bottom and a
bulb the whole screen or a steady colour. Runs without the vendor apps and reconnects by itself.

    pythonw glowdeck.py            normal start (no console window)
    python  glowdeck.py --demo     preview the interface with three fake lights
    python  glowdeck.py --hidden   start in the tray without opening the window (used by autostart)

Everything the app stores lives in %APPDATA%\\Glowdeck (devices + keys, state, log). Settings -> Log off
forgets all of it. From source:  pip install -r requirements.txt
"""
import argparse
import colorsys
import json
import logging
import os
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import discover
import glowdeck_sync as L
import strip_config
import tuya_cloud

APP_NAME = "Glowdeck"
APP_VERSION = "2.1.1"
FROZEN = bool(getattr(sys, "frozen", False))                      # True inside the installed .exe
HERE = os.path.dirname(os.path.abspath(sys.executable if FROZEN else __file__))
RES_DIR = getattr(sys, "_MEIPASS", HERE)                          # ui.html, qrcode.js


def _data_dir():
    """Where settings, state and the log live (GLOWDECK_DATA_DIR overrides, for testing)."""
    base = os.environ.get("GLOWDECK_DATA_DIR")
    if not base:
        root = os.environ.get("APPDATA") if os.name == "nt" else os.path.join(os.path.expanduser("~"), ".config")
        base = os.path.join(root or HERE, APP_NAME)
    try:
        os.makedirs(base, exist_ok=True)
        return base
    except OSError:
        return HERE


DATA_DIR = _data_dir()
STATE_PATH = os.path.join(DATA_DIR, "state.json")
LOG_PATH = os.path.join(DATA_DIR, "glowdeck.log")
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")
PROFILE_DIR = os.path.join(DATA_DIR, ".window-profile")
UI_PATH = os.path.join(RES_DIR, "ui.html")
QR_JS_PATH = os.path.join(RES_DIR, "qrcode.js")
L.CONFIG_PATH = CONFIG_PATH


def migrate_legacy_files():
    """Earlier versions kept config.json / state.json next to the script - move them over once."""
    if FROZEN or os.path.abspath(HERE) == os.path.abspath(DATA_DIR):
        return
    for name in ("config.json", "state.json"):
        old, new = os.path.join(HERE, name), os.path.join(DATA_DIR, name)
        if os.path.exists(old) and not os.path.exists(new):
            try:
                shutil.copy2(old, new)
            except OSError:
                pass


LOCK_PORT = 47651          # held while the app runs, so a second copy refuses to start
UI_PORTS = range(8765, 8785)
MODES = ("colour", "white", "screen", "top", "bottom")
log = logging.getLogger("glowdeck")

DEFAULT_DEV_STATE = {"power": True, "mode": "colour", "h": 0.75, "s": 1.0, "t": 0.5, "brightness": 0.8}
DEFAULT_FAVS = [[0.0, 1.0], [0.08, 1.0], [0.15, 1.0], [0.33, 1.0], [0.55, 1.0], [0.75, 1.0]]


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def clean_favourites(favs):
    out = []
    for f in (favs or [])[:6]:
        if isinstance(f, (list, tuple)) and len(f) == 2 and is_num(f[0]) and is_num(f[1]):
            out.append([clamp(float(f[0]), 0, 0.9999), clamp(float(f[1]), 0, 1)])
        else:
            out.append(None)
    out += [None] * (6 - len(out))
    return out


def clean_dev_state(saved, base=None):
    """A light's saved state, validated, on top of `base` (or the defaults)."""
    st = dict(base or DEFAULT_DEV_STATE)
    if not isinstance(saved, dict):
        return st
    if saved.get("mode") in MODES:
        st["mode"] = saved["mode"]
    for k, lo, hi in (("h", 0, 0.9999), ("s", 0, 1), ("t", 0, 1), ("brightness", 0.03, 1)):
        if is_num(saved.get(k)):
            st[k] = clamp(float(saved[k]), lo, hi)
    if isinstance(saved.get("power"), bool):
        st["power"] = saved["power"]
    return st


def load_state():
    """{"favourites", "selected", "devices": {id: state}, "legacy": state of the old single-strip layout}."""
    out = {"favourites": json.loads(json.dumps(DEFAULT_FAVS)), "selected": None, "devices": {}, "legacy": None}
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            saved = json.load(f)
        if not isinstance(saved, dict):
            return out
        if "favourites" in saved:
            out["favourites"] = clean_favourites(saved["favourites"])
        if isinstance(saved.get("selected"), str):
            out["selected"] = saved["selected"]
        if isinstance(saved.get("devices"), dict):
            out["devices"] = {k: clean_dev_state(v) for k, v in saved["devices"].items()}
        elif "mode" in saved:
            out["legacy"] = clean_dev_state(saved)
    except (OSError, ValueError):
        pass
    return out


# ====================================================================== screen capture (shared)
class Frame:
    __slots__ = ("seq", "avgs")

    def __init__(self, seq, avgs):
        self.seq, self.avgs = seq, avgs


class ScreenGrabber(threading.Thread):
    """Captures the screen once for all lights that mirror it. Idle (no capture) when nobody asks."""

    def __init__(self, tuning):
        super().__init__(daemon=True)
        self.tuning = tuning
        self.last_req = 0.0
        self.frame = None
        self.error = None
        self.seq = 0
        self.halt = threading.Event()

    def request(self):
        self.last_req = time.time()

    def latest(self):
        return self.frame

    def stop(self):
        self.halt.set()

    def run(self):
        sct = None
        np = None
        interval = 1.0 / max(1.0, float(self.tuning.get("fps", 8)))
        while not self.halt.is_set():
            if time.time() - self.last_req > 1.5:
                self.frame = None
                self.halt.wait(0.2)
                continue
            t = time.time()
            try:
                if sct is None:
                    import mss
                    import numpy as np
                    sct = mss.mss()
                mon = sct.monitors[clamp(int(self.tuning.get("monitor", 1)), 0, len(sct.monitors) - 1)]
                shot = sct.grab(mon)
                frame = np.asarray(shot)[::8, ::8, :3][:, :, ::-1]
                avgs = {r: L.average_colour(frame, r) for r in ("full", "top", "bottom")}
                self.seq += 1
                self.frame, self.error = Frame(self.seq, avgs), None
            except ImportError:
                self.error = "Screen sync needs: pip install mss numpy"
                self.halt.wait(2.0)
            except Exception as e:
                log.warning("screen capture failed: %s", e)
                self.error, sct = "Screen capture failed", None
                self.halt.wait(2.0)
            self.halt.wait(max(0.0, interval - (time.time() - t)))


# ====================================================================== light controller
class NotFound(Exception):
    pass


class Controller(threading.Thread):
    """Owns the connection to one light. Finds its address when unknown and reconnects automatically."""

    def __init__(self, cfg, state, grabber, locator, tuning, on_found):
        super().__init__(daemon=True)
        self.cfg = cfg
        self.reload = True
        self.lk = threading.Lock()
        self.cur = dict(state)
        self.version = 0
        self.grabber, self.locator, self.tuning, self.on_found = grabber, locator, tuning, on_found
        self.halt = threading.Event()
        self.wake = threading.Event()
        self.status = "Connecting..."
        self.online = None
        self.caps = {"colour": None, "white": None}       # learned after the first connection

    def reconfigure(self, cfg):
        with self.lk:
            self.cfg = cfg
            self.reload = True
        self.wake.set()

    def set_state(self, **kw):
        with self.lk:
            self.cur.update(kw)
            self.version += 1
        self.wake.set()

    def snapshot(self):
        with self.lk:
            return dict(self.cur), self.version

    def set_status(self, text, online):
        self.status, self.online = text, online

    def stop(self):
        self.halt.set()
        self.wake.set()

    def _params(self):
        t = self.tuning
        return {"interval": 1.0 / max(1.0, float(t.get("fps", 8))), "smooth": float(t.get("smoothing", 0.35)),
                "sat": float(t.get("saturation_boost", 1.3)), "bscale": float(t.get("brightness_scale", 1.0)),
                "min_delta": int(t.get("min_delta", 6))}

    def _locate(self, cfg):
        """Fill in ip/version by searching the network. Returns the updated cfg."""
        self.set_status("Looking for it on your network...", None)
        hit = self.locator.find(cfg["device_id"], cfg["local_key"])
        if not hit:
            raise NotFound("not found on the network")
        cfg = dict(cfg, ip=hit["ip"], version=hit["version"])
        with self.lk:
            self.cfg = cfg
        self.on_found(cfg["device_id"], hit)
        log.info("found %s at %s (protocol %s)", cfg["name"], hit["ip"], hit["version"])
        return cfg

    def run(self):
        P = self._params()
        dev = None
        fails = 0
        next_try = 0.0
        powered = None
        sent_ver = -1
        last_send = 0.0
        last_health = 0.0
        avg = None
        last_rgb = None
        last_mode = None
        last_seq = -1

        def read_caps(status):
            """What this light can do: coloured light and/or adjustable white (colour temperature)."""
            try:
                if not getattr(dev, "bulb_configured", True):
                    dev.detect_bulb(status)
            except Exception:
                pass
            colour = getattr(dev, "has_colour", None)
            white = getattr(dev, "has_colourtemp", None)
            self.caps = {"colour": None if colour is None else bool(colour), "white": None if white is None else bool(white)}

        def paint_white(brightness, temp, nowait=False):
            bp, tp = max(1, int(round(brightness * 100))), int(round(temp * 100))
            res = dev.set_white_percentage(bp, tp, nowait=nowait)
            if isinstance(res, dict) and res.get("Error"):           # some bulbs want the two values separately
                dev.set_brightness_percentage(bp, nowait=nowait)
                dev.set_colourtemp_percentage(tp, nowait=nowait)

        def paint(r, g, b, nowait=False):
            if getattr(dev, "has_colour", None) is False:      # white-only bulb: brightness is all it can do
                dev.set_brightness_percentage(max(1, int(round(max(r, g, b) / 2.55))), nowait=nowait)
            else:
                dev.set_colour(r, g, b, nowait=nowait)

        while not self.halt.is_set():
            wait = 0.25
            try:
                with self.lk:
                    cfg, reload = self.cfg, self.reload
                    self.reload = False
                if reload:                      # new or changed config: drop the old connection
                    try:
                        if dev:
                            dev.close()
                    except Exception:
                        pass
                    dev, fails, next_try = None, 0, 0.0
                    powered, sent_ver, last_rgb, avg, last_mode, last_seq = None, -1, None, None, None, -1

                st, ver = self.snapshot()
                now = time.time()

                if dev is None:
                    if now < next_try:          # backing off after a failure; do not rescan on every click
                        self.wake.wait(min(1.0, next_try - now))
                        self.wake.clear()
                        continue
                    self.set_status("Connecting...", None)
                    if not cfg.get("ip") or not cfg.get("version") or (fails >= 3 and fails % 3 == 0):
                        try:
                            cfg = self._locate(cfg)
                        except NotFound:
                            if not cfg.get("ip") or not cfg.get("version"):
                                raise
                            # address saved earlier may still be right; try it below
                    dev = L.connect(cfg)
                    s = dev.status()
                    if not isinstance(s, dict) or "Error" in s:
                        raise RuntimeError(s.get("Error") if isinstance(s, dict) else s)
                    fails, powered, sent_ver, last_rgb, last_health = 0, None, -1, None, now
                    read_caps(s)
                    self.set_status("Connected", True)
                    log.info("%s connected", cfg["name"])

                if not st["power"]:
                    if powered is not False:
                        dev.turn_off()
                        powered = False
                else:
                    if powered is not True:
                        dev.turn_on()
                        powered = True
                        sent_ver = -1
                    if st["mode"] != last_mode:
                        last_mode, avg, sent_ver = st["mode"], None, -1

                    mode = st["mode"]
                    if self.caps["white"] is False and mode == "white":
                        mode = "colour"                 # this light has no adjustable white
                    elif mode == "colour" and self.caps["colour"] is False and self.caps["white"]:
                        mode = "white"                  # a white-only bulb: its steady light is the white
                    if mode == "white":
                        if ver != sent_ver:
                            if now - last_send >= 0.08:
                                paint_white(st["brightness"], st["t"])
                                sent_ver, last_send = ver, now
                            else:
                                wait = 0.04
                    elif mode == "colour":
                        if ver != sent_ver:
                            if now - last_send >= 0.08:
                                r, g, b = colorsys.hsv_to_rgb(st["h"], st["s"], max(0.02, st["brightness"]))
                                paint(int(r * 255), int(g * 255), int(b * 255))
                                sent_ver, last_send = ver, now
                            else:
                                wait = 0.04
                    else:
                        region = "full" if mode == "screen" else mode
                        self.grabber.request()
                        fr = self.grabber.latest()
                        if fr is None:
                            if self.grabber.error:
                                self.set_status(self.grabber.error, True)
                                wait = 1.0
                            else:
                                wait = 0.03
                        else:
                            if fr.seq != last_seq or avg is None:
                                last_seq = fr.seq
                                cur = fr.avgs[region]
                                avg = cur if avg is None else avg + (cur - avg) * P["smooth"]
                                if self.status != "Connected":
                                    self.set_status("Connected", True)
                                changed = True
                            else:
                                changed = False
                            rgb = L.boost(avg, P["sat"], st["brightness"] * P["bscale"])
                            forced = ver != sent_ver
                            if forced or (changed and (last_rgb is None or
                                                       max(abs(a - b) for a, b in zip(rgb, last_rgb)) >= P["min_delta"])):
                                paint(*rgb, nowait=True)
                                last_rgb, sent_ver = rgb, ver
                            wait = min(0.05, P["interval"] / 3)

                if time.time() - last_health > 15:
                    s = dev.status()
                    if not isinstance(s, dict) or "Error" in s:
                        raise RuntimeError(s.get("Error") if isinstance(s, dict) else s)
                    last_health = time.time()
            except Exception as e:  # any link problem -> drop the connection and retry
                fails += 1
                missing = isinstance(e, NotFound)
                delay = 30 if missing else min(20, 2 * fails)
                log.warning("%s: link problem (%s); retry in %ss", (self.cfg or {}).get("name"), e, delay)
                self.set_status("Can't find it on your network" if missing else "Reconnecting...", False)
                try:
                    if dev:
                        dev.close()
                except Exception:
                    pass
                dev = None
                next_try = time.time() + delay
                wait = min(1.0, delay)

            if wait > 0:
                self.wake.wait(wait)
            self.wake.clear()

        try:
            if dev:
                dev.close()
        except Exception:
            pass


class DemoController:
    """Stand-in used by --demo: no light needed."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.status, self.online = "Demo (not connected)", None
        self.caps = {"colour": True, "white": cfg.get("category") == "dj"}

    def reconfigure(self, cfg):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def set_state(self, **kw):
        pass


DEMO_DEVICES = [
    {"device_id": "demo_strip_top", "name": "Desk strip (top)", "local_key": "x", "ip": "", "version": None, "category": "dd"},
    {"device_id": "demo_strip_bottom", "name": "Desk strip (bottom)", "local_key": "x", "ip": "", "version": None, "category": "dd"},
    {"device_id": "demo_bulb", "name": "Floor lamp", "local_key": "x", "ip": "", "version": None, "category": "dj"},
]


# ====================================================================== app core
class Core:
    def __init__(self, saved, demo=False):
        self.demo = demo
        self.lk = threading.RLock()
        self.favs = saved["favourites"]
        self.selected = saved["selected"]
        self.states = dict(saved["devices"])
        self.legacy = saved["legacy"]
        self.devices = []
        self.ctrls = {}
        self.tuning = strip_config.read_tuning(CONFIG_PATH)
        self.grabber = ScreenGrabber(self.tuning)
        self.locator = discover.Locator()
        self.login = None
        self.login_lk = threading.Lock()
        self.token = secrets.token_urlsafe(16)
        self.last_closed = 0.0
        self.save_timer = None
        self.listeners = []      # called after every state change
        self.quit_event = threading.Event()
        self.grabber.start()
        self.sync()

    # ---- devices
    def _read_devices(self):
        return [dict(d) for d in DEMO_DEVICES] if self.demo else strip_config.read_devices(CONFIG_PATH)

    def sync(self):
        """Make the running controllers match the saved devices."""
        with self.lk:
            devs = self._read_devices()
            ids = {d["device_id"] for d in devs}
            for d in devs:
                i = d["device_id"]
                if i not in self.states:
                    self.states[i] = clean_dev_state(self.legacy) if self.legacy else dict(DEFAULT_DEV_STATE)
                    self.legacy = None
                c = self.ctrls.get(i)
                if c is None:
                    if self.demo:
                        c = DemoController(d)
                    else:
                        c = Controller(d, self.states[i], self.grabber, self.locator, self.tuning, self.on_found)
                    self.ctrls[i] = c
                    c.start()
                elif c.cfg != d:
                    c.reconfigure(d)
            for i in list(self.ctrls):
                if i not in ids:
                    self.ctrls.pop(i).stop()
                    self.states.pop(i, None)
            self.devices = devs
            if self.selected not in ids:
                self.selected = devs[0]["device_id"] if devs else None
            self.save_soon()

    def on_found(self, device_id, hit):
        """A controller located its light: remember the address so the next start is instant."""
        try:
            strip_config.update_conn(CONFIG_PATH, device_id, hit["ip"], hit["version"])
        except OSError:
            log.exception("could not save the address")
            return
        with self.lk:
            for d in self.devices:
                if d["device_id"] == device_id:
                    d["ip"], d["version"] = hit["ip"], hit["version"]

    def save_device(self, body, test=True):
        """Manual add / edit form."""
        if self.demo:
            raise strip_config.ConfigError("Not available in demo mode.")
        wanted = str(body.get("original") or body.get("device_id") or "").strip()
        existing = next((d for d in strip_config.read_devices(CONFIG_PATH) if d["device_id"] == wanted), None)
        if existing and body.get("original") and str(body.get("device_id", "")).strip() != wanted:
            raise strip_config.ConfigError("The device ID of a saved light cannot be changed. Remove it and add it again.")
        dev = strip_config.check_device(body, existing, test)
        strip_config.upsert_device(CONFIG_PATH, dev)
        self.sync()
        with self.lk:
            if not existing:
                self.selected = dev["device_id"]
        return dev["version"]

    def remove_device(self, device_id):
        if self.demo:
            raise strip_config.ConfigError("Not available in demo mode.")
        strip_config.remove_device(CONFIG_PATH, device_id)
        self.sync()

    # ---- Tuya login
    def login_start(self, user_code):
        if self.demo:
            raise tuya_cloud.LoginError("Not available in demo mode.")
        lg = tuya_cloud.TuyaLogin()
        qr = lg.start(user_code)
        self.login = lg
        strip_config.set_extra(CONFIG_PATH, "tuya_user_code", lg.user_code)
        return qr

    def _login_result(self, lg):
        saved = {d["device_id"] for d in strip_config.read_devices(CONFIG_PATH)}
        devs = [dict(d, added=d["id"] in saved) for d in lg.public_devices()]
        return {"status": "ok", "devices": devs}

    def login_poll(self):
        lg = self.login
        if lg is None:
            return {"status": "none"}
        with self.login_lk:
            if lg.ready:
                return self._login_result(lg)
            st = lg.poll()
            if st != "ok":
                if st == "expired":
                    self.login = None
                return {"status": st}
            try:
                lg.fetch_devices()
            except tuya_cloud.LoginError:
                self.login = None
                raise
            return self._login_result(lg)

    def login_add(self, ids):
        lg = self.login
        if lg is None or not lg.ready:
            raise tuya_cloud.LoginError("The sign-in expired. Sign in again.")
        existing = {d["device_id"]: d for d in strip_config.read_devices(CONFIG_PATH)}
        added = []
        for i in ids if isinstance(ids, list) else []:
            info = lg.devices.get(i)
            if info and info["category"] in tuya_cloud.LIGHT_CATEGORIES:
                strip_config.upsert_device(CONFIG_PATH, strip_config.from_cloud(info, existing.get(i)))
                added.append(i)
        if not added:
            raise tuya_cloud.LoginError("Pick at least one light.")
        self.login = None
        self.sync()
        with self.lk:
            self.selected = added[0]
        return len(added)

    def logoff(self):
        """Forget the account's lights, their keys and the saved user code."""
        with self.login_lk:
            self.login = None
        strip_config.clear(CONFIG_PATH)
        with self.lk:
            self.favs = self.favs                       # favourites are kept
            self.states.clear()
            self.legacy = None
            self.selected = None
        self.sync()
        self.save_now()

    # ---- state
    def push(self, i):
        c, s = self.ctrls.get(i), self.states.get(i)
        if c and s:
            c.set_state(**s)

    def api_state(self):
        with self.lk:
            devs = []
            for d in self.devices:
                i = d["device_id"]
                c = self.ctrls[i]
                devs.append(strip_config.public(d, status=c.status, online=c.online, caps=dict(c.caps), state=dict(self.states[i])))
            return {"devices": devs, "selected": self.selected, "favourites": json.loads(json.dumps(self.favs)),
                    "user_code": strip_config.get_extra(CONFIG_PATH, "tuya_user_code"), "demo": self.demo}

    def selected_state(self):
        with self.lk:
            return dict(self.states[self.selected]) if self.selected in self.states else None

    def update(self, body):
        """POST /api/state: {id, power/mode/h/s/brightness}, {favourites}, {select}."""
        with self.lk:
            if "favourites" in body and isinstance(body["favourites"], list):
                self.favs = clean_favourites(body["favourites"])
            if isinstance(body.get("select"), str) and body["select"] in self.states:
                self.selected = body["select"]
            if isinstance(body.get("all_power"), bool):
                for j, st in self.states.items():
                    st["power"] = body["all_power"]
                    self.push(j)
            i = body.get("id")
            if i in self.states:
                self.states[i] = clean_dev_state({k: v for k, v in body.items() if k != "id"}, self.states[i])
                self.push(i)
            self.save_soon()
        self.notify()

    def set_all_power(self, on):
        with self.lk:
            for i, s in self.states.items():
                s["power"] = on
                self.push(i)
            self.save_soon()
        self.notify()

    def any_on(self):
        with self.lk:
            return any(s["power"] for s in self.states.values())

    def notify(self):
        for fn in self.listeners:
            try:
                fn()
            except Exception:
                log.exception("listener failed")

    def save_soon(self):
        if self.save_timer:
            self.save_timer.cancel()
        self.save_timer = threading.Timer(0.5, self.save_now)
        self.save_timer.daemon = True
        self.save_timer.start()

    def save_now(self):
        try:
            with self.lk:
                data = {"favourites": self.favs, "selected": self.selected, "devices": self.states}
                text = json.dumps(data)
            tmp = STATE_PATH + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(text)
            os.replace(tmp, STATE_PATH)
        except OSError:
            log.exception("could not save state")

    def stop_all(self):
        self.grabber.stop()
        for c in list(self.ctrls.values()):
            c.stop()

    def quit(self):
        self.quit_event.set()


# ====================================================================== http server
def make_handler(core, port_ref):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def host_ok(self):
            return self.headers.get("Host", "") in (f"127.0.0.1:{port_ref[0]}", f"localhost:{port_ref[0]}")

        def token_ok(self):
            return secrets.compare_digest(self.headers.get("X-Token", ""), core.token)

        def send_json(self, obj, code=200):
            data = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def deny(self):
            self.send_json({"error": "forbidden"}, 403)

        def page(self):
            with open(UI_PATH, "r", encoding="utf-8") as f:
                html = f.read()
            try:
                with open(QR_JS_PATH, "r", encoding="utf-8") as f:
                    qr = f.read()
            except OSError:
                qr = ""
            return html.replace("__TOKEN__", core.token).replace("/*__QRCODE_JS__*/", qr).encode()

        def do_GET(self):
            if not self.host_ok():
                return self.deny()
            u = urlparse(self.path)
            if u.path == "/":
                t = parse_qs(u.query).get("t", [""])[0]
                if not secrets.compare_digest(t, core.token):
                    return self.deny()
                html = self.page()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(html)
            elif u.path == "/api/state":
                if not self.token_ok():
                    return self.deny()
                self.send_json({**core.api_state(), "autostart": autostart_enabled(), "version": APP_VERSION})
            elif u.path == "/api/login/poll":
                if not self.token_ok():
                    return self.deny()
                try:
                    self.send_json(core.login_poll())
                except tuya_cloud.LoginError as e:
                    self.send_json({"error": str(e)}, 400)
            else:
                self.send_json({"error": "not found"}, 404)

        def do_POST(self):
            if not (self.host_ok() and self.token_ok()):
                return self.deny()
            try:
                n = int(self.headers.get("Content-Length", "0"))
                body = json.loads(self.rfile.read(min(n, 16384)) or b"{}")
                if not isinstance(body, dict):
                    raise ValueError
            except ValueError:
                return self.send_json({"error": "bad request"}, 400)
            path = urlparse(self.path).path
            try:
                if path == "/api/state":
                    core.update(body)
                elif path == "/api/closed":
                    core.last_closed = time.time()
                elif path == "/api/quit":
                    log.info("quit chosen in the window")
                    core.quit()
                elif path == "/api/login/start":
                    return self.send_json({"ok": True, "qr": core.login_start(body.get("user_code"))})
                elif path == "/api/login/add":
                    return self.send_json({"ok": True, "added": core.login_add(body.get("ids"))})
                elif path == "/api/device":
                    version = core.save_device(body, test=body.get("test", True) is not False)
                    return self.send_json({"ok": True, "version": version})
                elif path == "/api/device/remove":
                    core.remove_device(str(body.get("id", "")))
                elif path == "/api/logoff":
                    core.logoff()
                elif path == "/api/settings":
                    if isinstance(body.get("autostart"), bool):
                        set_autostart(body["autostart"])
                    return self.send_json({"ok": True, "autostart": autostart_enabled()})
                else:
                    return self.send_json({"error": "not found"}, 404)
            except (strip_config.ConfigError, tuya_cloud.LoginError) as e:
                return self.send_json({"error": str(e)}, 400)
            self.send_json({"ok": True})

    return Handler


def start_server(core):
    port_ref = [0]
    handler = make_handler(core, port_ref)
    last_err = None
    for p in UI_PORTS:
        try:
            srv = ThreadingHTTPServer(("127.0.0.1", p), handler)
            port_ref[0] = p
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            return srv, p
        except OSError as e:
            last_err = e
    raise RuntimeError(f"no free port for the control window: {last_err}")


# ====================================================================== window launcher
def find_browser():
    pf = os.environ.get("ProgramFiles", r"C:\Program Files")
    pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    local = os.environ.get("LOCALAPPDATA", "")
    for p in (
        os.path.join(pf86, r"Microsoft\Edge\Application\msedge.exe"),
        os.path.join(pf, r"Microsoft\Edge\Application\msedge.exe"),
        os.path.join(pf, r"Google\Chrome\Application\chrome.exe"),
        os.path.join(pf86, r"Google\Chrome\Application\chrome.exe"),
        os.path.join(local, r"Google\Chrome\Application\chrome.exe"),
    ):
        if os.path.exists(p):
            return p
    return None


class Window:
    def __init__(self, core, port):
        self.core, self.port, self.proc = core, port, None
        self.browser = find_browser()

    def url(self, app=True):
        u = f"http://127.0.0.1:{self.port}/?t={self.core.token}"
        return u + "&app=1" if app else u

    def alive(self):
        return self.proc is not None and self.proc.poll() is None

    def open(self):
        if self.alive():
            return
        if self.browser:
            try:
                self.proc = subprocess.Popen([
                    self.browser, f"--app={self.url()}", f"--user-data-dir={PROFILE_DIR}",
                    "--no-first-run", "--no-default-browser-check", "--disable-extensions",
                    "--window-size=372,660",
                ])
                return
            except OSError:
                log.exception("could not start %s, using the default browser", self.browser)
        webbrowser.open(self.url(app=False))

    def close(self):
        if self.alive():
            self.proc.terminate()

    def toggle(self):
        if self.alive():
            self.close()
        elif time.time() - self.core.last_closed > 0.6:   # the click that just closed it by blur
            self.open()


# ====================================================================== tray + autostart
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def autostart_command():
    if FROZEN:
        return '"%s" --hidden' % sys.executable
    exe = sys.executable
    pw = os.path.join(os.path.dirname(exe), "pythonw.exe")
    exe = pw if os.path.exists(pw) else exe
    return '"%s" "%s" --hidden' % (exe, os.path.abspath(__file__))


def autostart_enabled():
    if os.name != "nt":
        return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as k:
            winreg.QueryValueEx(k, APP_NAME)
        return True
    except OSError:
        return False


def set_autostart(on):
    if os.name != "nt":
        return
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
        if on:
            winreg.SetValueEx(k, APP_NAME, 0, winreg.REG_SZ, autostart_command())
        else:
            try:
                winreg.DeleteValue(k, APP_NAME)
            except FileNotFoundError:
                pass
def make_icon(Image, ImageDraw, dot=None):
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i in range(0, 360, 3):
        r, g, b = colorsys.hsv_to_rgb(i / 360, 0.85, 1)
        d.pieslice((2, 2, size - 2, size - 2), i - 90, i - 90 + 4, fill=(int(r * 255), int(g * 255), int(b * 255), 255))
    d.ellipse((17, 17, size - 17, size - 17), fill=(0, 0, 0, 0))
    if dot:
        d.ellipse((23, 23, size - 23, size - 23), fill=dot + (255,))
    return img


def message(text, title="Glowdeck"):
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, text, title, 0x40)
    except Exception:
        print(text, file=sys.stderr)


class TrayRunner:
    """Keeps the tray icon alive: runs it on its own thread, recreates it if it ever stops or crashes, and
    can rebuild it on demand (Windows throws tray icons away when Explorer restarts)."""

    def __init__(self, make):
        self.make = make                      # () -> a new pystray.Icon
        self.icon = None
        self.done = threading.Event()
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.last_key = None
        self.failures = 0

    def start(self):
        self.thread.start()

    def _loop(self):
        while not self.done.is_set():
            began = time.time()
            try:
                self.icon = self.make()
                self.last_key = None
                self.icon.run()                       # blocks until icon.stop()
            except Exception:
                log.exception("tray icon crashed")
            if self.done.is_set():
                break
            # a stop() we asked for (rebuild) is quick and fine; a run that dies at once is a failure
            self.failures = self.failures + 1 if time.time() - began < 5 else 0
            log.warning("tray icon stopped; creating it again")
            if self.failures == 3:
                message("The tray icon keeps failing to start.\nGlowdeck still runs; details are in " + LOG_PATH)
            self.done.wait(1.0 if self.failures < 3 else 10.0)

    def set_image(self, key, make_image):
        """Update the icon picture, but only when what it shows has changed."""
        ic = self.icon
        if ic is None or key == self.last_key:
            return
        try:
            ic.icon = make_image()
            self.last_key = key
        except Exception:
            log.exception("could not update the tray icon")

    def rebuild(self):
        ic = self.icon
        if ic is not None:
            try:
                ic.stop()                             # _loop notices and makes a fresh one
            except Exception:
                log.exception("could not stop the tray icon")

    def stop(self):
        self.done.set()
        ic = self.icon
        if ic is not None:
            try:
                ic.stop()
            except Exception:
                pass


def make_tray_menu(pystray, core, win):
    """The right-click menu. pystray calls actions as f(icon, item) and 'checked' as f(item), so every function
    below takes exactly those arguments (no default-argument tricks)."""
    def open_window(icon, item):
        win.toggle()

    def all_toggle(icon, item):
        core.set_all_power(not core.any_on())

    def all_checked(item):
        return core.any_on()

    def auto_toggle(icon, item):
        set_autostart(not autostart_enabled())

    def auto_checked(item):
        return autostart_enabled()

    def quit_app(icon, item):
        log.info("quit chosen in the tray menu")
        core.quit()

    def has_lights(item):
        return bool(core.devices)

    def light_item(did, name):
        def toggle(icon, item):
            core.update({"id": did, "power": not core.states.get(did, {}).get("power", True)})

        def checked(item):
            return bool(core.states.get(did, {}).get("power"))
        return pystray.MenuItem(name.replace("&", "&&"), toggle, checked=checked)

    def light_items():                                # rebuilt every time the menu opens
        return [light_item(d["device_id"], d["name"]) for d in list(core.devices)]

    return pystray.Menu(
        pystray.MenuItem("Open", open_window, default=True),
        pystray.MenuItem("Lights", pystray.Menu(light_items), visible=has_lights),
        pystray.MenuItem("All lights on", all_toggle, checked=all_checked),
        pystray.MenuItem("Start with Windows", auto_toggle, checked=auto_checked, visible=os.name == "nt"),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_app),
    )


def shell_window():
    """Handle of the taskbar (changes when Explorer restarts), 0 if unknown."""
    if os.name != "nt":
        return 0
    try:
        import ctypes
        return int(ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None) or 0)
    except Exception:
        return 0


def _main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true", help="three fake lights, just the interface")
    ap.add_argument("--hidden", action="store_true", help="start in the tray without opening the window")
    ap.add_argument("--no-tray", action="store_true", help="no tray icon; print the window URL instead")
    args = ap.parse_args()

    for stream in ("stdout", "stderr"):               # no console under pythonw / the installed exe
        if getattr(sys, stream) is None:
            setattr(sys, stream, open(os.devnull, "w"))
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    sys.excepthook = lambda *e: log.critical("uncaught error", exc_info=e)
    threading.excepthook = lambda a: log.critical("error in thread %s", getattr(a.thread, "name", "?"),
                                                  exc_info=(a.exc_type, a.exc_value, a.exc_traceback))
    log.info("Glowdeck %s starting (pid %s)", APP_VERSION, os.getpid())
    migrate_legacy_files()

    if not os.path.exists(UI_PATH):
        message("ui.html was not found.\nIt must be in the same folder as glowdeck.py:\n" + RES_DIR)
        return

    lock = socket.socket()
    try:
        lock.bind(("127.0.0.1", LOCK_PORT))
    except OSError:
        message("Glowdeck is already running (look for its icon in the tray).")
        return

    core = Core(load_state(), demo=args.demo)
    srv, port = start_server(core)
    win = Window(core, port)
    log.info("window server on port %s, browser=%s, %d light(s)", port, win.browser, len(core.devices))

    tray = None
    if not args.no_tray:
        try:
            import pystray
            from PIL import Image, ImageDraw
        except ImportError:
            message("Missing packages for the tray icon.\nRun:  pip install pystray pillow")
            core.stop_all()
            return

        def dot_colour():
            s = core.selected_state()
            if s and s["power"] and s["mode"] == "colour":
                return tuple(int(c * 255) for c in colorsys.hsv_to_rgb(s["h"], s["s"], 1))
            return None

        def new_icon():
            return pystray.Icon("glowdeck", make_icon(Image, ImageDraw, dot_colour()), "Glowdeck",
                                make_tray_menu(pystray, core, win))

        tray = TrayRunner(new_icon)
        core.listeners.append(lambda: tray.set_image(dot_colour(), lambda: make_icon(Image, ImageDraw, dot_colour())))
        tray.start()
    else:
        print("Open this in a browser:", win.url(app=False))

    if tray and (not args.hidden or not core.devices):    # nothing set up yet: always show the sign-in
        win.open()

    shell = shell_window()
    try:
        while not core.quit_event.wait(1.0):
            now = shell_window()
            if tray and now and shell and now != shell:       # Explorer restarted: its tray forgot our icon
                log.info("taskbar was recreated; re-adding the tray icon")
                tray.rebuild()
            shell = now or shell
    except KeyboardInterrupt:
        pass
    finally:
        log.info("Glowdeck is closing")
        core.save_now()
        win.close()
        core.stop_all()
        if tray:
            tray.stop()
        srv.shutdown()


def main():
    try:
        _main()
    except Exception as e:
        import traceback
        log.exception("fatal error")
        message("The app stopped:\n%s: %s\n\nDetails are in %s" % (type(e).__name__, e, LOG_PATH))
        traceback.print_exc()


if __name__ == "__main__":
    main()
