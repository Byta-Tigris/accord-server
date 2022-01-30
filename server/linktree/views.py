
import json
from typing import Dict, Tuple
from django.http import QueryDict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework import status
from accounts.models import Account
from linktree.models import LinkWall, LinkWallLink, LinkwallMediaHandles
from linktree.serializer import LinkWallSerializer
from django.contrib.auth.models import User
from django.db.models import QuerySet
from utils.errors import AccountAuthenticationFailed, AccountDoesNotExists, NoLinkExists, NoLinkwallExists
from log_engine.log import logger
from rest_framework.decorators import api_view, permission_classes, authentication_classes




class RetrieveMyLinkWall(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    linkwall_serializer  = LinkWallSerializer()


    def get(self, request: Request) -> Response:
        response = {}
        _status = status.HTTP_400_BAD_REQUEST
        try:
            if not request.account:
                raise AccountDoesNotExists("")
            linkwall_queryset: QuerySet[LinkWall] = LinkWall.objects.filter(account=request.account)
            if not linkwall_queryset.exists():
                raise NoLinkwallExists()
            linkwall: LinkWall = linkwall_queryset.first()
            serialied = self.linkwall_serializer(linkwall, current_username=request.account.username)
            response["data"] = serialied
            _status = status.HTTP_200_OK
        except Exception as err:
            if isinstance(err, AccountDoesNotExists):
                response["error"] = "Please login and try again"
                _status = status.HTTP_403_FORBIDDEN
            elif isinstance(err, NoLinkwallExists):
                response["data"] = {"links": []}
                _status = status.HTTP_200_OK
            else:
                logger.error(err)
                response["error"] = "Please try again"
        return Response(response, status=_status)


def get_linkwall(request: Request) -> LinkWall:
    if not request.account:
        raise AccountAuthenticationFailed()
    account: Account = request.account
    linkwall_queryset: QuerySet[LinkWall] = LinkWall.objects.select_related("links", "media_handles").filter(account=account)
    if not linkwall_queryset.exists():
        raise NoLinkwallExists()
    return linkwall_queryset.first()

def get_or_create_linkwall(request: Request) -> LinkWall:
    try:
        return get_linkwall(request)
    except NoLinkwallExists as err:
        account: Account = request.account
        return LinkWall(
            account=account,
            avatar_image=account.avatar,
            description=account.description,
            display_name=account.user.get_full_name(),
        )


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(["POST"])
def add_link(request: Request) -> Response:
    data = json.load(request.body)
    response = {}
    _status = status.HTTP_400_BAD_REQUEST
    serializer = LinkWallSerializer()
    try:
        assert "links" in data and data["links"] > 0, "Links must be provided"
        linkwall = get_or_create_linkwall(request)
        links = linkwall.links.bulk_create([LinkWallLink(**link) for link in data["links"]],ignore_conflicts=True)
        linkwall.links.add(*links)
        response["data"] = serializer(linkwall)
        _status = status.HTTP_202_ACCEPTED
    except Exception as exc:
        if isinstance(exc, (AccountAuthenticationFailed, NoLinkwallExists)):
            response["error"] = str(exc)
        else:
            logger.error(exc)
            response["error"] = "Unexpected error. Try again"
    return Response(response, status=_status)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(["POST"])
def edit_link(request: Request) -> Response:
    data = json.load(request.body)
    response = {}
    _status = status.HTTP_400_BAD_REQUEST
    serializer = LinkWallSerializer()
    try:
        assert "link" in data and data["link"] > 0, "Links must be provided"
        linkwall = get_linkwall(request)
        link_queryset: QuerySet[LinkWallLink] = linkwall.links.filter(url=data["link"]["url"])
        if not link_queryset.exists():
            raise NoLinkExists()
        link: LinkWallLink = link_queryset.first()
        if "icon" in data["link"]:
            link.icon = data["link"]["icon"]
        if "name" in data["link"]:
            link.name = data["linkn"]["name"]
        if "is_visible" in data["link"]:
            link.is_visible = data["link"]["is_visible"]
        link.save()
        response["data"] = serializer(linkwall, request.account.username)
        _status = status.HTTP_202_ACCEPTED

    except Exception as exc:
        if isinstance(exc, (AccountAuthenticationFailed, NoLinkwallExists, NoLinkExists)):
            response["error"] = str(exc)
        else:
            logger.error(exc)
            response["error"] = "Unexpected error. Try again"
    return Response(response, status=_status)





@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(["POST"])
def remove_link(request: Request) -> Response:
    data = json.load(request.body)
    response = {}
    _status = status.HTTP_400_BAD_REQUEST
    serializer = LinkWallSerializer()
    try:
        assert "links" in data and data["links"] > 0, "Links must be provided"
        linkwall = get_linkwall(request)
        links_queryset: QuerySet[LinkWallLink] = linkwall.links.filter(url__in=data["links"])
        if links_queryset.exists():
            links_queryset.delete()
        response["data"] = serializer(linkwall, request.account.username)
        _status = status.HTTP_202_ACCEPTED

    except Exception as exc:
        if isinstance(exc, (AccountAuthenticationFailed, NoLinkwallExists, NoLinkExists)):
            response["error"] = str(exc)
        else:
            logger.error(exc)
            response["error"] = "Unexpected error. Try again"
    return Response(response, status=_status)
    

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(["POST"])
def change_asset(request: Request) -> Response:
    data = json.load(request.body)
    response = {}
    _status = status.HTTP_400_BAD_REQUEST
    serializer = LinkWallSerializer()
    try:
        assert "asset" in data and data["asset"] > 0, "Assets must be provided"
        linkwall = get_linkwall(request)
        for key, value in data["asset"].items():
            setattr(linkwall, key, value)
        linkwall.save()
        response["data"] = serializer(linkwall, request.account.username)
        _status = status.HTTP_202_ACCEPTED
    except Exception as exc:
        if isinstance(exc, (AccountAuthenticationFailed, NoLinkwallExists)):
            response["error"] = str(exc)
        else:
            logger.error(exc)
            response["error"] = "Unexpected error. Try again"
    return Response(response, status=_status)

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(["POST"])
def set_props(request: Request) -> Response:
    data = json.load(request.body)
    response = {}
    _status = status.HTTP_400_BAD_REQUEST
    serializer = LinkWallSerializer()
    try:
        assert "props" in data and data["props"] > 0, "Display name or Description must be provided"
        linkwall = get_or_create_linkwall(request)
        for key, value in data["props"].items():
            setattr(linkwall, key, value)
        linkwall.save()
        response["data"] = serializer(linkwall, request.account.username)
        _status = status.HTTP_202_ACCEPTED
    except Exception as exc:
        if isinstance(exc, (AccountAuthenticationFailed, NoLinkwallExists)):
            response["error"] = str(exc)
        else:
            logger.error(exc)
            response["error"] = "Unexpected error. Try again"
    return Response(response, status=_status)

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(["POST"])
def set_media_handles(request: Request) -> Response:
    data = json.load(request.body)
    response = {}
    _status = status.HTTP_400_BAD_REQUEST
    serializer = LinkWallSerializer()
    try:
        assert "media_handles" in data and data["media_handles"] > 0, "Media handles must be provided"
        linkwall = get_or_create_linkwall(request)
        linkwall.media_handles.bulk_create([LinkwallMediaHandles(**handle) for handle in data["media_handles"]])
        response["data"] = serializer(linkwall, request.account.username)
        _status = status.HTTP_202_ACCEPTED

    except Exception as exc:
        if isinstance(exc, (AccountAuthenticationFailed, NoLinkwallExists, NoLinkExists)):
            response["error"] = str(exc)
        else:
            logger.error(exc)
            response["error"] = "Unexpected error. Try again"
    return Response(response, status=_status)

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(["POST"])
def remove_media_handle(request: Request, username: str) -> Response:
    data = json.load(request.body)
    response = {}
    _status = status.HTTP_400_BAD_REQUEST
    serializer = LinkWallSerializer()
    try:
        assert "media_handles" in data and data["media_handles"] > 0, "Links must be provided"
        linkwall = get_linkwall(request)
        linkwall.remove_handles(data["media_handles"])
        response["data"] = serializer(linkwall, request.account.username)
        _status = status.HTTP_202_ACCEPTED

    except Exception as exc:
        if isinstance(exc, (AccountAuthenticationFailed, NoLinkwallExists, NoLinkExists)):
            response["error"] = str(exc)
        else:
            logger.error(exc)
            response["error"] = "Unexpected error. Try again"
    return Response(response, status=_status)


class RetrieveLinkWall(APIView):
    permission_classes = [AllowAny]
    linkwall_serializer = LinkWallSerializer()

    def get(self, request: Request, username: str) -> Response:
        linkwall_queryset = LinkWall.objects.filter(account__username=username)
        current_username = None
        if request.account is not None:
            current_username = request.account.username
        if not linkwall_queryset.exists():
            return Response({"error": "No link wall related to such username"}, status=status.HTTP_404_NOT_FOUND)
        linkwall: LinkWall = linkwall_queryset.first()
        return Response({"data" :self.linkwall_serializer(linkwall, current_username=current_username)}, status=status.HTTP_200_OK)





class LinkwallActionAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny, IsAuthenticated]

    def get(self, request: Request, username: str) -> Response:
        _status = status.HTTP_200_OK
        response = {}
        params: QueryDict = request.GET
        try:
            linkwall_queryset: QuerySet[LinkWall] = LinkWall.objects.filter(account__username=username)
            if not linkwall_queryset.exists():
                raise NoLinkwallExists()
            linkwall: LinkWall = linkwall_queryset.first()
            user: User = request.user
            
            assert "action" in params, "Incomplete request, missing action"
            if linkwall.account.user != user:
                if params.get("action") == "view":
                    linkwall.add_view(user)
                elif params.get("action") == "click":
                    assert "link" in params, "Incomplete request, missing link"
                    linkwall.add_click(user, params.get("link"))
            response["data"] = ""

        except Exception as exc:
            _status = status.HTTP_400_BAD_REQUEST
            if isinstance(exc, (NoLinkwallExists, AssertionError)):
                response["error"] = str(exc)
            else:
                logger.error(exc)
        return Response(response, status=_status)
            






