"""
Finding a Tuya device on the local network and working out its protocol version.

The Tuya cloud login gives us each device's id and local key, but not its LAN address. `Locator.find` looks
it up: first Tuya's own UDP broadcast scan, then (many routers block broadcasts) a plain TCP connection to
port 6668 on every address of the local /24 network. Whatever answers is checked with the known key at
protocol 3.5, 3.4 and 3.3, so a hit is a verified one.
"""
import concurrent.futures as cf
import ipaddress
import logging
import socket
import threading
import time

log = logging.getLogger("glowdeck.discover")

TUYA_PORT = 6668
VERSIONS = (3.5, 3.4, 3.3)


def local_ipv4s():
    """The PC's private IPv4 addresses (the one used for internet first)."""
    found = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))            # no packet is sent; just picks the outgoing interface
        found.append(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    try:
        found += socket.gethostbyname_ex(socket.gethostname())[2]
    except OSError:
        pass
    out = []
    for ip in found:
        try:
            a = ipaddress.ip_address(ip)
        except ValueError:
            continue
        if a.is_private and not a.is_loopback and not a.is_link_local and ip not in out:
            out.append(ip)
    return out


def subnet_hosts(ip, prefix=24):
    net = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)
    return [str(h) for h in net.hosts() if str(h) != ip]


def port_open(host, port=TUYA_PORT, timeout=0.4):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def scan_hosts(hosts, port=TUYA_PORT, timeout=0.4, workers=96):
    """Hosts that accept a TCP connection on `port`."""
    open_hosts = []
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(port_open, h, port, timeout): h for h in hosts}
        for f in cf.as_completed(futs):
            try:
                if f.result():
                    open_hosts.append(futs[f])
            except Exception:
                pass
    return sorted(open_hosts, key=lambda h: tuple(int(p) for p in h.split(".")))


def probe(ip, device_id, local_key, versions=VERSIONS):
    """The protocol version at which this device answers with this key, or None."""
    import tinytuya
    for v in versions:
        d = None
        try:
            d = tinytuya.Device(device_id, ip, local_key, version=v)
            d.set_socketTimeout(3)
            d.set_socketRetryLimit(1)
            st = d.status()
            if isinstance(st, dict) and "dps" in st:
                return v
        except Exception as e:
            log.info("probe %s v%s: %s", ip, v, e)
        finally:
            try:
                if d is not None:
                    d.close()
            except Exception:
                pass
    return None


def udp_scan_all():
    """Tuya's own broadcast scan (works on many networks). Returns {device_id: {"ip", "version"}}."""
    out = {}
    try:
        import tinytuya
        found = tinytuya.deviceScan(False, 4)
        for ip, d in (found or {}).items():
            gw = d.get("gwId") or d.get("id")
            if gw:
                out[gw] = {"ip": d.get("ip") or ip, "version": d.get("version")}
    except Exception as e:
        log.info("udp scan failed: %s", e)
    return out


class Locator:
    """Shared by all device controllers: scans are slow, so results are cached and scans never overlap."""

    UDP_TTL = 20
    TCP_TTL = 60

    def __init__(self):
        self.lk = threading.Lock()
        self.udp, self.udp_t = {}, 0.0
        self.hosts, self.hosts_t = [], 0.0

    def _lan_hosts(self):
        now = time.time()
        if self.hosts and now - self.hosts_t < self.TCP_TTL:
            return self.hosts
        hosts = []
        for ip in local_ipv4s():
            hosts += [h for h in scan_hosts(subnet_hosts(ip)) if h not in hosts]
        self.hosts, self.hosts_t = hosts, now
        return hosts

    def find(self, device_id, local_key):
        """{"ip", "version"} for this device on the LAN, or None."""
        with self.lk:
            now = time.time()
            if now - self.udp_t > self.UDP_TTL:
                self.udp, self.udp_t = udp_scan_all(), now
            hit = self.udp.get(device_id)
            if hit and hit.get("ip"):
                try:
                    first = (float(hit.get("version")),)
                except (TypeError, ValueError):
                    first = ()
                v = probe(hit["ip"], device_id, local_key, first + tuple(x for x in VERSIONS if x not in first))
                if v:
                    return {"ip": hit["ip"], "version": v}
            for host in self._lan_hosts():
                v = probe(host, device_id, local_key)
                if v:
                    return {"ip": host, "version": v}
        return None
