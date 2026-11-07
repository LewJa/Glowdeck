"""
The saved lights (config.json): reading, checking and saving them.

Layout of config.json:
  {"devices": [{"device_id", "name", "local_key", "ip", "version", "category"}, ...],
   "tuya_user_code": "...", "fps": 8, "smoothing": 0.35, ...tuning options...}
An empty "ip" / null "version" means "find it on the network" (see discover.Locator).
The local keys stay on this PC and are never sent to the page.
"""
import ipaddress
import json
import os
import re
import threading

import discover

TUNING_DEFAULTS = {"fps": 8, "smoothing": 0.35, "saturation_boost": 1.3, "brightness_scale": 1.0,
                   "min_delta": 6, "monitor": 1}
VERSIONS = (3.3, 3.4, 3.5)
LEGACY_KEYS = ("device_id", "local_key", "ip", "version")
_lock = threading.RLock()


class ConfigError(Exception):
    """Raised with a message that is safe to show to the user."""


def _load(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def _version(v):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    return v if v in VERSIONS else None


def _normal(d):
    """One stored device cleaned up, or None when it lacks an id or key."""
    if not isinstance(d, dict):
        return None
    s = {k: (v.strip() if isinstance(v, str) else v) for k, v in d.items()}
    did, key = s.get("device_id"), s.get("local_key")
    if not did or not key or str(key).startswith("PUT_"):
        return None
    try:
        ipaddress.IPv4Address(s.get("ip") or "")
        ip = s["ip"]
    except ValueError:
        ip = ""
    return {"device_id": str(did), "name": str(s.get("name") or "Light")[:40], "local_key": str(key),
            "ip": ip, "version": _version(s.get("version")), "category": str(s.get("category") or "")}


def read_devices(path):
    """All saved devices. Also upgrades the old single-strip layout of earlier versions."""
    with _lock:
        data = _load(path)
        if "devices" not in data and data.get("device_id"):
            old = _normal({**{k: data.get(k) for k in LEGACY_KEYS}, "name": "LED strip", "category": "dd"})
            for k in LEGACY_KEYS:
                data.pop(k, None)
            data["devices"] = [old] if old else []
            try:
                _save(path, data)
            except OSError:
                pass
        out = []
        for d in data.get("devices", []) if isinstance(data.get("devices"), list) else []:
            n = _normal(d)
            if n and all(n["device_id"] != o["device_id"] for o in out):
                out.append(n)
        return out


def _write_devices(path, devices):
    data = _load(path)
    for k in LEGACY_KEYS:
        data.pop(k, None)
    for k, v in TUNING_DEFAULTS.items():
        data.setdefault(k, v)
    data["devices"] = devices
    _save(path, data)


def upsert_device(path, dev):
    with _lock:
        devices = read_devices(path)
        for i, d in enumerate(devices):
            if d["device_id"] == dev["device_id"]:
                devices[i] = dev
                break
        else:
            devices.append(dev)
        _write_devices(path, devices)


def remove_device(path, device_id):
    with _lock:
        _write_devices(path, [d for d in read_devices(path) if d["device_id"] != device_id])


def update_conn(path, device_id, ip, version):
    """Remember the address found on the network."""
    with _lock:
        devices = read_devices(path)
        for d in devices:
            if d["device_id"] == device_id:
                d["ip"], d["version"] = ip, _version(version)
        _write_devices(path, devices)


def clear(path):
    """Log off: forget every device, key and the saved user code. Tuning options stay."""
    with _lock:
        data = _load(path)
        for k in LEGACY_KEYS + ("devices", "tuya_user_code"):
            data.pop(k, None)
        _save(path, data)


def read_tuning(path):
    data = _load(path)
    out = dict(TUNING_DEFAULTS)
    for k in out:
        if isinstance(data.get(k), (int, float)) and not isinstance(data.get(k), bool):
            out[k] = data[k]
    return out


def get_extra(path, key, default=""):
    v = _load(path).get(key, default)
    return v if isinstance(v, str) else default


def set_extra(path, key, value):
    with _lock:
        data = _load(path)
        data[key] = value
        _save(path, data)


def public(d, **more):
    """What the page may know about a device. The local key itself is never included."""
    return {"id": d["device_id"], "name": d["name"], "ip": d["ip"], "version": d["version"] or "auto",
            "kind": "strip" if d["category"] == "dd" else "bulb", **more}


def from_cloud(info, existing=None):
    """A device chosen from the Tuya cloud list; keeps an address we already found."""
    return {"device_id": info["id"], "name": (info.get("name") or "Light")[:40], "local_key": info["key"],
            "ip": (existing or {}).get("ip", ""), "version": (existing or {}).get("version"),
            "category": info.get("category", "")}


def clean_device(body, existing):
    """Validate what the manual form sent. A blank key keeps the saved one. IP may be blank (= find it)."""
    device_id = str(body.get("device_id", "")).strip()
    key = str(body.get("local_key", "")).strip() or (existing or {}).get("local_key", "")
    ip = str(body.get("ip", "")).strip()
    version = body.get("version", "auto")
    name = str(body.get("name", "")).strip()[:40] or (existing or {}).get("name") or "Light"

    if not device_id:
        raise ConfigError("Enter the device ID.")
    if not re.fullmatch(r"[A-Za-z0-9_\-]{6,40}", device_id):
        raise ConfigError("The device ID should be letters and digits only (no spaces).")
    if not key:
        raise ConfigError("Enter the local key.")
    if any(c.isspace() for c in key):
        raise ConfigError("The local key must not contain spaces.")
    if ip:
        try:
            ipaddress.IPv4Address(ip)
        except ValueError:
            raise ConfigError("The IP address should look like 192.168.1.50 (or leave it empty to find it automatically).")
    if version != "auto":
        version = _version(version)
        if version is None:
            raise ConfigError("Pick a protocol version.")
    else:
        version = None
    return {"device_id": device_id, "name": name, "local_key": key, "ip": ip, "version": version,
            "category": (existing or {}).get("category", "dd")}


def check_device(body, existing, test=True):
    """Validate, optionally try the connection. Returns the device dict ready to save."""
    d = clean_device(body, existing)
    if d["ip"] and test:
        versions = discover.VERSIONS if d["version"] is None else (d["version"],)
        found = discover.probe(d["ip"], d["device_id"], d["local_key"], versions=versions)
        if found is None:
            raise ConfigError(
                "Could not talk to the light. Check the IP address, device ID, local key and protocol version, "
                "and close any other app that controls it (Smart Life or the vendor's own app).")
        d["version"] = found
    elif d["ip"] and d["version"] is None:
        raise ConfigError("Pick a protocol version to save without testing.")
    elif not d["ip"]:
        d["version"] = None                      # found on the network later
    return d
