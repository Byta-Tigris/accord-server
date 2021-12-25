from typing import Union
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework import status
from accounts.models import Account
from linktree.models import LinkWall
from linktree.serialzer import LinkWallSerializer

from utils import querydict_to_dict




class CreateOrUpdateLinkWall(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    linkwall_serializer  = LinkWallSerializer()

    def post(self, request: Request, **kwargs) -> Response:
        data = querydict_to_dict(request.POST)
        response_data = {}
        _status = status.HTTP_404_NOT_FOUND
        if request.account is None:
            response_data = {"error": "Unable to find account"}
        else:
            account: Account = request.account
            try:
                assert "links" in data, "Links must be provided for creating link tree"
                linkwall_queryset = LinkWall.objects.select_related("links").filter(account=account)
                if linkwall_queryset.exists():
                    linkwall = linkwall_queryset.first()
                else:
                    linkwall = LinkWall(account=account,
                                    avatar_image=account.avatar,
                                    description=account.description,
                                    display_name=account.user.get_full_name(),
                                    media_handles={},
                                    styles={}
                                    )
                    for attr in ["background_image", "avatar_image","description", "display_name", "styles", "links"]:
                        if attr in data:
                            setattr(linkwall,attr, data.get(attr, ""))
                    if "media_handles" in data:
                        linkwall.set_media_handles(data.get("media_handles", {}))
                    else:
                        linkwall.sync_media_handles()
                    linkwall.save()
                    response_data = self.linkwall_serializer(linkwall)
                    _status = status.HTTP_202_ACCEPTED
            except Exception as err:
                _status = status.HTTP_400_BAD_REQUEST
                if isinstance(err, AssertionError):
                    response_data = {"error": str(err)}
                    
                else:
                    response_data = {"erro": "Unable to interact with link wall, try again later"}
        return Response(response_data, status=_status)



class RetrieveLinkWall(APIView):
    permission_classes = [AllowAny]
    linkwall_serializer = LinkWallSerializer()

    def get(self, request: Request, username) -> Response:
        linkwall_queryset = LinkWall.objects.filter(account__username=username)
        if not linkwall_queryset.exists():
            return Response({"error": "No link wall related to such username"}, status=status.HTTP_404_NOT_FOUND)
        linkwall: LinkWall = linkwall_queryset.first()
        return Response(self.linkwall_serializer(linkwall), status=status.HTTP_200_OK)



