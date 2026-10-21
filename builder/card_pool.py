"""Retain observed native targets while authors change their original card pool."""
from collections import Counter, defaultdict
import json

from .contracts import BuilderError, contained, digest, encoded, input_hash, read_json, validate
from .project import atomic
from .verification import native_evidence


BASELINE = '.builder/card-pool-baseline.json'


def pool_cells(cards):
    return dict(sorted(Counter(c['rarity'] + '/' + c['type'] for c in cards).items()))


def comparator_cards(evidence, comparator):
    matches = [c for c in evidence.get('native_comparators', []) if c['character'] == comparator]
    if len(matches) != 1:
        raise BuilderError('Choose an exact native comparator ID: ' + ', '.join(
            c['character'] for c in evidence.get('native_comparators', [])))
    cards = matches[0]['cards']
    if not cards or any(c.get('rarity') not in ('Common', 'Uncommon', 'Rare')
                        or c.get('type') not in ('Attack', 'Skill', 'Power') for c in cards):
        raise BuilderError('Native comparator has no supported reward pool')
    return cards


def card_hash(card):
    # Ignore JSON property order, but retain every authored value including art/text.
    return digest(json.dumps(card, sort_keys=True, ensure_ascii=False, allow_nan=False).encode())


def plan_cards(toolkit, root, comparator=None, replace_baseline=False):
    config, cards, _, lock = validate(toolkit, root)
    if not config['features']['cards']:
        raise BuilderError('Card-pool planning requires custom cards; native fallback is not an original pool')
    path = contained(root, BASELINE)
    if replace_baseline and comparator is None:
        raise BuilderError('--replace-baseline requires --comparator and a passing current native lab')
    if comparator is not None:
        if path.exists() and not replace_baseline:
            raise BuilderError('Card-pool baseline already exists; omit --comparator to plan edits or use --replace-baseline explicitly')
        evidence = native_evidence(toolkit, root)
        if evidence is None:
            raise BuilderError('Capturing card-pool targets requires a passing current test-native lab')
        native = comparator_cards(evidence, comparator)
        index = read_json(contained(root, '.builder/native-evidence.json'))
        source = contained(root, index['path'])
        if digest(source.read_bytes()) != index['sha256'] or read_json(source) != evidence:
            raise BuilderError('Native evidence changed during baseline capture; previous baseline preserved')
        baseline = dict(schema_version=1, project=config['id'], target=config['target'],
                        toolkit_commit=lock['toolkit_commit'], game=evidence['game'],
                        comparator=comparator, target_cells=pool_cells(native),
                        evidence=index, input_sha256=input_hash(root),
                        original_cards={c['id']: card_hash(c) for c in cards})
        atomic(path, encoded(baseline))
    if not path.exists():
        raise BuilderError('No card-pool baseline; run plan-cards --comparator with a passing current native lab first')
    baseline = read_json(path)
    if (not isinstance(baseline, dict) or baseline.get('schema_version') != 1 or baseline.get('project') != config['id']
            or baseline.get('target') != config['target'] or baseline.get('toolkit_commit') != lock['toolkit_commit']):
        raise BuilderError('Card-pool baseline identity/target/toolkit changed; capture a fresh baseline explicitly')
    index = baseline['evidence']
    evidence_path = contained(root, index['path'])
    if not evidence_path.is_file() or digest(evidence_path.read_bytes()) != index['sha256']:
        raise BuilderError('Card-pool baseline native evidence changed or disappeared')
    evidence = read_json(evidence_path)
    target = pool_cells(comparator_cards(evidence, baseline['comparator']))
    if (evidence.get('kind') != 'native' or evidence.get('ok') is not True or evidence.get('process_exit') != 0
            or evidence.get('failures') or evidence.get('game') != baseline['game']
            or evidence.get('toolkit_commit') != baseline['toolkit_commit']
            or evidence.get('input_sha256') != baseline['input_sha256'] or target != baseline['target_cells']):
        raise BuilderError('Card-pool baseline does not match its captured native evidence')
    reward = [c for c in cards if c['rarity'] != 'Basic']
    actual = pool_cells(reward)
    keys = sorted(target.keys() | actual.keys())
    current = {c['id']: card_hash(c) for c in cards}
    original = baseline['original_cards']
    mechanics = defaultdict(list)
    for card in reward:
        mechanics[card_hash({key: card[key] for key in ('type', 'target', 'exhaust', 'base', 'upgrade')})].append(card['id'])
    return dict(kind='planning', baseline=BASELINE, comparator=baseline['comparator'], game=baseline['game'],
                native_validation='Not performed by planning',
                baseline_input_sha256=baseline['input_sha256'], input_sha256=input_hash(root),
                reward_cards=len(reward), expected_reward_cards=sum(target.values()),
                basic_cards=[c['id'] for c in cards if c['rarity'] == 'Basic'],
                target_cells=target, actual_cells=actual, distribution_matches=target == actual,
                deficits={k: target.get(k, 0) - actual.get(k, 0) for k in keys if target.get(k, 0) > actual.get(k, 0)},
                excess={k: actual.get(k, 0) - target.get(k, 0) for k in keys if actual.get(k, 0) > target.get(k, 0)},
                original_cards=dict(unchanged=sorted(k for k in original if current.get(k) == original[k]),
                                    changed=sorted(k for k in original if k in current and current[k] != original[k]),
                                    removed=sorted(original.keys() - current.keys())),
                added_cards=sorted(current.keys() - original.keys()),
                identical_mechanics=sorted(sorted(ids) for ids in mechanics.values() if len(ids) > 1),
                gaps=['Planning targets describe the captured build; edits require fresh native verification and balance --comparator',
                      'Cell counts and identical-mechanics warnings do not establish archetype coverage, originality or human balance'])
