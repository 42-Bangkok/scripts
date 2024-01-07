import os
import time
import httpx
from pydantic import validate_call
from datetime import datetime
from dateutil.parser import parse as datetime_parse

class User:
    """
    Represents a user from the 42 API.
    API object is optional
    """

    def __init__(
        self,
        data: dict,
        api = None,
    ):
        """_summary_

        Args:
            api (API): API object
            data (dict): data from api._user(login)
        """
        self.data = data
        self.api = api

    @property
    def login(self) -> str:
        """
        Returns the login of the user.
        """
        return self.data["login"]

    @property
    def id(self) -> int:
        """
        Returns the user ID.
        """
        return self.data["id"]

    @property
    def correction_point(self) -> int:
        """
        Returns the correction point of the user.
        """
        return self.data["correction_point"]

    def set_correction_point(
        self,
        value: int,
        reason: str,
        refresh: bool = True,
        allow_negative: bool = False,
    ) -> bool:
        """
        Args:
            value (int): The new correction point
            reason (str): The reason for the change
            refresh (bool, optional): Whether to refresh the user data after the change. Defaults to True.
            allow_negative (bool, optional): Whether to allow negative correction points. Defaults to False.

        Returns:
            bool: True if the change was successful

        Raises:
            ValueError: If the new correction point is negative and allow_negative is False
            Exception: If the change was not successful
        """
        if value < 0 and not allow_negative:
            raise ValueError("Correction point cannot be negative")
        if value == self.correction_point:
            return True

        current_val = self.correction_point
        diff = value - current_val
        headers = {"Authorization": f"Bearer {self.api.access_token}"}
        params = {
            "reason": reason,
            "amount": diff,
        }
        url = f"{self.api.BASE}/users/{self.login}/correction_points/add"
        with httpx.Client() as client:
            r = client.post(url, headers=headers, params=params)
        if r.status_code not in [i for i in range(200, 300)]:
            raise Exception("Could not set correction point")

        if refresh:
            self.data = self.api._user(self.login)
        else:
            self.data["correction_point"] = value

        return True

    def pts_socialism(self, target: int, refresh=True) -> int:
        """
        `OUR` points, comrade.
        If the user have more than target points, we ---take--- `DONATE` them,
        and add to `THE PEOPLE's POOL`.
        :param target: The target points
        :return: The number of points taken
        """
        REASON = "Evaluation point socialism."

        if self.correction_point <= target:
            return 0
        diff = self.correction_point - target
        self.set_correction_point(target, REASON)
        self.pool_add_pts(diff)

        if refresh:
            self.data = self.api._user(self.login)
        else:
            self.data["correction_point"] = target

        return diff

    def blackholed_at(self, cursus_id: int = 21) -> datetime:
        """
        Returns the date at which the user was blackholed.
        :param cursus_id: The cursus id
        :return: The date at which the user was blackholed
        """
        for cursus in self.data["cursus_users"]:
            if cursus["cursus_id"] == cursus_id:
                if cursus["blackholed_at"] is None:
                    return None
                blackholed_at = datetime_parse(cursus["blackholed_at"])
                return blackholed_at

        raise ValueError("User is not in this cursus")

    def is_blackholed(self, cursus_id: int = 21) -> bool:
        """
        Returns whether the user is blackholed.
        :param cursus_id: The cursus id
        :return: Whether the user is blackholed
        """
        blackholed_at = self.blackholed_at(cursus_id)
        if blackholed_at is None:
            return False

        return blackholed_at < datetime.now()

    def get_experiences(self) -> list:
        """
        Returns the user's experiences.
        :return: The user's experiences
        """
        url = self.api.BASE + f"/users/{self.login}/experiences"
        headers = {"Authorization": f"Bearer {self.api.access_token}"}
        r = httpx.get(url, headers=headers)
        return r.json()

    def change_email(self, email: str) -> bool:
        """Change user's email

        Args:
            email (str): new email

        Returns:
            bool: True if success,
        Exception: if failed
        """
        url = self.api.BASE + f"/users/{self.login}"
        headers = {
            "Authorization": f"Bearer {self.api.access_token}",
            "Content-Type": "application/json",
        }
        r = httpx.patch(url, headers=headers, json={"user": {"email": email}})
        r.raise_for_status()

        return True

    def __repr__(self):
        return f"<User {self.login}>"

    def __str__(self):
        return self.login


