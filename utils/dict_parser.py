from utils.mdict_query import IndexBuilder
from bs4 import BeautifulSoup
import re


class MDXDictParser:
    def __init__(self, path):
        self.adapter = IndexBuilder(path)
        self.cache = {}

    @staticmethod
    def _preprocess(html_string):
        soup = BeautifulSoup(html_string, 'html.parser')
        css_links = set(soup.find_all('link', {'rel': 'stylesheet'}) + soup.find_all('link', {'type': 'text/css'}))
        for link in css_links:
            link.decompose()
        return str(soup)

    def _query(self, query_word):
        if query_word in self.cache.keys():
            return self.cache[query_word]
        else:
            results = self.adapter.mdx_lookup(query_word)
            if len(results) == 0:
                self.cache[query_word] = None
                return None
            else:
                exp_list = []
                for result in results:  # 对于每一个匹配的结果
                    # 判断该结果是否仅为一个跳转链接
                    link_match = re.compile(r"@@@LINK=(.*)").match(result)
                    if link_match:  # 如果是一个跳转链接
                        link = link_match.group(1).replace("\r", "")
                        result = self.adapter.mdx_lookup(link)[0]  # 则将跳转之后的结果作为最终结果
                        result = self._preprocess(result)
                        exp_list.append(result)
                    else:  # 如果不是一个跳转链接，则视为以该搜索词为索引的一个结果
                        result = self._preprocess(result)
                        exp_list.append(result)
                self.cache[query_word] = exp_list
                return exp_list

    def query_dict(self, word):
        results = self._query(word)
        if results:
            return "<br>".join(results)
        else:
            return ""
