#!/usr/bin/env python3
"""Additional harness checks; electrical route checks stay independent.

This checks declared connector groups and wire widths against SVG output.
Visual review is still required for visibility, physical placement and legibility.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

from validate_candidate_routes import validate

ROOT = Path(__file__).resolve().parents[2]
NS = '{http://www.w3.org/2000/svg}'


def check(path):
    report = validate(Path(__file__).with_name('canonical-netlist.json'), path)
    data = json.loads(path.read_text())
    svg = ET.parse(path.with_name(path.name.replace('.routes.json', '.svg'))).getroot()
    errors = report['errors']
    for motor in (1, 2):
        for first, second in ((3, 4), (5, 6)):
            contacts = {f'Motor{motor}.{first}', f'Motor{motor}.{second}'}
            found = [h for h in data['housings'] if set(h['contacts']) == contacts]
            if len(found) != 1 or not found[0].get('shared_shell') or not found[0].get('isolated_cavities'):
                errors.append(f'Motor {motor}: A/B pair {first}/{second} needs one isolated two-cavity housing')
    for housing in data['housings']:
        if housing.get('cavity_count') != 2 or len(set(housing['contacts'])) != 2:
            errors.append(f'Invalid paired housing: {housing["id"]}')
        bodies = [node for node in svg.iter() if node.get('data-housing-id') == housing['id']]
        if len(bodies) != 1 or bodies[0].get('data-cavity-count') != '2':
            errors.append(f'Housing metadata does not match SVG shell: {housing["id"]}')
    power_widths = {float(r['width']) for r in data['routes'] if r['net'] in ('red', 'gnd')}
    if power_widths != {11.0}:
        errors.append(f'Power and ground must retain equal full width; found {power_widths}')
    for loom in data['looms']:
        if loom['plug_color'] != 'white' or loom['plug_contacts'] != 6:
            errors.append('Motor plug must be white, six-way')
        if loom['ground_wire_width'] != loom['power_wire_width']:
            errors.append('Motor harness ground is thinner than positive wire')
    report['passed'] = not errors
    report['harness_checks'] = {
        'one_two_cavity_shell_per_motor_pair': not errors,
        'power_and_ground_route_widths': sorted(power_widths),
        'white_six_way_plugs': len(data['looms']),
        'physical_geometry_requires_visual_review': True,
    }
    return report


if __name__ == '__main__':
    reports = [check(p) for p in sorted((ROOT / 'diagram-review/round2').glob('*.routes.json'))]
    assert reports, 'No round-two candidates found'
    target = ROOT / 'diagram-review/reviews/qa/round2-route-results.json'
    target.write_text(json.dumps(reports, indent=2) + '\n')
    for report in reports:
        print(('PASS' if report['passed'] else 'FAIL'), Path(report['candidate']).name)
        for error in report['errors']:
            print(' ', error)
    raise SystemExit(0 if all(r['passed'] for r in reports) else 1)
