import json


def get_structure_and_counts(data, parent_key=''):
  """Recursively traverses a JSON object and maps each nested key path

  to its type and the count of elements or sub-keys.
  """
  results = {}

  if isinstance(data, dict):
    for k, v in data.items():
      full_key = f'{parent_key}.{k}' if parent_key else k
      if isinstance(v, dict):
        results[full_key] = {'type': 'dict', 'count': len(v)}
        results.update(get_structure_and_counts(v, full_key))
      elif isinstance(v, list):
        results[full_key] = {'type': 'list', 'count': len(v)}
      else:
        results[full_key] = {'type': 'primitive', 'count': 1}
  return results


def compare_json_files(file_path_1, file_path_2):
  """Compares key paths and value counts between two JSON files

  (e.g., English template vs Bengali translation).
  """
  with open(file_path_1, 'r', encoding='utf-8') as f1:
    data1 = json.load(f1)

  with open(file_path_2, 'r', encoding='utf-8') as f2:
    data2 = json.load(f2)

  struct1 = get_structure_and_counts(data1)
  struct2 = get_structure_and_counts(data2)

  keys1 = set(struct1.keys())
  keys2 = set(struct2.keys())

  missing_in_2 = keys1 - keys2
  missing_in_1 = keys2 - keys1

  print('=== STRUCTURAL COMPARISON REPORT ===\n')

  if missing_in_2:
    print(f'[ERROR] Keys present in File 1 but MISSING in File 2:')
    for k in sorted(missing_in_2):
      print(f'  - {k}')
  else:
    print('[OK] No keys missing from File 2.')

  if missing_in_1:
    print(f'\n[ERROR] Extra keys present in File 2 not found in File 1:')
    for k in sorted(missing_in_1):
      print(f'  - {k}')

  print('\n=== VALUE COUNT COMPARISON (Common Keys) ===')
  common_keys = keys1.intersection(keys2)
  mismatch_found = False

  for k in sorted(common_keys):
    c1 = struct1[k]['count']
    c2 = struct2[k]['count']
    if c1 != c2:
      mismatch_found = True
      print(
          f'  [MISMATCH] {k} -> File 1 Count: {c1} | File 2 Count: {c2} (Diff:'
          f' {abs(c1 - c2)})'
      )

  if not mismatch_found and not missing_in_1 and not missing_in_2:
    print('\n[SUCCESS] Perfect match! All keys and value counts align.')

import json


def validate_json_structure(data1, data2, path='root'):
  """Recursively compares two JSON objects based on type, key counts,

  and list item counts, ignoring translated key names.
  """
  if type(data1) != type(data2):
    print(
        f'[MISMATCH] Type mismatch at "{path}": {type(data1)} vs {type(data2)}'
    )
    return False

  if isinstance(data1, dict):
    if len(data1) != len(data2):
      print(
          f'[MISMATCH] Key count mismatch at "{path}": File 1 has {len(data1)}'
          f' keys, File 2 has {len(data2)} keys'
      )
      return False

    # Sort keys to compare structural alignment by position/index
    # rather than strict string matching (handles English vs Bengali keys)
    keys1 = sorted(list(data1.keys()))
    keys2 = sorted(list(data2.keys()))

    match = True
    for k1, k2 in zip(keys1, keys2):
      # We compare the children recursively using their sorted positions
      if not validate_json_structure(
          data1[k1], data2[k2], f'{path}.{k1} -> {k2}'
      ):
        match = False
    return match

  elif isinstance(data1, list):
    if len(data1) != len(data2):
      print(
          f'[MISMATCH] List item count mismatch at "{path}": File 1 has'
          f' {len(data1)} items, File 2 has {len(data2)} items'
      )
      return False

    match = True
    for i, (item1, item2) in enumerate(zip(data1, data2)):
      if not validate_json_structure(item1, item2, f'{path}[{i}]'):
        match = False
    return match

  return True


def run_diagnostics(file_path_1, file_path_2):
  """Loads two JSON files and runs the structural shape and count validation."""
  try:
    with open(file_path_1, 'r', encoding='utf-8') as f1:
      data1 = json.load(f1)
    with open(file_path_2, 'r', encoding='utf-8') as f2:
      data2 = json.load(f2)
  except json.JSONDecodeError as e:
    print(f'[JSON ERROR] Syntax error in JSON file: {e}')
    return

  print('=== STARTING STRUCTURAL & COUNT DIAGNOSTICS ===\n')
  is_valid = validate_json_structure(data1, data2)

  if is_valid:
    print(
        '\n[SUCCESS] Perfect match! All nested key counts and value/item counts'
        ' align correctly.'
    )
  else:
    print(
        '\n[FAILURE] Discrepancies found in counts or structures (see details'
        ' above).'
    )


# Example usage:
# run_diagnostics('english_template.json', 'bengali_translation.json')

# Example usage:
from jhora import const
json_path = const._LANGUAGE_PATH
_file_type = "json"
json_en = json_path + 'prediction_msgs_en.json'
json_bn = json_path + 'prediction_msgs_or.json'
assert len(json_en) == len(json_bn)
if _file_type.lower() == "text": exit()
run_diagnostics(json_en, json_bn)