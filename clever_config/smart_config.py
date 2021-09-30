import os
from typing import Dict, List, Optional, Union

from attributedict.collections import AttributeDict

from clever_config._files_loader import ConfigFile, get_config_files, load_config
from clever_config.actions import BaseAction
from clever_config.dict_traversal import dict_traversal

JSONTypes = Union[dict, list, str, int]
PROD_ENV = "prod"
ENV_VARIABLE = "ENV"


class TrickyConfig(AttributeDict):
    """
    Supports several configs for different
    environments ('prod', 'dev', ...) at the same time
    """

    def __init__(
        self,
        config_dir: str,
        *,
        default_env: str = PROD_ENV,
        env_variable: str = ENV_VARIABLE,
        actions: Optional[List[BaseAction]] = None,
    ):
        super().__init__()
        self.__configs: Dict[str, AttributeDict] = {}
        self._get_configs(config_dir)

        self.__environment: str = self._get_environment(default_env, env_variable)

        self.update(self.__configs[self.get_active_env()])

        if actions:
            self._do_all_actions(actions)

    def __getattr__(self, item):
        try:
            return super().__getattr__(item)
        except AttributeError:
            if item in self.__configs.keys():
                return self.__configs[item]
        raise AttributeError(item)

    def get_envs(self) -> List[str]:
        """
        :return: ("prod", "dev", ...)
        """
        return list(str(key) for key in self.__configs.keys())

    def get_active_env(self) -> str:
        return self.__environment

    def _get_configs(self, config_dir: str) -> None:
        files: List[ConfigFile] = get_config_files(config_dir)
        for file in files:
            env_config: AttributeDict = load_config(file)
            self.__configs[file.environment] = env_config
        if PROD_ENV not in self.get_envs():
            raise RuntimeError("Config for 'prod'-environment is mandatory!")

    def _get_environment(self, default_env: str, env_variable: str) -> str:
        env: Optional[str] = os.getenv(env_variable)
        if not env:
            env = default_env
        if env not in self.get_envs():
            raise RuntimeError(f"There are no config-file for {env} environment!")
        return env

    def _do_all_actions(self, actions: List[BaseAction]) -> None:
        errors = dict_traversal(self, actions)
        if errors:
            raise RuntimeError(errors)
