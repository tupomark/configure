"""Проверки XML, диапазонов и взаимодействия с HTTP API."""

import json
import unittest
from src.nuget import NugetRepository, parse_nuspec
from src.versions import normalize, select_version, version_key

XML = b'''<package xmlns="urn:test"><metadata><dependencies>
<group targetFramework="net8.0"><dependency id="B" version="[1,2)"/>
</group><group targetFramework="net9.0"/>
</dependencies></metadata></package>'''


class NugetTests(unittest.TestCase):
    """Не использовать сеть в модульных тестах."""

    def test_xml_groups(self):
        """Различать пустую группу и отсутствие подходящей группы."""
        self.assertEqual(parse_nuspec(XML), [("B", "[1,2)")])
        self.assertEqual(parse_nuspec(XML, "net9.0"), [])
        with self.assertRaises(ValueError):
            parse_nuspec(XML, "net7.0")

    def test_ranges(self):
        """Проверить включённые границы, точность, минимум и floating."""
        versions = ["1.0.0", "1.5.0", "2.0.0", "3.0.0-beta.1"]
        cases = {
            "1": "1.0.0", "(1,2)": "1.5.0", "[2]": "2.0.0",
            "(,1]": "1.0.0", "1.*": "1.5.0", "*": "1.0.0",
        }
        for requirement, expected in cases.items():
            with self.subTest(requirement=requirement):
                self.assertEqual(select_version(versions, requirement), expected)
        for bad in ["[9]", "(1)", "[2,1]", "[1"]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                select_version(versions, bad)

    def test_normalization_and_prerelease(self):
        """Сортировать числовые prerelease-части численно."""
        self.assertEqual(normalize("01.2.0.0+build"), "1.2.0")
        self.assertLess(version_key("1-rc.2"), version_key("1-rc.10"))
        self.assertLess(version_key("1-rc.10"), version_key("1"))

    def test_repository_urls_and_cache(self):
        """Взять base URL из индекса и не повторять одинаковые запросы."""
        calls = []
        data = {
            "feed": json.dumps({"resources": [{
                "@type": "PackageBaseAddress/3.0.0", "@id": "https://flat/",
            }]}).encode(),
            "https://flat/b/index.json": b'{"versions":["1.0.0"]}',
            "https://flat/b/1.0.0/b.nuspec": XML,
        }

        def fetch(url):
            """Вернуть подготовленный ответ вместо сети."""
            calls.append(url)
            return data[url]

        repo = NugetRepository("feed", fetcher=fetch)
        self.assertEqual(repo.resolve("B", "1"), "1.0.0")
        repo.dependencies("B", "1")
        repo.dependencies("b", "1.0.0")
        self.assertEqual(len(calls), 3)
