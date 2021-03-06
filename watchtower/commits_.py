import os
import pandas as pd
from os.path import join
import json

from ._config import get_data_home
from . import _github_api


def load_commits(user, project, data_home=None):
    """
    Reads the commits json files from the data folder.

    Parameters
    ----------
    user : string
        user or organization name, e.g. "matplotlib"

    project : string
        project name, e.g, "matplotlib"

    Returns
    -------
    commits
    """
    # XXX We need to sometime update that folder - how to do that?
    # XXX for some projects, that's going to get ugly…
    data_home = get_data_home(data_home)
    filepath = join(data_home, user, project, "commits.json")
    try:
        commits = pd.read_json(filepath)
    except ValueError:
        return None
    return commits


def update_commits(user, project, auth, since=None,
                   max_pages=100, per_page=100,
                   data_home=None, **params):
    """Update the commit data for a repository.

    Parameters
    ----------
    user : string
        The user / organization of the repository
    project : string
        The repository name
    auth : string (user:api_key)
        The username / API key for github, separated by a colon.
    singe : ???
        ???
    max_pages : int
        The maximum number of pages to return in the GET request.
    per_page : int
        The number of commits to return per page.
    data_home : string
        A path to where the data is stored.
    params : dict-like
        Will be passed to `get_frames`.

    Returns
    -------
    raw : json
        The raw json returned by the github API.
    """
    auth = _github_api.colon_seperated_pair(auth)
    url = 'https://api.github.com/repos/{}/{}/commits'.format(user, project)
    raw = _github_api.get_frames(auth, url, since=since,
                                 max_pages=max_pages,
                                 per_page=per_page,
                                 **params)
    path = get_data_home(data_home=data_home)
    filename = os.path.join(path, user, project, "commits.json")
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError:
        pass
    with open(filename, "w") as f:
        json.dump(raw, f)
    return raw


def is_doc(commits, use_message=True, use_files=True):
    """
    Find commits that are documentation related.

    Parameters
    ----------
    commits : pd.DataFrame
        pandas dataframe containing the commits information.

    use_message : bool, optional, default: True

    use_files: bool, optional, default: True
    """
    is_doc_message = commits.message.apply(lambda x: "doc" in x.lower())
    is_doc_files = commits.added.apply(lambda x: "doc" in " ".join(x).lower())
    is_doc = is_doc_message | is_doc_files
    is_doc.rename("is_doc", inplace=True)
    return is_doc
