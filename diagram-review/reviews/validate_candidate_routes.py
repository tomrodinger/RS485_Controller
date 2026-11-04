#!/usr/bin/env python3
"""Validate candidate route metadata and SVG against independently sourced nets.

Usage: python3 diagram-review/reviews/validate_candidate_routes.py PATH.routes.json
The adjacent PATH.svg is checked. This does not inspect raster pixels or establish
physical connector-face orientation; the final image still needs visual review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

CLASSES = {"red": "MOTOR_VPLUS", "gnd": "COMMON_GND", "a": "RS485_A", "b": "RS485_B"}
# Independent rendering convention: source net classes must retain these colours.
STROKES = {"MOTOR_VPLUS": "#d84042", "COMMON_GND": "#283335", "RS485_A": "#16835e", "RS485_B": "#256bc1"}
SVG = "{http://www.w3.org/2000/svg}"


def normalize(ref):
    if re.fullmatch(r"J[12]\.\d+", ref):
        return "CONTROLLER." + ref
    match = re.fullmatch(r"Motor([12])\.([1-6])", ref)
    if match:
        return f"MOTOR{match[1]}.J4.{match[2]}"
    return ref


def points(value):
    if isinstance(value, str):
        nums = [float(n) for n in re.findall(r"[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?", value)]
        if len(nums) % 2:
            raise ValueError("odd SVG coordinate count")
        value = list(zip(nums[::2], nums[1::2]))
    result = tuple(tuple(float(n) for n in p) for p in value)
    if any(len(p) != 2 or not all(math.isfinite(n) for n in p) for p in result):
        raise ValueError("coordinates must be finite x/y pairs")
    return result


class Graph:
    def __init__(self):
        self.edges = {}

    def link(self, a, b):
        self.edges.setdefault(a, set()).add(b)
        self.edges.setdefault(b, set()).add(a)

    def component(self, start):
        seen, stack = {start}, [start]
        while stack:
            for node in self.edges.get(stack.pop(), ()):
                if node not in seen:
                    seen.add(node)
                    stack.append(node)
        return seen


def rounded_path_matches(element, route):
    """Accept a rounded path only when every bend preserves the route corridor.

    The quadratic control points must equal the declared bends. Each curve's
    endpoints must stay on its adjacent segments, within half their length.
    Arbitrary curves, extra segments and a changed terminal are rejected.
    """
    raw = element.get('d', '')
    tokens = re.findall(r'[A-Za-z]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?', raw)
    commands = []
    i = 0
    try:
        while i < len(tokens):
            op = tokens[i]
            count = {'M': 2, 'L': 2, 'Q': 4}[op]
            values = tuple(float(v) for v in tokens[i + 1:i + 1 + count])
            if len(values) != count or not all(math.isfinite(v) for v in values):
                return False
            commands.append((op, tuple(zip(values[::2], values[1::2]))))
            i += count + 1
    except (KeyError, ValueError):
        return False
    if not commands or commands[0] != ('M', (route[0],)) or commands[-1] != ('L', (route[-1],)):
        return False
    corners = [(route[j-1], route[j], route[j+1]) for j in range(1, len(route)-1)
               if route[j-1] != route[j] and route[j] != route[j+1]]
    if len(commands) != 2 + 2 * len(corners):
        return False
    def on_half_segment(p, corner, adjacent):
        length = math.dist(corner, adjacent)
        cross = (p[0]-corner[0])*(adjacent[1]-corner[1]) - (p[1]-corner[1])*(adjacent[0]-corner[0])
        dot = sum((p[k]-corner[k])*(adjacent[k]-corner[k]) for k in (0, 1))
        return abs(cross) < 1e-5 and dot >= -1e-5 and math.dist(p, corner) <= length / 2 + 1e-5
    for index, (before, corner, after) in enumerate(corners):
        line, curve = commands[1 + index*2:3 + index*2]
        if line[0] != 'L' or curve[0] != 'Q' or curve[1][0] != corner:
            return False
        if not on_half_segment(line[1][0], corner, before) or not on_half_segment(curve[1][1], corner, after):
            return False
    return True


def validate(canonical, route_path):
    errors, warnings = [], []
    check = lambda condition, message: errors.append(message) if not condition else None
    model = json.loads(canonical.read_text())
    candidate = json.loads(route_path.read_text())
    if not route_path.name.endswith(".routes.json"):
        raise ValueError("candidate filename must end in .routes.json")
    svg_path = Path(str(route_path)[:-len(".routes.json")] + ".svg")
    svg = ET.parse(svg_path).getroot()
    polylines = list(svg.iter(SVG + "polyline"))
    curves = list(svg.iter(SVG + "path"))
    parents = {child: parent for parent in svg.iter() for child in parent}
    source_classes = {}
    for net, endpoints in model["net_classes"].items():
        for endpoint in endpoints:
            check(endpoint not in source_classes, f"canonical endpoint appears in multiple classes: {endpoint}")
            source_classes[endpoint] = net

    # Verify the canonical source snapshots still match accessible source files.
    # Missing sibling repositories reduce coverage, rather than invalidating the
    # retained audited source-net snapshot embedded in the canonical document.
    project = Path(__file__).resolve().parents[2]
    source_hashes = 0
    sources = {s["id"]: s for s in model["source_evidence"]}
    for source in sources.values():
        path = project / source["path"]
        if path.exists():
            check(hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"],
                  f"canonical evidence is stale; source hash changed: {source['path']}")
            source_hashes += 1
        else:
            warnings.append(f"source unavailable; using retained audited snapshot: {source['path']}")

    # Cross-check the canonical classes and internal links against independent
    # raw PCB net names, not against the renderer's route list.
    raw_classes = {"GND": "COMMON_GND", "+20V": "MOTOR_VPLUS", "+24V": "MOTOR_VPLUS",
                   "+3.3V": "AUX_3V3", "+5V": "AUX_5V"}
    for source_id, devices in [("CONTROLLER_PCB", ["CONTROLLER"]), ("MOTOR_PCB", ["MOTOR1", "MOTOR2"])]:
        for contact, net in sources[source_id]["extracted_contact_nets"].items():
            expected = raw_classes.get(net)
            if expected is None:
                expected = {"RS485A": "RS485_A", "RS485B": "RS485_B"}.get(net.split("/")[-1].replace("_", ""))
            check(expected is not None, f"unrecognized independent source net: {net}")
            for device in devices:
                check(source_classes.get(device + "." + contact) == expected,
                      f"canonical class disagrees with source PCB: {device}.{contact}")

    external, full = Graph(), Graph()
    internal_groups = [set(group) for group in model["onboard_same_net_groups"]]
    for motor in ("MOTOR1", "MOTOR2"):
        for a, b in ((3, 5), (4, 6)):
            required = {f"{motor}.J4.{a}", f"{motor}.J4.{b}"}
            check(any(required <= group for group in internal_groups), f"missing motor internal equivalence: {sorted(required)}")
    for group in internal_groups:
        check(len({source_classes.get(e) for e in group}) == 1, f"internal link joins unlike source nets: {sorted(group)}")
        first = next(iter(group))
        for endpoint in group:
            full.link(first, endpoint)

    anchors = {ref: points([xy])[0] for ref, xy in candidate["anchors"].items()}
    endpoint_usage, node_classes, route_geometry = set(), {}, []
    for index, route in enumerate(candidate["routes"], 1):
        prefix = f"route {index} ({route['from']} -> {route['to']})"
        net = CLASSES.get(route["net"])
        check(net is not None, f"{prefix}: unknown net tag {route['net']}")
        if net is None:
            continue
        path = points(route["points"])
        check(len(path) >= 2, f"{prefix}: fewer than two points")
        for ref, point in [(route["from"], path[0]), (route["to"], path[-1])]:
            check(ref in anchors, f"{prefix}: missing declared anchor {ref}")
            check(anchors.get(ref) == point, f"{prefix}: route misses anchor {ref}")
            endpoint = normalize(ref)
            endpoint_usage.add(endpoint)
            if endpoint.startswith(("CONTROLLER.", "MOTOR1.", "MOTOR2.")):
                check(endpoint in source_classes, f"{prefix}: nonexistent electrical contact {endpoint}")
                check(source_classes.get(endpoint) == net, f"{prefix}: {endpoint} belongs to {source_classes.get(endpoint)}, not {net}")
            check(node_classes.get(endpoint, net) == net, f"{prefix}: splice/endpoint reused across unlike nets: {endpoint}")
            node_classes[endpoint] = net
        a, b = normalize(route["from"]), normalize(route["to"])
        external.link(a, b)
        full.link(a, b)
        width = float(route["width"])
        check(math.isfinite(width) and width > 0, f"{prefix}: invalid line width")
        matches = [p for p in polylines if points(p.get("points", "")) == path and p.get("stroke", "").lower() != "white"]
        matches += [p for p in curves if p.get('stroke', '').lower() != 'white' and rounded_path_matches(p, path)]
        check(len(matches) == 1, f"{prefix}: expected one matching rendered route; found {len(matches)}")
        if len(matches) == 1:
            inline = dict(part.split(":", 1) for part in matches[0].get("style", "").split(";") if ":" in part)
            inline = {key.strip(): value.strip() for key, value in inline.items()}
            check(inline.get("stroke", matches[0].get("stroke", "")).lower() == STROKES[net], f"{prefix}: rendered colour disagrees with source net class")
            check(float(inline.get("stroke-width", matches[0].get("stroke-width", "nan"))) == width, f"{prefix}: rendered width disagrees with metadata")
            check(inline.get("fill", matches[0].get("fill")) == "none", f"{prefix}: polyline must not have a filled interior")
            element = matches[0]
            while element is not None:
                style = dict(part.split(":", 1) for part in element.get("style", "").split(";") if ":" in part)
                style = {key.strip(): value.strip() for key, value in style.items()}
                check(not element.get("transform"), f"{prefix}: route has an unmodelled SVG transform")
                check(style.get("display", element.get("display")) != "none", f"{prefix}: route is hidden by display:none")
                check(style.get("visibility", element.get("visibility")) not in ("hidden", "collapse"), f"{prefix}: route is hidden")
                for attr in ("opacity", "stroke-opacity"):
                    check(float(style.get(attr, element.get(attr, "1"))) > 0, f"{prefix}: route has zero {attr}")
                element = parents.get(element)
        route_geometry.append((net, a, b, path))

    # This excludes internal motor links: a missing external onward pair cannot
    # be hidden by the source's duplicated A/B contacts. Allow the documented
    # alternate controller group without demanding a redundant external jumper.
    alternatives = model["allowed_variations"]["controller_bus_group_alternative"]
    for start, end in model["required_external_wire_paths"]:
        acceptable = [start] + ([alternatives[start]] if start in alternatives else [])
        check(any(end in external.component(s) for s in acceptable), f"missing required external path: {start} -> {end}")
    for spare in model["forbidden_connectivity"]["spare_motor2_contacts_must_have_no_external_termination"]:
        check(spare not in endpoint_usage, f"motor 2 spare has an unexpected external electrical route: {spare}")

    # Each source class must stay disjoint after real wires and source-derived
    # internal equivalences are combined, including the unused auxiliary rails.
    for endpoint in source_classes:
        component = full.component(endpoint)
        classes = {source_classes[e] for e in component if e in source_classes}
        check(len(classes) == 1, f"shorted source net classes in component at {endpoint}: {sorted(classes)}")
    for net in CLASSES.values():
        endpoints = model["net_classes"][net]
        check(set(endpoints) <= full.component(endpoints[0]), f"incomplete full net connectivity: {net}")

    # Different names cannot conceal two unlike-net physical endpoints occupying
    # the same location. Ordinary wire crossings remain a visual halo/dot check.
    positions = {}
    for net, a, b, path in route_geometry:
        for ref, point in ((a, path[0]), (b, path[-1])):
            check(positions.get(point, (net, ref))[0] == net,
                  f"unlike-net endpoints share coordinate {point}: {ref} and {positions.get(point)}")
            positions[point] = (net, ref)

    selected = sorted(e for e in endpoint_usage if e.startswith("CONTROLLER.J2."))
    coverage = [
        "Checked: independent source snapshots, actual contact net classes, external paths, internal A/B equivalence, four disjoint nets, route endpoints, SVG polyline geometry or constrained rounded-path bends, colours and widths.",
        "Not machine-checked: USB mechanical cable, insulation caps on omitted spare stubs, detached functional-key/body geometry, physical contact count or mating-face orientation, raster visibility/occlusion, crossing halos/junction dots, actual-size readability.",
        "Motor2 spare contacts are internally on their A/B nets; absence of an external route does not prove their caps are drawn correctly.",
    ]
    return {"candidate": str(route_path), "svg": str(svg_path), "passed": not errors,
            "route_count": len(candidate["routes"]), "required_path_count": len(model["required_external_wire_paths"]),
            "verified_source_hashes": source_hashes, "selected_controller_j2_contacts": selected,
            "errors": list(dict.fromkeys(errors)), "warnings": warnings, "coverage": coverage}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("routes", type=Path, nargs="+")
    parser.add_argument("--canonical", type=Path, default=Path(__file__).with_name("canonical-netlist.json"))
    parser.add_argument("--json", action="store_true", help="emit structured reports")
    args = parser.parse_args()
    results = []
    for path in args.routes:
        try:
            results.append(validate(args.canonical, path))
        except (OSError, ValueError, KeyError, TypeError, IndexError, ET.ParseError) as exc:
            results.append({"candidate": str(path), "passed": False, "errors": [f"invalid input: {exc}"]})
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            print(f"{'PASS' if result['passed'] else 'FAIL'} {result['candidate']}")
            if "route_count" in result:
                print(f"  {result['route_count']} routes; {result['required_path_count']} required external paths; {result['verified_source_hashes']} source hashes verified")
                print("  Selected J2 contacts: " + ", ".join(result["selected_controller_j2_contacts"]))
            for message in result.get("errors", []):
                print("  ERROR: " + message)
            for message in result.get("warnings", []):
                print("  WARNING: " + message)
            for message in result.get("coverage", []):
                print("  " + message)
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
