from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required


staff_required = staff_member_required(login_url=settings.LOGIN_URL)
