from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.contrib.auth.hashers import check_password, make_password
from django.dispatch import receiver
import cv2
import face_recognition


# Create your models here.
class SalesRepresentativeManager(models.Manager):
   @classmethod
   def normalize_email(cls, email):
       email = email or ''
       try:
           email_name, domain_part = email.strip().rsplit('@', 1)
       except ValueError:
           pass
       else:
           email = '@'.join([email_name, domain_part.lower()])
       return email

   def create_sales_rep_email(self, email, password, extra_fields):
       if not email:
           raise ValueError('The given email must be set')

       email = self.normalize_email(email)
       extra_fields.get('first_name', '')
       extra_fields.get('middle_name', '')
       extra_fields.get('last_name', '')
       user = self.model(email=email, **extra_fields)
       user.set_password(password)
       user.save(using=self._db)
       return user


class SalesRepresentative(models.Model):
    '''
    Sales Representative Details
    '''
    STATUS = (
        ('available', 'Available'),
        ('not_available', 'Not Available'),
    )

    first_name = models.CharField(_('First name'), max_length=150, )
    middle_name = models.CharField(_('Middle name'), max_length=150, blank=True)
    last_name = models.CharField(_('Last name'), max_length=150)
    email = models.EmailField(verbose_name=_('email address'),
                              max_length=255,
                              blank=True,
                              unique=True)
    password = models.CharField(_('password'), max_length=128, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='available', blank=True)
    store = models.CharField(max_length=50, blank=True)
    created = models.DateTimeField(_('date of joining'), auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    objects = SalesRepresentativeManager()

    def __str__(self):
        return self.email

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        def setter(raw_password):
            self.set_password(raw_password)
            self._password = None
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, setter)

    class Meta:
        verbose_name_plural = 'Sales Representatives'


class CustomerDetailsManager(models.Manager):
    @classmethod
    def normalize_email(cls, email):
        email = email or ''
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = '@'.join([email_name, domain_part.lower()])
        return email

    def create_parent_email(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        extra_fields.get('first_name', '')
        extra_fields.get('middle_name', '')
        extra_fields.get('last_name', '')
        user = self.model(email=email,
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomerProfile(models.Model):
    '''
    Customer Details
    '''
    CUSTOMER_TYPE = (
        ('elite', 'Elite'),
        ('pro', 'Pro'),
        ('platinum', 'Platinum')
    )

    first_name = models.CharField(_('First name'), max_length=150, )
    middle_name = models.CharField(_('Middle name'), max_length=150, blank=True)
    last_name = models.CharField(_('Last name'), max_length=150)
    email = models.EmailField(verbose_name=_('email address'),
                              max_length=255,
                              blank=True,
                              unique=True)
    password = models.CharField(_('password'), max_length=128, blank=True)
    profile_image = models.ImageField(upload_to='customers/', null=True, blank=True)
    date_of_birth = models.DateField(blank=True, default="")
    profession = models.CharField(max_length=250, blank=True, default="")
    customer_type = models.CharField(max_length=10, choices=CUSTOMER_TYPE, default='elite', blank=True)
    previous_sales_rep = models.ForeignKey(SalesRepresentative, on_delete=models.DO_NOTHING, null=True)
    created = models.DateTimeField(_('date of joining'), auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    objects = CustomerDetailsManager()

    def __str__(self):
        return self.email

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        def setter(raw_password):
            self.set_password(raw_password)
            self._password = None
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, setter)

    class Meta:
        verbose_name_plural = 'Customer Profiles'


class KnownEncoding(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    encoding = models.TextField()
    created = models.DateTimeField(_('date of joining'), auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.customer.first_name +' '+ self.customer.last_name

    class Meta:
        verbose_name_plural = 'Known Encodings'

@receiver(post_save, sender=CustomerProfile)
def save_known_encoding(sender, instance, **ksargs):
    get_image = instance.profile_image.path
    if get_image:
        curImg = cv2.imread(get_image)
        curImg = cv2.resize(curImg, (0, 0), None, 0.25, 0.25)
        img = cv2.cvtColor(curImg, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        KnownEncoding.objects.create(customer=instance, encoding=encode)
        print("Encoding is saved successfully")


class Products(models.Model):
    '''
    Product Details with desciption, photos, category, prize and product type
    '''
    name = models.CharField(_('Name'), max_length=150, blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(_('Category'), max_length=150, blank=True)
    product_type = models.CharField(_('Product Type'), max_length=150, blank=True)
    prize = models.FloatField(blank=True, null=True)
    product_image = models.ImageField(upload_to='product/', null=True, blank=True)
    created = models.DateTimeField(_('Created Date'), auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Product Details'


class Orders(models.Model):
    '''
    Orders details associated with customer ID
    '''
    customer_id = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    created = models.DateTimeField(_('Created Date'), auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.customer_id.first_name + " " + self.customer_id.last_name

    class Meta:
        verbose_name_plural = 'Order Details'


class OrderItems(models.Model):
    '''
    Order Items with Product details and quantity
    '''
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    created = models.DateTimeField(_('Created Date'), auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.order_id)

    class Meta:
        verbose_name_plural = 'Order Items'


class FCMDevice(models.Model):
    """
    This model stores registration id or device id of users and
    also store type of device
    """
    DEVICE_TYPES = (
        ('ios', 'ios'),
        ('android', 'android')
    )
    user = models.ForeignKey(SalesRepresentative, on_delete=models.CASCADE,
                             null=False, verbose_name=_('Fcm Mobile User')
                             )
    registration_id = models.TextField(verbose_name=_("Registration token"),
                                       default=''
                                       )
    type = models.CharField(choices=DEVICE_TYPES, max_length=10)
    active = models.BooleanField(
        verbose_name=_("Is active"), default=True,
        help_text=_("Inactive devices will not be sent notifications")
    )
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.id)

    class Meta:
        unique_together = ('user', 'registration_id',)
        verbose_name = _("FCM device")
        verbose_name_plural = _("FCM devices")


class FCMNotifications(models.Model):
    """
    FCMNotifications is a Mobile user Notification table
    notification_type: friend/postdetail/post/event/share.../report.../donation
    multicast_id: after sending notification fcm generate multicast_id
    """
    device = models.ForeignKey(FCMDevice, on_delete=models.CASCADE,
                               null=False, verbose_name=_('Device ID')
                               )
    user = models.ForeignKey(SalesRepresentative, on_delete=models.DO_NOTHING, null=True)
    message = models.TextField(verbose_name=_('Message'))
    data_message = models.TextField(verbose_name=_('extra_data'),
                                    blank=True, null=False
                                    )
    multicast_id = models.CharField(max_length=128, verbose_name=_('Multicast ID'),
                                    blank=True, null=False
                                    )
    notification_type = models.CharField(max_length=30, blank=False, null=True,
                                         default=None, verbose_name=_('type')
                                         )

    reminder = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.device.user.email)

    class Meta:
        verbose_name = _("FCM Notification")
        verbose_name_plural = _("FCM Notifications")


class Offers(models.Model):
    category = models.CharField(_('Category'), max_length=150, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='offers/', null=True, blank=True)
    created = models.DateTimeField(_('Created Date'), auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category

    class Meta:
        verbose_name_plural = 'Offers Details'

