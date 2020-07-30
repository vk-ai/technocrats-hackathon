from django.shortcuts import render
from django.http import HttpResponse,StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators import gzip
from .models import KnownEncoding, SalesRepresentative, FCMDevice, FCMNotifications, CustomerProfile, Orders, OrderItems, Offers
import cv2
import face_recognition
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import exceptions
from .serializers import CustomerProfileAndPurchaseHistorySerializer, OrderItemsDetails, SalesRepresentativesDetailsSerializer, OfferDetailsSerializer
from .core import format_response, success_message, is_authenticate_sales_rep, error_message, send_notification

# Returns (R, G, B) from name
def name_to_color(name):
    color = [(ord(c.lower())-97)*8 for c in name[:3]]
    return color


FRAME_THICKNESS = 3
FONT_THICKNESS = 2

# Known Encodings
know_encoding_list = []
know_names_list = []
know_ids_list = []
get_all_customers = CustomerProfile.objects.all()
for each_cust in get_all_customers:
    img = each_cust.profile_image.path
    curImg = cv2.imread(img)
    # curImg = cv2.resize(curImg, (0, 0), None, 0.25, 0.25)
    img = cv2.cvtColor(curImg, cv2.COLOR_BGR2RGB)
    encode = face_recognition.face_encodings(img)[0]
    know_encoding_list.append(encode)
    know_names_list.append(each_cust.first_name +' '+ each_cust.last_name)
    know_ids_list.append(each_cust.id)

print('encoding',know_encoding_list)
print('Names',know_names_list)

# Methods
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret,image = self.video.read()
        # image = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
        # import ipdb;ipdb.set_trace()
        imgS = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(know_encoding_list, encodeFace)
            faceDis = face_recognition.face_distance(know_encoding_list, encodeFace)
            matchIndex = np.argmin(faceDis)
            if matches[matchIndex]:
                cust_name = know_names_list[matchIndex]
                cust_id = know_ids_list[matchIndex]
                top_left = (faceLoc[3], faceLoc[0])
                bottom_right = (faceLoc[1], faceLoc[2])
                color = name_to_color(cust_name)
                cv2.rectangle(image, top_left, bottom_right, color, FRAME_THICKNESS)

                top_left = (faceLoc[3], faceLoc[2])
                bottom_right = (faceLoc[1], faceLoc[2] + 22)

                cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)

                cv2.putText(image, cust_name, (faceLoc[3] + 10, faceLoc[2] + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), FONT_THICKNESS)

                # send notification to sales rep
                # Find available sales rep
                # Customer previous sales rep
                try:
                    cust_sales_rep = get_object_or_404(CustomerProfile, id=cust_id)
                    current_store = "Alaska"
                    if cust_sales_rep.previous_sales_rep.status == "available" and cust_sales_rep.previous_sales_rep.store == current_store:
                        push_data = {
                            'type': 'customer_alert',
                            'title': 'Customer Walked-In to the Store',
                            'message': 'Kindly visit the customer that you had assisted last time.',
                            'data': {'customer_id': int(cust_id)}
                        }
                        # send_notification(user_id=cust_sales_rep.previous_sales_rep.id, data_message=push_data)
                    else:
                        sales_rep = SalesRepresentative.objects.filter(store=current_store, status='available')
                        if sales_rep:
                            for each_sales_rep in sales_rep:
                                push_data = {
                                    'type': 'customer_alert',
                                    'title': 'Customer Walked-In to the Store',
                                    'message': 'Kindly visit the customer to assist them in purchase.',
                                    'data': {'customer_id': int(cust_id)}
                                }
                                # send_notification(user_id=each_sales_rep.id, data_message=push_data)
                        else:
                            sales_rep = SalesRepresentative.objects.filter(store=current_store)
                            for each_sales_rep in sales_rep:
                                push_data = {
                                    'type': 'customer_alert',
                                    'title': 'Customer Walked-In to the Store',
                                    'message': 'Kindly visit the customer to assist them in purchase.',
                                    'data': {'customer_id': int(cust_id)}
                                }
                                # send_notification(user_id=each_sales_rep.id, data_message=push_data)
                except:
                    pass


                # y1, x2, y2, x1 = faceLoc
                # y1, x2, y2, x1 = y1 , x2 , y2 , x1
                # cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # cv2.rectangle(image, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                # cv2.putText(img, cust_name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (200, 200, 200), 2)
        ret,jpeg = cv2.imencode('.jpg',image)
        return jpeg.tobytes()

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Create your views here.
@gzip.gzip_page
def video_feed(request):
    try:
        return StreamingHttpResponse(gen(VideoCamera()), content_type="multipart/x-mixed-replace;boundary=frame")
    except HttpResponseServerError as e:
        print("aborted")

