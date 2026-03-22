#!/usr/bin/env python3
"""
Patch selected Ren'Py save keys inside the `log` entry and rewrite `signatures`
using the default Ren'Py signing flow validated for Eternum.
"""

from __future__ import annotations

import argparse
import base64
import os
import pathlib
import pickletools
import shutil
import struct
import tempfile
import zipfile

from ecdsa import SigningKey, VerifyingKey


DEFAULT_KEY_FILE = pathlib.Path.home() / "AppData" / "Roaming" / "RenPy" / "tokens" / "security_keys.txt"


def parse_assignments(items: list[str], expected_type: str) -> list[tuple[str, str | int]]:
    assignments: list[tuple[str, str | int]] = []
    for item in items:
        if "=" not in item:
            raise SystemExit(f"Invalid assignment '{item}'. Expected KEY=VALUE.")
        key, raw_value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise SystemExit(f"Invalid assignment '{item}'. Empty key.")
        if expected_type == "int":
            try:
                value: str | int = int(raw_value, 10)
            except ValueError as exc:
                raise SystemExit(f"Invalid integer value in '{item}'.") from exc
        else:
            value = raw_value
        assignments.append((key, value))
    return assignments


def load_signing_keys(key_file: pathlib.Path) -> tuple[bytes, str, VerifyingKey]:
    line = next((ln for ln in key_file.read_text(encoding="utf-8").splitlines() if ln.startswith("signing-key ")), None)
    if not line:
        raise SystemExit(f"No signing-key entry found in {key_file}")

    _, priv_b64, pub_b64 = line.split()
    private_key = base64.b64decode(priv_b64)
    public_key = VerifyingKey.from_der(base64.b64decode(pub_b64))
    return private_key, pub_b64, public_key


def find_value_op(ops: list[tuple[object, object, int]], key: str) -> tuple[object, object, int]:
    for index, (_, arg, _) in enumerate(ops[:-1]):
        if isinstance(arg, str) and arg == key:
            scan = index + 1
            while scan < len(ops) and ops[scan][0].name.endswith("INPUT"):
                scan += 1
            return ops[scan]
    raise RuntimeError(f"Key not found: {key}")


def read_current_value(log_data: bytes, key: str) -> object:
    return find_value_op(list(pickletools.genops(log_data)), key)[1]


def patch_string(log_data: bytes, key: str, new_value: str) -> bytes:
    ops = list(pickletools.genops(log_data))
    op, arg, pos = find_value_op(ops, key)
    if not isinstance(arg, str):
        raise RuntimeError(f"{key} is not a string")

    encoded = new_value.encode("utf-8")
    if op.name == "BINUNICODE":
        old_len = struct.unpack("<I", log_data[pos + 1:pos + 5])[0]
        return log_data[:pos] + b"X" + struct.pack("<I", len(encoded)) + encoded + log_data[pos + 5 + old_len:]

    if op.name == "SHORT_BINUNICODE":
        old_len = log_data[pos + 1]
        if len(encoded) > 255:
            raise RuntimeError(f"{key} is too long for SHORT_BINUNICODE")
        return log_data[:pos] + b"\x8c" + bytes([len(encoded)]) + encoded + log_data[pos + 2 + old_len:]

    raise RuntimeError(f"Unsupported opcode {op.name} for string key {key}")


def patch_int(log_data: bytes, key: str, new_value: int) -> bytes:
    ops = list(pickletools.genops(log_data))
    op, arg, pos = find_value_op(ops, key)
    if not isinstance(arg, int):
        raise RuntimeError(f"{key} is not an int")

    chunk = b"J" + struct.pack("<i", new_value)
    if op.name == "BININT":
        end = pos + 5
    elif op.name == "BININT1":
        end = pos + 2
    elif op.name == "BININT2":
        end = pos + 3
    else:
        raise RuntimeError(f"Unsupported opcode {op.name} for int key {key}")

    return log_data[:pos] + chunk + log_data[end:]


