#!/usr/bin/env python3
"""
Glowdeck Sync - minimal local controller for Tuya LED strips (command-line helpers used by Glowdeck).

Talks to the strip directly over your LAN (no vendor app needed).

Commands:
  python glowdeck_sync.py scan            find Tuya devices on the LAN (IP, device id, protocol version)
  python glowdeck_sync.py test            flash red/green/blue to check that control works
  python glowdeck_sync.py sync [options]  mirror the screen colour onto the strip

Config: config.json next to this file (copy config.example.json).
"""
import argparse
import json
import os
import sys
import time

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        sys.exit("config.json not found. Copy config.example.json to config.json and fill it in.")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    # trim stray whitespace (a leading space in "ip" breaks the connection)
    cfg = {k: (v.strip() if isinstance(v, str) else v) for k, v in cfg.items()}
    for key in ("device_id", "local_key"):
        if not cfg.get(key) or cfg[key].startswith("PUT_"):
            sys.exit(f"config.json: '{key}' is not filled in.")
    return cfg


def connect(cfg):
    import tinytuya

    ip = cfg.get("ip") or "Auto"
    # Pass the version to the constructor (as in the working probe). 3.4/3.5 devices need
    # it at creation time for the session-key handshake.
    dev = tinytuya.BulbDevice(
        cfg["device_id"], ip, cfg["local_key"],
        version=float(cfg.get("version", 3.3)),
        persist=True,
    )
    dev.set_socketTimeout(5)
    dev.set_socketRetryLimit(2)
    return dev


# ---------------------------------------------------------------- scan
def cmd_scan(_args):
    import tinytuya

    print("Scanning LAN for Tuya devices (takes ~20 s)...")
    devices = tinytuya.deviceScan(verbose=False, maxretry=None)
    if not devices:
        print("Nothing found. Check: same network/subnet as the strip, firewall, VPN off,")
        print("router client isolation off. Close the vendor app while scanning.")
        return
    for ip, d in devices.items():
        print(f"IP {ip}  device_id={d.get('gwId')}  version={d.get('version')}  product={d.get('productKey')}")
    print("\nPut ip / device_id / version into config.json (local_key comes from your Tuya account, see README).")


# ---------------------------------------------------------------- test
def cmd_test(_args):
    cfg = load_config()
    dev = connect(cfg)
    st = dev.status()
    print("status:", st)
    if "Error" in st:
        sys.exit("Could not read status. Wrong key/ip/version, or another client holds the connection.")
    dev.turn_on()
    for name, rgb in (("red", (255, 0, 0)), ("green", (0, 255, 0)), ("blue", (0, 0, 255)), ("white-ish", (255, 200, 150))):
        print("->", name)
        dev.set_colour(*rgb)
        time.sleep(1.2)
    print("Done. If the strip changed colour, local control works.")