def index(request):
    return render(request, 'customer/index.html', {})


class SalesRepresentativeRegister(APIView):

    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        device = request.data['device_token']
        device_type = request.data['device_type']
        data_dict = {
            "first_name": request.data['first_name'] if request.data['first_name'] else "",
            "middle_name": request.data['middle_name'] if request.data['middle_name'] else "",
            "last_name": request.data['last_name'] if request.data['last_name'] else ""
        }
        new_user = SalesRepresentative.objects.create_sales_rep_email(email=email,
                                                                      password=password,
                                                                      extra_fields=data_dict)
        FCMDevice.objects.create(user=new_user, registration_id=device,
                                 type=device_type)
        user_id = [{
            "sales_rep_id": new_user.id
        }]
        return Response(format_response(user_id))


class SalesRepresentativeLogin(APIView):
    def post(self, request):
        device = request.data['device_token']
        device_type = request.data['device_type']
        email = request.data['email']
        password = request.data['password']
        user = is_authenticate_sales_rep(email, password)
        if user:
            user.status = 'available'
            user.save()
            try:
                user_device = FCMDevice.objects.get(user=user)
                user_device.registration_id = device
                user_device.type = device_type
                user_device.save()
            except:
                FCMDevice.objects.create(user=user, registration_id=device,
                                         type=device_type)
            user_id = [{
                "sales_rep_id": user.id
            }]
            return Response(format_response(user_id))
        else:
            return Response(format_response(error_message("Unable to Login. Please check your email and password."), status.HTTP_400_BAD_REQUEST),
                            status=status.HTTP_400_BAD_REQUEST)


class CustomerProfileAndPurchaseHistoryAPI(APIView):
    def get(self, request, user_id):
        cust_obj = get_object_or_404(CustomerProfile, id=user_id)
        if cust_obj:
            serializer = CustomerProfileAndPurchaseHistorySerializer(cust_obj)
            data_dict = serializer.data
            # get_orders = Orders.objects.filter(customer_id=cust_obj.id)
            # data_dict['purchase_history'] = []
            # if get_orders:
            #     get_latest_order = get_orders.latest('id')
            #     get_orders_items = OrderItems.objects.filter(order_id=get_latest_order)
            #     order_serializers = OrderItemsDetails(get_orders_items, many=True)
            #     data_dict['purchase_history'] = order_serializers.data
            return Response(format_response(data_dict))
        return Response(format_response([], status.HTTP_404_NOT_FOUND),
                        status=status.HTTP_404_NOT_FOUND)


class CustomerPurchaseHistoryAPI(APIView):
    def get(self, request, user_id):
        get_orders = Orders.objects.filter(customer_id=user_id)
        if get_orders:
            get_latest_order = get_orders.latest('id')
            get_orders_items = OrderItems.objects.filter(order_id=get_latest_order)
            order_serializers = OrderItemsDetails(get_orders_items, many=True)
            return Response(format_response(order_serializers.data))
        return Response(format_response([], status.HTTP_404_NOT_FOUND),
                        status=status.HTTP_404_NOT_FOUND)

class SalesRepresentativeDetailsAPI(APIView):
    def get(self, request, sales_id):
        get_details = get_object_or_404(SalesRepresentative, id=sales_id)
        serializer = SalesRepresentativesDetailsSerializer(get_details)
        return Response(format_response(serializer.data))


class SalesRepresentativeLogout(APIView):
    def post(self, request):
        get_id = request.data['sales_rep_id']
        if get_id:
            sales_rep = get_object_or_404(SalesRepresentative, id=get_id)
            sales_rep.status = "not_available"
            sales_rep.save()
            user_device = FCMDevice.objects.get(user=sales_rep)
            user_device.registration_id = ""
            user_device.save()
            return Response(format_response(success_message("Logout successful")))
        return Response(format_response(success_message("Logout successful")))


class ListOffersAPI(APIView):
    def post(self, request):
        get_category = request.data['category']
        offer_details = Offers.objects.filter(category=get_category)
        if offer_details:
            serializers = OfferDetailsSerializer(offer_details, many=True)
            return Response(format_response(serializers.data))
        return Response(format_response(success_message("No Offers Found!")))






