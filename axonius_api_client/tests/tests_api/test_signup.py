# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.enforcements."""
import pytest
from axonius_api_client.api import Signup, json_api
from axonius_api_client.exceptions import ApiError, ResponseNotOk

from ..meta import EMAIL
from ..utils import get_url, random_string


class TestSignup:
    """Pass."""


class TestSignupPrivate(TestSignup):
    def test_signup_get(self, api_client):
        data = api_client.signup._get()
        assert isinstance(data, json_api.generic.BoolValue)
        assert data.value is True

    def test_signup(self, api_client):
        with pytest.raises(ResponseNotOk) as exc:
            api_client.signup._perform(password="x", company_name="x", contact_email=EMAIL)

        assert "Signup already completed" in str(exc.value)

    def test_system_status(self, api_client):
        value = api_client.signup._system_status()
        assert isinstance(value, json_api.signup.SystemStatus)
        assert "System status - ready" in str(value)


class TestSignupPublic(TestSignup):
    def test_system_status(self, api_client):
        value = api_client.signup.system_status
        assert isinstance(value, json_api.signup.SystemStatus)
        assert "System status - ready" in str(value)

    def test_is_signed_up(self, api_client):
        data = api_client.signup.is_signed_up
        assert isinstance(data, bool) and data

    def test_signup_already_done(self, api_client):
        with pytest.raises(ApiError) as exc:
            api_client.signup.signup(password="x", company_name="x", contact_email=EMAIL)
        assert "Initial signup already performed" in str(exc.value)

    def test_use_password_reset_token_invalid(self, api_client):
        with pytest.raises(ApiError):
            api_client.signup.use_password_reset_token(token="badwolf", password="x")

    def test_use_password_reset_token(self, api_client, temp_user):
        token = api_client.system_users.get_password_reset_link(name=temp_user.user_name)
        password = random_string(12)

        user = api_client.signup.use_password_reset_token(token=token, password=password)
        assert user.user_name == temp_user.user_name

        val = api_client.signup.validate_password_reset_token(token=token)
        assert val is False

        token2 = api_client.system_users.get_password_reset_link(name=temp_user.user_name)

        with pytest.raises(ResponseNotOk) as exc:
            api_client.signup.use_password_reset_token(token=token2, password=password)

        assert "password must be different" in str(exc.value)

    def test_get_api_keys_not_signed_up(self, api_client, monkeypatch):
        monkeypatch.setattr(Signup, "is_signed_up", False)
        with pytest.raises(ApiError):
            api_client.signup.get_api_keys(user_name="x", password="x")

    def test_reset_api_keys_not_signed_up(self, api_client, monkeypatch):
        monkeypatch.setattr(Signup, "is_signed_up", False)
        with pytest.raises(ApiError):
            api_client.signup.reset_api_keys(user_name="x", password="x")

    def test_backwards_compat_init(self, request):
        model = Signup(url=get_url(request))
        value = model.system_status
        assert isinstance(value, json_api.signup.SystemStatus)
