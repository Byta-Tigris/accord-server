
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

from utils.types import LinkwallManageActions




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
    linkwall_queryset: QuerySet[LinkWall] = LinkWall.objects.prefetch_related("links", "media_handles").filter(account=account)
    if not linkwall_queryset.exists():
        raise NoLinkwallExists()
    return linkwall_queryset.first()

def get_or_create_linkwall(request: Request) -> LinkWall:
    try:
        return get_linkwall(request)
    except NoLinkwallExists as err:
        account: Account = request.account
        return LinkWall.objects.create(
            account=account,
            avatar_image=account.avatar,
            description=account.description,
            display_name=account.user.get_full_name(),
        )



def add_link(request: Request) -> Response:
    data = json.loads(request.body)
    response = {}
    _status = status.HTTP_400_BAD_REQUEST
    serializer = LinkWallSerializer()
    try:
        assert "links" in data and len(data["links"]) > 0, "Links must be provided"
        linkwall = get_or_create_linkwall(request)
        links = linkwall.links.bulk_create([LinkWallLink(**link) for link in data["links"]])
        linkwall.links.add(*links)
        linkwall.refresh_from_db()
        response["data"] = serializer(linkwall, request.account.username)
        _status = status.HTTP_202_ACCEPTED
    except Exception as exc:
        if isinstance(exc, (AccountAuthenticationFailed, NoLinkwallExists)):
            response["error"] = str(exc)
        else:
            logger.error(exc)
            response["error"] = "Unexpected error. Try again"
    return Response(response, status=_status)


def edit_link(request: Request) -> Response:
    data = json.loads(request.body)
    response = {}
    _status = status.HTTP_400_BAD_REQUEST
    serializer = LinkWallSerializer()
    try:
        assert "link" in data and len(data["link"]) > 0, "Links must be provided"
        linkwall = get_linkwall(request)
        link_queryset: QuerySet[LinkWallLink] = linkwall.links.filter(url=data["link"]["url"])
        if not link_queryset.exists():
            raise NoLinkExists()
        link: LinkWallLink = link_queryset.first()
        if "icon" in data["link"]:
            link.icon = data["link"]["icon"]
        if "name" in data["link"]:
            link.name = data["link"]["name"]
        if "is_visible" in data["link"]:
            link.is_visible = data["link"]["is_visible"]
        if "type" in data["link"]:
            link.type = data["link"]["type"]
        link.save()
        linkwall.refresh_from_db()
        response["data"] = serializer(linkwall, request.account.username)
        _status = status.HTTP_202_ACCEPTED

    except Exception as exc:
        if isinstance(exc, (AccountAuthenticationFailed, NoLinkwallExists, NoLinkExists)):
            response["error"] = str(exc)
        else:
            logger.error(exc)
            response["error"] = "Unexpected error. Try again"
    return Response(response, status=_status)



def remove_link(request: Request) -> Response:
    data = json.loads(request.body)
    response = {}
    _status = status.HTTP_400_BAD_REQUEST
    serializer = LinkWallSerializer()
    try:
        assert "links" in data and len(data["links"]) > 0, "Links must be provided"
        linkwall = get_linkwall(request)
        links_queryset: QuerySet[LinkWallLink] = linkwall.links.filter(url__in=data["links"])
        if links_queryset.exists():
            links_queryset.delete()
        linkwall.refresh_from_db()
        response["data"] = serializer(linkwall, request.account.username)
        _status = status.HTTP_202_ACCEPTED

    except Exception as exc:
        if isinstance(exc, (AccountAuthenticationFailed, NoLinkwallExists, NoLinkExists)):
            response["error"] = str(exc)
        else:
            logger.error(exc)
            response["error"] = "Unexpected error. Try again"
    return Response(response, status=_status)
    

def edit_props(request: Request) -> Response:
    data = json.loads(request.body)
    response = {}
    _status = status.HTTP_400_BAD_REQUEST
    serializer = LinkWallSerializer()
    try:
        assert "props" in data and len(data["props"]) > 0, "Data must be provided"
        linkwall = get_linkwall(request)
        for key, value in data["props"].items():
            if key in ["background_image", "avatar_image", "display_name", "description", "styles"]:
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

