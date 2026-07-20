import json
from pathlib import Path

pkg = Path(
    r"C:\Users\Admin\.cursor\projects\c-Users-Admin-Healthcare-prior-auth-system-main\agent-tools\00a9a63e-d467-487f-997b-2e9f17520122.txt"
)
data = json.loads(pkg.read_text(encoding="utf-8"))
print("fhir_packages count", len(data))
for item in sorted(data, key=lambda x: x["name"]):
    print(f"{item['name']:70} {item['size']:>12}")

tree_path = Path(
    r"C:\Users\Admin\.cursor\projects\c-Users-Admin-Healthcare-prior-auth-system-main\agent-tools\c2758f92-a6de-4825-93c1-db230a014551.txt"
)
tree = json.loads(tree_path.read_text(encoding="utf-8"))["tree"]
print("\n--- IG-related paths ---")
keys = (
    "ig_constants",
    "fhir_packages",
    "fhir_packages_extra",
    ".tgz",
    "SUPPORTED",
    "download_extra",
    "mcode",
    "qicore",
    "carin",
    "sdc",
)
for item in tree:
    p = item["path"]
    pl = p.lower()
    if any(k.lower() in pl for k in keys) or p.endswith(".tgz"):
        print(item["type"], p, item.get("size", ""))
