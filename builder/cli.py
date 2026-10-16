"""No global installs, account assumptions or network access outside explicit init/build."""
import argparse
import json
from pathlib import Path

from .contracts import BuilderError, validate
from .project import STEPS, bootstrap, generate
from .verification import balance, build, compare_delivery, doctor, pin_check, record, resume, stage, verify

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
    commands.add_parser('balance')
    commands.add_parser('stage', help='Stage a closed private-test ZIP from the current native build')
    rec = commands.add_parser('record')
    rec.add_argument('step', choices=STEPS)
    rec.add_argument('--status', choices=['ready', 'running', 'complete', 'blocked'], required=True)
    rec.add_argument('--evidence', action='append', default=[])
    rec.add_argument('--note', required=True)
    commands.add_parser('compare-delivery').add_argument('--directory', type=Path, required=True)
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
            result = balance(TOOLKIT, root)
        elif args.command == 'build':
            result = build(TOOLKIT, root, args.game_data)
        elif args.command == 'stage':
            result = stage(TOOLKIT, root)
        elif args.command == 'compare-delivery':
            result = compare_delivery(root, args.directory)
        print(json.dumps(result, indent=2))
    except (BuilderError, OSError, KeyError) as error:
        parser.exit(1, f'character-builder: {error}\n')