def rewrite_archive(save_path: pathlib.Path, blobs: dict[str, bytes], infos: list[zipfile.ZipInfo], archive_comment: bytes) -> None:
    fd, tmp_name = tempfile.mkstemp(prefix="renpy-edit-", suffix=".save", dir=str(save_path.parent))
    os.close(fd)

    try:
        with zipfile.ZipFile(tmp_name, "w") as dst:
            dst.comment = archive_comment
            for info in infos:
                zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
                zi.compress_type = info.compress_type
                zi.comment = info.comment
                zi.extra = info.extra
                zi.create_system = info.create_system
                zi.create_version = info.create_version
                zi.extract_version = info.extract_version
                zi.flag_bits = info.flag_bits
                zi.volume = info.volume
                zi.internal_attr = info.internal_attr
                zi.external_attr = info.external_attr
                dst.writestr(zi, blobs[info.filename])

        shutil.move(tmp_name, save_path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Patch and re-sign a Ren'Py .save archive.")
    parser.add_argument("--save", required=True, type=pathlib.Path, help="Path to the .save archive.")
    parser.add_argument("--key-file", type=pathlib.Path, default=DEFAULT_KEY_FILE, help="Path to Ren'Py security_keys.txt.")
    parser.add_argument("--backup", action="store_true", help="Create <save>.bak before writing.")
    parser.add_argument("--set-string", action="append", default=[], metavar="KEY=VALUE", help="Patch a string value in log.")
    parser.add_argument("--set-int", action="append", default=[], metavar="KEY=VALUE", help="Patch an integer value in log.")
    parser.add_argument("--show", action="append", default=[], metavar="KEY", help="Print the current value for a key.")
    parser.add_argument("--verify-only", action="store_true", help="Verify the current signature and requested keys without writing.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    save_path = args.save.resolve()
    key_file = args.key_file.resolve()
    string_updates = parse_assignments(args.set_string, "string")
    int_updates = parse_assignments(args.set_int, "int")

    if not save_path.exists():
        raise SystemExit(f"Save file not found: {save_path}")
    if not key_file.exists():
        raise SystemExit(f"Key file not found: {key_file}")
    if not args.verify_only and not (string_updates or int_updates):
        raise SystemExit("Nothing to patch. Use --set-string, --set-int, or --verify-only.")

    private_key_der, pub_b64, verifying_key = load_signing_keys(key_file)

    with zipfile.ZipFile(save_path, "r") as src:
        infos = src.infolist()
        blobs = {info.filename: src.read(info.filename) for info in infos}
        archive_comment = src.comment

    if "log" not in blobs:
        raise SystemExit("Archive does not contain 'log'.")
    if "signatures" not in blobs:
        raise SystemExit("Archive does not contain 'signatures'.")

    current_log = blobs["log"]

    for key in args.show:
        print(f"{key}={read_current_value(current_log, key)}")

    if args.verify_only:
        parts = blobs["signatures"].decode("utf-8").strip().split()
        if len(parts) != 3 or parts[0] != "signature":
            raise SystemExit("Invalid signatures format.")
        _, _, sig_b64 = parts
        verified = verifying_key.verify(base64.b64decode(sig_b64), current_log)
        print(f"verify_default={verified}")
        return

    for key, value in string_updates:
        current_log = patch_string(current_log, key, str(value))

    for key, value in int_updates:
        current_log = patch_int(current_log, key, int(value))

    signing_key = SigningKey.from_der(private_key_der)
    signature = signing_key.sign(current_log)
    if not verifying_key.verify(signature, current_log):
        raise RuntimeError("Signature verification failed after patching.")

    if args.backup:
        backup_path = save_path.with_suffix(save_path.suffix + ".bak")
        shutil.copy2(save_path, backup_path)
        print(f"backup={backup_path}")

    blobs["log"] = current_log
    blobs["signatures"] = f"signature {pub_b64} {base64.b64encode(signature).decode()}\n".encode("utf-8")
    rewrite_archive(save_path, blobs, infos, archive_comment)

    for key in args.show:
        print(f"{key}={read_current_value(current_log, key)}")

    print("patched_and_resigned_ok")


if __name__ == "__main__":
    main()
