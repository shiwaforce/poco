import requests
import json
import yaml
import os

from .abstract_repository import AbstractRepository
from .state import StateHolder
from .console_logger import ColorPrint


class BitbucketRepository(AbstractRepository):

    HEADERS = {'Content-Type': 'application/json',
               'User-Agent': 'Python/python'}

    def __init__(self, name, user=None, passw=None, url=None, ssh=None):
        super(BitbucketRepository, self).__init__(os.path.join(StateHolder.home_dir, 'bitbucket', name))

        self.user = user
        self.passw = passw
        self.url = url
        self.name = name
        self.ssh = ssh

        self.lst = dict()
        if url is None:
            ColorPrint.exit_after_print_messages("Bitbucket.com is not supported now.")
        else:
            self.prepare_dict_bitbucket_own()

        self.write_yaml_file(os.path.join(self.target_dir, 'pocok-catalog.yml'),
                             yaml.dump(data=self.lst, default_flow_style=False), create=True)

    def prepare_dict_bitbucket_online(self):
        pass

    def prepare_dict_bitbucket_own(self, next_page=0):
        r = requests.get(url=self.url + "/rest/api/1.0/repos?start=" + str(next_page), auth=(self.user, self.passw),
                         headers=BitbucketRepository.HEADERS)
        if r.status_code == 401:
            ColorPrint.exit_after_print_messages(message="Bitbucket authentication error in section: " + self.name)

        if r.status_code == 200:
            j = json.loads(r.text)
            for elem in j['values']:
                if not elem['scmId'] == 'git':
                    continue
                repo_name = str(elem['name'])
                for cloneref in elem['links']['clone']:
                    if cloneref['name'] == 'ssh':
                        self.lst[repo_name] = dict()
                        self.lst[repo_name]['git'] = str(cloneref['href'])
                        if self.ssh is not None:
                            self.lst[repo_name]['ssh'] = self.ssh

        if not j['isLastPage']:
            self.prepare_dict_bitbucket_own(j['nextPageStart'])

    def push(self):
        print("TODO")

    def pull(self):
        print("TODO")
