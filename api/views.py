from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from wallet.models import Transaction, Wallet
from wallet.serializers import TransactionSerializer
from pixup.services import create_charge, get_charge_status, request_withdrawal
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        try:
            amount = Decimal(amount)
            if amount <= 0:
                return Response({'error':'Invalid amount'}, status=400)
        except Exception:
            return Response({'error':'Invalid amount format'}, status=400)
        # create pending transaction
        tx = Transaction.objects.create(user=request.user, type='deposit', amount=amount, status='pending')
        # call pixup
        resp = create_charge(amount, description=f"Deposit {request.user.email}")
        # Expect response contains charge id and qr code
        charge_id = resp.get('id') or resp.get('charge_id')
        qr = resp.get('qr_code') or resp.get('payload')
        return Response({'transaction_id': tx.id, 'charge_id': charge_id, 'qr': qr})

class WithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        pix_key = request.data.get('pix_key')
        recipient_name = request.data.get('recipient_name')
        try:
            amount = Decimal(amount)
            if amount <= 0:
                return Response({'error':'Invalid amount'}, status=400)
        except Exception:
            return Response({'error':'Invalid amount format'}, status=400)
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        if wallet.balance < amount:
            return Response({'error': 'Insufficient funds'}, status=400)
        tx = Transaction.objects.create(user=request.user, type='withdraw', amount=amount, status='pending')
        resp = request_withdrawal(amount, pix_key, recipient_name)
        # Depending on response, mark confirmed/failed
        tx.status = 'confirmed'
        tx.save()
        wallet.balance -= amount
        wallet.save()
        logger.info('withdraw confirmed user=%s amount=%s', request.user.email, amount)
        return Response({'transaction_id': tx.id, 'detail': 'withdrawal requested', 'pixup_response': resp})
