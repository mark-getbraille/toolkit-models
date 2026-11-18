"""A small writer of ZIM files (the offline library format of Kiwix and openZIM), written from the public description
of the format (https://wiki.openzim.org/wiki/ZIM_file_format) so that no GPL library (libzim) is needed. It uses only
the Python standard library, plus the `zstandard` package (BSD licence) when it is installed; without it the text is
compressed with xz (the standard lzma module), which every ZIM reader also reads.

It writes ZIM version 6.1 (the "new namespace" layout of libzim 7 and later):
  C/...                 the content: the book's pages (HTML), pictures and its style sheet
  M/...                 metadata: Name, Title, Language, Creator, Publisher, Date, Description, LongDescription,
                        License, Source, Tags, Flavour, Counter, and a 48x48 icon (Illustration_48x48@1)
  W/mainPage            a redirect to the welcome page (the book's index)
  X/listing/titleOrdered/v1   the front articles (the pages) in title order, for the Kiwix apps' suggestions
The header also has the old title pointer list (every entry in title order), which the Digital Accessibility
Toolkit's own reader (app/toolkit/library/zim.py) uses for its title search.

Clusters: the text (pages, metadata, style sheet) in zstd (or xz) clusters of about CLUSTER_SIZE bytes; pictures in
uncompressed clusters (they are compressed already). Everything is kept in memory until write(): fine for a textbook
(tens or hundreds of megabytes), not for a whole Wikipedia.

Use:
  w = ZimWriter()
  w.add("index", "Physics", html, "text/html", front=True)
  w.add("media/fig1.jpg", "", data, "image/jpeg")
  w.redirect("Physics_book", "Physics", "index")
  w.metadata({"Name": "openstax_physics", "Title": "Physics", ...})
  w.write("openstax_physics_2026-11.zim", main="index")
"""

import hashlib
import io
import lzma
import struct
import uuid
import zlib

CLUSTER_SIZE = 2_000_000          # bytes of text put together in one compressed cluster
HEADER = struct.Struct("<IHH16sIIQQQQIIQ")
MAGIC = 72173914
NO_PAGE = 0xFFFFFFFF
REDIRECT = 0xFFFF


def _zstd():
    """The zstandard module, or None when it is not installed (xz is used then)."""
    try:
        import zstandard
        return zstandard
    except ImportError:
        return None


def icon_png(rgb=(0x1F, 0x4E, 0x79), size=48):
    """A plain square PNG picture of one colour (the book's icon in the Kiwix apps), made with zlib only."""
    row = b"\x00" + bytes(rgb) * size
    raw = row * size

    def chunk(kind, data):
        """One PNG chunk: length, type, data and CRC."""
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


