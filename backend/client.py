import hashlib
import json
import requests
from .languages import c_lang_config, cpp_lang_config, java_lang_config, c_lang_spj_config, \
    c_lang_spj_compile, py2_lang_config, py3_lang_config


class JudgeServerClientError(Exception):
    pass


class JudgeServerClient(object):
    def __init__(self, token, server_base_url):
        self.token = hashlib.sha256(token.encode("utf-8")).hexdigest()
        self.server_base_url = server_base_url.rstrip("/")

    def _request(self, url, data=None):
        kwargs = {"headers": {"X-Judge-Server-Token": self.token,
                              "Content-Type": "application/json"}}
        if data:
            kwargs["data"] = json.dumps(data)
        try:
            return requests.post(url, **kwargs).json()
        except Exception as e:
            raise JudgeServerClientError(str(e))

    def ping(self):
        return self._request(self.server_base_url + "/ping")

    def judge(self, src, language_config, max_cpu_time, max_memory, test_case_id, spj_version=None, spj_config=None,
              spj_compile_config=None, spj_src=None, output=False):
        data = {"language_config": language_config,
                "src": src,
                "max_cpu_time": max_cpu_time,
                "max_memory": max_memory,
                "test_case_id": test_case_id,
                "spj_version": spj_version,
                "spj_config": spj_config,
                "spj_compile_config": spj_compile_config,
                "spj_src": spj_src,
                "output": output}
        return self._request(self.server_base_url + "/judge", data=data)

    def compile_spj(self, src, spj_version, spj_compile_config):
        data = {"src": src, "spj_version": spj_version,
                "spj_compile_config": spj_compile_config}
        return self._request(self.server_base_url + "/compile_spj", data=data)
        