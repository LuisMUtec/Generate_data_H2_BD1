#!/usr/bin/env python3
"""
generate_data.py

Genera datos sintéticos para las tablas del nuevo esquema:
  Paciente, Especialidad, Medico, Medico_Especialidad, Cabina,
  Consultorio, Personal, Turno y Cita

Cada tabla tendrá el mismo número de filas, indicado con --datos.

Requiere:
    pip install faker

Uso:
    python generate_data.py --datos 100000
"""

import argparse
import csv
import os
import random
from datetime import datetime, timedelta
from faker import Faker

def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

def random_time():
    h = random.randint(8, 18)
    m = random.randint(0, 59)
    s = random.randint(0, 59)
    return f"{h:02d}:{m:02d}:{s:02d}"

def generate_dni():
    """Genera un DNI de 8 dígitos"""
    return f"{random.randint(10000000, 99999999)}"

def main():
    parser = argparse.ArgumentParser(
        description="Genera datos sintéticos para todas las tablas.")
    parser.add_argument(
        '--datos', type=int, required=True,
        help='Número de filas a generar en cada tabla')
    args = parser.parse_args()

    N = args.datos
    fake = Faker()  # locale por defecto (en_US)

    # Crear directorio basado en el número de datos
    output_dir = f"datos_{N}"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Generando datos en el directorio: {output_dir}/")

    # Listas para almacenar los DNIs generados
    pacientes_dni = []
    medicos_dni = []
    personal_dni = []
    especialidades = []
    cabinas = []
    consultorios = []

    # 1) Paciente
    with open(os.path.join(output_dir, 'paciente.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([
            'dni','nombre','apellido','fecha_nacimiento',
            'sexo','correo','telefono','tipo_seguro','fecha_registro'
        ])
        for i in range(N):
            dni = generate_dni()
            while dni in pacientes_dni:  # Evitar duplicados
                dni = generate_dni()
            pacientes_dni.append(dni)
            
            dob = random_date(
                datetime(1940,1,1).date(),
                datetime(2005,12,31).date()
            )
            phone = fake.numerify('9########')
            w.writerow([
                dni,
                fake.first_name(),
                fake.last_name(),
                dob,
                random.choice(['M','F']),
                fake.unique.email(),
                phone,
                random.choice(['SIS','Essalud','Privado','Ninguno']),
                random_date(
                    datetime(2020,1,1).date(),
                    datetime(2025,6,28).date()
                )
            ])

    # 2) Especialidad
    with open(os.path.join(output_dir, 'especialidad.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['nombre','descripcion'])
        for i in range(int(N)):
            nombre = f"Especialidad_{i+1}"
            especialidades.append(nombre)
            w.writerow([
                nombre,
                fake.sentence(nb_words=6)
            ])

    # 3) Medico
    with open(os.path.join(output_dir, 'medico.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([
            'dni','nombre','apellido','fecha_nacimiento',
            'sexo','correo','telefono'
        ])
        for i in range(int(N)):
            dni = generate_dni()
            while dni in medicos_dni or dni in pacientes_dni:  # Evitar duplicados
                dni = generate_dni()
            medicos_dni.append(dni)
            
            dob = random_date(
                datetime(1960,1,1).date(),
                datetime(1990,12,31).date()
            )
            phone = fake.numerify('9########')
            w.writerow([
                dni,
                fake.first_name(),
                fake.last_name(),
                dob,
                random.choice(['M','F']),
                fake.unique.email(),
                phone
            ])

    # 4) Medico_Especialidad (Relación N:M)
    # Asegurar que cada médico tenga al menos una especialidad
    medico_especialidad_pairs = set()  # Para evitar duplicados
    
    with open(os.path.join(output_dir, 'medico_especialidad.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['dni_medico','nombre_especialidad'])
        
        # Primero, asignar al menos una especialidad a cada médico
        for medico_dni in medicos_dni:
            especialidad = random.choice(especialidades)
            pair = (medico_dni, especialidad)
            if pair not in medico_especialidad_pairs:
                medico_especialidad_pairs.add(pair)
                w.writerow([medico_dni, especialidad])
        
        # Luego, agregar más relaciones hasta completar N/10 registros
        target_count = max(len(medicos_dni), int(N/10))  # Al menos uno por médico
        while len(medico_especialidad_pairs) < target_count:
            medico_dni = random.choice(medicos_dni)
            especialidad = random.choice(especialidades)
            pair = (medico_dni, especialidad)
            if pair not in medico_especialidad_pairs:
                medico_especialidad_pairs.add(pair)
                w.writerow([medico_dni, especialidad])

    # 5) Cabina
    with open(os.path.join(output_dir, 'cabina.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['numero','ubicacion'])
        for i in range(int(N)):
            numero = f"C{i+1:04d}"
            cabinas.append(numero)
            w.writerow([
                numero,
                fake.city()
            ])

    # 6) Consultorio
    with open(os.path.join(output_dir, 'consultorio.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['numero','ubicacion'])

        print(f"Generando {N} consultorios...")  # Debug
        for i in range(N):
            numero = f"CONS{i+1:04d}"
            consultorios.append(numero)
            w.writerow([
                numero,
                fake.city()
            ])
        print(f"Consultorios generados: {len(consultorios)}")  # Debug

    # 7) Personal
    with open(os.path.join(output_dir, 'personal.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([
            'dni','nombre','apellido','fecha_nacimiento',
            'sexo','correo','telefono'
        ])
        for i in range(int(N)):
            dni = generate_dni()
            while dni in personal_dni or dni in pacientes_dni or dni in medicos_dni:  # Evitar duplicados
                dni = generate_dni()
            personal_dni.append(dni)
            
            dob = random_date(
                datetime(1970,1,1).date(),
                datetime(2000,12,31).date()
            )
            phone = fake.numerify('9########')
            w.writerow([
                dni,
                fake.first_name(),
                fake.last_name(),
                dob,
                random.choice(['M','F']),
                fake.unique.email(),
                phone
            ])

    # 8) Turno - NUEVA LÓGICA: todos los días, horarios y cabinas
    with open(os.path.join(output_dir, 'turno.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['dni_personal','numero_cabina','fecha','horario'])
        
        horarios = ['mañana', 'tarde', 'noche']
        
        # Fechas del período completo: 2024-01-01 a 2025-12-31
        fecha_inicio = datetime(2025, 7, 1).date()
        fecha_fin = datetime(2025, 8, 5).date()
        
        print(f"Generando turnos para el período {fecha_inicio} a {fecha_fin}")
        print(f"Cabinas disponibles: {len(cabinas)}")
        print(f"Personal disponible: {len(personal_dni)}")

        new_cabinas = cabinas[:int(N/100)]

        total_turnos = 0
        fecha_actual = fecha_inicio
        
        # Iterar día por día
        while fecha_actual <= fecha_fin:
            # Para cada día, generar los 3 horarios
            for horario in horarios:
                # Para cada horario, generar turnos para todas las cabinas
                for cabina in new_cabinas:
                    # Asignar personal aleatorio
                    personal_asignado = random.choice(personal_dni)
                    
                    w.writerow([
                        personal_asignado,
                        cabina,
                        fecha_actual,
                        horario
                    ])

                    if total_turnos >= N:
                        break
                    else:
                        total_turnos += 1
                if total_turnos >= N:
                    break
            if total_turnos >= N:
                break
            
            # Avanzar al siguiente día
            fecha_actual += timedelta(days=1)
            
            # Mostrar progreso cada 30 días
            if (fecha_actual - fecha_inicio).days % 30 == 0:
                print(f"Procesado hasta: {fecha_actual}, turnos generados: {total_turnos}")
        
        print(f"Total de turnos generados: {total_turnos}")
        print(f"Fórmula: {(fecha_fin - fecha_inicio).days + 1} días × 3 horarios × {len(cabinas)} cabinas = {((fecha_fin - fecha_inicio).days + 1) * 3 * len(cabinas)} turnos esperados")

    # 9) Cita - NO incluir id_cita (se genera automáticamente)
    with open(os.path.join(output_dir, 'cita.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        # Remover 'id_cita' del header
        w.writerow([
            'dni_paciente','dni_medico','fecha','hora',
            'estado','dni_personal','numero_consultorio'
        ])
        for i in range(N):
            w.writerow([
                random.choice(pacientes_dni),
                random.choice(medicos_dni),
                random_date(
                    datetime(2024,1,1).date(),
                    datetime(2025,6,28).date()
                ),
                random_time(),
                random.choice(['pendiente','confirmada','cancelada','atendida']),
                random.choice(personal_dni),
                random.choice(consultorios)
            ])

    print(f"Archivos CSV generados en el directorio: {output_dir}/")
    print("NOTA: La tabla 'turno' ahora contiene turnos para todos los días del período 2024-2025")

if __name__ == '__main__':
    main()

# docker run --name mi-postgres -e POSTGRES_PASSWORD=123 -p 5555:5432 -d postgres:15
# docker cp tu_archivo.csv 008a8db97481c4f96109d3a12bb9ff6e53ea9f7bf7fa7376df92318aa5496dff:/tmp/datos.csv