class ZimWriter:
    """Collects entries and writes them as one ZIM file (see the module docstring)."""

    def __init__(self, compression=None):
        """compression: "zstd", "xz" or None (zstd when the zstandard package is installed, else xz)."""
        self.compression = compression or ("zstd" if _zstd() else "xz")
        self.items = {}           # (namespace, path) -> dict(title, data, mimetype, front) or dict(target)
        self.counts = {}          # mimetype -> number of entries (M/Counter)

    def add(self, path, title, data, mimetype, front=False, namespace="C"):
        """Add an entry: path ("index", "media/fig1.jpg"), its title ("" for none), its bytes (or text) and its
        content type; front=True for a page a reader should list and search (an article)."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        self.items[(namespace, path)] = {"title": title, "data": data, "mimetype": mimetype, "front": front}
        if namespace == "C":
            self.counts[mimetype] = self.counts.get(mimetype, 0) + 1

    def redirect(self, path, title, target, namespace="C", target_namespace="C"):
        """Add a redirect: path (with its title) leads to target."""
        self.items[(namespace, path)] = {"title": title, "target": (target_namespace, target)}

    def has(self, path, namespace="C"):
        """True when path is already in the file."""
        return (namespace, path) in self.items

    def metadata(self, values, icon=None):
        """Add the metadata entries (M/Name, M/Title ...) and the icon (PNG bytes; a plain one when None)."""
        for name, value in values.items():
            if value:
                self.add(name, "", str(value), "text/plain", namespace="M")
        self.add("Illustration_48x48@1", "", icon or icon_png(), "image/png", namespace="M")

    # ------------------------------------------------------------------ writing

    def _clusters(self, keys):
        """Put the entries with data into clusters: [(compressed?, [key])]; text together, pictures apart."""
        text, binary = [], []
        for key in keys:
            item = self.items[key]
            if "data" not in item:
                continue
            kind = item["mimetype"]
            (text if kind.startswith("text/") or kind in ("application/javascript", "image/svg+xml")
             else binary).append(key)
        clusters = []
        for compressed, group in ((True, text), (False, binary)):
            current, size = [], 0
            for key in group:
                n = len(self.items[key]["data"])
                if current and size + n > CLUSTER_SIZE:
                    clusters.append((compressed, current))
                    current, size = [], 0
                current.append(key)
                size += n
            if current:
                clusters.append((compressed, current))
        return clusters

    def _cluster_bytes(self, compressed, keys):
        """The bytes of one cluster: the info byte, then the offsets and blobs (compressed or not)."""
        blobs = [self.items[k]["data"] for k in keys]
        total = 4 * (len(blobs) + 1) + sum(len(b) for b in blobs)
        wide = total >= 0xFFFFFFFF
        size, fmt = (8, "<Q") if wide else (4, "<I")
        pos, offsets = size * (len(blobs) + 1), []
        for b in blobs:
            offsets.append(pos)
            pos += len(b)
        offsets.append(pos)
        body = b"".join(struct.pack(fmt, o) for o in offsets) + b"".join(blobs)
        flag = 0x10 if wide else 0
        if not compressed:
            return bytes([1 | flag]) + body
        if self.compression == "zstd":
            return bytes([5 | flag]) + _zstd().ZstdCompressor(level=19).compress(body)
        return bytes([4 | flag]) + lzma.compress(body, format=lzma.FORMAT_XZ, preset=9)

    def write(self, path, main="index"):
        """Write the ZIM file to path; main: the path of the welcome page (C namespace). Returns the number of
        front articles."""
        if main and ("C", main) in self.items:
            self.redirect("mainPage", "", main, namespace="W")
        counter = ";".join(f"{k}={v}" for k, v in sorted(self.counts.items()))
        self.add("Counter", "", counter, "text/plain", namespace="M")
        # The title listing of the front articles needs their final numbers, so it is added as a placeholder now
        # (its size depends only on how many there are) and filled once the order is known.
        fronts = [k for k, v in self.items.items() if v.get("front")]
        self.add("listing/titleOrdered/v1", "", b"\0" * (4 * len(fronts)), "application/octet-stream",
                 namespace="X")
        keys = sorted(self.items, key=lambda k: (k[0] + k[1]).encode("utf-8"))
        index = {k: i for i, k in enumerate(keys)}

        def title_of(k):
            """The title used for sorting: the title, else the path."""
            return self.items[k].get("title") or k[1]
        by_title = sorted(keys, key=lambda k: (k[0] + title_of(k)).encode("utf-8"))
        listing = [index[k] for k in by_title if self.items[k].get("front")]
        self.items[("X", "listing/titleOrdered/v1")]["data"] = b"".join(struct.pack("<I", i) for i in listing)
        mimes = sorted({v["mimetype"] for v in self.items.values() if "data" in v})
        mime_no = {m: i for i, m in enumerate(mimes)}
        clusters = self._clusters(keys)
        where = {}
        for c, (_compressed, group) in enumerate(clusters):
            for b, key in enumerate(group):
                where[key] = (c, b)
        dirents = []
        for key in keys:
            ns, p = key
            item = self.items[key]
            title = item.get("title", "")
            title_bytes = b"" if title == p else title.encode("utf-8")
            if "target" in item:
                head = struct.pack("<HBcII", REDIRECT, 0, ns.encode(), 0, index[item["target"]])
            else:
                c, b = where[key]
                head = struct.pack("<HBcIII", mime_no[item["mimetype"]], 0, ns.encode(), 0, c, b)
            dirents.append(head + p.encode("utf-8") + b"\0" + title_bytes + b"\0")
        mime_list = b"".join(m.encode("utf-8") + b"\0" for m in mimes) + b"\0"
        n = len(keys)
        mime_pos = HEADER.size
        path_ptr_pos = mime_pos + len(mime_list)
        title_ptr_pos = path_ptr_pos + 8 * n
        dirent_pos = title_ptr_pos + 4 * n
        positions, pos = [], dirent_pos
        for d in dirents:
            positions.append(pos)
            pos += len(d)
        cluster_ptr_pos = pos
        cluster_data = [self._cluster_bytes(compressed, group) for compressed, group in clusters]
        pos = cluster_ptr_pos + 8 * len(cluster_data)
        cluster_positions = []
        for data in cluster_data:
            cluster_positions.append(pos)
            pos += len(data)
        checksum_pos = pos
        main_index = index[("W", "mainPage")] if ("W", "mainPage") in index else NO_PAGE
        out = io.BytesIO()
        out.write(HEADER.pack(MAGIC, 6, 1, uuid.uuid4().bytes, n, len(cluster_data), path_ptr_pos, title_ptr_pos,
                              cluster_ptr_pos, mime_pos, main_index, NO_PAGE, checksum_pos))
        out.write(mime_list)
        out.write(b"".join(struct.pack("<Q", p) for p in positions))
        out.write(b"".join(struct.pack("<I", index[k]) for k in by_title))
        out.write(b"".join(dirents))
        out.write(b"".join(struct.pack("<Q", p) for p in cluster_positions))
        for data in cluster_data:
            out.write(data)
        body = out.getvalue()
        with open(path, "wb") as f:
            f.write(body)
            f.write(hashlib.md5(body).digest())
        return len(listing)