# ---------------------------------------------------------------- sync
def region_slice(h, w, region):
    """Pick the part of the frame to average."""
    if region == "full":
        return slice(0, h), slice(0, w)
    if region == "top":
        return slice(0, max(1, h // 5)), slice(0, w)
    if region == "bottom":
        return slice(h - max(1, h // 5), h), slice(0, w)
    if region == "edges":  # ring around the border, handled in caller
        return slice(0, h), slice(0, w)
    raise ValueError(region)


def average_colour(frame, region, weights=None):
    import numpy as np

    h, w = frame.shape[:2]
    if region == "mix":
        # one colour for the whole strip, blended from the left edge, the top edge and the right edge
        wt = {"left": 0.3, "top": 0.4, "right": 0.3}
        wt.update(weights or {})
        t = max(1, h // 5)
        s = max(1, w // 8)
        zones = {"left": frame[:, :s], "top": frame[:t], "right": frame[:, -s:]}
        total = sum(wt[k] for k in zones) or 1.0
        return sum(zones[k].reshape(-1, 3).mean(axis=0) * wt[k] for k in zones) / total
    if region == "edges":
        t = max(1, h // 10)
        s = max(1, w // 10)
        parts = [frame[:t].reshape(-1, 3), frame[-t:].reshape(-1, 3),
                 frame[:, :s].reshape(-1, 3), frame[:, -s:].reshape(-1, 3)]
        px = np.concatenate(parts)
    else:
        ys, xs = region_slice(h, w, region)
        px = frame[ys, xs].reshape(-1, 3)
    return px.mean(axis=0)  # float (r,g,b)


def boost(rgb, saturation, brightness):
    import colorsys

    r, g, b = [c / 255.0 for c in rgb]
    hh, ss, vv = colorsys.rgb_to_hsv(r, g, b)
    ss = min(1.0, ss * saturation)
    vv = min(1.0, vv * brightness)
    r, g, b = colorsys.hsv_to_rgb(hh, ss, vv)
    return int(r * 255), int(g * 255), int(b * 255)


def cmd_sync(args):
    import mss
    import numpy as np

    cfg = load_config()
    fps = args.fps or float(cfg.get("fps", 8))
    smooth = args.smooth if args.smooth is not None else float(cfg.get("smoothing", 0.35))  # 0..1, higher = faster
    region = args.region or cfg.get("region", "edges")
    sat = float(cfg.get("saturation_boost", 1.3))
    bri = float(cfg.get("brightness_scale", 1.0))
    min_delta = int(cfg.get("min_delta", 6))
    interval = 1.0 / fps

    dev = None
    last_sent = None
    avg = None
    fails = 0
    last_keepalive = 0.0
    print(f"Syncing: region={region} fps={fps} smoothing={smooth}. Ctrl+C to stop.")

    with mss.mss() as sct:
        mon = sct.monitors[args.monitor]
        while True:
            t0 = time.time()
            try:
                if dev is None:
                    dev = connect(cfg)
                    st = dev.status()
                    if "Error" in st:
                        raise RuntimeError(st.get("Error"))
                    dev.turn_on()
                    print("connected")
                    fails = 0
                    last_sent = None

                shot = sct.grab(mon)
                frame = np.asarray(shot)[::8, ::8, :3][:, :, ::-1]  # BGRA -> RGB, downsample
                cur = average_colour(frame, region, cfg.get("mix_weights"))
                avg = cur if avg is None else avg + (cur - avg) * smooth
                rgb = boost(avg, sat, bri)

                changed = last_sent is None or max(abs(a - b) for a, b in zip(rgb, last_sent)) >= min_delta
                if changed:
                    dev.set_colour(*rgb, nowait=True)
                    last_sent = rgb
                    last_keepalive = t0
                elif t0 - last_keepalive > 8:  # heartbeat so the link does not idle out
                    dev.heartbeat(nowait=True)
                    last_keepalive = t0
            except KeyboardInterrupt:
                print("\nstopped")
                break
            except Exception as e:  # reconnect on any link problem
                fails += 1
                wait = min(30, 2 * fails)
                print(f"link problem ({e}); reconnecting in {wait}s")
                try:
                    if dev:
                        dev.close()
                except Exception:
                    pass
                dev = None
                time.sleep(wait)
                continue

            time.sleep(max(0.0, interval - (time.time() - t0)))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scan").set_defaults(fn=cmd_scan)
    sub.add_parser("test").set_defaults(fn=cmd_test)
    s = sub.add_parser("sync")
    s.add_argument("--fps", type=float, help="colour updates per second (default 8)")
    s.add_argument("--smooth", type=float, help="0..1, higher reacts faster (default 0.35)")
    s.add_argument("--region", choices=["full", "edges", "top", "bottom", "mix"], help="screen area to average")
    s.add_argument("--monitor", type=int, default=1, help="monitor number (1 = primary)")
    s.set_defaults(fn=cmd_sync)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
