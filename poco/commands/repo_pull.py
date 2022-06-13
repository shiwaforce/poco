from .catalog_update import CatalogUpdate


class RepoUpdate(CatalogUpdate):
    sub_command = "repo"
    command = "pull"
