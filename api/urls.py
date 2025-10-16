
from django.urls import path
from users.views import RegisterView, ProfileView, LogoutView
from wallet.views import WalletView, TransactionListView, PixupDepositView, PixupWebhookView
from api.views import DepositView, WithdrawView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('wallet/', WalletView.as_view(), name='wallet'),
    path('transactions/', TransactionListView.as_view(), name='transactions'),
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('withdraw/', WithdrawView.as_view(), name='withdraw'),
    path('pixup/deposit/', PixupDepositView.as_view(), name='pixup_deposit'),
    path('pixup/webhook/', PixupWebhookView.as_view(), name='pixup_webhook'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
