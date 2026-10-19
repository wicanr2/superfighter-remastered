"""在 Docker 內安全盤點原始包，保留唯讀基準與 dosgolem 來源身分。"""

import argparse
import calendar
import hashlib
import json
import pathlib
import os
import stat
import subprocess
import sys


EXPECTED = "aaec980cbef5679fda8274ed3549eccc97229be48221360427718a1e635f9b1d"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def prepare(project, archive, source, snapshot=False):
    import zipfile

    raw = archive.read_bytes()
    if sha(raw) != EXPECTED:
        raise ValueError("來源包 SHA-256 不符，停止解包")
    work = project / "workplace"
    work.mkdir(exist_ok=True)
    records = []
    with zipfile.ZipFile(archive) as bundle:
        members = bundle.infolist()
        if len(members) > 2048 or sum(i.file_size for i in members) > 64 * 1024 * 1024:
            raise ValueError("來源項目或解包總量超過本次盤點上限")
        seen = set()
        # 完整驗證清單後才開始寫入。
        for item in members:
            name = item.filename
            path = pathlib.PurePosixPath(name)
            if (not path.parts or path.is_absolute() or ".." in path.parts
                    or "\\" in name or ":" in name or "\x00" in name
                    or stat.S_ISLNK(item.external_attr >> 16)):
                raise ValueError(f"不安全路徑：{name}")
            key = str(path).casefold()
            if key in seen:
                raise ValueError(f"正規化後重複路徑：{name}")
            seen.add(key)
        for item in members:
            if item.is_dir():
                continue
            path = pathlib.PurePosixPath(item.filename)
            group = "quarantine" if path.parts[0].casefold() == "cheat" else "orig"
            target = work / group / path
            if not target.resolve().is_relative_to((work / group).resolve()):
                raise ValueError(f"輸出路徑跳脫：{item.filename}")
            data = bundle.read(item)  # zipfile 同時核對 CRC。
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.is_symlink():
                raise ValueError(f"目的地不可為符號連結：{target}")
            if target.exists():
                if target.read_bytes() != data:
                    raise ValueError(f"既有來源副本已變動：{item.filename}")
            else:
                target.write_bytes(data)
                target.chmod(0o444)
            timestamp = calendar.timegm((*item.date_time, 0, 0, 0))
            os.utime(target, (timestamp, timestamp))
            records.append({"name": item.filename, "bytes": len(data),
                            "sha256": sha(data), "location": str(target.relative_to(work)),
                            "zip_date_time": item.date_time,
                            "mtime_policy": "ZIP DOS date/time interpreted as UTC for deterministic extraction"})
    save_json(work / "source-manifest.json", {
        "archive": archive.name, "archive_sha256": sha(raw),
        "zip_entries": len(members), "files": records,
        "python": sys.version, "method": "zipfile CRC + SHA-256; no executable run",
    })

    def git(*args):
        return subprocess.check_output(["git", "-C", str(source), *args])

    head = git("rev-parse", "HEAD").decode().strip()
    status = git("status", "--porcelain").decode()
    names = git("ls-files", "-z").decode().split("\x00")
    source_files = []
    for name in sorted(n for n in names if n):
        path = source / name
        if path.is_symlink():
            raise ValueError(f"dosgolem 來源含符號連結，須先核對：{name}")
        source_files.append({"name": name, "sha256": sha(path.read_bytes())})
    identity = sha(json.dumps(source_files, sort_keys=True).encode())
    if snapshot:
        output = work / "dosgolem-source"
        for record in source_files:
            target = output / record["name"]
            data = (source / record["name"]).read_bytes()
            if sha(data) != record["sha256"]:
                raise ValueError("建立副本期間來源已變動")
            if target.exists() and target.read_bytes() != data:
                raise ValueError(f"既有副本已變動，不覆寫：{record['name']}")
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_bytes(data)
    save_json(work / "dosgolem-source-manifest.json", {
        "source": "/home/anr2/cht/dosgolem", "head": head,
        "working_tree_status": status, "tracked_files": source_files,
        "tracked_files_digest": identity,
        "scope": "tracked working-tree files; source mounted read-only; no patches",
    })
    (work / "bin").mkdir(exist_ok=True)
    print(json.dumps({"files": len(records), "quarantined": sum(
        r["location"].startswith("quarantine/") for r in records),
        "dosgolem_head": head, "source_clean": not status,
        "tracked_files_digest": identity}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=pathlib.Path, default="/project")
    parser.add_argument("--archive", type=pathlib.Path, default="/inputs/快打至尊.jsdos")
    parser.add_argument("--source", type=pathlib.Path, default="/source")
    parser.add_argument("--snapshot", action="store_true", help="同時建立已驗證的獨立 dosgolem 副本")
    args = parser.parse_args()
    prepare(args.project, args.archive, args.source, args.snapshot)
