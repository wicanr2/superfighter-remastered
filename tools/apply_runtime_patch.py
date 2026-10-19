"""只在已驗證的本專案 dosgolem 副本套用規格 001，輸出可回查補丁身分。"""

import difflib
import hashlib
import json
import pathlib


def sha(data):
    return hashlib.sha256(data).hexdigest()


project = pathlib.Path("/project")
work = project / "workplace"
source = work / "dosgolem-source"
base = json.loads((work / "dosgolem-source-manifest.json").read_text())
relative = "internal/dos/exec.go"
target = source / relative
old = target.read_text()
anchor = "\td.enterProgram(c, prog)\n\tif d.freeSeg < oldFree {"
replacement = ("\td.enterProgram(c, prog)\n"
               "\t// Spec 001: a supervisor-queued program starts with interrupts enabled.\n"
               "\t// Preserve the other flags; do not inherit CLI from a terminated TSR.\n"
               "\tc.SetFlags(c.Flags | cpu.IF)\n"
               "\tif d.freeSeg < oldFree {")
if old.count(anchor) != 1:
    raise ValueError("來源不符或補丁已套用，不自動改寫")
for record in base["tracked_files"]:
    if sha((source / record["name"]).read_bytes()) != record["sha256"]:
        raise ValueError(f"基底已變動：{record['name']}")
new = old.replace(anchor, replacement)
patch = "".join(difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True),
                                     fromfile="a/" + relative, tofile="b/" + relative))
target.write_text(new)
(project / "tools/dosgolem-queued-entry.patch").write_text(patch)
fixture = (project / "tools/queued_entry_test.go").read_bytes()
(source / "internal/dos/kdzz_queue_entry_test.go").write_bytes(fixture)
records = [{"name": r["name"], "sha256": sha((source / r["name"]).read_bytes())}
           for r in base["tracked_files"]]
records.append({"name": "internal/dos/kdzz_queue_entry_test.go", "sha256": sha(fixture)})
base["baseline_tracked_files_digest"] = base["tracked_files_digest"]
base["tracked_files"] = records
base["tracked_files_digest"] = sha(json.dumps(records, sort_keys=True).encode())
base["scope"] = "isolated project snapshot; queued-entry IF patch only; shared source unchanged"
base["patch"] = {"file": "tools/dosgolem-queued-entry.patch", "sha256": sha(patch.encode()),
                 "spec": "docs/spec/001-queued-entry-interrupts.md"}
base["working_tree_status"] = "local patch and additional regression test in isolated snapshot"
(work / "dosgolem-patched-manifest.json").write_text(json.dumps(base, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(base["patch"]))
