import copy

import hashlib
import json
import sys


def hash_dict(d):
    """Method, which makes dict hashable recursively"""
    def hash_item(item):

        if isinstance(item, dict):
            return hash_dict(item)
        elif isinstance(item, (list, tuple)):
            return hashlib.sha256(
                ''.join(hash_item(i) for i in item).encode('utf-8')
            ).hexdigest()
        else:
            return hashlib.sha256(json.dumps(item, sort_keys=True).encode('utf-8')).hexdigest()

    items = tuple((k, hash_item(v)) for k, v in sorted(d.items()))

    return hashlib.sha256(json.dumps(items).encode('utf-8')).hexdigest()


def remove_duplicates(dict_list_to_correct: list[dict], fields_to_ignore_in_dict: list[str]) -> tuple[list[dict], int]:
    """Method, which removes every duplicate through verifying the hashes of the dictionaries"""
    all_hashes = list()
    dict_to_return = []
    count_removed = 0

    for d in dict_list_to_correct:
        to_compare = copy.deepcopy(d)
        for field in fields_to_ignore_in_dict:
            del to_compare[field]
        if to_compare["login"]["uris"][0]["uri"][-1] == "/":
            to_compare["login"]["uris"][0]["uri"] = to_compare["login"]["uris"][0]["uri"][:-1]
        if hash_dict(to_compare) in all_hashes:
            count_removed += 1
        else:
            dict_to_return.append(d)
            all_hashes.append(hash_dict(to_compare))

    return dict_to_return, count_removed


def ask(to_ignore):
    contin = False
    while True:
        inp = input("\"c\" to continue, \"a\" to delete added and retry,"
                    " \"abort\" to stop execution, anything else to stop: ")
        if inp == "c":
            contin = True
        elif inp == "a":
            to_ignore = []
        elif inp == "abort":
            sys.exit()
        break
    return to_ignore, contin


if __name__ == "__main__":
    if_ignore = input("Do you want to specify fields to ignore? (y/n) ")
    fields_to_ignore = None
    if if_ignore != "y":
        fields_to_ignore = ["id", "creationDate", "revisionDate", "folderId"]
    else:
        fields_to_ignore = []
        while True:
            fields_to_ignore.append(input("write field names: "))
            ans = ask(fields_to_ignore)
            fields_to_ignore = ans[0]
            print(fields_to_ignore)
            if not ans[1]:
                break

    path = input("write the path of the file to check: ")
    with open(path) as f:
        full_dict = json.load(f)

    with open(path) as f:
        dict_list = json.load(f)["items"]

    # Remove duplicates and get the number of deleted duplicates
    dict_fixed, deleted_count = remove_duplicates(dict_list, fields_to_ignore)
    del full_dict["items"]
    full_dict["items"] = dict_fixed

    with open("file_checked.json", "w") as f:
        json.dump(full_dict, f, indent=2)
        print("file_checked.json has been written in script directory")

    # Output the results
    print(f"Number of deleted logins: {deleted_count}")
