from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Asset, AssetMaintenance, AssetAssignment, AssetRequest
from apps.users.models import UserProfile
from apps.departments.models import Department
from apps.categories.models import Category
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()

class AssetTests(APITestCase):
    def setUp(self):
        """Set up test data"""
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            firstName='Admin',
            lastName='User'
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            role='ADMIN',
            employee_id='ADM001'
        )

        # Create manager user
        self.manager_user = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='managerpass123',
            firstName='Manager',
            lastName='User'
        )

        # Create department
        self.department = Department.objects.create(
            name='Test Department',
            code='TEST01'
        )

        self.manager_profile = UserProfile.objects.create(
            user=self.manager_user,
            role='MANAGER',
            department=self.department,
            employee_id='MGR001'
        )

        # Create category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Category Description'
        )

        # Create test asset
        self.asset = Asset.objects.create(
            name='Test Asset',
            description='Test Asset Description',
            category=self.category,
            department=self.department,
            purchase_date=timezone.now().date(),
            purchase_price=Decimal('1000.00'),
            manufacturer='Test Manufacturer',
            model_number='TEST123',
            serial_number='SN123456'
        )

        # API endpoints
        self.list_url = reverse('assets:asset-list')
        self.detail_url = reverse('assets:asset-detail', args=[self.asset.id])
        self.assign_url = reverse('assets:asset-assign', args=[self.asset.id])
        self.return_url = reverse('assets:asset-return-asset', args=[self.asset.id])
        self.maintenance_url = reverse('assets:asset-maintenance', args=[self.asset.id])

    def test_create_asset(self):
        """Test creating a new asset"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'name': 'New Asset',
            'category': self.category.id,
            'department': self.department.id,
            'purchase_date': timezone.now().date().isoformat(),
            'purchase_price': '1500.00',
            'manufacturer': 'New Manufacturer',
            'model_number': 'NEW123'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Asset.objects.count(), 2)
        self.assertTrue(Asset.objects.filter(name='New Asset').exists())

    def test_list_assets(self):
        """Test listing assets with different user roles"""
        # Test admin access
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        # Test manager access
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_�����5�62'��s��S�p����/�������P⟮�X�i�bP��c�7/��L$ �i΂J��U�����	0��"����'��X�Y�t��F ���60�C�&m�|�7�R��~ ����_�(����D�_���`
�{�w̸��`|#�������(ؕ@����7����G�P-O�����.[��0�����9�j���m$�l?�v_�_p�B)X������Ba�d����f���:��0�S(>��hX_�b�;��|��	�(�#���U�i�mt�xB��G�Z<�L ���fġ,�q<�
?+�����M�YP�^�8��(��u(7��隸�x�	U��?�J�������D��	lH�t>��VQ�3�\���ؠi�����r��k��?�B��yx�WE�{=( ��j��ه�%���`�'P�I�<;��?��x��*��x���
�b_9W;Kc.�<��p�������)z��1 ��"+Y6T7��HPZ{��L��=3�������.Z@�/D��f'�t�Jjy0�:�qC]��\2ޟ��(��~��	S����&C���� �S4x]�E�l\dh"�,���t�B��K�G�q�AD'W)�PF�y&B+�.*���8VAF.nbs!����V>J����j��#��Z^Ģ�^�9R���,����^����B6zgS�9�;�&\+�x����&������	M�O��msX�	z[7��m���~%�{}1Kd��I"K���;О�7���C���c�~ �ħ;��9��3��C�N�'�  �[<�c[�v|�&�C_ߊ��D���G�u����{�����%���A����"G�H��.Hk�#M���x�bE��o�ڦ]sٳCEv����"4c)�	�b�g��g{bĳz�3��0�*=��9u{7��v�4R�YX��u~@X�e��JQW��nޫ߆��U�:�<r�fy���B��*��-dp0ԅ��X�����{-��^et���#���Q�s�B����Ł��Ng0%0����%��K4�]T�QOq�̼�!��Rw��Id	X���L=��FI=
_�DZ�½C���n��Rg �wfof8
��t��D/������0?�g���(�R�ۭ�����S$��w���<����Y��B�g�R=�}�c�#�{y5 .`���>f{%W����S<6�K���2�;�3��r��PD	'm=��nr�0�bSBE%$�T_Uh��>�k�=8��?���	���_G:8���E�ڬ�{4�\�x����Vê��gp�h��I�����m,E���=��r�u���"ֿ(,8Y7��)&Q�gy�&>�J0X����	�_$�g*�"�{g�����~?��A��T���c��M1�fK( ���L�ϧyU��Rx�6����-�.����~1�K�tI��M]�@׬/�Օ��[l�W�)�6����!\p�j��N��E�)8�X��d�eXx9ʱD/G'�KEV����C�T�9l��/���!�����$h�x�XVz��c&�CL{�X�n>f,su?gڵ������ /m�1���@埥�BGTVj*��Kz��2.�뢐�?�
'� ��Lw"�iȼJ,o����	����5�e�x�6���{�9�t��4Û�,/�=v����M�8���v{I�p�G%;�\������Lz���j`U��W����j~E67w�}��flD6i矍Y^��ՠ!�ojJ������܊���\�[����J�����[8�.�1����잤�����?����q ��L
{q��⚈�拁/��q·{QuO,JF%����R5�m��i�f�PqS�܂F�覎[�jъ1 Q䞔��ñI�¬��v�h��H��h�h}z1�EO�Fv�}��tu��0"|K��e,o*��nh����Mx�#vc����o�(~���|�A�;�CMD�H3�����i�ؤ��}���)9x�H��Ж�����Y�෧x�^K�C�fl4�����h$�p�a�Z��(Y.�b�u��Щz�܊{�
������%��{��l�����S���(������F�=�$�3��3���
�7�B�e��Q�<v0D�^���݂�:��$�n�ۆ��,�V{���N���w�Lp�ɸx���*x���v���L6��C��m4��UӉA���u��Z`��=k�C%�6!��l�N��	<#yF������{B|�̘��L�{�O���<)��Q���cr�yF�'X�Z>$,��!�8ME2�w�q�P�`G'
&[��)�'
&q�����ݢ�
6��(�c:(���F̏7�g��8�Q�	�z�������yz��XGy�jyv�(�!m�hJ7mL�^mՎ�k!ʓ�	����Ǻ��J�K��q������\w`�n7�\�^����S�kIBH��L�r��S����)�"�uH��)���j���:��V���T�9�l�C�gi�yq������8>M�n�ov�ɪnǢC�I�F���+�r�{�W����G�'puY�f�܇Sպ�xd��z4\8�t�oS|��b���N���R�'ހ���"��!��Z�����X8�;>�c�E��:H_�\ �7S��dC�F_��3���0�u��z����:`����x�>���&�j�e��BN��f��->V�L�?��?��D@���r�C��Mo��������:d�N��)"�s�+g����D���.�TNS]����-n(N��K*(������^6v�x�P�st@a����-�%��΂��DZ��Ms\�c�4��R�p�k�n���}62�7N�\ p�E� 	{��eV^���ѕ�-u�o�zi	I,rzЯk�&ZxW-��� I?:k�LC�E�����u�h���f�BT��wK�gE���n��_�Z^�s|�����s�F��O��BG�5�����q���~z�Γ����W���<��-��A>�{f<y�<G���L#��t	ކpKv6.	��pR�x���u��kȳ`KA<jBCz �8w�ÌC�}H�a���X9����,�Q����� r�u���i#���y?N����NU�m�(���+Y��9t��
ev�����4����N`�X���̯r�����¾�KǓ��+�%��w"��I��S���I�<ͩ�qi��Q>��SKG��|�(�%�|���M2��ۣ|B�op�H�lER<�S`����cq�/�()����h�sȱ�W�
�-���(���엽��!캽���V�5����*x�%DK��C�oՏ�o	-6�����m���;�/�h?��Z�t���|N=pڀ����n=ց.-L
�WTD��������3s���"�,��=	찏	��MS�59��y�2�&'҇G���ӫ����xraKK�L3�?�
O���g��^L���uB<��\RA�К������CD�|��P`=��\��ʢс�ԓע��&��%���dKBɗ^)�����[_�`-�a9ڟ�i�BzȾ����buu�˰}��聡
+����h��	U�:��3![�;����q	�䋑���	���Ю��%�?W���쳟�B;���.~����R��_ �IN��i�� �.n��'7�J,4��g1v�	|����j��<��ni �m}ؾmq��NC[���>��[�>ˉ?� �]�V��s��^O�+ �~���Q���W��,Axb?ׇ�(�@Y; �֋�!����V��,q��,�������9�£�' ��v! }�P������＝&՞�4�tur3����h�`��p&�ҹ��::V]��`EHw}��+��I��c�[ʑmuW�y��L��ޏ�aV��L%� W�FX�ܩ���đ�3��p+)�6��;�	�:��w�U�U3�*�w���Hi%�) a��Z��2ӷI�|�;wq�gi����^(��$�1��`��lGQ���3<�;h'SA��?�U�*��_y>��D�ܑ�}���5��l�@�A�&u+|�������i�7}�W�ӗ�c��Cъ���2����А���\��-	�8$4b�A��j+^S�Vs��@�~�ҙ��B�+��VKL�����0P�3X�L-�=�,���FoY@v ɁJ�'���dÓ�S�M���#j}������SQ����Y���6��oi�[Q+�_"���xmU��T�N�`fd&�|b�I�.�� ?D��pDj��8U%�<��au��i׈Z0�(!��ǀ��@�H?=�FD�N����C����(�0��
�/ԝ��F��6�ga�Eíx�UZP*�<g4�h�x�h�-�#F��J��{��#^�<b���<"�}�<⯡��?� �����01�+LFQ<�a����l�b�2�x�4��7���!� kk�`��Kt���*؇�wFO#�Np��[���!F}v�q�&��J�9d���`��_e�#�#Z����v�it����O������C#��WW�$xu�z?|ӝ]w1B�~�n2��!xW8x�������S��+�lيS�i�hT5���??�"���b>��������'j[�\Vy�u�3kO��ƽ��Co��_F��Wn6z�a$c�#.�c7m�I����T�����xT�V�0��NUc햺���1� `���<�\D�o���Cru��ו�Q��g'5E%����r�?~'	��PQ��]Gw7Bz<�@�d�-6D�J�mDf�r���]���.�-)p�c�y]`�$�3OkGD�9 ��.�\�<[p
�I���x�[Ș*�W�2Z�����o�ptIｱ�d��b�!xKw�κ���]E�����WA�����3Ż�ʰ[��c�3�(��˔��t��ꮺ|^�i�luk�c��C<;��>�<h-�)���
Wղ��NU�YŃ��r����u/P՞��[wNi\Fi\�<��*�4�^��q�B&־W���zܖ��_p+�V����-$��P��`��4.�2�G���a��5`��šX�^����T�"T�;|JN�z ��,MC
����޺?�Г�AA����m�Q���/	z�N~88Dċ֝_V�X#MԞ#{0 E�ٮ�8l��rp��`��'V��K�Hy�y��:��$��(���g^���*�m�ڌ�ᲃ��q��
Y,ӑO��N���P?^/Zګp��ՑW�	�VI��q5��V��:a���h����A`d�u���0".�Θ�����9m�p�m1����~5~���b���1"���5<�x���-�Gz��㉇�_����	�*5B���$��+���x��LI0c�C{��Sqn�o~sci��PkkQo�'��k4D���$�l�Ȫ�T�!u�|��&y�
���E�}D4�q����S�����j6�]���$������?�k[�����@?����x�����Dm"�������h��B(����66:��h�\���Wywy~{W'��o~p�x878ZԮY0��'��׫��]�=�rOz���	J�*��Q8ϖ�������6��(��bL�k	Kun��:�˕}�5ڕ]����ٷE���݉��#�w����O�����o���g�i�=>�3;�q�w?���"Z�'��|+�HACph�3o��q��q"�Du1Q�T)��j?Tf��1(y4\C����+m�P�\~D�Bu���Q�]�_���Q��&��D����N��A��^�,yb�'O����K����N̔���Ǡ�����c���h,w��5����P�Cd]PoJ{36+tb�����n�|dl'A��s�g=R�]/�j�6�E��~pv�9u}5<uC�<u�6����6���ӄ(^��"�kn
�@v[|���8zS1��V[��x�b�K��]�2�\��3�� �)ë�Wu���_Uq8)��<�E�r�I�������ak��������1�V��8�ޗ�qVg?h��t����4�}��p�ո��cՌ>�*�h8�Us�qV�-�pV�-;_��_.;�*El,ZaA�������>~?��
�)�ْ�P�H��^<�դeaH�r��	��[#�VC�ېVoii0�V����z|�?��X��ax��3��Y��3+Y�K���:�ͳmO�{���
�҄�'���D��)��KD�2��1���*솁�b��ɀsQ�s�R�U70����ŭ��	��t�ݶڅ�NP9Z���r�1�"�ó�ߏt4���xPp/��7H�H�Oo
�Xg�ӳk�������;�~����G��LT�&վ�~Yͯ^�k�yDn���,�O B9EU�xNY�v?]̲8�7۬F�B����Mce�f`u�ج�H�)�o[L����;�8�0���A4�]�L��-�(v�ǘ宰Rp�N�/�f{_8�-���픫uf���pf�9�d�I/�������l_x���l��G3ے_����_�/�����`�Z�]u��}����F�~�F-S�G�?�d���p�����t?���I�=
l�^w�������Nu!���S�|�ǞҸj⣔�߹��(�-�M]�K�҂I(�<i���$��.�т���>Aݐ(-qdcQA�����H/	!�&A���̲�PBB��;��i[&Y����$�3s�ν��Ϲ瞹sO�dG�E;:J˼ECj�܂@5��������}��6��E�7Ns5�{�1���PC��'hH����٬;�6$̉�� ��5ʮ��� ����5��wof�tʟ�2k8$�\�lI�'�7�T������������X��P��� �A!�D8�/��І��s��U��	�׳LIW`����.�=w�v�!�ަ%�Ծ[}T�7�;R�!��zA��qH����8�9�b��D���I�� \�>�OL�����,8"Z�n�+��~V_�e>YS���h?���q[��m(��xс/��.�8g�
�q���-�B �g(W���Xu4?F�z�u��3TH������X� o�c"���h�`�&�+7@�ɒZ�P��O8� O�ٻ��b����! �����4 �� ]�Z�T4@s�B��� q�J���;^؞�Ke�g����m�]�_9�p���g.�ۥ2n�G�.\d���ï4�̡ԡ���������4����KZ��N��lG�
:�KJ"���R3�W��d?�qDI�w�$:S�$�&JJ��������B�Pғ�d��;o9�Iv-����zr�QO
��*���PKf�%�K�CI魥���
~�$�/�6P�O��2�BK_ל?�@��Q���%rh�L����� �@(Mڨm	Y���	ڒZB;�EwhS���x�8E��Ca()�FX�X2KZALҋ`�"�bًb�
�ؙ�ܠ>
~n\�î�o�J,!��ϐ�U���Τyd�7�D�#�?�;S����F�ʾG��L�{R��P��1�v�t�o� h�>;<?����R�fGPr0k����G��W��O����ĮM�*_�k!`v���Q��.�Z��R
jԪ��U��}�VT�� ��'�Q�
��F��x/b�ȹh��lV0d�v4d��r�ЖP���|'�h ���2\o��U<��<���q��ěO�#F6?bPNo�x�������]Z����4��<h�!ԑ4�i�O�a�mE��&���ΓACL��r�4nT��FEC:n��޴*i�/H�����
]�*qȐ����