# nominas2excel
No busques datos personales, no hay :)
Todo lo que aquí puedas encontrar ya está publicado en mi LinkedIn.

Este repositorio contiene un flujo completo para poder realizar una extracción de datos desde un PDF, insertar dichos datos en una BD y luego poder realizar visualizaciones customizadas a través de una conexión con Metabase a dicha BD.

El proyecto está pensado para que tu puedas añadirte tus propias clases, teniendo en cuenta que cada clase implementa la forma particular de leer el PDF que quieras. Es decir, unos PDFs tendrán unas características y otros PDF otros. Se debe crear una clase para cada tipo de PDF.

El script obtiene los PDF de una carpeta en mi correo de iCloud, para otros proveedores de correo la implementación puede variar. Una vez se obtienen dichos PDF, la herramienta instancia la clase correspondiente y obtiene los campos a partir de un fichero .ini donde se definen los bounding box donde se encuentran los valores de los campos a leer. Los PDF únicamente se instancian si no se han analizado ya en la BD. Para ello se crea una tabla con PK el hash del fichero, y se comprueba si ya se ha analizado previamente.

Si no se analizado, se abre el fichero, se obtienen los campos y se insertan en la BD. Después el fichero se borra. Una vez se han analizado todos los ficheros, la carpeta completa se borra.

Es interesante explorar la posibilidad de utilizar https://github.com/openfaas/faas para la detección de nuevos correos con los archivos y que este evento dispare el job. Actualmente está desplegado en forma de cronjob.
