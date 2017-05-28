from rest_framework import permissions, authentication, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.serializers import UserSerializer, ConnectionRequestSerializer
from rest_framework.authtoken.models import Token
from api.models import User, ConnectionRequest
from rest_framework.decorators import api_view
from django.db.models import Q


class UserCreate(APIView):
    """ 
    Creates the user. 
    """
    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                json = serializer.data
                json['token'] = token.key
                return Response(json, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SendRequest(APIView):

    def post(self, request, format=None):
        to_user_id = request.data.get('to_user')
        if not to_user_id:
            return Response({'Detail': 'to_user is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            to_user = User.objects.filter(id=to_user_id).only('id')[0]
        except IndexError:
            return Response({'Detail': 'to_user id does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        from_user = request.user
        # import pdb; pdb.set_trace();
        if to_user_id == from_user.id:
            return Response({'Detail': "Can't connect to self"}, status=status.HTTP_400_BAD_REQUEST)

        if to_user in from_user.connected_users.all():
            return Response({'Detail': 'User already connected'}, status=status.HTTP_200_OK)

        if ConnectionRequest.objects.filter(from_user=from_user, to_user=to_user, status=ConnectionRequest.PENDING).exists():
            return Response({'Detail': 'You have already sent a request'}, status=status.HTTP_200_OK)

        if ConnectionRequest.objects.filter(from_user=to_user, to_user=from_user, status=ConnectionRequest.PENDING).exists():
            return Response({'Detail': 'The user has already sent you a request, please take action on it'}, status=status.HTTP_200_OK)

        ConnectionRequest.objects.create(from_user=from_user, to_user=to_user)
        ConnectionRequest.objects.create(from_user=to_user, to_user=from_user)
        return Response({'Detail': 'Request Sent'}, status=status.HTTP_200_OK)


class ConnectionRequestDetail(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.TokenAuthentication,)

    def get_queryset(self):
        return ConnectionRequest.objects.filter(to_user=self.request.user, status=ConnectionRequest.PENDING)

    def put(self, request, pk, format=None):	
        connection_request = self.get_object()
        action = request.data.get('action')
        if not action:
            return Response({'Detail': 'action is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            action = int(action)
        except ValueError:
            return Response({'Detail': 'action must be 2(accepted) or 3(rejected) or 4(Blocked)'}, status=status.HTTP_400_BAD_REQUEST)

        if not action in [2,3,4]:
            return Response({'Detail': 'action must be 2(accepted) or 3(rejected) or 4(Blocked)'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 2:
            connection_request.status = ConnectionRequest.ACCEPTED
            connection_request.save()
            return Response({'Detail': 'Request Accepted'}, status=status.HTTP_200_OK)
        elif action == 3:
            connection_request.status = ConnectionRequest.REJECTED
            connection_request.save()
            return Response({'Detail': 'Request Rejected'}, status=status.HTTP_200_OK)
        elif action == 4:
        	connection_request.status = ConnectionRequest.BLOCKED
        	connection_request.save()
        	return Response({'Detail': 'Blocked by User'}, status=status.HTTP_200_OK)



@api_view(['GET'])
def requests_list(request):
	permission_classes = (permissions.IsAuthenticated,)
	authentication_classes = (authentication.TokenAuthentication,)
	if request.method == 'GET':
		requests = ConnectionRequest.objects.filter(to_user=request.user, status=ConnectionRequest.PENDING)
		serializer = ConnectionRequestSerializer(requests, many=True)
		return Response(serializer.data)


@api_view(['GET'])
def friend_list(request):
	permission_classes = (permissions.IsAuthenticated,)
	authentication_classes = (authentication.TokenAuthentication,)
	if request.method == 'GET':
		friends = request.user.connected_users.all().filter(sender__status=2)
		serializer = UserSerializer(friends, many=True)
		return Response(serializer.data)

class SearchFriends(generics.ListAPIView):
   serializer_class = UserSerializer
   permission_classes = (permissions.IsAuthenticated,)
   authentication_classes = (authentication.TokenAuthentication,)

   def get_queryset(self):
      query = self.request.query_params.get('query', None)
      users = User.objects.filter(Q(first_name__icontains=query) | Q( last_name__icontains=query))
      blocked_users = self.request.user.connected_users.all().filter(sender__status=4).values('id')      
      users = users.exclude(id__in=blocked_users).exclude(pk=self.request.user.pk)
      return users

