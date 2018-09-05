import os
from .state import StateHolder


class CTAUtils:

    CTA_STRINGS = {
        "default": "'poco repo add sample https://github.com/shiwaforce/poco-example'\n"
                   "Run if you want sample projects.",
        "have_file": "'poco init'\nYou have some local files for virtualize your project. "
                     "Run above for full functionality.",
        "have_cat": "You have an catalog. If you want to see available projects, run:\n'poco catalog'",
        "have_all": "You have local files to run, only one command left:\n'poco up'"
    }

    @staticmethod
    def get_cta():
        res = ""
        if CTAUtils.one_of_local_files_exits(files=['poco.yml', 'poco.yaml']):
            res = CTAUtils.CTA_STRINGS['have_all']
        elif not CTAUtils.catalog_exists() and CTAUtils.one_of_local_files_exits(
                files=['docker-compose.yml', 'docker-compose.yaml', '.poco', 'docker']) \
                and not CTAUtils.one_of_local_files_exits(files=['poco.yml', 'poco.yaml']):
            res = CTAUtils.CTA_STRINGS['have_file']
        elif not CTAUtils.catalog_exists() and not CTAUtils.one_of_local_files_exits(
                files=['docker-compose.yml', 'docker-compose.yaml', '.poco', 'docker']):
            res = CTAUtils.CTA_STRINGS['default']
        elif CTAUtils.catalog_exists():
            res = CTAUtils.CTA_STRINGS['have_cat']
        return res

    @staticmethod
    def one_of_local_files_exits(files):
        actual_dir = os.getcwd()
        ''' TODO handle extension'''
        for file in files:
            if os.path.exists(os.path.join(actual_dir, file)):
                return True
        return False

    @staticmethod
    def catalog_exists():
        if not os.path.exists(StateHolder.home_dir):
            return False
        return os.path.exists(os.path.join(StateHolder.home_dir, 'config'))
