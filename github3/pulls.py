# -*- coding: utf-8 -*-
"""
github3.pulls
=============

This module contains all the classes relating to pull requests.

"""
from __future__ import unicode_literals

from json import dumps

from uritemplate import URITemplate

from . import models
from .decorators import requires_auth
from .issues import Issue
from .issues.comment import IssueComment
from .repos.commit import RepoCommit
from .repos.contents import Contents
from .users import User


class PullDestination(models.GitHubCore):
    """The :class:`PullDestination <PullDestination>` object.

    See also: http://developer.github.com/v3/pulls/#get-a-single-pull-request
    """

    def __init__(self, dest, direction):
        super(PullDestination, self).__init__(dest)
        from .repos.repo import Repository
        #: Direction of the merge with respect to this destination
        self.direction = direction
        #: Full reference string of the object
        self.ref = dest.get('ref')
        #: label of the destination
        self.label = dest.get('label')
        #: :class:`User <github3.users.User>` representing the owner
        self.user = None
        if dest.get('user'):
            self.user = User(dest.get('user'), None)
        #: SHA of the commit at the head
        self.sha = dest.get('sha')
        self._repo_name = ''
        self._repo_owner = ''
        if dest.get('repo'):
            self._repo_name = dest['repo'].get('name')
            self._repo_owner = dest['repo']['owner'].get('login')
            self.repository = Repository(dest.get('repo'), self)
        self.repo = (self._repo_owner, self._repo_name)

    def _repr(self):
        return '<{0} [{1}]>'.format(self.direction, self.label)


class PullFile(models.GitHubCore):

    """The :class:`PullFile <PullFile>` object.

    See also: http://developer.github.com/v3/pulls/#list-pull-requests-files
    """

    def _update_attributes(self, pfile):
        #: SHA of the commit
        self.sha = self._get_attribute(pfile, 'sha')

        #: Name of the file
        self.filename = self._get_attribute(pfile, 'filename')

        #: Status of the file, e.g., 'added'
        self.status = self._get_attribute(pfile, 'status')

        #: Number of additions on this file
        self.additions_count = self._get_attribute(pfile, 'additions')

        #: Number of deletions on this file
        self.deletions_count = self._get_attribute(pfile, 'deletions')

        #: Number of changes made to this file
        self.changes_count = self._get_attribute(pfile, 'changes')

        #: URL to view the blob for this file
        self.blob_url = self._get_attribute(pfile, 'blob_url')

        #: URL to view the raw diff of this file
        self.raw_url = self._get_attribute(pfile, 'raw_url')

        #: Patch generated by this pull request
        self.patch = self._get_attribute(pfile, 'patch')

        #: URL to JSON object with content and metadata
        self.contents_url = self._get_attribute(pfile, 'contents_url')

    def _repr(self):
        return '<Pull Request File [{0}]>'.format(self.filename)

    def contents(self):
        """Return the contents of the file.

        :returns: :class:`Contents <github3.repos.contents.Contents>`
        """
        json = self._json(self._get(self.contents_url), 200)
        return self._instance_or_null(Contents, json)


