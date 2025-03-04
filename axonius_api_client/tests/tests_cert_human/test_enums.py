# -*- coding: utf-8 -*-
"""Test suite."""
from axonius_api_client.cert_human import enums


class TestGetNameByValue:
    def test_mapped(self):
        exp = enums.SignatureAlgorithms.rsa.name
        data = enums.SignatureAlgorithms.get_name_by_value(enums.SignatureAlgorithms.rsa.value)
        assert data == exp

    def test_unmapped(self):
        exp = None
        data = enums.SignatureAlgorithms.get_name_by_value("badwolf")
        assert data == exp


class TestGetValueByName:
    def test_mapped(self):
        exp = enums.SignatureAlgorithms.rsa.value
        data = enums.SignatureAlgorithms.get_value_by_name(enums.SignatureAlgorithms.rsa.name)
        assert data == exp

    def test_unmapped(self):
        exp = None
        data = enums.SignatureAlgorithms.get_value_by_name("badwolf")
        assert data == exp
