from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, generics, status
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer
from django.shortcuts import get_object_or_404
import requests

class WalletView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)

class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')

class PixupDepositView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            import base64
            amount = request.data.get('amount', 10.0)
            
            # 1. Autenticar na PIXUP usando credenciais corretas
            client_id = 'leilsonpessoa_0709065799910204'
            client_secret = '15dfccbcb0583feaae937e552d01a9b8955b7ea3885340fcd0e2de6e0391afa0'
            
            # Concatenar e codificar em base64
            credentials = f'{client_id}:{client_secret}'
            base64_credentials = base64.b64encode(credentials.encode()).decode()
            
            auth_response = requests.post(
                'https://api.pixupbr.com/v2/oauth/token',
                json={'grant_type': 'client_credentials'},
                headers={
                    'accept': 'application/json',
                    'Authorization': f'Basic {base64_credentials}'
                }
            )
            
            if auth_response.status_code != 200:
                print(f'Erro PIXUP Auth: {auth_response.status_code} - {auth_response.text}')
                return Response(
                    {'error': f'Erro ao autenticar na PIXUP: {auth_response.text}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            access_token = auth_response.json().get('access_token')
            
            # 2. Gerar QR Code PIX (endpoint correto da documentação)
            charge_response = requests.post(
                'https://api.pixupbr.com/v2/pix/qrcode',
                json={
                    'amount': float(amount),
                    'description': 'Depósito Truco PIX',
                    'payer': {
                        'name': request.user.first_name or 'Jogador',
                        'document': '00000000000'
                    }
                },
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'accept': 'application/json',
                    'content-type': 'application/json'
                }
            )
            
            if charge_response.status_code != 200:
                print(f'Erro PIXUP Charge: {charge_response.status_code} - {charge_response.text}')
                return Response(
                    {'error': f'Erro ao gerar cobrança PIX: {charge_response.text}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            charge_data = charge_response.json()
            print(f'Resposta da API PIXUP: {charge_data}')
            
            # Tenta diferentes campos possíveis para o QR Code
            qr_code = charge_data.get('qr_code') or charge_data.get('qrcode') or charge_data.get('code') or charge_data.get('pix_code')
            
            # ID da transação PIXUP para rastreamento
            charge_id = charge_data.get('id') or charge_data.get('charge_id') or charge_data.get('transaction_id')
            
            # 3. Criar transação pendente com ID externo
            Transaction.objects.create(
                user=request.user,
                type='deposit',
                amount=amount,
                status='pending',
                external_id=charge_id
            )
            
            return Response({
                'qr_code': qr_code,
                'amount': amount
            })
            
        except Exception as e:
            print(f'Exceção capturada: {str(e)}')
            import traceback
            traceback.print_exc()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PixupWebhookView(APIView):
    permission_classes = [permissions.AllowAny]  # Webhook público

    def post(self, request):
        try:
            # Log do webhook recebido
            print(f'Webhook PIXUP recebido: {request.data}')
            
            # Dados do webhook
            event_type = request.data.get('event') or request.data.get('type')
            charge_id = request.data.get('id') or request.data.get('charge_id') or request.data.get('transaction_id')
            status_pixup = request.data.get('status')
            amount = request.data.get('amount')
            
            # Verifica se é um evento de pagamento confirmado
            if event_type in ['payment.confirmed', 'charge.succeeded', 'pix.received']:
                # Busca a transação pelo external_id
                try:
                    transaction = Transaction.objects.get(external_id=charge_id, status='pending')
                    
                    # Atualiza status da transação
                    transaction.status = 'confirmed'
                    transaction.save()
                    
                    # Atualiza saldo da carteira
                    wallet = transaction.user.wallet
                    wallet.balance += transaction.amount
                    wallet.save()
                    
                    print(f'Pagamento confirmado! Transação {transaction.id} - Valor: {transaction.amount}')
                    
                    return Response({'status': 'success', 'message': 'Pagamento confirmado'})
                    
                except Transaction.DoesNotExist:
                    print(f'Transação não encontrada para charge_id: {charge_id}')
                    return Response({'status': 'error', 'message': 'Transação não encontrada'}, status=status.HTTP_404_NOT_FOUND)
            
            elif event_type in ['payment.failed', 'charge.failed', 'pix.expired']:
                # Marca transação como falha
                try:
                    transaction = Transaction.objects.get(external_id=charge_id, status='pending')
                    transaction.status = 'failed'
                    transaction.save()
                    print(f'Pagamento falhou! Transação {transaction.id}')
                    return Response({'status': 'success', 'message': 'Pagamento falhou'})
                except Transaction.DoesNotExist:
                    pass
            
            return Response({'status': 'received'})
            
        except Exception as e:
            print(f'Erro no webhook: {str(e)}')
            import traceback
            traceback.print_exc()
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
