from .models import SalesRepresentative, FCMDevice
from django.conf import settings
from pyfcm import FCMNotification

def format_response(data, status=200):
    context = {
        'statusCode': status,
        'data': data
    }
    return context

def success_message(message_variable, start_custom_message = '', end_custom_message = ''):
    return {"message": message_variable}

def error_message(message_variable, start_custom_message = '', end_custom_message = ''):
    return {"message": message_variable}


def is_authenticate_sales_rep(username, password):
    """
    Authenticate the user
    1. on the basis of email + password
    2. on the basis of username + password + company link
    :param username: required(email/username)
    :param password: required
    :return: if success user object, otherwise pass
    """
    try:
        user = SalesRepresentative.objects.get(email__iexact=username)
        if user.check_password(password):
            return user
    except ObjectDoesNotExist:
        pass


def send_notification(user_id, **kwargs):
    """
    Send notification with the help of FCM service.
    It requires 'FCM key' which is written in settings
    :param registration_id: string, device id
    :param kwargs: title(string), body(string)
    :return: result(json)
    """

    proxy_dict = {
        "http": "http://127.0.0.1",
        "https": "http://127.0.0.1",
        "http": "http://172.20.221.67:11170",
        "https": "http://172.20.221.67:11170",
        "http": "http://172.20.221.67",
        "https": "http://172.20.221.67"
    }

    try:
        user_device = FCMDevice.objects.get(user__id=user_id, active=True)
    except ObjectDoesNotExist:
        return True
    data_message = kwargs.get('data_message', {})
    api_key = getattr(settings, 'FCM_SERVER_KEY', '')
    push_service = FCMNotification(api_key=api_key, proxy_dict=proxy_dict)
    if user_device.type == 'ios':
        result = push_service.notify_single_device(registration_id=user_device.registration_id,
                                                   message_title=data_message['title'],
                                                   message_body=data_message['message'],
                                                   data_message=data_message,
                                                   extra_kwargs={'data': data_message},
                                                   content_available=True,
                                                   sound='default'
                                                   )
    else:
        result = push_service.notify_single_device(
            registration_id=user_device.registration_id,
            data_message=data_message,
            message_title=data_message['title'],
            message_body=data_message['message']
            )
    print(result)
    return result