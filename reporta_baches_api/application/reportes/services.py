import os 
import numpy as np
import cv2
import ssl
from django.conf import settings
from reporta_baches_api.domain.user.models import User
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from reporta_baches_api.domain.reportes.models import(
    Calle, 
    Alcaldia,
    ReporteCiudadano,
    ReporteTrabajador
)
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from reporta_baches_api.domain.reportes.services import ReportesService

from reporta_baches_api.domain.reportes.models import (
    ReporteCiudadanoBaseParams,
    ReporteTiempoRealBaseParams,
    ReporteTrabajadorBaseParams
)


class ReportesAppServices: 
    def __init__(self):
        self.reportes_service = ReportesService()

    def create_reporte_trabajador_from_dict(self, data:dict):


        params = ReporteTrabajadorBaseParams(
            user=data['user'],
            ancho=data['ancho'],
            profundidad=data['profundidad'],
            prioridad=data['prioridad'],
            tipo_bache=data['tipo_bache'],
            estado_reporte=data['estado_reporte'],
            latitud=data['latitud'],
            longitud=data['longitud'],
            cp = data['cp'],
            direccion=data['direccion'],
            modo=data['modo']
        )

        return self.reportes_service.create_reporte_trabajador(params)

    def create_reporte_ciudadano_from_dict(self, data:dict): 

        params = ReporteCiudadanoBaseParams(
          
                user=data['user'],
                latitud=data['latitud'],
                longitud=data['longitud'],
                num_ext=data['num_ext'],
                num_int=data['num_int'],
                cp=data['cp'],
                descripcion=data['descripcion'],
                referencia_adicional=data['referencia_adicional'],
                direccion=data['direccion'],
                modo=data['modo']
            
        )
        reporte = self.reportes_service.create_reporte_ciudadano(params)
        return reporte
    
    def create_reporte_tiempo_real_from_dict(self, data:dict, img_file): 
        params = ReporteTiempoRealBaseParams(
                user=data['user'],
                latitud=data['latitud'],
                longitud=data['longitud'],
                cp=data['cp'],
                direccion=data['direccion'],   
                img_file= img_file
        )
        reporte = self.reportes_service.create_reporte_tiempo_real(params)
        return reporte
    

    def create_direction_if_not_exist(self,calle, alcaldia):
        if not Alcaldia.objects.filter(alcaldia = alcaldia):
            alcaldia_repostory = Alcaldia.objects.create(alcaldia = alcaldia)
            print("Se crea alcaldia", alcaldia_repostory)
            if not Calle.objects.filter(calle = calle):
                Calle.objects.create(calle = calle, alcaldia = alcaldia_repostory)

        if Alcaldia.objects.filter(alcaldia = alcaldia): 
            alcaldia_repostory = Alcaldia.objects.filter(alcaldia = alcaldia).first()
            if not Calle.objects.filter(calle = calle):
                Calle.objects.create(calle = calle, alcaldia = alcaldia_repostory)
    
        # Función para aplicar el filtro de nitidez
    def aplicar_nitidez(self, imagen):
        # Definir un kernel de nitidez
        kernel = np.array([[-1, -1, -1],
                        [-1,  9, -1],
                        [-1, -1, -1]])

        # Aplicar el kernel a la imagen
        imagen_nitida = cv2.filter2D(imagen, -1, kernel)
        return imagen_nitida

    # Filtro para estandarizar el contraste y brillo de la imagen
    def filtroContrasteBrillo(self, imagen):
        alpha = 1  # Factor de contraste
        beta = -10  # Factor de brillo
        imagen_ajustada = cv2.convertScaleAbs(imagen, alpha=alpha, beta=beta)
        return imagen_ajustada

    def preprocess_image(self, image):

        imagen_nitida = self.aplicar_nitidez(image)
        imagen_contraste = self.filtroContrasteBrillo(imagen_nitida)

        return imagen_contraste


    def procces_image(self, detections, categories, image_np):
         # All outputs are batches tensors.
        # Convert to numpy arrays, and take index [0] to remove the batch dimension.
        # We're only interested in the first num_detections.
        num_detections = int(detections.pop('num_detections'))
        detections = {key: value[0, :num_detections].numpy()
                    for key, value in detections.items()}
        detections['num_detections'] = num_detections

        # detection_classes should be ints.
        detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

        image_np_with_detections = image_np.copy()

        viz_utils.visualize_boxes_and_labels_on_image_array(
            image_np_with_detections,
            detections['detection_boxes'],
            detections['detection_classes'],
            detections['detection_scores'],
            categories,
            use_normalized_coordinates=True,
            max_boxes_to_draw=200,
            min_score_thresh=.4, # Adjust this value to set the minimum probability boxes to be classified as True
            agnostic_mode=False)
    
        return image_np_with_detections



    def send_email(self, user:User, reporte: ReporteCiudadano | ReporteTrabajador):
        # Variables dentro del correo
        nombre = user.name
        folio = reporte.id
        estado = "Aceptado" if reporte.valido else "Rechazado"  # Puede ser "Aceptado" o "Rechazado"

        """descripcion = ""
        if(type(reporte)== ReporteCiudadano): 
            descripcion = reporte.descripcion
        elif(type(reporte)== ReporteTrabajador):
            descripcion = reporte.comentarios"""
        lugar = reporte.direccion.calle + ' ' + reporte.direccion.alcaldia.alcaldia + ' ' + str(reporte.cp)

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Información del email
        email_sender = settings.EMAIL_SENDER
        email_receiver = user.email
        password = settings.EMAIL_SENDER_PASSWORD
        subject = "Registro de solicitud"

        # Definimos la ruta de la imagen (opcional)
        image_path = BASE_DIR+'/reportes/bacheo.png'
        # Leemos la imagen si está disponible
        img_data = None
        if os.path.exists(image_path):
            with open(image_path, 'rb') as img:
                img_data = img.read()

        # Creamos el email
        em = MIMEMultipart("related")
        em["From"] = email_sender
        em["To"] = email_receiver
        em["Subject"] = subject

        # Cuerpo del correo en HTML con formato
        body = f"""
        <html>
        <body style="background-color: #f2f2f2; padding: 20px; margin: 0;">
            <div style="background-color: #ffffff; max-width: 600px; margin: 0 auto; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); text-align: center;">
            <h2 style="color: #333333;">Hola, {nombre}.</h2>
            <p>Gracias por confiar en BacheoApp.</p>
            <p>Hemos validado tu petición de reporte.</p>
            <p>El estado de tu reporte en {lugar} es:</p>
            <div style="margin: 20px 0;">
                <span style="display: inline-block; padding: 10px 20px; border-radius: 5px; background-color: {'#4CAF50' if estado == 'Aceptado' else '#f44336'}; color: #ffffff; font-weight: bold;">
                {estado}
                </span>
            </div>
            <p>Folio: {folio}</p>
            {'<img src="cid:image1" style="max-width: 100%; height: auto; margin-top: 20px; border-radius: 10px;">' if img_data else ''}
            </div>
        </body>
        </html>
        """
        try: 
            em.attach(MIMEText(body, 'html'))

            # Adjuntamos la imagen si está disponible
            if img_data:
                image = MIMEImage(img_data, name=os.path.basename(image_path))
                image.add_header('Content-ID', '<image1>')
                em.attach(image)
            print("LLEGA AQUI A ENVIAR EL EMAIL")
            # Contexto de SSL y envío del email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(email_sender, password)
                smtp.sendmail(email_sender, email_receiver, em.as_string())
                print("ENVIA EMAIL")
        except Exception as e:
            print(f"Error al enviar el email: {e}")