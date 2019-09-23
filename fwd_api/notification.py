

class IssueType(object):
    LICENSE_EXPIRED = "LICENSE_EXPIRED"
    LICENSE_WILL_EXPIRE = "LICENSE_WILL_EXPIRE"
    LOW_STORAGE = "LOW_STORAGE"
    NO_STORAGE = "NO_STORAGE"
    COLLECTION_ERRORS = "COLLECTION_ERRORS"
    COLLECTION_WARNINGS = "COLLECTION_WARNINGS"
    DO_NOT_CARE = "DO_NOT_CARE"

    @classmethod
    def from_string(cls, string):
        if string == "LICENSE_EXPIRED":
            return IssueType.LICENSE_EXPIRED
        elif string == "LICENSE_WILL_EXPIRE":
            return IssueType.LICENSE_WILL_EXPIRE
        elif string == "LOW_STORAGE":
            return IssueType.LOW_STORAGE
        elif string == "NO_STORAGE":
            return IssueType.NO_STORAGE
        elif string == "COLLECTION_ERRORS":
            return IssueType.COLLECTION_ERRORS
        elif string == "COLLECTION_WARNINGS":
            return IssueType.COLLECTION_WARNINGS
        else:
            return IssueType.DO_NOT_CARE


class Issue(object):
    """Python-ized representation of a notification.
    """
    def __init__(self, issue_type, issue_title, issue_body, creation_time, snapshot_id):
        """
        @param {IssueType} issue_type
        @param {string} issue_title
        @param {string} issue_body
        @param {long} creation_time
        @param {string} snapshot_id, may be None for certain issue types
        """
        self._issue_type = issue_type
        self._issue_title = issue_title
        self._issue_body = issue_body
        self._creation_time = creation_time
        self._snapshot_id = snapshot_id

    def get_type(self):
        return self._issue_type

    def get_title(self):
        return self._issue_title

    def get_body(self):
        return self._issue_body

    def get_creation_time(self):
        return self._creation_time

    def get_snapshot_id(self):
        return self._snapshot_id


class Notification(object):
    """Python-ized representation of server's json returned from call to
    get notification endpoint.
    """
    def __init__(self, issues):
        """
        @param {[Issue]} list of issue
        """
        self._issues = issues

    @classmethod
    def from_json(cls, json_response):
        """
        @param {dict} json_response
        """
        issues = []
        for issue_json in json_response['notifications']:
            issue_type = IssueType.from_string(issue_json["issues"][0]["issueType"])
            if issue_type is IssueType.DO_NOT_CARE:
                continue
            issue_title = issue_json["title"]
            issue_body = issue_json["body"]
            creation_time = long(issue_json["creationTime"])
            snapshot_id = issue_json["snapshotId"]
            issues.append(Issue(issue_type, issue_title, issue_body, creation_time, snapshot_id))
        return Notification(issues)

    def get_issues(self):
        return list(self._issues)
