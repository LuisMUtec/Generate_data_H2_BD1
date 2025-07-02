# Script para cargar datos CSV a PostgreSQL en Docker (Windows)
# Autor: AI Assistant

# Configuración
$CONTAINER_ID = "788ab163529b5b709731a5f281ab5f93af4e5b9360ea210b58222bbbd6ab647c"
$DB_USER = "postgres"  # Cambia este valor por tu usuario de PostgreSQL
$DB_NAME = "postgres"  # Cambia este valor por tu base de datos

Write-Host "Iniciando carga de datos a PostgreSQL..." -ForegroundColor Green
Write-Host "Contenedor: $CONTAINER_ID" -ForegroundColor Cyan
Write-Host "Usuario: $DB_USER" -ForegroundColor Cyan
Write-Host "Base de datos: $DB_NAME" -ForegroundColor Cyan
Write-Host ""

# Función para manejar errores
function Handle-Error {
    param($ErrorMessage)
    Write-Host "Error en: $ErrorMessage" -ForegroundColor Red
    exit 1
}

# Paso 1: Copiar archivos CSV al contenedor
Write-Host "Copiando archivos CSV al contenedor..." -ForegroundColor Yellow

try {
    docker cp datos_1000/cabina.csv ${CONTAINER_ID}:/tmp/cabina.csv
    docker cp datos_1000/especialidad.csv ${CONTAINER_ID}:/tmp/especialidad.csv
    docker cp datos_1000/personal.csv ${CONTAINER_ID}:/tmp/personal.csv
    docker cp datos_1000/paciente.csv ${CONTAINER_ID}:/tmp/paciente.csv
    docker cp datos_1000/medico.csv ${CONTAINER_ID}:/tmp/medico.csv
    docker cp datos_1000/medico_especialidad.csv ${CONTAINER_ID}:/tmp/medico_especialidad.csv
    docker cp datos_1000/consultorio.csv ${CONTAINER_ID}:/tmp/consultorio.csv
    docker cp datos_1000/turno.csv ${CONTAINER_ID}:/tmp/turno.csv
    docker cp datos_1000/cita.csv ${CONTAINER_ID}:/tmp/cita.csv
    
    Write-Host "Todos los archivos CSV copiados exitosamente" -ForegroundColor Green
} 
catch {
    Handle-Error "copia de archivos CSV"
}

Write-Host ""

# Paso 2: Crear script SQL CORREGIDO
Write-Host "Creando script SQL..." -ForegroundColor Yellow

$sqlScript = @"
-- Script para cargar datos CSV a PostgreSQL
\echo 'Cargando datos de cabina...'
\COPY cabina (numero, ubicacion) FROM '/tmp/cabina.csv' DELIMITER ',' CSV HEADER;

\echo 'Cargando datos de especialidad...'
\COPY especialidad (nombre, descripcion) FROM '/tmp/especialidad.csv' DELIMITER ',' CSV HEADER;

\echo 'Cargando datos de personal...'
\COPY personal (dni, nombre, apellido, fecha_nacimiento, sexo, correo, telefono) FROM '/tmp/personal.csv' DELIMITER ',' CSV HEADER;

\echo 'Cargando datos de paciente...'
\COPY paciente (dni, nombre, apellido, fecha_nacimiento, sexo, correo, telefono, tipo_seguro, fecha_registro) FROM '/tmp/paciente.csv' DELIMITER ',' CSV HEADER;

\echo 'Cargando datos de medico...'
\COPY medico (dni, nombre, apellido, fecha_nacimiento, sexo, correo, telefono) FROM '/tmp/medico.csv' DELIMITER ',' CSV HEADER;

\echo 'Cargando datos de consultorio...'
\COPY consultorio (numero, ubicacion) FROM '/tmp/consultorio.csv' DELIMITER ',' CSV HEADER;

\echo 'Cargando datos de medico_especialidad...'
\COPY medico_especialidad (dni_medico, nombre_especialidad) FROM '/tmp/medico_especialidad.csv' DELIMITER ',' CSV HEADER;

\echo 'Cargando datos de turno...'
\COPY turno (dni_personal, numero_cabina, fecha, horario) FROM '/tmp/turno.csv' DELIMITER ',' CSV HEADER;

\echo 'Cargando datos de cita...'
\COPY cita (dni_paciente, dni_medico, fecha, hora, estado, dni_personal, numero_consultorio) FROM '/tmp/cita.csv' DELIMITER ',' CSV HEADER;

\echo ''
\echo '=== VERIFICACION DE DATOS CARGADOS ==='
SELECT 'cabina' AS tabla, COUNT(*) AS registros FROM cabina
UNION ALL
SELECT 'especialidad' AS tabla, COUNT(*) AS registros FROM especialidad
UNION ALL
SELECT 'personal' AS tabla, COUNT(*) AS registros FROM personal
UNION ALL
SELECT 'paciente' AS tabla, COUNT(*) AS registros FROM paciente
UNION ALL
SELECT 'medico' AS tabla, COUNT(*) AS registros FROM medico
UNION ALL
SELECT 'consultorio' AS tabla, COUNT(*) AS registros FROM consultorio
UNION ALL
SELECT 'medico_especialidad' AS tabla, COUNT(*) AS registros FROM medico_especialidad
UNION ALL
SELECT 'turno' AS tabla, COUNT(*) AS registros FROM turno
UNION ALL
SELECT 'cita' AS tabla, COUNT(*) AS registros FROM cita
ORDER BY tabla;

\echo ''
\echo 'Carga de datos completada exitosamente!'
"@

# Paso 3: Crear archivo SQL temporal
$sqlScript | Out-File -FilePath "load_data.sql" -Encoding UTF8

# Paso 4: Copiar script SQL al contenedor
Write-Host "Copiando script SQL al contenedor..." -ForegroundColor Yellow
try {
    docker cp load_data.sql ${CONTAINER_ID}:/tmp/load_data.sql
    Write-Host "Script SQL copiado exitosamente" -ForegroundColor Green
}
catch {
    Handle-Error "copia del script SQL"
}

Write-Host ""

# Paso 5: Ejecutar script SQL
Write-Host "Ejecutando carga de datos..." -ForegroundColor Yellow
try {
    docker exec -it $CONTAINER_ID psql -U $DB_USER -d $DB_NAME -f /tmp/load_data.sql
    Write-Host "Datos cargados exitosamente!" -ForegroundColor Green
}
catch {
    Handle-Error "ejecución del script SQL"
}

# Limpiar archivo temporal
Remove-Item "load_data.sql" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Proceso completado!" -ForegroundColor Green
Write-Host "Revisa los conteos de registros arriba para verificar que todos los datos se cargaron correctamente." -ForegroundColor Cyan