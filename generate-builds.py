import requests
import json
import os
import urllib.parse
import dateutil.parser
from datetime import datetime
from datetime import timezone


source_user = "satdump"
source_repository = "satdump"

target_user = "lunyaadev"
target_repository_cli = "satdump"
target_repository_gui = "satdump-gui"

only_newer_than = datetime(2024, 10, 1, tzinfo=timezone.utc)


def get_docker_tags(user="library", repository=None, search=None):
    if not repository:
        raise Exception("repository needs to be set")

    nextUrl = f"https://registry.hub.docker.com/v2/namespaces/{user}/repositories/{repository}/tags?page=1&page_size=1000"
    if search:
        nextUrl += f"&{urllib.parse.urlencode({'name': search})}"
    images = []
    while nextUrl:
        try:
            res = requests.get(nextUrl)
            data = res.json()
            nextUrl = data["next"]
            images.extend(data["results"])
        except Exception:
            nextUrl = None
    return images


def get_github_releases(user=None, repository=None):
    if not user or not repository:
        raise Exception("repository needs to be set")

    url = f"https://api.github.com/repos/{user}/{repository}/releases"
    try:
        res = requests.get(url)
        data = res.json()
        return data
    except Exception:
        return []


source_releases = get_github_releases(source_user, source_repository)
target_tags_cli = get_docker_tags(target_user, target_repository_cli)
target_tags_gui = get_docker_tags(target_user, target_repository_gui)

commit_hash = os.environ.get("GITHUB_SHA", "")
commit_hash_short = commit_hash[:7] or "unknown"


build_list = []
is_latest = True

for source_release in source_releases:
    # skip releases older than `only_newer_than`
    last_pushed_source = dateutil.parser.parse(source_release["updated_at"])
    if last_pushed_source.tzinfo is None:
        last_pushed_source = last_pushed_source.replace(tzinfo=timezone.utc)
    if last_pushed_source < only_newer_than:
        continue

    day = source_release["updated_at"].split("T")[0]
    tags = []
    release_file_amd = ''
    release_file_arm = ''

    if source_release["tag_name"] == 'nightly':
        tags = [
            'nightly-' + day + '-' + commit_hash_short,
            'nightly-' + day,
            'nightly',
        ]
        release_file_amd = 'satdump_ubuntu_24.04_amd64.deb'
        release_file_arm = 'satdump_rpi64_latest_arm64.deb'
    else:
        tags = [
            source_release["tag_name"] + '-' + commit_hash_short,
            source_release["tag_name"],
        ]
        if is_latest:
            tags.append('latest')
        # reset is latest to not add "latest" to next release
        is_latest = False
        release_file_amd = 'satdump_' + source_release["tag_name"] + '_ubuntu_24.04_amd64.deb'
        release_file_arm = 'satdump_' + source_release["tag_name"] + '_arm64.deb'
    
    # add cli if not published
    if not any(target_tag["name"] == tags[0] for target_tag in target_tags_cli):
        build_list.append({
            "tags": [target_user + '/' + target_repository_cli + ':' + tag for tag in tags],
            "dockerfile": "Dockerfile",
            "type": 'CLI',
            "version": source_release["tag_name"],
            "release_file_amd": release_file_amd,
            "release_file_arm": release_file_arm,
        })

    # add gui if not published
    if not any(target_tag["name"] == tags[0] for target_tag in target_tags_gui):
        build_list.append({
            "tags": [target_user + '/' + target_repository_gui + ':' + tag for tag in tags],
            "dockerfile": "Dockerfile.gui",
            "type": 'GUI',
            "version": source_release["tag_name"],
            "release_file_amd": release_file_amd,
            "release_file_arm": release_file_arm,
        })

print(
    json.dumps(
        [
            build
            for build in build_list
        ]
    )
)
