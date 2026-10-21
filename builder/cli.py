"""Agent-neutral authoring with explicit project, dependency and native-lab inputs."""
import argparse
import json
from pathlib import Path

from .contracts import BuilderError, validate
from .project import STEPS, bootstrap, generate
from .verification import balance, build, compare_delivery, doctor, pin_check, record, resume, stage, verify
from .native_lab import prepare, run_native
from .publishing import prepare_publish, check_publish
from .card_pool import plan_cards

TOOLKIT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description='Standalone StS2 character authoring toolkit (Python 3.11+)')
    parser.add_argument('--project', type=Path, default=Path.cwd(), help='Project root; never the toolkit submodule')
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init', help='Create a new local Git repository with a pinned toolkit submodule')
    init.add_argument('--id', required=True)
    init.add_argument('--name')
    init.add_argument('--idea', required=True)
    init.add_argument('--author', default='Character author')
    init.add_argument('--mode', choices=['guided', 'expedited'], default='guided')
    init.add_argument('--toolkit-source', default='https://github.com/CapeKid/Sts2CharacterBuilder.git')
    init.add_argument('--toolkit-commit', help='Full SHA; defaults to the invoking toolkit commit')
    for name in ('doctor', 'build'):
        commands.add_parser(name).add_argument('--game-data', required=name == 'build')
    commands.add_parser('validate')
    commands.add_parser('generate').add_argument('--check', action='store_true')
    commands.add_parser('resume')
    commands.add_parser('test', help='Structural verification; never claims native gameplay coverage')
    commands.add_parser('balance').add_argument('--comparator', help='Exact character ID from current native lab evidence')
    pool = commands.add_parser('plan-cards', help='Capture native pool targets, then track authoring gaps without claiming current native parity')
    pool.add_argument('--comparator', help='Capture targets from an exact native character ID in a passing current lab')
    pool.add_argument('--replace-baseline', action='store_true', help='Explicitly replace targets and the original-card snapshot from current native evidence')
    commands.add_parser('stage', help='Stage a closed private-test ZIP from the current native build')
    lab = commands.add_parser('prepare-lab', help='Build a test-only probe and independently copy an owned game into a disposable lab')
    lab.add_argument('--game-root', required=True, type=Path)
    lab.add_argument('--baselib-root', required=True, type=Path)
    lab.add_argument('--workshop-root', required=True, type=Path)
    lab.add_argument('--steam-userdata', required=True, type=Path)
    lab.add_argument('--lab-id', required=True)
    native = commands.add_parser('test-native', help='Run a prepared one-shot isolated native probe')
    native.add_argument('--lab-id', required=True)
    native.add_argument('--timeout', default=240, type=int)
    rec = commands.add_parser('record')
    rec.add_argument('step', choices=STEPS)
    rec.add_argument('--status', choices=['ready', 'running', 'complete', 'blocked'], required=True)
    rec.add_argument('--evidence', action='append', default=[])
    rec.add_argument('--note', required=True)
    commands.add_parser('compare-delivery').add_argument('--directory', type=Path, required=True)
    for name in ('prepare-publish', 'check-publish'):
        publish = commands.add_parser(name, help='Prepare/check an offline private official-uploader workspace; never uploads')
        publish.add_argument('--workspace', required=True, help='New ID under private/workshop, not a path')
        publish.add_argument('--existing-item', type=int, help='Must match the explicit publishing.json update item')
        if name == 'prepare-publish':
            publish.add_argument('--uploader-archive', type=Path, required=True)
    args = parser.parse_args()
    root = args.project.resolve()
    try:
        if root.is_relative_to(TOOLKIT) and args.command != 'doctor':
            raise BuilderError('Choose a separate parent character project outside the toolkit checkout')
        if args.command not in {'init', 'doctor'}:
            *_, lock = validate(TOOLKIT, root)
            pin_check(TOOLKIT, root, lock)
        if args.command == 'init':
            result = bootstrap(TOOLKIT, root, args)
        elif args.command == 'doctor':
            result = doctor(TOOLKIT, root, args.game_data)
        elif args.command == 'validate':
            validate(TOOLKIT, root)
            result = {'status': 'valid', 'scope': 'authoring data only'}
        elif args.command == 'generate':
            result = generate(TOOLKIT, root, args.check)
        elif args.command == 'resume':
            result = resume(TOOLKIT, root)
        elif args.command == 'record':
            result = record(TOOLKIT, root, args.step, args.status, args.evidence, args.note)
        elif args.command == 'test':
            result = verify(TOOLKIT, root)
        elif args.command == 'balance':
            result = balance(TOOLKIT, root, args.comparator)
        elif args.command == 'plan-cards':
            result = plan_cards(TOOLKIT, root, args.comparator, args.replace_baseline)
        elif args.command == 'build':
            result = build(TOOLKIT, root, args.game_data)
        elif args.command == 'stage':
            result = stage(TOOLKIT, root)
        elif args.command == 'prepare-lab':
            result = prepare(TOOLKIT, root, args.game_root, args.baselib_root, args.workshop_root, args.steam_userdata, args.lab_id)
        elif args.command == 'test-native':
            result = run_native(TOOLKIT, root, args.lab_id, args.timeout)
        elif args.command == 'compare-delivery':
            result = compare_delivery(root, args.directory)
        elif args.command == 'prepare-publish':
            result = prepare_publish(TOOLKIT, root, args.workspace, args.uploader_archive, args.existing_item)
        elif args.command == 'check-publish':
            result = check_publish(TOOLKIT, root, args.workspace, args.existing_item)
        print(json.dumps(result, indent=2))
    except (BuilderError, OSError, KeyError) as error:
        parser.exit(1, f'character-builder: {error}\n')
