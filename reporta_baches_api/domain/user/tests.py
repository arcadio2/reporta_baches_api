

""" $url = "http://localhost:8000/reportes/trabajador/"

$body = @{
    ancho =10
    prioridad = "Alta"
    profundidad = 10
    tipo_bache = "grieta cocodrilo"
    estado_reporte = "Enviado"
    latitud = 0 
    longitud = 0   
    user = "15a245db03ad43dba2640dc7f5b2b88b"
}

$jsonBody = $body | ConvertTo-Json

$response = Invoke-RestMethod -Uri $url -Method Post -Body $jsonBody -ContentType "application/json"

$response

/**/



$url = "http://localhost:8000/reportes/ciudadano/"

$body = @{
    latitud = 0 
    longitud = 0   
    cp = 54469
    user = "15a245db03ad43dba2640dc7f5b2b88b"
    descripcion = "esta es una descripción"
    referencia_adicional = "XD"
    num_int = 10
    num_ext = 12
}

$jsonBody = $body | ConvertTo-Json

$response = Invoke-RestMethod -Uri $url -Method Post -Body $jsonBody -ContentType "application/json"

$response
 """