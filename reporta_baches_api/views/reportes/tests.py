from django.test import TestCase

from django.urls import reverse


class TestReportes(TestCase):
    def test_save_reportes_trabajador(self): 
        #url = reverse('trabajador')
        data = {
            "xd":"xd"
        }
        print("DATA",data)

        response = self.client.post('/reportes/trabajador',data)
        print(response)