class PullRequest(models.GitHubCore):

    """The :class:`PullRequest <PullRequest>` object.

    Two pull request instances can be checked like so::

        p1 == p2
        p1 != p2

    And is equivalent to::

        p1.id == p2.id
        p1.id != p2.id

    See also: http://developer.github.com/v3/pulls/
    """

    def _update_attributes(self, pull):
        self._api = self._get_attribute(pull, 'url')

        #: Base of the merge
        self.base = self._class_attribute(
            pull, 'base', PullDestination, 'Base'
        )

        #: Body of the pull request message
        self.body = self._get_attribute(pull, 'body')

        #: Body of the pull request as HTML
        self.body_html = self._get_attribute(pull, 'body_html')

        #: Body of the pull request as plain text
        self.body_text = self._get_attribute(pull, 'body_text')

        #: Number of additions on this pull request
        self.additions_count = self._get_attribute(pull, 'additions')

        #: Number of deletions on this pull request
        self.deletions_count = self._get_attribute(pull, 'deletions')

        #: datetime object representing when the pull was closed
        self.closed_at = self._strptime_attribute(pull, 'closed_at')

        #: Number of comments
        self.comments_count = self._get_attribute(pull, 'comments')

        #: Comments url (not a template)
        self.comments_url = self._get_attribute(pull, 'comments_url')

        #: Number of commits
        self.commits_count = self._get_attribute(pull, 'commits')

        #: GitHub.com url of commits in this pull request
        self.commits_url = self._get_attribute(pull, 'commits_url')

        #: datetime object representing when the pull was created
        self.created_at = self._strptime_attribute(pull, 'created_at')

        #: URL to view the diff associated with the pull
        self.diff_url = self._get_attribute(pull, 'diff_url')

        #: The new head after the pull request
        self.head = self._class_attribute(
            pull, 'head', PullDestination, 'Head'
        )

        #: The URL of the pull request
        self.html_url = self._get_attribute(pull, 'html_url')

        #: The unique id of the pull request
        self.id = self._get_attribute(pull, 'id')

        #: The URL of the associated issue
        self.issue_url = self._get_attribute(pull, 'issue_url')

        #: Statuses URL
        self.statuses_url = self._get_attribute(pull, 'statuses_url')

        #: Dictionary of _links. Changed in 1.0
        self.links = self._get_attribute(pull, '_links', {})

        #: Boolean representing whether the pull request has been merged
        self.merged = self._get_attribute(pull, 'merged')

        #: datetime object representing when the pull was merged
        self.merged_at = self._strptime_attribute(pull, 'merged_at')

        #: Whether the pull is deemed mergeable by GitHub
        self.mergeable = self._get_attribute(pull, 'mergeable', False)

        #: Whether it would be a clean merge or not
        self.mergeable_state = self._get_attribute(pull, 'mergeable_state')

        #: :class:`User <github3.users.User>` who merged this pull
        self.merged_by = self._class_attribute(pull, 'merged_by', User, self)

        #: Number of the pull/issue on the repository
        self.number = self._get_attribute(pull, 'number')

        #: The URL of the patch
        self.patch_url = self._get_attribute(pull, 'patch_url')

        #: Review comment URL Template. Expands with ``number``
        self.review_comment_url = self._class_attribute(
            pull, 'review_comment_url', URITemplate
        )

        #: Number of review comments on the pull request
        self.review_comments_count = self._get_attribute(
            pull, 'review_comments'
        )

        #: GitHub.com url for review comments (not a template)
        self.review_comments_url = self._get_attribute(
            pull, 'review_comments_url'
        )

        #: Returns ('owner', 'repository') this issue was filed on.
        self.repository = self.base
        if self.repository:
            self.repository = self.base.repo

        #: The state of the pull
        self.state = self._get_attribute(pull, 'state')

        #: The title of the request
        self.title = self._get_attribute(pull, 'title')

        #: datetime object representing the last time the object was changed
        self.updated_at = self._strptime_attribute(pull, 'updated_at')

        #: :class:`User <github3.users.User>` object representing the creator
        #: of the pull request
        self.user = self._class_attribute(pull, 'user', User, self)

        #: :class:`User <github3.users.User>` object representing the assignee
        #: of the pull request
        self.assignee = self._class_attribute(pull, 'assignee', User, self)

    def _repr(self):
        return '<Pull Request [#{0}]>'.format(self.number)

    @requires_auth
    def close(self):
        """Close this Pull Request without merging.

        :returns: bool
        """
        return self.update(self.title, self.body, 'closed')

    @requires_auth
    def create_comment(self, body):
        """Create a comment on this pull request's issue.

        :param str body: (required), comment body
        :returns: :class:`IssueComment <github3.issues.comment.IssueComment>`
        """
        url = self.comments_url
        json = None
        if body:
            json = self._json(self._post(url, data={'body': body}), 201)
        return self._instance_or_null(IssueComment, json)

    @requires_auth
    def create_review_comment(self, body, commit_id, path, position):
        """Create a review comment on this pull request.

        All parameters are required by the GitHub API.

        :param str body: The comment text itself
        :param str commit_id: The SHA of the commit to comment on
        :param str path: The relative path of the file to comment on
        :param int position: The line index in the diff to comment on.
        :returns: The created review comment.
        :rtype: :class:`~github3.pulls.ReviewComment`
        """
        url = self._build_url('comments', base_url=self._api)
        data = {'body': body, 'commit_id': commit_id, 'path': path,
                'position': int(position)}
        json = self._json(self._post(url, data=data), 201)
        return self._instance_or_null(ReviewComment, json)

    def diff(self):
        """Return the diff.

        :returns: bytestring representation of the diff.
        """
        resp = self._get(self._api,
                         headers={'Accept': 'application/vnd.github.diff'})
        return resp.content if self._boolean(resp, 200, 404) else b''

    def is_merged(self):
        """Check to see if the pull request was merged.

        :returns: bool
        """
        if self.merged:
            return self.merged

        url = self._build_url('merge', base_url=self._api)
        return self._boolean(self._get(url), 204, 404)

    def issue(self):
        """Retrieve the issue associated with this pull request.

        :returns: :class:`~github3.issues.Issue`
        """
        json = self._json(self._get(self.issue_url), 200)
        return self._instance_or_null(Issue, json)

    def commits(self, number=-1, etag=None):
        r"""Iterate over the commits on this pull request.

        :param int number: (optional), number of commits to return. Default:
            -1 returns all available commits.
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of
            :class:`RepoCommit <github3.repos.commit.RepoCommit>`\ s
        """
        url = self._build_url('commits', base_url=self._api)
        return self._iter(int(number), url, RepoCommit, etag=etag)

    def files(self, number=-1, etag=None):
        r"""Iterate over the files associated with this pull request.

        :param int number: (optional), number of files to return. Default:
            -1 returns all available files.
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`PullFile <PullFile>`\ s
        """
        url = self._build_url('files', base_url=self._api)
        return self._iter(int(number), url, PullFile, etag=etag)

    def issue_comments(self, number=-1, etag=None):
        r"""Iterate over the issue comments on this pull request.

        :param int number: (optional), number of comments to return. Default:
            -1 returns all available comments.
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`IssueComment <IssueComment>`\ s
        """
        comments = self.links.get('comments', {})
        url = comments.get('href')
        if not url:
            url = self._build_url(
                'comments', base_url=self._api.replace('pulls', 'issues')
            )
        return self._iter(int(number), url, IssueComment, etag=etag)

    @requires_auth
    def merge(self, commit_message=None, sha=None, squash=False):
        """Merge this pull request.

        :param str commit_message: (optional), message to be used for the
            merge commit
        :param str sha: (optional), SHA that pull request head must match
            to merge.
        :param bool squash: (optional), commit a single commit to the
            head branch.
        :returns: bool
        """
        parameters = {'squash': squash}
        if sha:
            parameters['sha'] = sha
        if commit_message is not None:
            parameters['commit_message'] = commit_message
        url = self._build_url('merge', base_url=self._api)
        json = self._json(self._put(url, data=dumps(parameters)), 200)
        if not json:
            return False
        return json['merged']

    def patch(self):
        """Return the patch.

        :returns: bytestring representation of the patch
        """
        resp = self._get(self._api,
                         headers={'Accept': 'application/vnd.github.patch'})
        return resp.content if self._boolean(resp, 200, 404) else b''

    @requires_auth
    def reopen(self):
        """Re-open a closed Pull Request.

        :returns: bool
        """
        return self.update(self.title, self.body, 'open')

    def review_comments(self, number=-1, etag=None):
        r"""Iterate over the review comments on this pull request.

        :param int number: (optional), number of comments to return. Default:
            -1 returns all available comments.
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`ReviewComment <ReviewComment>`\ s
        """
        url = self._build_url('comments', base_url=self._api)
        return self._iter(int(number), url, ReviewComment, etag=etag)

    def reviews(self, number=-1, etag=None):
        r"""Iterate over the reviews associated with this pull request.

        :param int number: (optional), number of reviews to return. Default:
            -1 returns all available files.
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of :class:`PullReview <PullReview>`\ s
        """
        # Accept the preview headers for reviews
        headers = {'Accept': 'application/vnd.github.black-cat-preview+json'}
        url = self._build_url('reviews', base_url=self._api)
        return self._iter(int(number), url, PullReview, etag=etag,
                          headers=headers)

    @requires_auth
    def update(self, title=None, body=None, state=None):
        """Update this pull request.

        :param str title: (optional), title of the pull
        :param str body: (optional), body of the pull request
        :param str state: (optional), ('open', 'closed')
        :returns: bool
        """
        data = {'title': title, 'body': body, 'state': state}
        json = None
        self._remove_none(data)

        if data:
            json = self._json(self._patch(self._api, data=dumps(data)), 200)

        if json:
            self._update_attributes(json)
            return True
        return False


