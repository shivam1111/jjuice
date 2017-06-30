from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
import requests
from django.conf import settings

class Ratings(View):

    def get(self, request, template_name="index.html"):
        response = {}
        payload ={
            'access_token':settings.FACEBOOK_ACCESSS_TOKEN,
            'fields':"has_rating,has_review,rating,review_text,reviewer"
        }
        res = requests.get('https://graph.facebook.com/v2.9/vapejjuice/ratings',params=payload)
        return JsonResponse(data=res.json(), status=200, safe=False)