def set_media_handles(request: Request) -> Response:
    data = json.loads(request.body)
    response = {}
    _status = status.HTTP_400_BAD_REQUEST
    serializer = LinkWallSerializer()
    try:
        assert "media_handles" in data and len(data["media_handles"]) > 0, "Media handles must be provided"
        linkwall = get_or_create_linkwall(request)
        links = linkwall.media_handles.bulk_create([LinkwallMediaHandles(**handle) for handle in data["media_handles"] if "url" in handle])
        linkwall.media_handles.add(*links)
        linkwall.refresh_from_db()
        response["data"] = serializer(linkwall, request.account.username)
        _status = status.HTTP_202_ACCEPTED

    except Exception as exc:
        if isinstance(exc, (AccountAuthenticationFailed, NoLinkwallExists, NoLinkExists)):
            response["error"] = str(exc)
        else:
            logger.error(exc)
            response["error"] = "Unexpected error. Try again"
    return Response(response, status=_status)


def remove_media_handle(request: Request) -> Response:
    data = json.loads(request.body)
    response = {}
    _status = status.HTTP_400_BAD_REQUEST
    serializer = LinkWallSerializer()
    try:
        assert "media_handles" in data and len(data["media_handles"]) > 0, "Links must be provided"
        linkwall = get_linkwall(request)
        linkwall.remove_handles(data["media_handles"])
        linkwall.refresh_from_db()
        response["data"] = serializer(linkwall, request.account.username)
        _status = status.HTTP_202_ACCEPTED

    except Exception as exc:
        if isinstance(exc, (AccountAuthenticationFailed, NoLinkwallExists, NoLinkExists)):
            response["error"] = str(exc)
        else:
            logger.error(exc)
            response["error"] = "Unexpected error. Try again"
    return Response(response, status=_status)


def edit_style(request: Request) -> Response:
    """
    Request Data:
    {styles: {component: {propert_name: property_value}}}
    """
    data = json.loads(request.body)
    response = {}
    _status = status.HTTP_400_BAD_REQUEST
    serializer = LinkWallSerializer()
    try:
        assert "styles" in data and len(data["styles"]) > 0, "Styles must be provided"
        linkwall = get_or_create_linkwall(request)
        for component, props in data["styles"].items():
            if component not in linkwall.styles:
                linkwall.styles[component] = {}
            for property_name, property_value in props.items():
                linkwall.styles[component][property_name] = property_value
        linkwall.save()
        response["data"] = serializer(linkwall, request.account.username)
        _status = status.HTTP_202_ACCEPTED

    except Exception as exc:
        if isinstance(exc, (AccountAuthenticationFailed, NoLinkwallExists, NoLinkExists)):
            response["error"] = str(exc)
        else:
            logger.error(exc)
            response["error"] = "Unexpected error. Try again"
    return Response(response, status=_status)


def remove_style(request: Request) -> Response:
    """
    Request Data:
    {styles: {component: [property_name]}}
    """
    data = json.loads(request.body)
    response = {}
    _status = status.HTTP_400_BAD_REQUEST
    serializer = LinkWallSerializer()
    try:
        assert "styles" in data and len(data["styles"]) > 0, "Styles must be provided"
        linkwall = get_or_create_linkwall(request)
        for component, props in data["styles"].items():
            if component in linkwall.styles:
                if len(props) == 0:
                    del linkwall.styles[component]
                else:
                    for property_name in props:
                        del linkwall.styles[component][property_name]
        linkwall.save()
        response["data"] = serializer(linkwall, request.account.username)
        _status = status.HTTP_202_ACCEPTED

    except Exception as exc:
        if isinstance(exc, (AccountAuthenticationFailed, NoLinkwallExists, NoLinkExists)):
            response["error"] = str(exc)
        else:
            logger.error(exc)
            response["error"] = "Unexpected error. Try again"
    return Response(response, status=_status)



class ManageLinkwallAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, action: str) -> Response:
        calback_map = {
            LinkwallManageActions.AddLink: add_link,
            LinkwallManageActions.EditLink: edit_link,
            LinkwallManageActions.RemoveLink: remove_link,
            LinkwallManageActions.EditProps: edit_props,
            LinkwallManageActions.AddHandles: set_media_handles,
            LinkwallManageActions.RemoveHandles: remove_media_handle,
            LinkwallManageActions.EditStyle: edit_style,
            LinkwallManageActions.RemoveStyle: remove_style
        }
        if action not in calback_map:
            return Response({"error": f"Invalid action {action}"}, status=status.HTTP_400_BAD_REQUEST)
        callback = calback_map[action]
        return callback(request)



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
            






