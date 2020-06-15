import base64
from collections import defaultdict
from typing import List, Tuple, Dict

import requests


def handle_response(response, error_msg) -> Dict:
    if response.status_code != 200:
        # This means something went wrong.
        raise Exception(error_msg)

    return response.json()


def decode_content(encoded_content: str) -> str:
    base64_bytes = encoded_content.encode("utf-8")
    message_bytes = base64.b64decode(base64_bytes)
    return message_bytes.decode("utf-8")


def encode_content(str_content: str) -> str:
    message_bytes = str_content.encode("utf-8")
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes.decode("utf-8")


def snake_to_camel(word):
    return ' '.join(x.capitalize() or '_' for x in word.split('_'))


def create_categories(blob_paths: List) -> List:
    return [f"* [{bp.split('/')[0]}](#{bp.split('/')[0]})" for bp in blob_paths]


def categories_vs_blob(blob_paths: List) -> Dict:
    cat_vs_blob_list = defaultdict(list)
    for bp in blob_paths:
        split = bp.split("/")
        cat = split[0]
        cat_vs_blob_list[snake_to_camel(cat)].append(f"- [{snake_to_camel(split[-1]).replace('.md', '')}]({bp})")

    return cat_vs_blob_list


def create_content(user_name: str, repo_name: str) -> Tuple:
    response = requests.get(f"https://api.github.com/repos/{user_name}/{repo_name}/branches/master")
    resp_json = handle_response(response, "Unable to fetch master branch data")
    sha = resp_json["commit"]["sha"]
    response = requests.get(f"https://api.github.com/repos/{user_name}/{repo_name}/git/trees/{sha}",
                            params={"recursive": "True"})
    resp_json = handle_response(response, "Unable to fetch tree")

    # Truncate false says, nothing more to load. Not supported True as of now.
    assert not resp_json["truncated"]

    blob_paths = [r["path"] for r in resp_json["tree"] if r["type"] == "blob" and len(r["path"].split("/")) > 1 and
                  not r["path"].startswith("_")]
    count = len(blob_paths)
    categories = create_categories(blob_paths)
    category_vs_blobs = categories_vs_blob(blob_paths)

    return count, categories, category_vs_blobs


username = input('Enter github username:')
auth_token = input('Enter github auth token:')
repo = input('Enter github repo name:')

readme_resp = requests.get(
    f"https://api.github.com/repos/{username}/{repo}/readme"
)

readme_json = handle_response(
    readme_resp, f"Error while fetching readme for user {username}, repo {repo}"
)

with open('_resources/til.md', 'r') as file:
    data = file.read()
    count, categories, cat_vs_blob = create_content(user_name=username, repo_name=repo)
    data = data.replace("<#count>", str(count))
    data = data.replace("<#category>", "\n".join(categories))
    result = ""
    for cat, blobs in cat_vs_blob.items():
        cat = snake_to_camel(cat)
        content = "\n".join(blobs)
        result += f"### {cat}\n{content}\n"

    data = data.replace("<#content>", result)

resp = requests.put(
    f"https://api.github.com/repos/{username}/{repo}/contents/{readme_json['path']}",
    json={
        "message": "Update readme",
        "content": encode_content(data),
        "sha": readme_json["sha"],
    },
    headers={"Authorization": f"token {auth_token}"},
)
