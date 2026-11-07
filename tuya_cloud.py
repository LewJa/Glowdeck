"""
Tuya sign-in without a developer account.

Uses Tuya's official `tuya-device-sharing-sdk` (the library Home Assistant uses): the user types the
"User Code" from the Tuya Smart / Smart Life app, scans a QR code with that app, and we get the list of their
devices including each device's local key. Nothing from the login session is stored - only the lights the user
picks (device id, name and local key) are kept, see strip_config.py.

Notes:
  * Works for devices added in the Tuya Smart or Smart Life apps, not seller-branded apps.
  * Tuya does not return the LAN address of a device, so discover.py finds it.
  * CLIENT_ID / SCHEMA are Home Assistant's public registration. Tuya may change or limit them;
    override with the environment variables GLOWDECK_TUYA_CLIENT_ID / GLOWDECK_TUYA_SCHEMA.
"""
import logging
import os
import time

log = logging.getLogger("glowdeck.tuya")

CLIENT_ID = os.environ.get("GLOWDECK_TUYA_CLIENT_ID", "HA_3y9q4ak7g4ephrvke")
SCHEMA = os.environ.get("GLOWDECK_TUYA_SCHEMA", "haauthorize")
QR_PREFIX = "tuyaSmart--qrLogin?token="
QR_LIFETIME = 180            # seconds we wait for the scan
# Tuya product categories that are lights: strip (dd), light (dj), others (dc string, xdd ceiling, fwd ambient ...)
LIGHT_CATEGORIES = {"dj", "dd", "dc", "xdd", "fwd", "fwl", "tgq", "tgkg", "dsd", "gyd"}
MISSING = "The Tuya sign-in component is missing (pip install tuya-device-sharing-sdk)."


class LoginError(Exception):
    """Raised with a message that is safe to show to the user."""


class TuyaLogin:
    def __init__(self, client_id=CLIENT_ID, schema=SCHEMA):
        self.client_id, self.schema = client_id, schema
        self.user_code = None
        self.qrcode = None
        self.started = 0.0
        self.info = None
        self.ready = False
        self.devices = {}          # id -> {"id","name","key","category","product","online"}
        self._lc = None

    def start(self, user_code):
        """Step 1: returns the text to put in the QR code."""
        user_code = (user_code or "").strip()
        if not user_code:
            raise LoginError("Type your user code first.")
        try:
            from tuya_sharing import LoginControl
        except ImportError:
            raise LoginError(MISSING)
        self._lc = LoginControl()
        try:
            resp = self._lc.qr_code(self.client_id, self.schema, user_code)
        except Exception as e:
            log.warning("qr_code failed: %s", e)
            raise LoginError("Could not reach Tuya. Check your internet connection.")
        if not isinstance(resp, dict) or not resp.get("success"):
            raise LoginError("Tuya did not accept that user code. Check it and try again.")
        try:
            self.qrcode = resp["result"]["qrcode"]
        except (KeyError, TypeError):
            raise LoginError("Tuya sent an unexpected answer. Try again in a minute.")
        self.user_code = user_code
        self.started = time.time()
        return QR_PREFIX + self.qrcode

    def poll(self):
        """Step 2: 'ok', 'pending' or 'expired'."""
        if time.time() - self.started > QR_LIFETIME:
            return "expired"
        try:
            ret, info = self._lc.login_result(self.qrcode, self.client_id, self.user_code)
        except Exception as e:                      # network hiccup - keep waiting
            log.info("login_result error: %s", e)
            return "pending"
        if ret:
            self.info = info
            return "ok"
        return "pending"

    def fetch_devices(self):
        """Step 3: reads the account's devices (with keys) into self.devices."""
        try:
            from tuya_sharing import Manager, SharingTokenListener
        except ImportError:
            raise LoginError(MISSING)

        class _Listener(SharingTokenListener):
            def update_token(self, token_info):     # we do not keep the session
                pass

        i = self.info or {}
        token_info = {k: i.get(k) for k in ("t", "uid", "expire_time", "access_token", "refresh_token")}
        try:
            mgr = Manager(self.client_id, self.user_code, i.get("terminal_id"), i.get("endpoint"), token_info, _Listener())
            mgr.update_device_cache()
        except Exception as e:
            log.warning("device list failed: %s", e)
            raise LoginError("Signed in, but could not read your devices from Tuya.")
        self.devices = {}
        for d in list(getattr(mgr, "device_map", {}).values()):
            key = getattr(d, "local_key", None)
            if not key:
                continue                            # e.g. Bluetooth-only devices
            self.devices[d.id] = {"id": d.id, "name": getattr(d, "name", d.id), "key": key,
                                  "category": getattr(d, "category", "") or "",
                                  "product": getattr(d, "product_name", "") or "",
                                  "online": getattr(d, "online", None)}
        try:
            mgr.unload()
        except Exception:
            pass
        self.ready = True

    def public_devices(self):
        """Device list for the UI - never includes the local keys. Lights first."""
        out = [{"id": d["id"], "name": d["name"], "category": d["category"], "product": d["product"],
                "online": d["online"], "light": d["category"] in LIGHT_CATEGORIES} for d in self.devices.values()]
        out.sort(key=lambda d: (not d["light"], d["name"].lower()))
        return out