class API:
    """
    Wraps the 42 API. Caches the access token. Object returned from this class is meant to be shared between ex. user objects.
    """

    BASE = "https://api.intra.42.fr/v2"

    def __init__(
        self,
        uid: str | None = None,
        secret: str | None = None,
    ):
        """
        Args:
            uid (str | None, optional): 42's UID. If not provided, will try to get it from the environment FT_UID. Defaults to None.
            secret (str | None, optional): 42's Secret. If not provided, will try to get it from the environment FT_SECRET. Defaults to None.
        """
        self.uid = uid
        self.secret = secret
        if self.uid is None:
            self.uid = os.getenv("FT_UID")
        if self.secret is None:
            self.secret = os.getenv("FT_SECRET")

        self.cache = {}
        """
        self.cache = {
            'oauth_resp': {
                'access_token': 'd64ea05408005a46d3745355______6fb6f58e7d24062b8d',
                'token_type': 'bearer',
                'expires_in': 7200,
                'scope': 'public',
                'created_at': 1694885546,
                'secret_valid_until': 1716528913
            }
        }
        """

    @property
    def access_token(self) -> str:
        """
        Returns the token from the cache, or fetches it if it's not there.

        Returns:
            The access token
        [docs](https://api.intra.42.fr/apidoc/guides/getting_started)
        """
        oauth_resp = self.cache.get("oauth_resp")
        if (
            oauth_resp is not None
            and oauth_resp["secret_valid_until"] > time.time() - 60
        ):
            return oauth_resp["access_token"]

        data = {"grant_type": "client_credentials"}
        auth = (self.uid, self.secret)
        url = f"{self.BASE}/oauth/token"
        with httpx.Client() as client:
            r = client.post(url, data=data, auth=auth)
        if r.status_code != 200:
            raise Exception("Could not fetch token.")

        self.cache["oauth_resp"] = r.json()

        return r.json()["access_token"]

    @validate_call
    def _user(self, login: str) -> dict:
        """
        Fetches a user from the API.
        :param login: The login of the user or the user id
        :return: The user data
        """

        url = f"{self.BASE}/users/{login}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        with httpx.Client() as client:
            r = client.get(url, headers=headers)
        if r.status_code != 200:
            raise Exception("Could not fetch user")

        return r.json()

    def user(self, login: str) -> User:
        """
        Returns a User object.
        Args:
            login (str): The login of the user or the user id
        Returns:
            User: The user object
        """
        user = User(self._user(login), self)

        return user

    @validate_call
    def users(self, filter_params: dict, per_page: int = 100) -> list:
        """
        Filter users from the API.
        Our campus id is 33
        :param filter_params: The filter to apply
            ex: {
            'filter[primary_campus_id]': 33,
            'filter[pool_month]': 'january',
            'filter[pool_year]': 2022,
        }
        """
        page = 1
        count = 1
        ret = []
        filter_params.update(
            {
                "per_page": per_page,
                "page": page,
            }
        )
        url = f"{self.BASE}/users"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        with httpx.Client() as client:
            r = client.get(url, headers=headers, params=filter_params)
            if r.status_code != 200:
                raise Exception("Could not fetch users")
            ret += r.json()

            while count > 0:
                count = len(r.json())
                page += 1
                filter_params.update({"page": page})
                r = client.get(url, headers=headers, params=filter_params)
                if r.status_code != 200:
                    raise Exception("Could not fetch users")
                ret += r.json()

        return ret

    @validate_call
    def cursus_users(
        self, cursus_id: int, filter_params: dict, per_page: int = 100
    ) -> list:
        page = 1
        count = 1
        ret = []
        filter_params.update(
            {
                "per_page": per_page,
                "page": page,
            }
        )
        url = f"{self.BASE}/cursus/{cursus_id}/users/"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        with httpx.Client() as client:
            r = client.get(url, headers=headers, params=filter_params)
            if r.status_code != 200:
                raise Exception("Could not fetch users")
            ret += r.json()

            while count > 0:
                count = len(r.json())
                page += 1
                filter_params.update({"page": page})
                r = client.get(url, headers=headers, params=filter_params)
                if r.status_code != 200:
                    raise Exception("Could not fetch users")
                ret += r.json()

        return ret

    def pools(self, pool_id: int = 73) -> dict:
        """
        The pool of evaluation points.
        :param pool_id: The pool id
        :return: The pool data
        """
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{self.BASE}/pools/{pool_id}"
        with httpx.Client() as client:
            r = client.get(url, headers=headers)
        if r.status_code != 200:
            raise Exception("Could not fetch pool")

        return r.json()

    def pool_add_pts(self, value: int, pool_id: int = 73) -> dict:
        """
        Add point to pool apparently you can add negative point
        :param value: point to add
        :param pool_id: id of the pool
        :return: response from 42 Intra
        """
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{self.BASE}/pools/{pool_id}/points/add"
        data = {"points": value}
        with httpx.Client() as client:
            r = client.post(url, headers=headers, data=data)
        if r.status_code != 200:
            raise Exception("Could not add points to pool")

        return r.json()

    def delete_experiences(self, ids: list[int]) -> dict:
        """delete an experience https://api.intra.42.fr/apidoc/2.0/experiences/destroy.html

        Args:
            ids (list[int]): list of experience ids

        Returns:
            dict: success and fail ids
        """
        ret = {
            "success": [],
            "fail": [],
        }
        with httpx.Client() as client:
            for id in ids:
                url = f"{self.BASE}/experiences/{id}"
                r = client.delete(url, headers={"Authorization": f"Bearer {self.access_token}"})
                if r.status_code == 204:
                    ret["success"].append(id)
                else:
                    ret["fail"].append(id)

        return ret
