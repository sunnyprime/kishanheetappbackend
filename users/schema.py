from django.contrib.auth import get_user_model
from authy.api import AuthyApiClient
import graphene
from graphql import GraphQLError
from django.contrib.auth.models import User
from graphene_django import DjangoObjectType
import requests
import json
# from rest_framework.authtoken.models import Token

authy_api = AuthyApiClient('4UPTJPKbaxRyAauLRZBWLQiWTSoI1iwi')

class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class Query(graphene.ObjectType):
    user = graphene.Field(UserType, id=graphene.Int(required=True))
    me = graphene.Field(UserType)

    def resolve_user(self, info, id):
        Love = get_user_model().objects.get(id=id)
        print(Love.email)
        # return get_user_model().objects.get(id=id)
        # raise GraphQLError('Not logged in!')
        return Love.email

    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('Not logged in!')

        return user


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, username, password, email):
        user = get_user_model()(
            username=username,
            email=email
        )
        user.set_password(password)
        user.save()
        # query = """mutation{
        #         verifyToken(token:"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6Ijg1MjIxNTIzNjkiLCJleHAiOjE1OTI1ODIyNjUsIm9yaWdJYXQiOjE1OTI1ODE5NjV9.s-j9fZ1QN4k88b8uNWl2YwpfxxRLb2TWiXpCz9dT-Gc"){
        #         payload
        #          }
        #         }"""
        # url = 'http://127.0.0.1:8000/graphql/'
        query = """mutation {
                tokenAuth(username:"%s",password:"%s"){
                 token
                    }
                }"""%(username,password)
        url = 'http://127.0.0.1:8000/graphql/'
        r = requests.post(url, json={'query': query})
        print(r.status_code)
        print(r.text)
        # token = Token.objects.create(user=user)
        # return token
        # print(r)
        # res = generate_token(username=username,password=password)
        if User.objects.filter(username=username).exists():
            print("Exist")
            raise GraphQLError("Username Exist")
            
        else:
            print("Not Exist")
            return r.text

        
        

class OTPUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        # password = graphene.String(required=True)
        # email = graphene.String(required=True)

    def mutate(self, info, username):
        start=authy_api.phones.verification_start(int(username),+91,'sms')
        
        if start.ok():
            print("SMS OK")
            print(start.content)
            # user = get_user_model()(
            #     username=username,
            #     # email=email
            # )
        # user.set_password(password)
        # user.save()
        # return CreateUser(user=user)
            return "sucess"
        else:
            # print("Not ")
            raise GraphQLError('Mobile number is not valid')
            # return "Unsucss"

class OTPConfirm(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        # password = graphene.String(required=True)
        # email = graphene.String(required=True)
        otp = graphene.String(required=True)

    def mutate(self, info, username,otp):
        verification=authy_api.phones.verification_check(int(username),+91,int(otp))
        print("VERRRRRRR")
        print(verification.content)

        if verification.ok():
            print("Verification OK")
            print(verification)
            user = get_user_model()(
                username=username,
            )
            password=username+"pass"
            user.set_password(password)
            user.save()
            return CreateUser(user=user)
            # return "sucess"
        else:
            raise "A valid mobile number"



class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    otp_user = OTPUser.Field()
    otp_confirm = OTPConfirm.Field()
