from logging import getLogger
from opentelemetry.sdk.resources import (
    Resource,
    ResourceDetector,
    ProcessResourceDetector,
    OTELResourceDetector,
    OsResourceDetector,
    get_aggregated_resources,
)
from opentelemetry_resourcedetector_docker import DockerResourceDetector
from middleware.options import MWOptions
from middleware.detectors.detector import process_detector_input, get_detectors
from middleware.version import __version__
import typing
import os
import git

_logger = getLogger(__name__)


def create_resource(options: MWOptions):
    """
    Configures and returns a new OpenTelemetry Resource.

    Args:
        options (MWOptions): the middleware options to configure with
        resource (Resource): the resource to use with the new resource

    Returns:
        Resource: the new Resource
    """
    attributes = {
        "service.name": options.service_name,
        "mw.sdk.version": __version__,
        "mw.app.lang": "python",
        "runtime.metrics.python": "true",
    }
    if "https" in options.target:
        attributes["mw.serverless"] = "true"
    if options.access_token is not None:
        attributes["mw.account_key"] = options.access_token
    if options.project_name is not None:
        attributes["project.name"] = options.project_name
    if options.custom_resource_attributes is not None:
        try:
            extra = {
                k.strip(): v.strip()
                for k, v in (
                    item.split("=")
                    for item in options.custom_resource_attributes.split(",")
                )
            }
            attributes.update(extra)
        except Exception as exc:
            _logger.warning(
                "Skipped Custom attributes: parsing error expected format `abcd=1234,wxyz=5678`"
            )

    mw_vcs_repository_url = os.getenv("MW_VCS_REPOSITORY_URL")
    mw_vcs_commit_sha = os.getenv("MW_VCS_COMMIT_SHA")

    # Fallback to git if env vars are missing (independent logic, single Repo call)
    git_url, git_sha = None, None
    if not mw_vcs_repository_url or not mw_vcs_commit_sha:
        git_url, git_sha = get_git_info()
    if not mw_vcs_repository_url and git_url:
        mw_vcs_repository_url = git_url
    if not mw_vcs_commit_sha and git_sha:
        mw_vcs_commit_sha = git_sha

    if mw_vcs_repository_url:
        attributes["vcs.repository_url"] = mw_vcs_repository_url
    if mw_vcs_commit_sha:
        attributes["vcs.commit_sha"] = mw_vcs_commit_sha

    detectors: typing.List["ResourceDetector"] = [
        OTELResourceDetector(),
        ProcessResourceDetector(),
        OsResourceDetector(),
        DockerResourceDetector(),
    ]

    if options.detectors is not None:
        extra_detectors = get_detectors(process_detector_input(options.detectors))
        if extra_detectors is not None and len(extra_detectors) > 0:
            detectors.extend(extra_detectors)
    resources = get_aggregated_resources(
        detectors,
        initial_resource=Resource.create(attributes),
    )
    return resources


def get_git_info():
    """
    Returns (repository_url, commit_sha) from the local .git directory.
    Returns (None, None) if not a git repo or info unavailable.
    """
    try:
        repo = git.Repo(search_parent_directories=True)
        commit_sha = repo.head.commit.hexsha
        remote_url = None
        if repo.remotes:
            remote_url = repo.remotes.origin.url
            if remote_url and remote_url.endswith('.git'):
                remote_url = remote_url[:-4]
        return remote_url, commit_sha
    except Exception:
        return None, None