class PullReview(models.GitHubCore):

    """The :class:`PullReview <PullReview>` object.

    See also: https://developer.github.com/v3/pulls/reviews/
    """

    def _update_attributes(self, preview):
        #: ID of the review
        self.id = self._get_attribute(preview, 'id')

        #: SHA of the commit the review is on
        self.commit_id = self._get_attribute(preview, 'commit_id')

        #: :class:`User <github3.users.User>` who made the comment
        self.user = self._class_attribute(preview, 'user', User, self)

        #: State of the review
        self.state = self._get_attribute(preview, 'state')

        #: datetime object representing when the event was created.
        self.created_at = self._strptime_attribute(preview, 'created_at')

        #: Body text of the review
        self.body = self._get_attribute(preview, 'body')

        #: API URL for the Pull Request
        self.pull_request_url = self._get_attribute(
            preview, 'pull_request_url'
        )

    def _repr(self):
        return '<Pull Request Review [{0}]>'.format(self.id)


class ReviewComment(models.BaseComment):

    """The :class:`ReviewComment <ReviewComment>` object.

    This is used to represent comments on pull requests.

    Two comment instances can be checked like so::

        c1 == c2
        c1 != c2

    And is equivalent to::

        c1.id == c2.id
        c1.id != c2.id

    See also: http://developer.github.com/v3/pulls/comments/
    """

    def _update_attributes(self, comment):
        super(ReviewComment, self)._update_attributes(comment)
        #: :class:`User <github3.users.User>` who made the comment
        self.user = self._class_attribute(comment, 'user', User, self)

        #: Original position inside the file
        self.original_position = self._get_attribute(
            comment,
            'original_position'
        )

        #: Path to the file
        self.path = self._get_attribute(comment, 'path')

        #: Position within the commit
        self.position = self._get_attribute(comment, 'position')

        #: SHA of the commit the comment is on
        self.commit_id = self._get_attribute(comment, 'commit_id')

        #: The diff hunk
        self.diff_hunk = self._get_attribute(comment, 'diff_hunk')

        #: Original commit SHA
        self.original_commit_id = self._get_attribute(
            comment, 'original_commit_id'
        )

        #: API URL for the Pull Request
        self.pull_request_url = self._get_attribute(
            comment, 'pull_request_url'
        )

    def _repr(self):
        return '<Review Comment [{0}]>'.format(self.user.login)

    @requires_auth
    def reply(self, body):
        """Reply to this review comment with a new review comment.

        :param str body: The text of the comment.
        :returns: The created review comment.
        :rtype: :class:`~github3.pulls.ReviewComment`
        """
        url = self._build_url('comments', base_url=self.pull_request_url)
        index = self._api.rfind('/') + 1
        in_reply_to = self._api[index:]
        json = self._json(self._post(url, data={
            'body': body, 'in_reply_to': in_reply_to
        }), 201)
        return self._instance_or_null(ReviewComment, json)
