"""
Module that retrieves bug information from github issues and formats
it properly for the local bug database.
"""

import datetime
import json

import requests

from tracewhack import log
from tracewhack.config import GITHUB_HOST


def update(cache_shelf, db_configs, options):
    """
    Update the cache_shelf from the remote github repos issues, as
    specified by options['refresh'] behavior.
    """
    _handle_stale_repos(cache_shelf, db_configs, options)
    _slurp_repos(cache_shelf, db_configs, options)


def _handle_stale_repos(cache_shelf, db_configs, _options):
    """
    Handle the case where issue repos exist in the cache but no longer
    in the profile.

    For now, just warn.
    """
    cached_repos = _get_repos_with_ts(cache_shelf)
    existing_repos = set(cached_repos.keys())
    config_repos = set([db_config['repo'] for db_config in db_configs])

    stale_repos = existing_repos - config_repos
    if stale_repos:
        log.warn("Found cached github repos not in config: %s" % stale_repos)


def _slurp_repos(cache_shelf, db_configs, options):
    """
    Slurp down, either partially or fully, the issues from a set of
    github repos.
    """
    cached_repos_with_ts = _get_repos_with_ts(cache_shelf)

    gh_now = _gh_now()

    for db_config in db_configs:
        repo = db_config['repo']
        since = cached_repos_with_ts.get(repo, None)
        _slurp(cache_shelf, db_config, since, gh_now, options)


def _slurp(cache_shelf, db_config, since, gh_now, options):
    """
    Slurp down the issues, partially or fully, from a single github
    repo.
    """
    if options['refresh'] == 'full':
        since = None
        log.verbose("Grabbing all github issues due to refresh=full",
                    options)

    log.verbose("Slurping github issues for %s since %s" %
                (db_config['repo'],
                 since if since else 'always'),
                 options)
    issues = _issues(db_config, since, options=options)
    _record_issues(issues=issues,
                   cache_shelf=cache_shelf,
                   gh_now=gh_now,
                   db_config=db_config,
                   options=options)


def _record_issues(issues, cache_shelf, gh_now, db_config, options):
    """
    Record github issues in the cache.
    """
    # ok, pylint, for now I'm not using this.
    options = options

    for issue in issues:
        issue_key = 'bug:github_%s' % issue['id']
        cache_shelf[issue_key] = issue

    cached_repos_with_ts = _get_repos_with_ts(cache_shelf)
    cached_repos_with_ts[db_config['repo']] = gh_now
    cache_shelf['conf:github_repos'] = cached_repos_with_ts


def _issues(db_config, since, options):
    """
    Use the github api to get all the issues for a single repo since
    `since`, and format them for inclusion in the local db.
    """
    fmted_issues = []
    issues = _just_issues_since(db_config, since, options)
    for issue in issues:
        fmted_issue = {'url': issue['html_url'],
                        'title': issue['title'],
                        'id': issue['number']}
        txt = _all_issue_text(issue, db_config, options)
        fmted_issue['text'] = txt
        fmted_issues.append(fmted_issue)
    return fmted_issues


def _just_issues_since(db_config, since, options):
    """
    Get the raw github issues since `since` for a single github repo.
    """
    all_issues = []

    url_template = "/repos/{repo}/issues?state={state}"
    if since:
        url_template = url_template + "&since={since}"
    for state in ['open', 'closed']:
        issues = _api(url_template.format(state=state,
                                          repo=db_config['repo'],
                                          since=since),
                      db_config,
                      options)
        all_issues.extend(issues)

    return all_issues


def _all_issue_text(gh_issue, db_config, options):
    """
    Extract all the issue text, meaning the body and the bodies of the
    comments if there are such.
    """
    txts = [gh_issue['body']]
    if gh_issue.get('comments', 0):
        log.verbose("Github issue %s has comments" % gh_issue['number'],
                    options)
        txts.extend(_all_comment_bodies(gh_issue, db_config, options))
    return "\n\n".join(txts)


def _all_comment_bodies(gh_issue, db_config, options):
    """
    Get all comment bodies for this gh_issue.
    """
    url_template = "/repos/{repo}/issues/{number}/comments"
    return [comment['body'] for
            comment in
            _api(url_template.format(repo=db_config['repo'],
                                     number=gh_issue['number']),
                db_config,
                options=options)]


def _api(url, db_config, options):
    """
    Return a python list, being the aggregated, de-jsonified results
    of calling the github api at url and potentially the linked pages.
    """
    full_url = "{host}{url}".format(host=GITHUB_HOST,
                                     url=url)
    all_jsons = _walk_api(full_url, db_config, options)

    lst = []
    for j in all_jsons:
        lst.extend(json.loads(j))

    return lst


def _walk_api(full_url, db_config, options):
    """
    Call the github api at full_url, and continue to aggregate json
    results as long as a "next" link exists.

    Errors will raise an exception.
    """
    all_jsons = []

    resp = _raw_api(full_url, db_config, options)
    if not resp.ok:
        # for now, just bomb out totally, on the theory that we don't
        # want to deal with stale caches etc.  LATER in the future,
        # make this a little more robust.
        err = "Github API error: %s" % resp.text
        log.error(err)
        raise RuntimeError(err)

    all_jsons.append(resp.text)

    # walk through any "next" links
    if 'link' in resp.headers:
        links = [h.strip() for h in resp.headers['link'].split(',')]
        for link in links:
            pieces = [piece.strip() for piece in link.split(';')]
            if pieces[1] == 'rel="next"':
                next_url = pieces[0].strip('<>')
                log.verbose("Found a next link %s, following it." % next_url,
                            options)
                all_jsons.extend(_walk_api(next_url, db_config, options))

    return all_jsons


def _raw_api(full_url, db_config, options):
    """
    Make a single api call at full_url to the github api, and return
    the json found there.
    """
    log.verbose("Hitting github url: %s" % full_url, options)
    return requests.get(full_url,
                        auth=(db_config['api_user'],
                              db_config['api_password']))


def _get_repos_with_ts(cache_shelf):
    """
    Get all the repos we know about, with the timestamps of the last
    refresh.
    """
    return cache_shelf.get('conf:github_repos', {})


def _gh_now():
    """
    Get a date/time string representing 'now' in accordance with
    github api expectations.
    """
    return _gh_fmt(datetime.datetime.utcnow())


def _gh_fmt(dt_o):
    """
    Formt dt in accordance with github api expectations.

    dt_o must be in utc.
    """
    return dt_o.strftime('%Y-%m-%dT%H:%M:%SZ')
