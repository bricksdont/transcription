import gzip
import json
import os
import pathlib
from collections import defaultdict, Counter
from random import shuffle
from typing import List


def load_pair(spoken_files: List[str], signed_files: List[str]):
    for spoken in spoken_files:
        with open(spoken, "r", encoding="utf-8") as spoken_f:
            spoken_lines = spoken_f.read().splitlines()
        for signed in signed_files:
            with open(signed, "r", encoding="utf-8") as signed_f:
                signed_lines = signed_f.read().splitlines()

            for sp, si in zip(spoken_lines, signed_lines):
                if sp != "" and si != "":
                    yield sp, si


def load_data():
    raw_dir = pathlib.Path(__file__).parent.joinpath('raw')

    for match in sorted(pathlib.Path(raw_dir).glob("**/*")):
        # if "sign_bank/46" not in str(match):
        #     continue

        if match.is_dir():
            children = [match.joinpath(str(f_name)) for f_name in os.listdir(match)]
            if all((c.is_file() for c in children)):
                spoken_files = [c for c in children if c.name.startswith('spoken')]
                signed_files = [c for c in children if c.name.startswith('signed')]  # and "us-ase" in c.name
                dir_name = str(match).partition("/raw/")[2]
                yield dir_name, load_pair(spoken_files, signed_files)


if __name__ == "__main__":
    statistics = defaultdict(Counter)

    compressed_dir = pathlib.Path(__file__).parent.joinpath('compressed')

    sets = defaultdict(list)

    mono = 0
    total = 0
    data = load_data()
    for name, data in data:
        dataset_dir = compressed_dir.joinpath(name)
        dataset_dir.mkdir(parents=True, exist_ok=True)

        data_list = list(data)
        shuffle(data_list)

        # At least 100 examples per dataset
        if len(data_list) < 100:
            continue

        for split, split_start, split_end in [('train', 0, 95), ('devtest', 95, 99), ('test', 99, 100)]:
            start_index, end_index = int(len(data_list) * split_start / 100), int(len(data_list) * split_end / 100)
            split_data = data_list[start_index: end_index]
            if len(split_data) == 0:
                continue

            sets[split].append(name)
            spoken_f = gzip.open(dataset_dir.joinpath(f'{split}.spoken.gz'), 'wt')
            signed_f = gzip.open(dataset_dir.joinpath(f'{split}.signed.gz'), 'wt')

            for sp, si in split_data:
                if sp[4:].strip() == "":
                    mono += 1
                    # TODO save mono sign language data
                    continue

                if sp[0] == '<' and "<" in si[1:]:
                    language = sp[1:3]
                    signed_second_tax = si[1:].index('<') + 2
                    country = si[signed_second_tax:signed_second_tax + 2]
                    statistics[country][language] += 1

                tgt_params, tgt = si.split(" | ")
                src = tgt_params + " " + sp

                if len(tgt.strip()) == 0:
                    continue

                total += 1

                spoken_f.write(src.strip())
                signed_f.write(tgt.strip())

            spoken_f.close()
            signed_f.close()

    for split, set_names in sets.items():
        print(f"  {split}:")
        for name in set_names:
            if name != "swojs_glossario":
                print(f"    - custom-corpus_/custom_corpus/{name}/{split}")

    print("total", total)
    print("signed mono total", mono)

    with open("statistics.json", "w") as f:
        json.dump(statistics, f)
